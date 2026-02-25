# 🚢 Titanic Dataset Chat Agent

A complete, production-ready chat application that uses **LangChain**, **FastAPI**, and **Streamlit** to answer natural language questions about the Titanic dataset with intelligent data analysis and visualizations.

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Usage Examples](#usage-examples)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## ✨ Features

- **Natural Language Interface**: Ask questions in plain English about the Titanic dataset
- **Intelligent Analysis**: LangChain agent with specialized tools for data analysis
- **Automatic Visualizations**: Charts generated automatically when relevant
- **Conversation Memory**: Chat maintains context across multiple questions
- **Real-time Responses**: Fast processing with streaming capabilities
- **Modern UI**: Clean, responsive Streamlit interface
- **RESTful API**: FastAPI backend with comprehensive documentation
- **Production-Ready**: Proper error handling, logging, and configuration management

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance API framework
- **LangChain**: AI orchestration and agent framework
- **Groq**: Ultra-fast LLM inference (Mixtral-8x7b)
- **Pandas**: Data analysis and manipulation
- **Matplotlib**: Chart generation

### Frontend
- **Streamlit**: Interactive web interface
- **Requests**: API communication

### Data
- **Titanic Dataset**: Historic passenger data (CSV format)

## 📁 Project Structure

```
titanic-chat-agent/
├── backend/
│   ├── __init__.py
│   ├── app.py                 # FastAPI application
│   ├── agent.py               # LangChain agent implementation
│   ├── tools.py               # Data analysis tools
│   ├── data_loader.py         # Dataset loading and caching
│   ├── visualization.py       # Chart generation
│   └── config.py              # Configuration management
├── frontend/
│   ├── __init__.py
│   └── streamlit_app.py       # Streamlit UI
├── data/
│   └── Titanic-Dataset.csv    # Dataset (already present)
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- Groq API key ([Get one here](https://console.groq.com/))
- pip package manager

### Step 1: Clone or Navigate to Project

```powershell
cd "D:\Titanic Dataset Chat Agent Assignment\titanic-chat-agent"
```

### Step 2: Create Virtual Environment (Recommended)

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: Verify Installation

```powershell
python -c "import fastapi, langchain, streamlit, pandas; print('All packages installed successfully!')"
```

## ⚙️ Configuration

### Step 1: Create Environment File

Copy the example environment file:

```powershell
copy .env.example .env
```

### Step 2: Add Your Groq API Key

Edit the `.env` file and add your Groq API key:

```env
GROQ_API_KEY=gsk-your-actual-api-key-here
```

### Step 3: Adjust Settings (Optional)

You can customize other settings in `.env`:

- `MODEL_NAME`: Change AI model (default: mixtral-8x7b-32768, also available: llama3-70b-8192, gemma-7b-it)
- `API_PORT`: Change API port (default: 8000)
- `TEMPERATURE`: Adjust response creativity (0-1, default: 0)

## 🏃 Running the Application

### Method 1: Run Backend and Frontend Separately (Recommended)

#### Terminal 1 - Start Backend API:

```powershell
# Make sure you're in the project root directory
cd "D:\Titanic Dataset Chat Agent Assignment\titanic-chat-agent"

# Activate virtual environment
.\venv\Scripts\activate

# Run FastAPI backend
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

#### Terminal 2 - Start Streamlit Frontend:

```powershell
# Open a new terminal
cd "D:\Titanic Dataset Chat Agent Assignment\titanic-chat-agent"

# Activate virtual environment
.\venv\Scripts\activate

# Run Streamlit app
streamlit run frontend/streamlit_app.py
```

The UI will automatically open in your browser at: `http://localhost:8501`

### Method 2: Quick Start Scripts

Create these helper scripts in the project root:

**start_backend.ps1**:
```powershell
.\venv\Scripts\activate
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

**start_frontend.ps1**:
```powershell
.\venv\Scripts\activate
streamlit run frontend/streamlit_app.py
```

Then run:
```powershell
# Terminal 1
.\start_backend.ps1

# Terminal 2
.\start_frontend.ps1
```

## 💬 Usage Examples

### Example Questions

Try asking these questions in the chat interface:

1. **General Information**:
   - "Give me a summary of the dataset"
   - "How many passengers were on the Titanic?"

2. **Demographics**:
   - "What percentage of passengers were male?"
   - "What was the average age of passengers?"
   - "Show histogram of passenger ages"

3. **Survival Analysis**:
   - "What was the overall survival rate?"
   - "Survival rate by gender"
   - "Show survival distribution"
   - "Which class had the highest survival rate?"

4. **Economic Data**:
   - "What was the average ticket fare?"
   - "Show fare distribution"
   - "Compare average fares by class"

5. **Embarkation**:
   - "How many passengers embarked from each port?"
   - "Show embarkation distribution"

6. **Family Data**:
   - "How many passengers traveled alone?"
   - "What was the average family size?"

### Understanding Responses

The agent will:
- Provide detailed text answers with statistics
- Automatically generate relevant visualizations
- Maintain conversation context for follow-up questions
- Show loading indicators during processing

## 📚 API Documentation

### Endpoints

#### POST /chat
Ask a question about the dataset.

**Request**:
```json
{
  "question": "What percentage of passengers were male?"
}
```

**Response**:
```json
{
  "answer": "Approximately 64.76% of passengers were male...",
  "chart": "base64_encoded_image_or_null",
  "chart_type": "chart_type_or_null"
}
```

#### GET /health
Check API health status.

**Response**:
```json
{
  "status": "healthy",
  "dataset_loaded": true,
  "total_passengers": 891
}
```

#### GET /summary
Get dataset summary.

**Response**:
```json
{
  "total_passengers": 891,
  "total_survived": 342,
  "survival_rate": "38.38%",
  ...
}
```

#### POST /reset
Reset conversation memory.

**Response**:
```json
{
  "message": "Conversation memory reset successfully"
}
```

### Interactive API Docs

Visit `http://localhost:8000/docs` for interactive Swagger documentation where you can test all endpoints.

## 🌐 Deployment

### Deploy Backend (FastAPI)

#### Option 1: Local Server
```powershell
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

#### Option 2: Docker (Create Dockerfile)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ ./backend/
COPY data/ ./data/

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Option 3: Cloud Platforms
- **Railway**: Connect GitHub repo and deploy
- **Render**: Deploy as Web Service
- **AWS**: Use EC2 + Docker or Lambda
- **Heroku**: Use Procfile with uvicorn

### Deploy Frontend (Streamlit)

#### Option 1: Streamlit Cloud (Easiest)

1. Push code to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Set environment variables (API_BASE_URL)
5. Deploy!

#### Option 2: Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY frontend/ ./frontend/

CMD ["streamlit", "run", "frontend/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Option 3: Cloud Platforms
- **Heroku**: Use Procfile
- **AWS**: EC2 or ECS
- **Azure**: App Service
- **Google Cloud**: Cloud Run

### Environment Variables for Deployment

Set these in your deployment platform:

```env
GROQ_API_KEY=your_api_key
API_BASE_URL=https://your-backend-url.com
MODEL_NAME=mixtral-8x7b-32768
```

## 🔧 Troubleshooting

### Issue: API Returns 503 Error

**Solution**: Make sure you've set the GROQ_API_KEY in your `.env` file.

```powershell
# Check if .env file exists
cat .env

# If not, copy from example
copy .env.example .env
```

### Issue: "Module not found" Error

**Solution**: Install dependencies again:

```powershell
pip install -r requirements.txt --upgrade
```

### Issue: Streamlit Can't Connect to API

**Solutions**:
1. Verify backend is running: `http://localhost:8000/health`
2. Check CORS settings in `backend/config.py`
3. Update API_BASE_URL in Streamlit if needed:
   ```powershell
   $env:API_BASE_URL="http://localhost:8000"
   streamlit run frontend/streamlit_app.py
   ```

### Issue: Charts Not Displaying

**Solution**: Install matplotlib backend:

```powershell
pip install matplotlib pillow --upgrade
```

### Issue: Dataset Not Found

**Solution**: Verify the CSV file path in `backend/config.py` points to:
```
data/Titanic-Dataset.csv
```

### Issue: Groq Rate Limit

**Solution**: 
- Wait a few moments between requests
- Groq provides very generous free tier limits
- Use a different model if needed (llama3-70b-8192, gemma-7b-it)

### Issue: Permission Denied on Windows

**Solution**: Run PowerShell as Administrator or adjust execution policy:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📊 Features Deep Dive

### LangChain Agent Tools

The agent has access to these specialized tools:

1. **get_dataset_summary**: Overall dataset statistics
2. **calculate_gender_distribution**: Male/female passenger counts
3. **calculate_survival_rate**: Survival statistics by various categories
4. **calculate_average_fare**: Ticket fare analysis
5. **calculate_age_statistics**: Age distribution and statistics
6. **get_embarkation_distribution**: Port statistics
7. **get_class_distribution**: Class breakdown
8. **get_family_statistics**: Family relationships analysis

### Automatic Chart Generation

The system automatically generates charts for:

- Age histograms
- Embarkation port bar charts
- Class distribution charts
- Survival rate comparisons
- Fare distributions
- Pie charts for categorical data

### Conversation Memory

The agent maintains context across questions, allowing natural follow-ups like:

```
User: "What was the survival rate?"
Agent: "The overall survival rate was 38.38%..."

User: "How does that compare by gender?"
Agent: "Female passengers had a 74.20% survival rate..."
```

## 🤝 Contributing

To extend the project:

1. **Add New Tools**: Edit `backend/tools.py`
2. **Add Chart Types**: Edit `backend/visualization.py`
3. **Modify UI**: Edit `frontend/streamlit_app.py`
4. **Add Endpoints**: Edit `backend/app.py`

## 📝 License

This project is for educational purposes. The Titanic dataset is publicly available.

## 🙏 Acknowledgments

- Titanic dataset from Kaggle
- Groq for ultra-fast LLM inference
- LangChain community
- Streamlit team

## 📧 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API documentation at `/docs`
3. Verify environment variables are set correctly

---

**Built with ❤️ using FastAPI, LangChain, and Streamlit**

Happy analyzing! 🚢📊