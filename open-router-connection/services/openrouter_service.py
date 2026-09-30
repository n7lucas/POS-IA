from typing import Dict, Any, Optional, List
from openai import AsyncOpenAI
from config import OpenRouterConfig, default_config

class OpenRouterService:
    def __init__(self, config_override: Optional[OpenRouterConfig] = None):
        # Permite injetar uma configuração alternativa (útil para testes)
        self.config = config_override or default_config
        
        # Inicializa o cliente apontando para o endpoint do OpenRouter
        self.client = AsyncOpenAI(
            api_key=self.config.api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": self.config.http_referer,
                "X-Title": self.config.x_title,
            }
        )

    async def generate_response(
        self, 
        user_message: str, 
        system_prompt: str = "Você é um assistente virtual prestativo e objetivo."
    ) -> Dict[str, Any]:
        """
        Executa a chamada ao OpenRouter enviando o sistema multi-modelo,
        parâmetros operacionais e estratégia de roteamento.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        # Payload estendido para o OpenRouter gerir o roteamento de fornecedores
        extra_body = {
            "models": self.config.models,
            "provider": {
                "sort": {
                    "by": self.config.provider_sort_by,
                    "partition": self.config.provider_partition,
                }
            }
        }

        # Chamada defensiva ao modelo
        response = await self.client.chat.completions.create(
            model=self.config.models[0],  # Modelo primário / fallback inicial
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            extra_body=extra_body
        )

        # Extração defensiva da resposta e observabilidade do modelo escolhido
        choice = response.choices[0] if response.choices else None
        content = choice.message.content if choice and choice.message else ""
        chosen_model = getattr(response, "model", "unknown")

        return {
            "model": chosen_model,
            "content": content
        }