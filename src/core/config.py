from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application settings
    PROJECT_NAME: str = "SynthDrive RAG Service"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # Testing settings
    ENABLE_INTEGRATION_TESTS: bool = False
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    BACKEND_SERVICE_URL: str = "http://192.168.0.98:8000"
    
    # Database settings
    # PostgreSQL
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "synthdrive"
    POSTGRES_PORT: str = "5432"
    
    @property
    def POSTGRES_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Weaviate
    WEAVIATE_URL: str = "https://synthdrive-rag-service.weaviate.network"
    WEAVIATE_EMAIL: str
    WEAVIATE_PASSWORD: str
    WEAVIATE_API_KEY: str
    
    @property
    def WEAVIATE_URI(self) -> str:
        return f"{self.WEAVIATE_URL}"
    
    # Neo4j
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # LLM settings
    OPENAI_API_KEY: str
    GEMINI_API_KEY: str
    LLM_MODEL: str = "gpt-4-turbo"
    
    # OpenAI Embedding Model
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    
    # LangSmith settings
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_TRACING: Optional[str] = None
    LANGSMITH_PROJECT: Optional[str] = None
    
    # Model configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Create a global settings object
settings = Settings()