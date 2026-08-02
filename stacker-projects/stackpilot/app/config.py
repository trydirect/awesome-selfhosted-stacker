from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://stackpilot:stackpilot@localhost:5432/stackpilot"
    redis_url: str = "redis://localhost:6379"
    ollama_base_url: str = "http://localhost:11434"
    n8n_webhook_url: str = ""
    secret_key: str = "change-me"
    ollama_model: str = "llama3.1"
    ollama_embed_model: str = "nomic-embed-text"
    admin_user: str = "admin"
    admin_password: str = "change-me"
    embed_dimensions: int = 768

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
