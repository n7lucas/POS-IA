# graph/nodes/cypher_correction.py
import logging
from graph.state import GraphState
from services.llm_service import LLMService
from services.neo4j_service import Neo4jService
from prompts.cypher_correction import CypherCorrectionSchema, get_system_prompt, get_user_prompt

logger = logging.getLogger(__name__)

def create_cypher_correction_node(llm_service: LLMService, neo4j_service: Neo4jService):
    async def cypher_correction_node(state: GraphState) -> dict:
        try:
            logger.info("🔧 Auto-corrigindo Cypher query...")
            
            schema = await neo4j_service.get_schema()
            system_prompt = get_system_prompt(schema)
            user_prompt = get_user_prompt(
                failed_query=state.get("query", ""),
                error_message=state.get("validation_error", ""),
                original_question=state.get("question", "")
            )

            data, error = await llm_service.generate_structured(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                schema=CypherCorrectionSchema
            )

            if error or not data:
                return {"error": f"Query correction failed: {error or 'Unknown error'}"}

            logger.info(f"✅ Query corrigida. Explicação: {data.explanation}")

            # Atualiza a query com a versão corrigida, incrementa a tentativa e zera o erro
            return {
                "query": data.corrected_query,
                "original_query": state.get("original_query") or state.get("query"),
                "correction_attempts": (state.get("correction_attempts") or 0) + 1,
                "validation_error": None,
                "needs_correction": False
            }

        except Exception as e:
            logger.error(f"Erro corrigindo query: {str(e)}")
            return {"error": f"Query correction failed: {str(e)}"}

    return cypher_correction_node