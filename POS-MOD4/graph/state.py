# graph/state.py
from typing import Annotated, Optional, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from models import UserPreferences


class GraphState(TypedDict):
    # O add_messages soma novas mensagens ao histórico de curto prazo
    messages: Annotated[list[BaseMessage], add_messages]
    
    user_id: str
    
    # Flags e Objetos de Preferência
    user_context: Optional[UserPreferences]
    extracted_preferences: Optional[UserPreferences]
    should_save_preferences: bool
    
    # Controle de Sumarização e Economia de Tokens
    need_summarization: bool
    conversation_summary: Optional[str]