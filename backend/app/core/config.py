from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str
    DEEPGRAM_API_KEY: str
    GROQ_API_KEY: str
    OPENROUTER_EMBEDDING_KEY: str
    GOOGLE_API_KEY: str

    class Config:
        env_file = "../.env"
        extra = "ignore"

settings = Settings()
