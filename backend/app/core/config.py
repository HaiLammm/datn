from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, model_validator, EmailStr
from typing import Optional, Any
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    PROJECT_NAME: str = "DATN"
    API_V1_STR: str = "/api/v1"

    # Database configuration
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DATABASE_URL: Optional[PostgresDsn] = None

    @model_validator(mode='before')
    def assemble_db_connection(cls, v: Any) -> Any:
        if isinstance(v, dict) and not v.get("DATABASE_URL"):
            v["DATABASE_URL"] = PostgresDsn.build(
                scheme="postgresql+asyncpg",  # Use asyncpg driver
                username=v.get("DB_USER","luonghailam"),
                password=v.get("DB_PASSWORD","12070123a"),
                host=v.get("DB_HOST","localhost"),
                port=int(v.get("DB_PORT", 5432)),
                path=v.get("DB_NAME","datn"),  # Let PostgresDsn.build handle the leading slash
            )
        return v

    # Security settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    ENVIRONMENT: str = "development"  # "development" or "production"

    # Mail settings (ensure these are set in your .env file)
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int = 587
    MAIL_SERVER: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    MAIL_FROM_NAME: str = PROJECT_NAME
    
    # Path to email templates
    TEMPLATE_FOLDER: Path = Path(__file__).parent.parent / "templates"

    # Path for CV storage
    CV_STORAGE_PATH: Path = Path("data/cv_uploads")

    # AI/Ollama settings
    OLLAMA_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "llama3.1:8b"  # Changed from llama3.1:8b to reduce memory usage

    # ChromaDB / RAG settings
    CHROMA_PERSIST_PATH: Path = Path("data/chroma_db")
    CHROMA_COLLECTION_JOBS: str = "job_descriptions"
    CHROMA_COLLECTION_REFERENCE: str = "reference_docs"
    EMBEDDING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    RAG_TOP_K: int = 3
    RAG_MIN_SIMILARITY_SCORE: float = 0.3  # Minimum similarity score threshold
    RAG_RELEVANCE_CHECK_ENABLED: bool = True  # Enable career field relevance checking


settings = Settings()  # type: ignore
