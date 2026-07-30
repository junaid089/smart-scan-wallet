"""
App Core Configuration Module

Manages application settings using Pydantic Settings for environment variable loading.
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/smartscan_wallet"
    
    # OpenAI
    openai_api_key: str = ""
    
    # JWT Authentication
    secret_key: str = "change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Supabase Storage
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_bucket: str = "receipts"
    
    # Currency Settings
    default_currency: str = "INR"
    currency_symbol: str = "₹"
    
    # App info
    app_name: str = "Smart-Scan Wallet"
    app_version: str = "1.0.0"
    debug: bool = False


# Global settings instance
settings = Settings()
