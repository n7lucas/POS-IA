from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    #API Keys and OpenRouter
    openrouter_api_key: str = Field(..., validation_alias="OPENROUTER_API_KEY")
    openai_api_key: str = Field(..., validation_alias="OPENAI_API_KEY")
    default_model: str = "google/gemini-2.0-flash-lite-preview-02-05:free"
    temperature: float = 0.3

    # Headers
    http_referer: str = "http://localhost:3000"
    x_title: str = "IA Devs - Song Highlights Recommender"

    #Banco de Dados
    postgres_url: str = Field("postgresql://postgres:postgres@localhost:5432/song_highlights",
        validation_alias="POSTGRES_URI"
    )

    sqlite_db_path: str = Field("preferences.db", validate_alias="SQLITE_DB_PATH")

    # Limite de Controle de Janela de Contexto
    max_messages_to_summary: int = Field(4, validation_alias="MAX_MESSAGES_TO_SUMMARY")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
