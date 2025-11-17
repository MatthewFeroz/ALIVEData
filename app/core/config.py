"""
Configuration settings for the application.
"""

import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings."""
    
    # API Configuration
    API_V1_PREFIX: str = "/api"
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        # Add your production frontend URL here
        # "https://your-app.vercel.app",
        # "https://your-domain.com",
    ]
    
    # File Upload Configuration
    UPLOAD_DIR: Path = Path("uploads")
    STATIC_DIR: Path = Path("static/uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".png", ".jpg", ".jpeg", ".gif", ".bmp"]
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Session Configuration
    SESSIONS_DIR: Path = Path("docs/sessions")
    
    # OCR Configuration
    TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", "")

settings = Settings()

