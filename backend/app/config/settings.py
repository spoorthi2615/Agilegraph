import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Literal

class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables.
    Provides configuration for the entire AgileGraph Backend.
    """
    ENVIRONMENT: Literal["development", "testing", "production"] = Field(
        default="development", 
        description="Deployment environment profile"
    )
    
    APP_NAME: str = "AgileGraph Backend"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False)
    
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    
    LOG_LEVEL: str = Field(default="INFO")
    
    # Storage Paths
    UPLOAD_DIRECTORY: str = Field(default="uploads")
    REPORT_DIRECTORY: str = Field(default="reports")
    
    # Neo4j Settings
    NEO4J_URI: str = Field(default="", description="Neo4j connection string (e.g. bolt://neo4j:7687)")
    NEO4J_USERNAME: str = Field(default="", description="Neo4j authentication username")
    NEO4J_PASSWORD: str = Field(default="", description="Neo4j authentication password")
    
    # Security / CORS
    CORS_ORIGINS: str = Field(default="*")
    SUPABASE_JWT_SECRET: str = Field(default="", description="JWT secret from Supabase to verify tokens")
    ADMIN_EMAILS: str = Field(
        default="spoorthipyadav@gmail.com,spoorthi2615@gmail.com",
        description="Comma separated list of admin emails"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


    @field_validator("UPLOAD_DIRECTORY", "REPORT_DIRECTORY")
    def validate_directories(cls, v):
        # Ensure directories exist
        os.makedirs(v, exist_ok=True)
        return v

# Using development-friendly fallbacks only if explicitly overriding via .env,
# but because fields don't have default values (e.g. NEO4J_URI), 
# they MUST be provided via env or the app crashes instantly (Fail-Fast).
settings = Settings()
