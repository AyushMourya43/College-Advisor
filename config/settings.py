import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Logs directory
LOGS_DIR = BASE_DIR / "logs"

# Data paths
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

# API keys / secrets (from .env)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# AIKosh API (AISHE College Directory)
AIKOSH_API_KEY = os.getenv("AIKOSH_API_KEY")
AIKOSH_API_BASE_URL = os.getenv("AIKOSH_API_BASE_URL")
AIKOSH_DATASET_ID = os.getenv("AIKOSH_DATASET_ID")
AIKOSH_VERSION = os.getenv("AIKOSH_VERSION")

# Embedding model
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
