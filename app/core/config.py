from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "HR Connect Backend"
    SQLALCHEMY_DATABASE_URI: str  # ✅ directly loaded from .env
    groq_api_key: str

    class Config:
        env_file = ".env"

settings = Settings()
