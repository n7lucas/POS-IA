# graph/state.py
from typing import Annotated, Optional, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from models import UserProfile, GuardrailCheckResult


class GraphState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user: UserProfile
    guardrailCheck: Optional[GuardrailCheckResult]
    guardrailsEnabled: bool