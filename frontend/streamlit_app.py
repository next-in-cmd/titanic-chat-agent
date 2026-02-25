"""Streamlit frontend for the Titanic Chat Agent."""

import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image
import os
from typing import Optional

# Page configuration
st.set_page_config(
    page_title="Titanic Chat Agent",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .stButton>button {
        width: 100%;
        background-color: #2196f3;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1976d2;
    }
    .example-question {
        background-color: #fff3e0;
        padding: 0.5rem;
        border-radius: 0.3rem;
        border-left: 3px solid #ff9800;
        margin: 0.5rem 0;
        cursor: pointer;
    }
    .stats-box {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def check_api_health() -> bool:
    """Check if the API is healthy and accessible."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def get_dataset_summary() -> Optional[dict]:
    """Get dataset summary from API."""
    try:
        response = requests.get(f"{API_BASE_URL}/summary", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def send_question(question: str) -> Optional[dict]:
    """Send a question to the API and get response."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={"question": question},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")
        return None
    except Exception as e:
        st.error(f"Error communicating with API: {str(e)}")
        return None


def reset_conversation() -> bool:
    """Reset the conversation memory."""
    try:
        response = requests.post(f"{API_BASE_URL}/reset", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def display_image_from_base64(base64_string: str):
    """Display an image from base64 string."""
    try:
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        st.image(image, use_column_width=True)
    except Exception as e:
        st.error(f"Error displaying image: {str(e)}")


def initialize_session_state():
    """Initialize session state variables."""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'api_healthy' not in st.session_state:
        st.session_state.api_healthy = False


def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">🚢 Titanic Dataset Chat Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Ask questions about the Titanic passengers and get instant insights!</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📊 System Information")
        
        # Check API health
        if st.button("🔄 Check API Status"):
            with st.spinner("Checking API..."):
                st.session_state.api_healthy = check_api_health()
        
        if st.session_state.api_healthy or check_api_health():
            st.success("✅ API is online")
            st.session_state.api_healthy = True
            
            # Get and display dataset summary
            with st.spinner("Loading dataset info..."):
                summary = get_dataset_summary()
            
            if summary:
                st.markdown("### Dataset Overview")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Passengers", summary.get("total_passengers", "N/A"))
                    st.metric("Survived", summary.get("total_survived", "N/A"))
                with col2:
                    st.metric("Survival Rate", summary.get("survival_rate", "N/A"))
                    st.metric("Classes", len(summary.get("passenger_classes", [])))
        else:
            st.error("❌ API is offline")
            st.warning(f"Please ensure the backend is running at {API_BASE_URL}")
            st.info("Run: `python -m backend.app` or `uvicorn backend.app:app`")
        
        st.markdown("---")
        
        # Example questions
        st.markdown("### 💡 Example Questions")
        example_questions = [
            "What percentage of passengers were male?",
            "Show histogram of passenger ages",
            "What was the average ticket fare?",
            "How many passengers embarked from each port?",
            "Survival rate by gender",
            "Show survival distribution",
            "How many passengers were in each class?",
            "What's the average age of passengers?",
            "How many people traveled alone?",
        ]
        
        for i, question in enumerate(example_questions):
            if st.button(question, key=f"example_{i}"):
                st.session_state.current_question = question
        
        st.markdown("---")
        
        # Clear chat history
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            reset_conversation()
            st.success("Chat history cleared!")
            st.rerun()
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.info("""
        This chat agent uses:
        - **FastAPI** for the backend
        - **LangChain** for AI orchestration
        - **OpenAI GPT** for natural language understanding
        - **Pandas** for data analysis
        - **Matplotlib** for visualizations
        """)
    
    # Main chat interface
    if not st.session_state.api_healthy:
        st.warning("⚠️ Please check API status in the sidebar before asking questions.")
        return
    
    # Display chat history
    st.markdown("### 💬 Chat History")
    
    if not st.session_state.chat_history:
        st.info("👋 Ask me anything about the Titanic dataset! Try the example questions in the sidebar.")
    else:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
                    
                    # Display chart if available
                    if "chart" in message and message["chart"]:
                        with st.expander("📊 View Visualization", expanded=True):
                            display_image_from_base64(message["chart"])
    
    # Input area
    st.markdown("### ❓ Ask a Question")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        # Check if there's a question from example buttons
        default_question = st.session_state.get("current_question", "")
        user_question = st.text_input(
            "Your question:",
            value=default_question,
            placeholder="E.g., What percentage of passengers survived?",
            label_visibility="collapsed"
        )
        # Clear the saved question
        if "current_question" in st.session_state:
            del st.session_state.current_question
    
    with col2:
        send_button = st.button("Send 📤", use_container_width=True)
    
    # Process question
    if send_button and user_question.strip():
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_question
        })
        
        # Show loading spinner
        with st.spinner("🔍 Analyzing data..."):
            response = send_question(user_question)
        
        if response:
            # Add assistant response to history
            assistant_message = {
                "role": "assistant",
                "content": response.get("answer", "I couldn't generate an answer."),
            }
            
            if response.get("chart"):
                assistant_message["chart"] = response["chart"]
                assistant_message["chart_type"] = response.get("chart_type")
            
            st.session_state.chat_history.append(assistant_message)
        else:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "I'm sorry, I encountered an error processing your question. Please try again."
            })
        
        # Rerun to update the display
        st.rerun()
    
    elif send_button:
        st.warning("Please enter a question first!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>Built with ❤️ using Streamlit, FastAPI, and LangChain</p>
        <p>Analyzing the historic Titanic passenger dataset</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
