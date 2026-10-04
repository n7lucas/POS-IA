# graph/builder.py
from typing import Optional
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from graph.nodes import (
    chat_node,
    save_preferences_node,
    summarize_node,
    route_after_chat,
    route_after_save_preferences,
)
from graph.state import GraphState
from services.openrouter_service import OpenRouterService
from services.preferences_service import PreferencesService
from services.memory_service import MemoryService
from config import settings


async def create_graph(services: Optional[dict] = None):
    """
    Função construtora interna que aceita injeção de dependências
    para testes (pytest) e execução via CLI local (main.py).
    """
    svc_dict = services or {}
    llm_svc = svc_dict.get("llm_service") or OpenRouterService()
    pref_svc = svc_dict.get("preferences_service") or PreferencesService(settings.sqlite_db_path)
    mem_svc = svc_dict.get("memory_service") or MemoryService()

    # Inicializa as tabelas do SQLite e do PostgreSQL Checkpointer
    await pref_svc.init_db()
    checkpointer = await mem_svc.setup()

    workflow = StateGraph(GraphState)

    # 1. Nós envelopados com injeção de dependências
    async def _chat_node(state: GraphState):
        return await chat_node(state, llm_svc, pref_svc)

    async def _save_preferences_node(state: GraphState):
        return await save_preferences_node(state, pref_svc)

    async def _summarize_node(state: GraphState):
        return await summarize_node(state, llm_svc, pref_svc)

    # 2. Adição dos nós ao grafo
    workflow.add_node("chat", _chat_node)
    workflow.add_node("save_preferences", _save_preferences_node)
    workflow.add_node("summarize", _summarize_node)

    # 3. Definição das arestas (Edges)
    workflow.add_edge(START, "chat")

    # Aresta condicional após o Chat
    workflow.add_conditional_edges(
        "chat",
        route_after_chat,
        {
            "save_preferences": "save_preferences",
            "summarize": "summarize",
            "end": END,
        },
    )

    # Aresta condicional após salvar preferências
    workflow.add_conditional_edges(
        "save_preferences",
        route_after_save_preferences,
        {
            "summarize": "summarize",
            "end": END,
        },
    )

    # Aresta simples após sumarização
    workflow.add_edge("summarize", END)

    # 4. Compilação com o Checkpointer do Postgres
    return workflow.compile(checkpointer=checkpointer)


async def build_graph(config: RunnableConfig = None):
    """
    Factory oficial exposta para o LangGraph CLI (langgraph.json).
    Utiliza estritamente a tipagem 'RunnableConfig' exigida pela langgraph_api.
    """
    return await create_graph()