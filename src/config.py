"""
Configuration module for the Financial Writing AI System
"""

import os
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class"""
    
    # Google AI Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "")
    GOOGLE_LOCATION = os.getenv("GOOGLE_LOCATION", "us-central1")
    
    # Model Configuration
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-pro")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "2048"))
    
    # Application Settings
    APP_ENV = os.getenv("APP_ENV", "development")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./financial_writer.db")
    
    # Loop Agent Settings
    MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "5"))
    QUALITY_THRESHOLD = float(os.getenv("QUALITY_THRESHOLD", "0.9"))
    TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "300"))
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    TEMPLATES_DIR = BASE_DIR / "templates"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Document Types
    DOCUMENT_TYPES = {
        "email": "고객 안내 이메일",
        "proposal": "투자 제안서",
        "product_description": "금융 상품 설명서",
        "compliance_report": "규정 준수 보고서",
        "official_letter": "대외 공식 문서"
    }
    
    # Quality Criteria
    QUALITY_CRITERIA = {
        "grammar": 0.95,  # 문법 정확도
        "terminology": 0.98,  # 금융 용어 정확성
        "compliance": 1.0,  # 규정 준수율
        "clarity": 0.9,  # 명확성
        "professionalism": 0.9  # 전문성
    }
    
    @classmethod
    def get_agent_config(cls) -> Dict[str, Any]:
        """Get configuration for ADK agents"""
        return {
            "model": cls.MODEL_NAME,
            "temperature": cls.TEMPERATURE,
            "max_output_tokens": cls.MAX_OUTPUT_TOKENS,
            "api_key": cls.GOOGLE_API_KEY
        }
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required in environment variables")
        
        # Create necessary directories
        cls.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        return True

# Initialize configuration
config = Config()