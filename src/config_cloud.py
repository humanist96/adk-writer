"""
Configuration module for Streamlit Cloud deployment
"""

import os
from typing import Dict, Any
from pathlib import Path
import streamlit as st

class Config:
    """Application configuration class for Streamlit Cloud"""
    
    # Try to get from Streamlit secrets first, then environment variables
    try:
        # Google AI Configuration
        GOOGLE_API_KEY = st.secrets["google"]["api_key"]
        GOOGLE_PROJECT_ID = st.secrets["google"].get("project_id", "")
        GOOGLE_LOCATION = st.secrets["google"].get("location", "us-central1")
        
        # Model Configuration
        MODEL_NAME = st.secrets["model"].get("name", "gemini-1.5-flash")
        TEMPERATURE = float(st.secrets["model"].get("temperature", 0.7))
        MAX_OUTPUT_TOKENS = int(st.secrets["model"].get("max_output_tokens", 2048))
        
        # Loop Agent Settings
        MAX_ITERATIONS = int(st.secrets["app"].get("max_iterations", 5))
        QUALITY_THRESHOLD = float(st.secrets["app"].get("quality_threshold", 0.9))
        TIMEOUT_SECONDS = int(st.secrets["app"].get("timeout_seconds", 300))
    except:
        # Fallback to environment variables for local development
        from dotenv import load_dotenv
        load_dotenv()
        
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "")
        GOOGLE_LOCATION = os.getenv("GOOGLE_LOCATION", "us-central1")
        
        MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash")
        TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
        MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "2048"))
        
        MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "5"))
        QUALITY_THRESHOLD = float(os.getenv("QUALITY_THRESHOLD", "0.9"))
        TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "300"))
    
    # Application Settings
    APP_ENV = os.getenv("APP_ENV", "production")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./financial_writer.db")
    
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
        "grammar": 0.95,
        "terminology": 0.98,
        "compliance": 1.0,
        "clarity": 0.9,
        "professionalism": 0.9
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
            raise ValueError("GOOGLE_API_KEY is required. Please set it in Streamlit secrets or environment variables.")
        
        # Create necessary directories
        cls.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        return True

# Initialize configuration
config = Config()