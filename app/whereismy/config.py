import secrets
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... другие настройки ...
    database_url: str
    embedding_model_path: str = "paraphrase-multilingual-MiniLM-L12-v2"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    secret_key: str = secrets.token_urlsafe(32)
    model_config = {"env_file": ".env"}


settings = Settings()
