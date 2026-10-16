from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # LLM Auth
    openai_api_key: str = Field(..., validation_alias="OPENAI_API_KEY")
    default_model: str = Field("gpt-4o-mini", validation_alias="DEFAULT_MODEL")

    #Neo4j Auth
    neo4j_uri: str = Field("neo4j://localhost:7687", validation_alias="NEO4J_URI")
    neo4j_user: str = Field("neo4j", validation_alias="NEO4J_USER")
    neo4j_password: str = Field("password", validation_alias="NEO4J_PASSWORD")

    #Graph Limits
    max_correction_attemps: int = 1
    max_sub_questions: int = 3

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()