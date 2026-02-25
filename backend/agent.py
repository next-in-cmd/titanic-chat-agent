"""LangChain agent for the Titanic dataset chat system."""

from typing import Dict, Optional
import logging
import re

from langchain.agents import AgentExecutor, initialize_agent, AgentType
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

from backend.tools import create_titanic_tools
from backend.data_loader import data_loader
from backend.visualization import chart_generator
from backend.config import GROQ_API_KEY, MODEL_NAME, TEMPERATURE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TitanicChatAgent:
    """Chat agent for answering questions about the Titanic dataset."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the chat agent.
        
        Args:
            api_key: Groq API key. If None, uses config value.
        """
        self.api_key = api_key or GROQ_API_KEY
        if not self.api_key:
            raise ValueError("Groq API key is required")
        
        # Initialize LLM with correct parameters for langchain-groq 0.1.3
        self.llm = ChatGroq(
            groq_api_key=self.api_key,
            model_name=MODEL_NAME,
            temperature=TEMPERATURE
        )
        
        # Initialize tools
        self.tools = create_titanic_tools()
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create agent
        self.agent_executor = self._create_agent()
        
        # Load dataset
        self.df = data_loader.get_data()
    
    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent with tools.
        
        Returns:
            Configured AgentExecutor.
        """
        system_message = """You are a helpful data analyst assistant specializing in the Titanic dataset. 
Your role is to answer questions about the Titanic passengers using the available tools.

Guidelines:
1. Use the provided tools to analyze the data accurately
2. Always provide specific numbers and percentages when available
3. Be conversational and helpful
4. When users ask to "show", "display", "visualize", "chart", "graph", or "plot" data, mention that a visualization will be generated
5. For questions about distributions, comparisons, or breakdowns, suggest that visualizations are available
6. When discussing statistics, provide context to make them meaningful
7. If you're unsure, use the dataset_summary tool first

Available information:
- Passenger demographics (age, sex, class)
- Survival data
- Ticket fares
- Embarkation ports
- Family relationships (siblings/spouses, parents/children)

IMPORTANT: When users request visualizations (using words like "show", "display", "histogram", "chart", "graph", "plot"), 
acknowledge this in your response and mention that a chart is being generated.

Always strive to give complete, accurate answers based on the data."""
        
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True,
            agent_kwargs={
                "prefix": system_message
            }
        )
    
    def _should_generate_chart(self, question: str, answer: str) -> Optional[str]:
        """Determine if a chart should be generated based on the question and answer.
        
        Args:
            question: User's question.
            answer: Agent's answer.
            
        Returns:
            Chart type to generate, or None.
        """
        question_lower = question.lower()
        
        # Keywords that suggest visualizations
        show_keywords = ['show', 'display', 'visualize', 'plot', 'graph', 'chart']
        histogram_keywords = ['histogram', 'distribution of age', 'age distribution', 'show age']
        bar_keywords = ['bar chart', 'bar graph', 'embark', 'port', 'class distribution']
        pie_keywords = ['pie chart', 'pie graph']
        survival_keywords = ['survival', 'survived', 'survive']
        
        # Check for explicit visualization requests first
        has_show_keyword = any(keyword in question_lower for keyword in show_keywords)
        
        # Age histogram
        if 'age' in question_lower and (has_show_keyword or any(kw in question_lower for kw in histogram_keywords)):
            return 'age_histogram'
        
        # Embarkation distribution
        if ('embark' in question_lower or 'port' in question_lower) and (has_show_keyword or 'distribution' in question_lower):
            return 'embarkation_bar'
        
        # Class distribution
        if 'class' in question_lower and (has_show_keyword or 'distribution' in question_lower):
            return 'class_distribution'
        
        # Survival by gender
        if any(kw in question_lower for kw in survival_keywords) and 'gender' in question_lower:
            return 'survival_by_gender'
        
        # Survival distribution pie chart
        if any(kw in question_lower for kw in survival_keywords) and (has_show_keyword or 'distribution' in question_lower):
            return 'survival_pie'
        
        # Fare distribution
        if 'fare' in question_lower and (has_show_keyword or 'distribution' in question_lower or 'histogram' in question_lower):
            return 'fare_histogram'
        
        return None
    
    def _generate_chart(self, chart_type: str) -> Optional[str]:
        """Generate a chart based on the type.
        
        Args:
            chart_type: Type of chart to generate.
            
        Returns:
            Base64 encoded chart image, or None.
        """
        try:
            if chart_type == 'age_histogram':
                return chart_generator.create_histogram(
                    data=self.df['Age'],
                    title='Distribution of Passenger Ages',
                    xlabel='Age (years)',
                    bins=30,
                    color='#3498db'
                )
            
            elif chart_type == 'embarkation_bar':
                embark_counts = self.df['Embarked'].value_counts()
                port_names = {
                    'S': 'Southampton',
                    'C': 'Cherbourg',
                    'Q': 'Queenstown'
                }
                labels = [port_names.get(port, port) for port in embark_counts.index]
                return chart_generator.create_bar_chart(
                    labels=labels,
                    values=embark_counts.values.tolist(),
                    title='Passengers by Embarkation Port',
                    xlabel='Port',
                    ylabel='Number of Passengers',
                    color='#2ecc71'
                )
            
            elif chart_type == 'class_distribution':
                class_counts = self.df['Pclass'].value_counts().sort_index()
                labels = [f'Class {c}' for c in class_counts.index]
                return chart_generator.create_bar_chart(
                    labels=labels,
                    values=class_counts.values.tolist(),
                    title='Passengers by Class',
                    xlabel='Passenger Class',
                    ylabel='Number of Passengers',
                    color='#9b59b6'
                )
            
            elif chart_type == 'survival_by_gender':
                survival_by_gender = self.df.groupby('Sex')['Survived'].agg(['sum', 'count'])
                survival_by_gender['rate'] = (survival_by_gender['sum'] / survival_by_gender['count']) * 100
                
                labels = [sex.capitalize() for sex in survival_by_gender.index]
                return chart_generator.create_bar_chart(
                    labels=labels,
                    values=survival_by_gender['rate'].values.tolist(),
                    title='Survival Rate by Gender',
                    xlabel='Gender',
                    ylabel='Survival Rate (%)',
                    color='#e74c3c'
                )
            
            elif chart_type == 'survival_pie':
                survival_counts = self.df['Survived'].value_counts()
                labels = ['Survived', 'Perished']
                values = [survival_counts.get(1, 0), survival_counts.get(0, 0)]
                return chart_generator.create_pie_chart(
                    labels=labels,
                    values=values,
                    title='Survival Distribution',
                    colors=['#2ecc71', '#e74c3c']
                )
            
            elif chart_type == 'fare_histogram':
                return chart_generator.create_histogram(
                    data=self.df['Fare'],
                    title='Distribution of Ticket Fares',
                    xlabel='Fare ($)',
                    bins=50,
                    color='#f39c12'
                )
            
            return None
        
        except Exception as e:
            logger.error(f"Error generating chart: {e}")
            return None
    
    def chat(self, question: str) -> Dict[str, any]:
        """Process a user question and return an answer with optional chart.
        
        Args:
            question: User's question about the Titanic dataset.
            
        Returns:
            Dictionary containing answer and optional chart.
        """
        try:
            logger.info(f"Processing question: {question}")
            
            # Get answer from agent
            response = self.agent_executor.invoke({"input": question})
            answer = response.get("output", "I couldn't process that question.")
            
            # Determine if a chart should be generated
            chart_type = self._should_generate_chart(question, answer)
            chart_data = None
            
            if chart_type:
                logger.info(f"Generating chart: {chart_type}")
                chart_data = self._generate_chart(chart_type)
            
            return {
                "answer": answer,
                "chart": chart_data,
                "chart_type": chart_type
            }
        
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return {
                "answer": f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question.",
                "chart": None,
                "chart_type": None
            }
    
    def reset_memory(self):
        """Reset the conversation memory."""
        self.memory.clear()
        logger.info("Conversation memory cleared")
