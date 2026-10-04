#async def chat_node -> carrega contexto de preferencias do SQLite swe nao estiver no estado.
                #    -> carrega resumo anterior do SQLite se nao estiver no estado
                #    -> Send to get_chat_system_prompt the user context and conversation history
#                    -> Avalia se o limite de msg foi atingido


# graph/nodes.py
import logging
from typing import List
from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage, BaseMessage
from graph.state import GraphState
from models import ChatResponseSchema, SummarySchema, UserPreferences
from services.openrouter_service import OpenRouterService
from services.preferences_service import PreferencesService
from prompts import get_chat_system_prompt, get_summarize_system_prompt
from config import settings

logger = logging.getLogger(__name__)


# --- Nó 1: ChatNode ---
async def chat_node(
    state: GraphState, 
    llm_service: OpenRouterService, 
    preferences_service: PreferencesService
) -> dict:
    user_id = state.get("user_id", "default_user")
    messages = state.get("messages", [])
    
    # 1. Carrega o contexto de preferências do SQLite se não estiver no estado
    user_context = state.get("user_context")
    if not user_context:
        user_context = await preferences_service.get_preferences(user_id)

    # 2. Carrega o resumo anterior do SQLite se não estiver no estado
    conversation_summary = state.get("conversation_summary")
    if not conversation_summary:
        conversation_summary = await preferences_service.get_summary(user_id)

    # 3. Prepara os prompts
    system_prompt = get_chat_system_prompt(user_context, conversation_summary)
    
    # Pega a última mensagem enviada pelo usuário
    latest_user_message = messages[-1].content if messages else ""
    
    try:
        response: ChatResponseSchema = await llm_service.generate_structured(
            system_prompt=system_prompt,
            user_prompt=latest_user_message,
            schema=ChatResponseSchema,
        )
        
        # 4. Avalia se atingiu o limite de mensagens para disparar sumarização
        need_summarization = len(messages) >= settings.max_messages_to_summary

        return {
            "messages": [AIMessage(content=response.message)],
            "user_context": user_context,
            "conversation_summary": conversation_summary,
            "should_save_preferences": response.should_save_preferences,
            "extracted_preferences": response.extracted_preferences if response.should_save_preferences else None,
            "need_summarization": need_summarization,
        }
    except Exception as e:
        logger.error(f"Erro no ChatNode: {e}")
        fallback_msg = "Desculpe, tive um problema ao processar sua mensagem. Pode repetir?"
        return {
            "messages": [AIMessage(content=fallback_msg)],
            "should_save_preferences": False,
            "need_summarization": False,
        }


# --- Nó 2: SavePreferencesNode ---
async def save_preferences_node(state: GraphState, preferences_service: PreferencesService) -> dict:
    user_id = state.get("user_id", "default_user")
    extracted = state.get("extracted_preferences")

    if extracted:
        # Mescla de forma incremental no SQLite
        updated_context = await preferences_service.merge_preferences(user_id, extracted)
        logger.info(f"Preferências atualizadas no SQLite para user_id={user_id}")
        return {
            "user_context": updated_context,
            "extracted_preferences": None,
            "should_save_preferences": False,
        }
    
    return {"should_save_preferences": False}


# --- Nó 3: SummarizeNode (Compactador de Janela de Contexto) ---
async def summarize_node(
    state: GraphState, 
    llm_service: OpenRouterService, 
    preferences_service: PreferencesService
) -> dict:
    user_id = state.get("user_id", "default_user")
    messages = state.get("messages", [])
    previous_summary = state.get("conversation_summary")

    # Formatador de histórico legível para o prompt de resumo
    formatted_history = []
    for msg in messages:
        role = "Usuário" if isinstance(msg, HumanMessage) else "Assistente"
        formatted_history.append(f"{role}: {msg.content}")
    history_text = "\n".join(formatted_history)

    system_prompt = get_summarize_system_prompt(previous_summary)
    
    try:
        summary_response: SummarySchema = await llm_service.generate_structured(
            system_prompt=system_prompt,
            user_prompt=f"Histórico Atual de Mensagens:\n{history_text}",
            schema=SummarySchema,
        )
        
        new_summary = summary_response.summary
        
        # 1. Salva o novo resumo compacto no SQLite
        await preferences_service.save_summary(user_id, new_summary)
        logger.info(f"Resumo de contexto gerado e salvo no SQLite para user_id={user_id}")

        # 2. REDUÇÃO DE TOKENS: Prepara RemoveMessage para apagar mensagens antigas do estado ativo,
        # mantendo apenas as 2 mensagens mais recentes.
        messages_to_remove = []
        if len(messages) > 2:
            # Seleciona todas as mensagens exceto as últimas duas
            for msg in messages[:-2]:
                messages_to_remove.append(RemoveMessage(id=msg.id))

        return {
            "messages": messages_to_remove,  # Remove as mensagens antigas do LangGraph State
            "conversation_summary": new_summary,
            "need_summarization": False,
        }
    except Exception as e:
        logger.error(f"Erro no SummarizeNode: {e}")
        return {"need_summarization": False}


# --- Roteadores Condicionais ---
def route_after_chat(state: GraphState) -> str:
    """Decide se deve ir para salvar preferências, resumir contexto ou encerrar."""
    if state.get("should_save_preferences"):
        return "save_preferences"
    if state.get("need_summarization"):
        return "summarize"
    return "end"


def route_after_save_preferences(state: GraphState) -> str:
    """Após salvar preferências, verifica se também precisa resumir o histórico."""
    if state.get("need_summarization"):
        return "summarize"
    return "end"