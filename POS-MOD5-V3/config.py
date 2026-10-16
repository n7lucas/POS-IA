# config.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = Field(..., validation_alias="OPENAI_API_KEY")
    default_model: str = Field("gpt-4o-mini", validation_alias="DEFAULT_MODEL")
    safeguard_model: str = Field("gpt-4o-mini", validation_alias="SAFEGUARD_MODEL")
    guardrails_enabled: bool = Field(True, validation_alias="GUARDRAILS_ENABLED")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()