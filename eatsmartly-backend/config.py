"""
Configuration module for EatSmartly backend.
Manages environment variables and application settings.
"""
import os
from typing import Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL connection string"
    )
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://:password@localhost:6379/0",
        description="Redis connection string"
    )
    REDIS_CACHE_TTL: int = Field(
        default=86400,  # 24 hours
        description="Redis cache TTL in seconds"
    )
    
    # API Keys
    GEMINI_API_KEY: Optional[str] = Field(
        default=None,
        description="Google Gemini API key for LLM"
    )
    USDA_API_KEY: str = Field(
        ...,
        description="USDA FoodData Central API key"
    )
    NUTRITIONIX_APP_ID: Optional[str] = Field(
        default=None,
        description="Nutritionix App ID"
    )
    NUTRITIONIX_APP_KEY: Optional[str] = Field(
        default=None,
        description="Nutritionix App Key"
    )
    
    # RapidAPI Configuration
    RAPIDAPI_KEY: Optional[str] = Field(
        default=None,
        description="RapidAPI Key for nutrition APIs"
    )
    RAPIDAPI_NUTRITIONAL_HOST: str = Field(
        default="ai-nutritional-facts.p.rapidapi.com",
        description="RapidAPI AI Nutritional Facts host"
    )
    RAPIDAPI_DIETAGRAM_HOST: str = Field(
        default="dietagram.p.rapidapi.com",
        description="RapidAPI DietaGram host"
    )
    
    # API Ninjas Configuration (Natural Language Nutrition)
    API_NINJAS_KEY: Optional[str] = Field(
        default=None,
        description="API Ninjas key for nutrition text extraction"
    )
    API_NINJAS_BASE_URL: str = Field(
        default="https://api.api-ninjas.com/v1",
        description="API Ninjas base URL"
    )
    
    # Application
    DEBUG: bool = Field(default=False)
    LOG_LEVEL: str = Field(default="INFO")
    
    # API Configuration
    API_TIMEOUT: int = Field(
        default=30,
        description="External API timeout in seconds"
    )
    MAX_RETRIES: int = Field(
        default=3,
        description="Maximum retries for failed API calls"
    )
    
    # USDA API Configuration
    USDA_BASE_URL: str = Field(
        default="https://api.nal.usda.gov/fdc/v1",
        description="USDA FoodData Central base URL"
    )
    
    # Nutritionix API Configuration
    NUTRITIONIX_BASE_URL: str = Field(
        default="https://trackapi.nutritionix.com/v2",
        description="Nutritionix API base URL"
    )
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        """Validate database URL."""
        if not v.startswith("postgresql://"):
            raise ValueError("DATABASE_URL must start with 'postgresql://'")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
