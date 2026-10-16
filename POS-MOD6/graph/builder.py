import logging
from langgraph.graph import StateGraph, START, END
from graph.state import GraphState
from config import settings

from graph.nodes.extract_question import extract_question_node
from graph.nodes.query_planner import create_query_planner_node
from graph.nodes.cypher_generator import create_cypher_generator_node
from graph.nodes.cypher_executor import create_cypher_executor_node
from graph.nodes.cypher_correction import create_cypher_correction_node
from graph.nodes.analytical_response import create_analytical_response_node

from services.llm_service import LLMService
from services.neo4j_service import Neo4jService


logger = logging.getLogger(__name__)

#Funcao de Roteamento Condificional


def route_after_extract(state: GraphState) -> str:
    """Se houver erro na extração, encerra. Senão, vai para o Planner."""
    if state.get("error"):
        return END
    return "query_planner"

def route_after_executor(state: GraphState) -> str:
    """A grande encruzilhada: Correção, Loop Multi-step ou Resposta Final."""

    # 0. BLINDAGEM: Se houve um erro fatal (excedeu limite de correções), aborta o loop!
    if state.get("error"):
        return "analytical_response"
    
    #1 Precisa de correção ?
    if state.get("needs_correction"):
        attempts = state.get("correction_attempts") or 0
        if attempts < settings.max_correction_attemps:
            return "cypher_correction"

    # 2. É multi-step e ainda tem passos?
    is_multistep = state.get("is_multistep")
    sub_questions = state.get("sub_questions") or []
    current_step = state.get("current_step")
    
    if is_multistep and sub_questions and current_step is not None:
        if current_step < len(sub_questions):
            return "cypher_generator" # 🔄 Retorna para gerar a próxima query!
            
    # 3. Tudo concluído com sucesso
    return "analytical_response"
# --------Construtor Principal --------

def build_sales_qa_graph(llm_service: LLMService, neo4j_service: Neo4jService):

    workflow = StateGraph(GraphState)
    # 1 Registrar os Nos
    workflow.add_node("extract_question", extract_question_node)
    workflow.add_node("query_planner", create_query_planner_node(llm_service))
    workflow.add_node("cypher_generator", create_cypher_generator_node(llm_service, neo4j_service))
    workflow.add_node("cypher_executor", create_cypher_executor_node(neo4j_service))
    workflow.add_node("cypher_correction", create_cypher_correction_node(llm_service, neo4j_service))
    workflow.add_node("analytical_response", create_analytical_response_node(llm_service))

    #2 Desenhar as Arestas (O fluxo)
    workflow.add_edge(START, "extract_question")

    workflow.add_conditional_edges("extract_question", route_after_extract, 
                        {
                            "query_planner": "query_planner",
                            END: END
                        }
                             )
    workflow.add_edge("query_planner", "cypher_generator")
    workflow.add_edge("cypher_generator", "cypher_executor")

    # Adicionando o dicionário de mapeamento explícito para a encruzilhada
    workflow.add_conditional_edges(
        "cypher_executor", 
        route_after_executor,
        {
            "cypher_correction": "cypher_correction",
            "cypher_generator": "cypher_generator",
            "analytical_response": "analytical_response"
        }
    )
    
    workflow.add_edge("cypher_correction", "cypher_executor")
    workflow.add_edge("analytical_response", END)

    return workflow.compile()