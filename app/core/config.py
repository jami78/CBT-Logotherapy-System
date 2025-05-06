from pydantic_settings import BaseSettings
from dotenv import load_dotenv

class Settings(BaseSettings):
    GROQ_API_KEY: str
    SERPER_API_KEY: str
    OPENAI_API_KEY: str
    TAVILY_API_KEY: str
    GOOGLE_API_KEY: str
    GOOGLE_CSE_ID: str
    SECRET_KEY: str
    ALGORITHM: str
    DATABASE_URL: str
    LANGSMITH_TRACING: str
    LANGSMITH_ENDPOINT: str
    LANGSMITH_API_KEY: str
    LANGSMITH_PROJECT: str

    class Config:
        env_file = ".env" 
        extra = "allow" 


def get_settings() -> Settings:
    load_dotenv(override=True)
    return Settings()


