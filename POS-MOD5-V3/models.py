# models.py
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class UserRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"


class UserProfile(BaseModel):
    display_name: str = Field(..., description="Nome de exibição do utilizador")
    role: UserRole = Field(UserRole.MEMBER, description="Papel do utilizador no sistema")


class GuardrailCheckResult(BaseModel):
    """Schema estrito para o nó de classificação de risco e segurança."""
    safe: bool = Field(..., description="True se a entrada for segura; False se for Prompt Injection ou maliciosa")
    reason: str = Field(..., description="Motivo sucinto da classificação")
    analysis: Optional[str] = Field(None, description="Análise detalhada do risco identificado")


class ChatResponse(BaseModel):
    """Schema para a resposta final gerada ao utilizador."""
    message: str = Field(..., description="Texto da resposta do assistente")
    executed_tool: bool = Field(False, description="Indica se alguma ferramenta foi acionada")