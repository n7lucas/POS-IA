import logging
from typing import Type, TypeVar, Optional, Tuple
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from config import settings


logger = logging.getLogger(__name__)


# Variável de tipo para aceitar qualquer Schema Pydantic
#T can be any type you want, as long as it is a subclass of Pydantic's BaseModel
T = TypeVar('T', bound=BaseModel)

class LLMService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.default_model,
            temperature=0.0,
            api_key=settings.openai_api_key,
        )

    async def generate_structured(
            self, system_prompt: str, user_prompt: str, schema: Type[T]
    ) -> Tuple[Optional[T], Optional[str]]:
        """Encapsula a chamada estruturada, retornando (dados, erro)."""
        try:
            structured_llm = self.llm.with_structured_output(schema)
            messages  =[
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            response = await structured_llm.ainvoke(messages)

            return response, None
        except Exception as e:
            logger.error(f"Erro na geração estruturada: {str(e)}")
            return None, str(e)
           