"""
config.py
---------
Central configuration for the AI Business Assistant.
All secrets are read from environment variables (via python-dotenv),
never hard-coded here.
"""

import os
from dotenv import load_dotenv

# Load variables from a .env file (if present) into the environment
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # --- Flask ---
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-fallback-secret-key-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "True") == "True"

    # --- Database ---
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'app.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- LLM / Demo Mode ---
    LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "none").lower()
    LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
    LLM_API_BASE = os.environ.get("LLM_API_BASE", "https://api.openai.com/v1")
    LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")

    # The app is considered to be in DEMO MODE whenever no usable API key/provider
    # is configured. This is checked at runtime (see ai/llm.py) so the app never
    # crashes just because an external AI service is unavailable.
    DEMO_MODE = (LLM_PROVIDER == "none") or (LLM_API_KEY.strip() == "")

    # --- Paths used across the app ---
    DATA_DIR = os.path.join(BASE_DIR, "data")
    KNOWLEDGE_BASE_DIR = os.path.join(BASE_DIR, "knowledge_base")
    ML_DIR = os.path.join(BASE_DIR, "ml")
    REPORTS_DIR = os.path.join(BASE_DIR, "reports")
    MODEL_PATH = os.path.join(ML_DIR, "model.pkl")
    ENCODERS_PATH = os.path.join(ML_DIR, "encoders.pkl")
    SEGMENTATION_MODEL_PATH = os.path.join(ML_DIR, "segmentation_model.pkl")
