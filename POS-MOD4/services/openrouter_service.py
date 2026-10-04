# services/openrouter_service.py
import logging
from typing import Type, TypeVar, Optional
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from config import settings

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)


class OpenRouterService:
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.default_model

        # Cliente Primário (OpenRouter)
        self.primary_client = ChatOpenAI(
            model=self.model_name,
            temperature=settings.temperature,
            openai_api_key=settings.openrouter_api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": settings.http_referer,
                "X-Title": settings.x_title,
            },
        )

        # Cliente Secundário (Fallback Oficial OpenAI)
        self.fallback_client = None
        if settings.openai_api_key:
            self.fallback_client = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=settings.temperature,
                openai_api_key=settings.openai_api_key,
            )

    async def generate_structured(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        schema: Type[T]
    ) -> T:
        """Gera uma saída estritamente vinculada a um Pydantic Schema com Fallback."""
        primary_llm = self.primary_client.with_structured_output(schema)

        if self.fallback_client:
            fallback_llm = self.fallback_client.with_structured_output(schema)
            runnable_llm = primary_llm.with_fallbacks([fallback_llm])
        else:
            runnable_llm = primary_llm

        messages = [
            ("system", system_prompt),
            ("human", user_prompt)
        ]

        result: T = await runnable_llm.ainvoke(messages)
        return result