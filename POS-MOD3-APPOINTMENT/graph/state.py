# graph/state.py
from typing import Annotated, Literal, Optional, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class GraphState(TypedDict):
    # Histórico exigido pelo LangGraph Studio (preserva mensagens)
    messages: Annotated[list[BaseMessage], add_messages]
    
    # Intenção e dados extraídos pela IA
    intent: Literal["schedule", "cancel", "unknown"]
    professional_id: Optional[int]
    professional_name: Optional[str]
    date_time: Optional[str]
    patient_name: Optional[str]
    reason: Optional[str]
    
    # Estado da execução da regra de negócio determinística
    action_success: bool
    action_error: Optional[str]
    
    # Resultado final de texto para o usuário
    output: str