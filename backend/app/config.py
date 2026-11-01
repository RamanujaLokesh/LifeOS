from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    openai_api_key: str = ""
    model_name: str = "gpt-4o-mini"
    database_url: str = ""
    jwt_secret: str = ""
    jwt_expire_minutes: int = 60 * 24 * 7   # 7 days
    allow_signup: bool = False
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

settings = Settings()