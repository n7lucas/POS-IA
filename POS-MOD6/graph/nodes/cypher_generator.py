# graph/nodes/cypher_generator.py
import logging
from typing import Optional, Dict, Any
from graph.state import GraphState
from services.llm_service import LLMService
from services.neo4j_service import Neo4jService
from prompts.sales_context import SALES_CONTEXT
from prompts.cypher_generator import CypherQuerySchema, get_system_prompt, get_user_prompt

logger = logging.getLogger(__name__)

def get_current_step_question(state: GraphState) -> Optional[Dict[str, Any]]:
    """Decide se estamos respondendo a pergunta original ou uma sub-pergunta (Multi-step)."""
    if not state.get("is_multistep") or not state.get("sub_questions") or state.get("current_step") is None:
        return None
    
    current_step = state["current_step"]
    sub_questions = state["sub_questions"]
    
    if current_step >= len(sub_questions):
        return None
        
    return {
        "question": sub_questions[current_step],
        "step_number": current_step + 1
    }

def create_cypher_generator_node(llm_service: LLMService, neo4j_service: Neo4jService):
    async def cypher_generator_node(state: GraphState) -> dict:
        try:
            step_info = get_current_step_question(state)
            target_question = step_info["question"] if step_info else state.get("question", "")
            
            if step_info:
                total_steps = len(state.get("sub_questions", []))
                logger.info(f"🤖 Gerando query (Step {step_info['step_number']}/{total_steps}): '{target_question}'")
            else:
                logger.info(f"🤖 Gerando query para pergunta simples: '{target_question}'")

            # Injeta Schema do Banco e Regras de Negócio no Prompt
            schema = await neo4j_service.get_schema()
            system_prompt = get_system_prompt(schema, SALES_CONTEXT)
            user_prompt = get_user_prompt(target_question)

            # Gera a Query
            data, error = await llm_service.generate_structured(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                schema=CypherQuerySchema
            )

            if error or not data:
                return {"error": f"Failed to generate query: {error or 'Unknown error'}"}

            logger.info(f"✅ Cypher Query gerada: {data.query}")
            
            # Se for multi-step, acumulamos a query. Senão, só retornamos a query.
            if state.get("is_multistep") and state.get("sub_queries") is not None:
                sub_queries = list(state["sub_queries"]) # Cópia para evitar mutação indesejada
                sub_queries.append(data.query)
                return {
                    "query": data.query,
                    "sub_queries": sub_queries,
                    "correction_attempts": 0, # Reseta para o novo passo ter direito a errar
                    "error": None
                }

            return {
                "query": data.query,
                "correction_attempts": 0,
                "error": None
            }

        except Exception as e:
            logger.error(f"Erro ao gerar Cypher query: {str(e)}")
            return {"error": f"Failed to generate query: {str(e)}"}

    return cypher_generator_node