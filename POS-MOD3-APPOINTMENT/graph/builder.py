# graph/builder.py
from functools import partial
from langgraph.graph import StateGraph, START, END

from graph.state import GraphState
from graph.nodes import (
    identify_intent_node,
    scheduler_node,
    canceller_node,
    fallback_node,
    message_generator_node
)
from services.openrouter_service import OpenRouterService
from services.appointment_service import AppointmentService

def route_intent(state: GraphState) -> str:
    """Função roteadora que lê o campo 'intent' do estado."""
    return state.get("intent", "unknown")

def build_graph(
    llm_service: OpenRouterService = None,
    appointment_service: AppointmentService = None
):
    """
    Factory que injeta dependências nos nós e compila o StateGraph.
    """
    # Instâncias padrão caso não sejam injetadas (ex: em produção)
    llm_svc = llm_service or OpenRouterService()
    appt_svc = appointment_service or AppointmentService()

    workflow = StateGraph(GraphState)

    # 1. Adição dos nós utilizando partial para injetar os serviços
    workflow.add_node(
        "identify_intent", 
        partial(identify_intent_node, llm_service=llm_svc, appointment_service=appt_svc)
    )
    workflow.add_node(
        "scheduler", 
        partial(scheduler_node, appointment_service=appt_svc)
    )
    workflow.add_node(
        "canceller", 
        partial(canceller_node, appointment_service=appt_svc)
    )
    workflow.add_node("fallback", fallback_node)
    workflow.add_node(
        "message_generator", 
        partial(message_generator_node, llm_service=llm_svc)
    )

    # 2. Conectando a entrada do grafo
    workflow.add_edge(START, "identify_intent")

    # 3. Roteamento Condicional
    workflow.add_conditional_edges(
        "identify_intent",
        route_intent,
        {
            "schedule": "scheduler",
            "cancel": "canceller",
            "unknown": "fallback"
        }
    )

    # 4. Todos os nós operacionais convergem para o gerador de mensagem final
    workflow.add_edge("scheduler", "message_generator")
    workflow.add_edge("canceller", "message_generator")
    workflow.add_edge("fallback", "message_generator")

    # 5. O gerador de mensagem encerra o fluxo
    workflow.add_edge("message_generator", END)

    return workflow.compile()

# Exportação global para o LangGraph Studio / CLI
app_graph = build_graph()