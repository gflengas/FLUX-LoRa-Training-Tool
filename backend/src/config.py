import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).resolve().parents[2] / '.env')

# Configuration settings
XAI_API_KEY = os.getenv("XAI_API_KEY")
COMFYUI_URL = os.getenv("COMFYUI_URL", "http://127.0.0.1:8188").rstrip("/")
MODELS_DIR = Path(os.getenv("MODELS_DIR", Path(__file__).resolve().parents[2] / "models"))
INFERENCE_OUTPUT = Path(__file__).resolve().parents[2] / "outputs" / "inference"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRAINING_DIR = PROJECT_ROOT / ".runtime" / "training"
TRAINING_OUTPUT = PROJECT_ROOT / "outputs" / "training"
TRAINING_IMAGE = os.getenv("TRAINING_IMAGE", "lora-studio-training:local")
