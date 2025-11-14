# from pydantic_settings import BaseSettings

# class Settings(BaseSettings):
#     APP_NAME: str = "HR Connect Backend"
#     SQLALCHEMY_DATABASE_URI: str  # ✅ directly loaded from .env

#     class Config:
#         env_file = ".env"

# settings = Settings()

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    SQLALCHEMY_DATABASE_URI: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Azure OpenAI
    AZURE_OPENAI_API_KEY: str | None = None
    AZURE_OPENAI_ENDPOINT: str | None = None
    AZURE_OPENAI_DEPLOYMENT: str | None = None
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"

    # Azure Embeddings
    AZURE_EMBEDDINGS_DEPLOYMENT: str | None = None
    AZURE_EMBEDDINGS_ENDPOINT: str | None = None
    AZURE_EMBEDDINGS_API_KEY: str | None = None

    GROQ_API_KEY: str

    class Config:
        env_file = ".env"  # loads variables from your .env file

# Create a single instance to import anywhere
settings = Settings()
