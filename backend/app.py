"""FastAPI application for the Titanic Chat Agent."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging

from backend.agent import TitanicChatAgent
from backend.data_loader import data_loader
from backend.config import CORS_ORIGINS, GROQ_API_KEY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Titanic Chat Agent API",
    description="API for chatting about the Titanic dataset",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
chat_agent: Optional[TitanicChatAgent] = None


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    question: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What percentage of passengers were male?"
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: str
    chart: Optional[str] = None
    chart_type: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Approximately 64.76% of passengers were male.",
                "chart": None,
                "chart_type": None
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    dataset_loaded: bool
    total_passengers: int


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    global chat_agent
    
    try:
        logger.info("Starting Titanic Chat Agent API...")
        
        # Load dataset
        logger.info("Loading Titanic dataset...")
        df = data_loader.load_data()
        logger.info(f"Dataset loaded: {len(df)} passengers")
        
        # Initialize agent
        if not GROQ_API_KEY:
            logger.warning("Groq API key not found. Agent will not be initialized.")
            logger.warning("Set GROQ_API_KEY environment variable to enable the agent.")
        else:
            logger.info("Initializing chat agent...")
            chat_agent = TitanicChatAgent(api_key=GROQ_API_KEY)
            logger.info("Chat agent initialized successfully")
        
        logger.info("API startup complete!")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to the Titanic Chat Agent API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    try:
        df = data_loader.get_data()
        return HealthResponse(
            status="healthy",
            dataset_loaded=True,
            total_passengers=len(df)
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.get("/summary", tags=["Data"])
async def get_summary():
    """Get dataset summary."""
    try:
        summary = data_loader.get_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """Chat endpoint for asking questions about the Titanic dataset.
    
    Args:
        request: ChatRequest containing the user's question.
        
    Returns:
        ChatResponse with answer and optional chart.
    """
    global chat_agent
    
    if not chat_agent:
        raise HTTPException(
            status_code=503,
            detail="Chat agent not initialized. Please set GROQ_API_KEY environment variable."
        )
    
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        logger.info(f"Received question: {request.question}")
        
        # Get response from agent
        response = chat_agent.chat(request.question)
        
        return ChatResponse(
            answer=response["answer"],
            chart=response.get("chart"),
            chart_type=response.get("chart_type")
        )
    
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.post("/reset", tags=["Chat"])
async def reset_conversation():
    """Reset the conversation memory."""
    global chat_agent
    
    if not chat_agent:
        raise HTTPException(
            status_code=503,
            detail="Chat agent not initialized"
        )
    
    try:
        chat_agent.reset_memory()
        return {"message": "Conversation memory reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    from backend.config import API_HOST, API_PORT, API_RELOAD
    
    uvicorn.run(
        "backend.app:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_RELOAD
    )
