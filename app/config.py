from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "MailFlow Application"
    APP_VERSION: str = "0.1.0"
    
    SARVAM_API_KEY: str
    GROQ_API_KEY: str
    GROQ_MODEL_NAME: str = "your-groq-model-name"
    
    DATABASE_URL: str = "sqlite+aiosqlite:///./mailflow.db"
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    
    CORS_ORIGINS: list[str] = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
