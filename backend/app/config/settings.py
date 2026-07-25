from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables.
    Provides configuration for the entire AgileGraph Backend.
    """
    APP_NAME: str = "AgileGraph Backend"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    UPLOAD_DIRECTORY: str = "uploads"
    LOG_LEVEL: str = "INFO"
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
