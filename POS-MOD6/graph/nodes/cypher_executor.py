import logging
from typing import Any, Dict, List, Tuple
from graph.state import GraphState
from services.neo4j_service import Neo4jService
from config import settings



logger = logging.getLogger(__name__)

async def execute_query(query: str, neo4j_service: Neo4jService) -> Tuple[List[Any], str]:
    """Valida e executa a query, retornando (resultados, mensagem_de_erro)."""
    try:
        # 1. Validacao defensiva com EXPLAIN
        is_valid = await neo4j_service.validade_query(query)
        if not is_valid:
            return None, "Query validation failed - syntax or structure error"

        #2. Execução real
        results = await neo4j_service.query(query)
        if not results:
            return [], "No results found"

        logger.info(f"✅ Recuperados {len(results)} resultado(s)")
        return results, None
    
    except Exception as e:
        return None, str(e)


def has_more_steps(state: GraphState, current_step: int) -> bool:
    if not state.get("is_multistep") or not state.get("sub_questions"):
        return False
    return current_step < len(state["sub_questions"])

def handle_multistep_progression(state: GraphState, results: List[Any]) -> dict:
    """ Acumula resultados intermediários e avança o passo"""
    updated_sub_results = list(state.get("sub_results") or [])
    updated_sub_results.append(results)

    next_step = (state.get("current_step") or 0) +1

    multi_step_state = {
        "db_results": results,
        "sub_results": updated_sub_results,
        "current_step": next_step,
        "needs_correction": False,
    }

    total_steps = len(state.get("sub_questions") or [])
    logger.info(f"✅ Step {next_step}/{total_steps} concluído (Index anterior: {next_step - 1})")


    if has_more_steps(state, next_step):
        logger.info(f"➡️  Avançando para o próximo passo...")
    else:
        logger.info(f"✅ Todos os {total_steps} passos concluídos - indo para síntese.")

    return multi_step_state


def create_cypher_executor_node(neo4j_service: Neo4jService):
    async def cypher_executor_node(state: GraphState) -> dict:
        try:
            query = state.get("query")
            if not query:
                return {"error": "Nenhuma query fornecida para execução"}
            results, error = await execute_query(query, neo4j_service)

            # --- CENÁRIO A: Erro de Sintaxe (Needs Correction) --- 
            if error and results is None:
                correction_attempts = state.get("correction_attempts") or 0

                if correction_attempts < settings.max_correction_attemps:
                    logger.warning(" Tentativa de auto-correção da query ativada...")
                    return {
                        "validation_error": error,
                        "original_query": state.get("original_query") or state.get("query"),
                        "needs_correction": True,
                    }
                return {"error": "Invalid Cypher query - correction failed"}

            # --- CENÁRIO B: Multi-step Loop ---
            if state.get("is_multistep") and state.get("sub_questions") and state.get("current_step") is not None:
                return handle_multistep_progression(state, results or [])

            # --- CENÁRIO C: Sucesso (Simples) mas sem dados no banco ---
            if not results:
                return {
                    "db_results": [],
                    "error": "No resutls found"
                }
            # --- CENÁRIO D: Sucesso (Simples) com dados ---
            return {
                    "db_results": results,
                    "needs_correction": False,
                }    

        except Exception as e:
            logger.error(f"Erro inesperado no executor: {str(e)}")
            return {"error": "Invalid Cypher query - execution failed"}

    return cypher_executor_node