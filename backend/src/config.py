import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("/home/emma/Desktop/FLUX LoRa Training Tool/.env")

# Configuration settings
XAI_API_KEY = os.getenv("XAI_API_KEY")
REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY")
TEMP_FOLDER = os.getenv("TEMP_FOLDER", "./temp")