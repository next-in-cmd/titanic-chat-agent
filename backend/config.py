"""Configuration settings for the Titanic Chat Agent backend."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data configuration
DATA_DIR = BASE_DIR / "data"
TITANIC_CSV_PATH = DATA_DIR / "Titanic-Dataset.csv"

# API configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_RELOAD = os.getenv("API_RELOAD", "True").lower() == "true"

# CORS settings
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8501,http://localhost:3000").split(",")

# LangChain configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))

# Visualization configuration
CHART_DPI = int(os.getenv("CHART_DPI", "100"))
CHART_FIGSIZE = (10, 6)
