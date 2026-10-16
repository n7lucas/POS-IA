from typing import Annotated, Any, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class GraphState(TypedDict):

    #Input
    messages: Annotated[list[BaseMessage], add_messages]
    question: Optional [str]


    #Cypher generation
    query: Optional[str]
    original_query: Optional[str]

    #Query execution
    db_results: Optional[list[Any]]

    #Self-Correction
    correction_attempts: Optional[int]
    validation_error: Optional[str]
    need_correction: Optional[bool]

    #Multi-step Decomposition
    is_multistep: Optional[bool]
    sub_questions: Optional[list[str]]
    current_step: Optional[int]
    sub_queries: Optional[list[str]]
    sub_results: Optional[list[list[Any]]]

    # Response generation
    answer: Optional[str]
    follow_up_questions: Optional[list[str]]

    #Error handling
    error: Optional[str]

