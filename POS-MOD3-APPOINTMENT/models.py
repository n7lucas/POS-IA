# models.py
from typing import Literal, Optional
from pydantic import BaseModel, Field

# --- Entities do Sistema ---
class Professional(BaseModel):
    id: int
    name: str
    specialty: str

class Appointment(BaseModel):
    id: int
    professional_id: int
    date_time: str  # ISO string Ex: '2026-10-10T09:00:00'
    patient_name: str
    reason: str

# --- Structured Output Schema (Contrato com a LLM) ---
class IntentExtractionSchema(BaseModel):
    """Schema estrito para o nó identify_intent extrair da linguagem natural."""
    intent: Literal["schedule", "cancel", "unknown"] = Field(
        ..., description="Intenção identificada do usuário."
    )
    professional_id: Optional[int] = Field(
        None, description="ID numérico do profissional de saúde, se mencionado."
    )
    professional_name: Optional[str] = Field(
        None, description="Nome do profissional mencionado pelo usuário."
    )
    date_time: Optional[str] = Field(
        None, description="Data e hora resolvidas no formato YYYY-MM-DDTHH:MM:SS."
    )
    patient_name: Optional[str] = Field(
        None, description="Nome do paciente mencionado na solicitação."
    )
    reason: Optional[str] = Field(
        None, description="Motivo ou sintoma da consulta."
    )

class FinalMessageSchema(BaseModel):
    """Schema para a resposta final gerada ao cliente."""
    message: str = Field(..., description="Mensagem polida, clara e em português enviada ao usuário.")