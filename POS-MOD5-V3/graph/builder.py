# graph/builder.py
from typing import Optional
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from graph.nodes import (
    create_guardrails_check_node,
    create_chat_node,
    blocked_node,
    route_after_guardrails,
)
from graph.state import GraphState
from services.openrouter_service import OpenRouterService
from services.mcp_service import McpService


async def create_graph(services: Optional[dict] = None):
    svc_dict = services or {}
    llm_svc = svc_dict.get("llm_service") or OpenRouterService()
    mcp_svc = svc_dict.get("mcp_service") or McpService(root_dir=".")

    workflow = StateGraph(GraphState)

    # Registro dos nós (Idêntico ao graph.ts do professor)
    workflow.add_node("guardrails_check", create_guardrails_check_node(llm_svc))
    workflow.add_node("chat", create_chat_node(llm_svc, mcp_svc))
    workflow.add_node("blocked", blocked_node)

    # Fluxo de Arestas
    workflow.add_edge(START, "guardrails_check")

    workflow.add_conditional_edges(
        "guardrails_check",
        route_after_guardrails,
        {
            "chat": "chat",
            "blocked": "blocked",
        }
    )

    workflow.add_edge("chat", END)
    workflow.add_edge("blocked", END)

    return workflow.compile()


async def build_graph(config: RunnableConfig = None):
    return await create_graph()