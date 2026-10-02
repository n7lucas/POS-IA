# graph/nodes.py
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ValidationError
from langchain_core.messages import AIMessage

from graph.state import GraphState
from models import IntentExtractionSchema, FinalMessageSchema
from services.openrouter_service import OpenRouterService
from services.appointment_service import AppointmentService
from prompts import get_identify_intent_system_prompt, SYSTEM_GENERATE_MESSAGE_PROMPT

# --- Schemas Pydantic para Validação Secundária ("safeParse") nos Nós ---
class ScheduleNodePayload(BaseModel):
    professional_id: int = Field(..., description="ID do profissional é obrigatório")
    date_time: str = Field(..., description="Data/hora é obrigatória")
    patient_name: str = Field(..., description="Nome do paciente é obrigatório")
    reason: Optional[str] = "Consulta Geral"

class CancelNodePayload(BaseModel):
    professional_id: int = Field(..., description="ID do profissional é obrigatório")
    date_time: str = Field(..., description="Data/hora é obrigatória")
    patient_name: str = Field(..., description="Nome do paciente é obrigatório")


# --- NÓ 1: Identificador de Intenção ---
async def identify_intent_node(
    state: GraphState, 
    llm_service: OpenRouterService, 
    appointment_service: AppointmentService
) -> Dict[str, Any]:
    user_message = state["messages"][-1].content if state["messages"] else ""
    
    # 1. Constrói contexto de profissionais cadastrados
    profs = appointment_service.get_professionals()
    profs_context = "\n".join([f"- ID {p.id}: {p.name} ({p.specialty})" for p in profs])
    
    system_prompt = get_identify_intent_system_prompt(profs_context)
    
    try:
        # Chama a LLM para extração estruturada estrita
        extracted: IntentExtractionSchema = await llm_service.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_message,
            schema=IntentExtractionSchema
        )
        
        return {
            "intent": extracted.intent,
            "professional_id": extracted.professional_id,
            "professional_name": extracted.professional_name,
            "date_time": extracted.date_time,
            "patient_name": extracted.patient_name,
            "reason": extracted.reason,
            "action_success": False,
            "action_error": None
        }
    except Exception as e:
        logging.error(f"Erro na extração de intenção: {str(e)}")
        # Em caso de falha de rede/model, fallback Gracioso para 'unknown'
        return {
            "intent": "unknown",
            "action_success": False,
            "action_error": f"Falha no processamento de linguagem natural: {str(e)}"
        }


# --- NÓ 2: Execução de Agendamento ---
async def scheduler_node(
    state: GraphState, 
    appointment_service: AppointmentService
) -> Dict[str, Any]:
    # Validação Secundária Defensiva (estilo Zod safeParse)
    try:
        payload = ScheduleNodePayload(
            professional_id=state.get("professional_id"),
            date_time=state.get("date_time"),
            patient_name=state.get("patient_name"),
            reason=state.get("reason")
        )
    except ValidationError as val_err:
        return {
            "action_success": False,
            "action_error": f"Dados insuficientes para agendamento: {val_err.errors()[0]['msg']}"
        }

    # Execução da Regra Determinística
    try:
        appointment = appointment_service.book(
            professional_id=payload.professional_id,
            date_time=payload.date_time,
            patient_name=payload.patient_name,
            reason=payload.reason
        )
        return {
            "action_success": True,
            "action_error": None
        }
    except ValueError as domain_err:
        return {
            "action_success": False,
            "action_error": str(domain_err)
        }


# --- NÓ 3: Execução de Cancelamento ---
async def canceller_node(
    state: GraphState, 
    appointment_service: AppointmentService
) -> Dict[str, Any]:
    # Validação Secundária Defensiva
    try:
        payload = CancelNodePayload(
            professional_id=state.get("professional_id"),
            date_time=state.get("date_time"),
            patient_name=state.get("patient_name")
        )
    except ValidationError as val_err:
        return {
            "action_success": False,
            "action_error": f"Dados insuficientes para cancelamento: {val_err.errors()[0]['msg']}"
        }

    # Execução da Regra Determinística
    try:
        appointment_service.cancel(
            professional_id=payload.professional_id,
            patient_name=payload.patient_name,
            date_time=payload.date_time
        )
        return {
            "action_success": True,
            "action_error": None
        }
    except ValueError as domain_err:
        return {
            "action_success": False,
            "action_error": str(domain_err)
        }


# --- NÓ 4: Fallback ---
async def fallback_node(state: GraphState) -> Dict[str, Any]:
    return {
        "action_success": False,
        "action_error": "Não foi possível entender sua solicitação. Por favor, informe se deseja agendar ou cancelar uma consulta, especificando o médico e o horário."
    }


# --- NÓ 5: Gerador da Mensagem Final ---
async def message_generator_node(
    state: GraphState, 
    llm_service: OpenRouterService
) -> Dict[str, Any]:
    user_message = state["messages"][-1].content if state["messages"] else ""
    
    # Isola apenas os detalhes relevantes para economizar tokens
    details_context = (
        f"Intenção: {state.get('intent')}\n"
        f"Sucesso na Operação: {state.get('action_success')}\n"
        f"Erro na Operação: {state.get('action_error') or 'Nenhum'}\n"
        f"Profissional ID: {state.get('professional_id')}\n"
        f"Data/Hora: {state.get('date_time')}\n"
        f"Paciente: {state.get('patient_name')}"
    )
    
    user_prompt = f"Mensagem original do usuário: '{user_message}'\n\nResultado Interno da Operação:\n{details_context}"
    
    try:
        final_data: FinalMessageSchema = await llm_service.generate_structured(
            system_prompt=SYSTEM_GENERATE_MESSAGE_PROMPT,
            user_prompt=user_prompt,
            schema=FinalMessageSchema
        )
        output_text = final_data.message
    except Exception:
        # Fallback de texto se a LLM falhar na resposta final
        if state.get("action_success"):
            output_text = "Sua solicitação foi processada com sucesso!"
        else:
            output_text = f"Desculpe, não foi possível concluir a operação. Motivo: {state.get('action_error')}"

    return {
        "output": output_text,
        "messages": [AIMessage(content=output_text)]
    }