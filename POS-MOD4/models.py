# models.py
from typing import List, Optional
from pydantic import BaseModel, Field


class UserPreferences(BaseModel):
    """Objeto que armazena as preferências de longo prazo do usuário."""
    name: Optional[str] = Field(None, description="Nome do usuário")
    age: Optional[int] = Field(None, description="Idade do usuário")
    favorite_genres: List[str] = Field(default_factory=list, description="Gêneros musicais preferidos")
    favorite_artists: List[str] = Field(default_factory=list, description="Artistas ou bandas favoritos")
    additional_info: Optional[str] = Field(None, description="Informações de contexto adicionais (ex: surfista, estuda ouvindo música)")


class ChatResponseSchema(BaseModel):
    """Schema de retorno do ChatNode, combinando mensagem ao usuário com extração de preferências."""
    message: str = Field(..., description="Resposta ao usuário focada no tema musical")
    should_save_preferences: bool = Field(False, description="Flag indicando se a mensagem revelou novas preferências")
    extracted_preferences: Optional[UserPreferences] = Field(None, description="Objeto com preferências extraídas se houver")


class SummarySchema(BaseModel):
    """Schema para o nó de sumarização incremental de histórico."""
    summary: str = Field(..., description="Resumo conciso mantendo pontos essenciais da conversa")