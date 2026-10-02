# config.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Keys
    openrouter_api_key: str = Field(..., validation_alias="OPENROUTER_API_KEY")
    openai_api_key: str = Field("", validation_alias="OPENAI_API_KEY")  # Chave Oficial OpenAI
    
    langchain_tracing_v2: str = Field("true", validation_alias="LANGCHAIN_TRACING_V2")
    langchain_api_key: str = Field("", validation_alias="LANGCHAIN_API_KEY")
    langchain_project: str = Field("appointment-agent", validation_alias="LANGCHAIN_PROJECT")

    http_referer: str = "http://localhost:3000"
    x_title: str = "IA Devs - Appointment Agent"

    # Modelos
    default_model: str = "google/gemini-2.0-flash-lite-preview-02-05:free"  # Primário (OpenRouter)
    fallback_model: str = "gpt-4o-mini"                                    # Secundário (OpenAI Direto)
    temperature: float = 0.2

    port: int = Field(3000, validation_alias="PORT")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()