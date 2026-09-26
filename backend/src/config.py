import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).resolve().parents[2] / '.env')

# Configuration settings
XAI_API_KEY = os.getenv("XAI_API_KEY")
