from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # API Security
    NEXTMIND_API_KEY: str = "default_secure_key_change_me"

    # OpenRouter (Unified API for all models)
    OPENROUTER_API_KEY: Optional[str] = None

    # OpenAI (For embeddings)
    OPENAI_API_KEY: Optional[str] = None

    # Retrieval APIs
    TAVILY_API_KEY: Optional[str] = None
    OPENALEX_EMAIL: Optional[str] = None
    SEMANTIC_SCHOLAR_API_KEY: Optional[str] = None
    LENS_API_KEY: Optional[str] = None

    # Vector DB
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None

    # Storage
    DATABASE_URL: str = "sqlite:///./nextmind.db"
    REDIS_URL: str = "redis://localhost:6379"

    # OpenRouter Model Mapping
    CHEAP_MODEL: str = "deepseek/deepseek-chat"
    REASONING_MODEL: str = "deepseek/deepseek-r1"
    CRITICAL_MODEL: str = "anthropic/claude-3.5-sonnet"
    EMBEDDING_MODEL: str = "text-embedding-3-small" # Embeddings still usually OpenAI or local

    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
