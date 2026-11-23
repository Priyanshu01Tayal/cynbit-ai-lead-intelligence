"""
Cynbit AI - Application Configuration
Loads environment variables and application constants.
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Cynbit AI Lead Intelligence"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    FRONTEND_PORT: int = 8501
    
    DATABASE_URL: str = "sqlite:///./data/cynbit_leads.db"
    
    ML_MODEL_PATH: str = "models/lead_classifier.joblib"
    ML_VECTORIZER_PATH: str = "models/tfidf_vectorizer.joblib"
    ML_METRICS_PATH: str = "models/model_metrics.json"
    
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

settings = Settings()
