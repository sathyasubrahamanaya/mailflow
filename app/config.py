from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "MailFlow Application"
    APP_VERSION: str = "0.1.0"
    
    SARVAM_API_KEY: str = "sk_wdvjyl40_bmgncR5HIn5tPB78IYffWxCC"
    GROQ_API_KEY: str ="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"
    GROQ_MODEL_NAME: str = "moonshotai/kimi-k2-instruct-0905"
    
    DATABASE_URL: str = "sqlite+aiosqlite:///./mailflow.db"
    CHATBASE_URL: str = "./mailflow.db"
    
    SECRET_KEY: str="abcd1234xef123sd"
    ALGORITHM: str = "HS256"
    
    CORS_ORIGINS: list[str] = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
