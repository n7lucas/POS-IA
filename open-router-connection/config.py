from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class OpenRouterConfig(BaseSettings):
    # A chave é obrigatória. Se não existir no .env ou ambiente, o Pydantic lança erro no startup.
    api_key: str =Field(..., validation_alias="OPENROUTER_API_KEY")

    #Headers exigidos pelo OpenRouter para identificação
    http_referer: str = "http://localhost:3000"    
    x_title: str= "IA DEVS - OpenRouter Integration"

    # Lista de modelos aceites (Roteamento Multi-Modelo)
    models: List[str] = [
        "arcee-ai/trinity-large-preview:free",
        "google/gemini-2.5-flash",
    ]
    
    # Estratégia de ordenação do roteador ("price", "latency", "throughput")
    provider_sort_by: str = "price"
    provider_partition: str = "none"
    
    # Parâmetros operacionais do modelo
    temperature: float = 0.7
    max_tokens: int = 1000
    
    # Porta do servidor
    port: int = Field(3000, validation_alias="PORT")

    class Config:
        env_file = ".env" # env_file = ".env" → Automatically load missing field values from a .env file.
        extra = "ignore" # Ignore extra environment variables in the file rather than raising a validation error.

# Instância padrão utilizada pela aplicação em produção
default_config = OpenRouterConfig()


