from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, model_validator, EmailStr
from typing import Optional, Any, Dict
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
                username=v.get("DB_USER"),
                password=v.get("DB_PASSWORD"),
                host=v.get("DB_HOST"),
                port=int(v.get("DB_PORT", 5432)),
                path=f"/{v.get('DB_NAME') or ''}",
            )
        return v

    # Security settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

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


settings = Settings()
