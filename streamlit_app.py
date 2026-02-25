"""
🚢 Titanic Dataset Chat Agent - Streamlit Cloud Deployment Version
Combined frontend and backend for Streamlit Cloud deployment.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import base64
from io import BytesIO
import logging
from typing import Optional
import os

# LangChain imports
from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, AgentType, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from langchain.schema import AIMessage, HumanMessage, SystemMessage

# Use non-interactive backend for matplotlib
matplotlib.use('Agg')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="🚢 Titanic Dataset Chat Agent",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CONFIGURATION & SECRETS MANAGEMENT
# ============================================================================

def load_config():
    """Load configuration from secrets or environment variables."""
    try:
        # Try Streamlit Cloud secrets first
        GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
        MODEL_NAME = st.secrets.get("MODEL_NAME", "llama-3.3-70b-versatile")
        TEMPERATURE = float(st.secrets.get("TEMPERATURE", "0"))
        CHART_DPI = int(st.secrets.get("CHART_DPI", "100"))
    except:
        # Fall back to environment variables for local development
        from dotenv import load_dotenv
        load_dotenv()
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
        TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))
        CHART_DPI = int(os.getenv("CHART_DPI", "100"))
    
    return {
        "GROQ_API_KEY": GROQ_API_KEY,
        "MODEL_NAME": MODEL_NAME,
        "TEMPERATURE": TEMPERATURE,
        "CHART_DPI": CHART_DPI
    }

config = load_config()

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data
def load_titanic_data():
    """Load and cache the Titanic dataset."""
    try:
        df = pd.read_csv('data/Titanic-Dataset.csv')
        logger.info(f"Loaded Titanic dataset with {len(df)} passengers")
        return df
    except Exception as e:
        logger.error(f"Error loading dataset: {e}")
        st.error(f"Failed to load dataset: {e}")
        return None

# Load dataset
df = load_titanic_data()

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def fig_to_base64(fig) -> str:
    """Convert matplotlib figure to base64 string."""
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=config['CHART_DPI'], bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return img_base64

def create_histogram(data: pd.Series, title: str, xlabel: str, bins: int = 30):
    """Create a histogram."""
    fig, ax = plt.subplots(figsize=(10, 6))
    clean_data = data.dropna()
    ax.hist(clean_data, bins=bins, color='#3498db', edgecolor='black', alpha=0.7)
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.grid(True, alpha=0.3)
    return fig

def create_bar_chart(labels: list, values: list, title: str, xlabel: str, ylabel: str):
    """Create a bar chart."""
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(labels, values, color='#2ecc71', edgecolor='black', alpha=0.7)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}', ha='center', va='bottom', fontsize=10)
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')
    return fig

def create_pie_chart(labels: list, values: list, title: str):
    """Create a pie chart."""
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, autopct='%1.1f%%',
        colors=colors[:len(labels)], startangle=90,
        textprops={'fontsize': 12}
    )
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    ax.set_title(title, fontsize=16, fontweight='bold')
    return fig

def create_grouped_bar_chart(data_df: pd.DataFrame, title: str, xlabel: str, ylabel: str):
    """Create a grouped bar chart."""
    fig, ax = plt.subplots(figsize=(10, 6))
    data_df.plot(kind='bar', ax=ax, color=['#3498db', '#e74c3c'], 
                 edgecolor='black', alpha=0.7)
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.legend(title='', fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    plt.xticks(rotation=45, ha='right')
    return fig

# ============================================================================
# TOOL FUNCTIONS (Backend Logic)
# ============================================================================

def get_dataset_summary(input: str = "") -> str:
    """Get comprehensive dataset summary."""
    if df is None:
        return "Error: Dataset not loaded"
    
    total = len(df)
    survived = df['Survived'].sum()
    survival_rate = (survived / total) * 100
    
    result = f"""📊 Dataset Summary:
- Total Passengers: {total}
- Total Survived: {int(survived)} ({survival_rate:.2f}%)
- Total Perished: {int(total - survived)} ({100-survival_rate:.2f}%)
- Passenger Classes: {sorted(df['Pclass'].unique())}
- Embarkation Ports: {sorted(df['Embarked'].dropna().unique().tolist())}
- Age Range: {df['Age'].min():.1f} to {df['Age'].max():.1f} years (mean: {df['Age'].mean():.1f})
- Fare Range: ${df['Fare'].min():.2f} to ${df['Fare'].max():.2f} (mean: ${df['Fare'].mean():.2f})
"""
    return result

def calculate_gender_distribution(input: str = "") -> str:
    """Calculate gender distribution."""
    if df is None:
        return "Error: Dataset not loaded"
    
    total = len(df)
    male_count = len(df[df['Sex'] == 'male'])
    female_count = len(df[df['Sex'] == 'female'])
    male_pct = (male_count / total) * 100
    female_pct = (female_count / total) * 100
    
    result = f"""Gender Distribution:
- Male: {male_count} passengers ({male_pct:.2f}%)
- Female: {female_count} passengers ({female_pct:.2f}%)
- Total: {total} passengers
"""
    
    # Store chart for display
    fig = create_pie_chart(['Male', 'Female'], [male_count, female_count], 
                          'Gender Distribution')
    st.session_state.current_chart = fig
    
    return result

def calculate_survival_rate(input: str = "") -> str:
    """Calculate survival rates."""
    if df is None:
        return "Error: Dataset not loaded"
    
    overall_survival = df['Survived'].mean() * 100
    total_survived = df['Survived'].sum()
    total = len(df)
    
    result = f"""Survival Statistics:
- Overall Survival Rate: {overall_survival:.2f}%
- Survived: {int(total_survived)} passengers
- Perished: {int(total - total_survived)} passengers

Survival by Gender:
"""
    for gender in ['male', 'female']:
        gender_df = df[df['Sex'] == gender]
        survival_rate = gender_df['Survived'].mean() * 100
        survived = gender_df['Survived'].sum()
        total_gender = len(gender_df)
        result += f"- {gender.capitalize()}: {survival_rate:.2f}% ({int(survived)}/{total_gender})\n"
    
    result += "\nSurvival by Class:\n"
    for pclass in sorted(df['Pclass'].unique()):
        class_df = df[df['Pclass'] == pclass]
        survival_rate = class_df['Survived'].mean() * 100
        survived = class_df['Survived'].sum()
        total_class = len(class_df)
        result += f"- Class {pclass}: {survival_rate:.2f}% ({int(survived)}/{total_class})\n"
    
    # Create pie chart
    fig = create_pie_chart(['Survived', 'Perished'], 
                          [int(total_survived), int(total - total_survived)],
                          'Overall Survival Distribution')
    st.session_state.current_chart = fig
    
    return result

def calculate_average_fare(input: str = "") -> str:
    """Calculate fare statistics."""
    if df is None:
        return "Error: Dataset not loaded"
    
    avg_fare = df['Fare'].mean()
    median_fare = df['Fare'].median()
    min_fare = df['Fare'].min()
    max_fare = df['Fare'].max()
    
    result = f"""Fare Statistics:
- Average Fare: ${avg_fare:.2f}
- Median Fare: ${median_fare:.2f}
- Minimum Fare: ${min_fare:.2f}
- Maximum Fare: ${max_fare:.2f}

Average Fare by Class:
"""
    for pclass in sorted(df['Pclass'].unique()):
        class_avg = df[df['Pclass'] == pclass]['Fare'].mean()
        result += f"- Class {pclass}: ${class_avg:.2f}\n"
    
    # Create histogram
    fig = create_histogram(df['Fare'], 'Fare Distribution', 'Fare ($)', bins=50)
    st.session_state.current_chart = fig
    
    return result

def calculate_age_statistics(input: str = "") -> str:
    """Calculate age statistics."""
    if df is None:
        return "Error: Dataset not loaded"
    
    age_data = df['Age'].dropna()
    
    result = f"""Age Statistics:
- Average Age: {age_data.mean():.2f} years
- Median Age: {age_data.median():.2f} years
- Minimum Age: {age_data.min():.2f} years
- Maximum Age: {age_data.max():.2f} years
- Standard Deviation: {age_data.std():.2f} years
- Total passengers with age data: {len(age_data)} out of {len(df)}
"""
    
    # Create histogram
    fig = create_histogram(age_data, 'Age Distribution of Passengers', 'Age (years)')
    st.session_state.current_chart = fig
    
    return result

def get_embarkation_distribution(input: str = "") -> str:
    """Get embarkation distribution."""
    if df is None:
        return "Error: Dataset not loaded"
    
    embark_counts = df['Embarked'].value_counts()
    total_with_data = embark_counts.sum()
    
    port_names = {
        'S': 'Southampton',
        'C': 'Cherbourg',
        'Q': 'Queenstown'
    }
    
    result = "Embarkation Port Distribution:\n"
    labels = []
    values = []
    
    for port, count in embark_counts.items():
        port_name = port_names.get(port, port)
        percentage = (count / total_with_data) * 100
        result += f"- {port_name} ({port}): {count} passengers ({percentage:.2f}%)\n"
        labels.append(f"{port_name}\n({port})")
        values.append(count)
    
    # Create bar chart
    fig = create_bar_chart(labels, values, 'Embarkation Port Distribution',
                          'Port', 'Number of Passengers')
    st.session_state.current_chart = fig
    
    return result

def get_class_distribution(input: str = "") -> str:
    """Get class distribution."""
    if df is None:
        return "Error: Dataset not loaded"
    
    class_counts = df['Pclass'].value_counts().sort_index()
    total = len(df)
    
    result = "Passenger Class Distribution:\n"
    labels = []
    values = []
    
    for pclass, count in class_counts.items():
        percentage = (count / total) * 100
        result += f"- Class {pclass}: {count} passengers ({percentage:.2f}%)\n"
        labels.append(f"Class {pclass}")
        values.append(count)
    
    # Create bar chart
    fig = create_bar_chart(labels, values, 'Passenger Class Distribution',
                          'Class', 'Number of Passengers')
    st.session_state.current_chart = fig
    
    return result

def get_family_statistics(input: str = "") -> str:
    """Get family statistics."""
    if df is None:
        return "Error: Dataset not loaded"
    
    df_copy = df.copy()
    df_copy['FamilySize'] = df_copy['SibSp'] + df_copy['Parch'] + 1
    
    alone = len(df_copy[df_copy['FamilySize'] == 1])
    with_family = len(df_copy[df_copy['FamilySize'] > 1])
    
    result = f"""Family Statistics:
- Passengers traveling alone: {alone} ({(alone/len(df_copy)*100):.2f}%)
- Passengers with family: {with_family} ({(with_family/len(df_copy)*100):.2f}%)
- Average family size: {df_copy['FamilySize'].mean():.2f} people
- Largest family: {int(df_copy['FamilySize'].max())} people
- Average siblings/spouses: {df_copy['SibSp'].mean():.2f}
- Average parents/children: {df_copy['Parch'].mean():.2f}
"""
    return result

# ============================================================================
# LANGCHAIN AGENT SETUP
# ============================================================================

def create_tools():
    """Create LangChain tools."""
    tools = [
        Tool(
            name="get_dataset_summary",
            func=get_dataset_summary,
            description="Get comprehensive summary of the Titanic dataset including total passengers, survival rate, age range, fare range. Use for general overview questions."
        ),
        Tool(
            name="calculate_gender_distribution",
            func=calculate_gender_distribution,
            description="Calculate gender distribution with counts and percentages. Shows pie chart. Use when asked about gender, male/female distribution."
        ),
        Tool(
            name="calculate_survival_rate",
            func=calculate_survival_rate,
            description="Calculate survival rates overall and by gender/class. Shows pie chart. Use when asked about survival, who survived, death statistics."
        ),
        Tool(
            name="calculate_average_fare",
            func=calculate_average_fare,
            description="Calculate fare statistics including average, median, min, max by class. Shows histogram. Use when asked about ticket prices, fares, costs."
        ),
        Tool(
            name="calculate_age_statistics",
            func=calculate_age_statistics,
            description="Calculate age statistics and show histogram. Use when asked about passenger ages, age distribution."
        ),
        Tool(
            name="get_embarkation_distribution",
            func=get_embarkation_distribution,
            description="Get embarkation port distribution (Southampton, Cherbourg, Queenstown). Shows bar chart. Use when asked about boarding locations."
        ),
        Tool(
            name="get_class_distribution",
            func=get_class_distribution,
            description="Get passenger class distribution (1st, 2nd, 3rd class). Shows bar chart. Use when asked about class distribution."
        ),
        Tool(
            name="get_family_statistics",
            func=get_family_statistics,
            description="Get family statistics including traveling alone vs with family. Use when asked about families, relationships."
        ),
    ]
    return tools

@st.cache_resource
def create_agent():
    """Create and cache the LangChain agent."""
    if not config['GROQ_API_KEY']:
        st.error("GROQ_API_KEY not found. Please configure in Streamlit secrets.")
        return None
    
    try:
        llm = ChatGroq(
            api_key=config['GROQ_API_KEY'],
            model=config['MODEL_NAME'],
            temperature=config['TEMPERATURE']
        )
        
        tools = create_tools()
        
        # Create agent with system message
        system_message = """You are a helpful data analyst specializing in the Titanic dataset.

IMPORTANT: When users request visualizations (using words like 'show', 'display', 'visualize', 'chart', 'graph', 'plot', 'histogram'), 
acknowledge this in your response and mention that a chart is being generated.

Provide clear, concise answers based on the data. Use the available tools to gather information.
When appropriate tools generate charts, they will be displayed automatically.

Be friendly, informative, and data-driven in your responses."""
        
        agent_executor = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            agent_kwargs={
                "prefix": system_message
            }
        )
        
        logger.info("LangChain agent created successfully")
        return agent_executor
        
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        st.error(f"Failed to create agent: {e}")
        return None

# Initialize agent
agent_executor = create_agent()

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'current_chart' not in st.session_state:
    st.session_state.current_chart = None

# ============================================================================
# USER INTERFACE
# ============================================================================

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #7f8c8d;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<div class="main-header">🚢 Titanic Dataset Chat Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ask me anything about the Titanic dataset! I can provide statistics and visualizations.</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📊 Dataset Overview")
    
    if df is not None:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Passengers", len(df))
            st.metric("Survivors", int(df['Survived'].sum()))
        with col2:
            st.metric("Perished", int((df['Survived'] == 0).sum()))
            st.metric("Survival Rate", f"{(df['Survived'].mean()*100):.1f}%")
        
        st.divider()
        
        st.subheader("💡 Example Questions")
        examples = [
            "What was the average ticket fare?",
            "Show me the age distribution",
            "How many passengers were in each class?",
            "What was the survival rate by gender?",
            "Display the embarkation port distribution",
            "Show survival statistics",
            "What's the gender distribution?",
            "Tell me about family statistics"
        ]
        
        for example in examples:
            if st.button(example, key=f"example_{example}", use_container_width=True):
                # Add to chat
                st.session_state.messages.append({"role": "user", "content": example})
                st.rerun()
        
        st.divider()
        
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.session_state.current_chart = None
            st.rerun()
        
        st.divider()
        st.caption("Powered by LangChain & Groq")
        st.caption(f"Model: {config['MODEL_NAME']}")
    else:
        st.error("Dataset not loaded!")

# Main chat interface
chat_container = st.container()

with chat_container:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "chart" in message and message["chart"] is not None:
                st.pyplot(message["chart"])

# Chat input
if prompt := st.chat_input("Ask about the Titanic dataset...", key="chat_input"):
    if df is None:
        st.error("Cannot process query: Dataset not loaded")
    elif agent_executor is None:
        st.error("Cannot process query: Agent not initialized")
    else:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analyzing data..."):
                try:
                    # Clear previous chart
                    st.session_state.current_chart = None
                    
                    # Run agent with simple input
                    response = agent_executor.invoke({"input": prompt})
                    
                    answer = response["output"]
                    st.markdown(answer)
                    
                    # Display chart if generated
                    chart_fig = None
                    if st.session_state.current_chart is not None:
                        chart_fig = st.session_state.current_chart
                        st.pyplot(chart_fig)
                    
                    # Save to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "chart": chart_fig
                    })
                    
                except Exception as e:
                    error_msg = f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question."
                    st.error(error_msg)
                    logger.error(f"Error processing query: {e}", exc_info=True)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "chart": None
                    })

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d;'>
    <p>Built with Streamlit • LangChain • Groq AI • Matplotlib</p>
    <p>Titanic Dataset Analysis & Q&A Agent</p>
</div>
""", unsafe_allow_html=True)
