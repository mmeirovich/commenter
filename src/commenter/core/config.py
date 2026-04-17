from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "Commenter API"
    app_version: str = "0.1.0"
    app_description: str = (
        "AI-powered post comment generator. "
        "Analyzes blog posts and generates thoughtful, opinionated comments "
        "using a multi-agent CrewAI pipeline."
    )
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    serper_api_key: str = ""

    log_level: str = "INFO"


settings = Settings()
