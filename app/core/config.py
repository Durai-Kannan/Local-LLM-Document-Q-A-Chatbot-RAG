import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = "Local RAG Chatbot"
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434")
    OLLAMA_MODEL: str = Field(default="qwen2.5:3b")
    CHROMA_PATH: str = Field(default="./data/chroma")
    DOCUMENTS_PATH: str = Field(default="./data/documents")
    EMBEDDING_MODEL: str = Field(default="all-MiniLM-L6-v2")
    TOP_K: int = Field(default=5)
    SCORE_THRESHOLD: float = Field(default=0.3)
    CHUNK_SIZE: int = Field(default=700)
    CHUNK_OVERLAP: int = Field(default=100)
    LOG_LEVEL: str = Field(default="INFO")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

os.makedirs(settings.CHROMA_PATH, exist_ok=True)
os.makedirs(settings.DOCUMENTS_PATH, exist_ok=True)
