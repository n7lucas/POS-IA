# graph/nodes/query_planner.py
import logging
from graph.state import GraphState
from services.llm_service import LLMService
from prompts.query_analyzer import QueryAnalysisSchema, get_system_prompt, get_user_prompt

logger = logging.getLogger(__name__)

def create_query_planner_node(llm_service: LLMService):
    async def query_planner_node(state: GraphState) -> dict:
        try:
            question = state.get("question")
            if not question:
                return {"error": "Nenhuma pergunta no estado para analisar."}

            system_prompt = get_system_prompt()
            user_prompt = get_user_prompt(question)

            # Chama a LLM forçando a saída para bater com o QueryAnalysisSchema
            data, error = await llm_service.generate_structured(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                schema=QueryAnalysisSchema
            )

            # Fallback seguro: se der erro, assume que é uma pergunta simples
            if error or not data:
                logger.warning('⚠️ Falha ao analisar a query, assumindo como simples (simple).')
                return {
                    "error": error,
                    "is_multistep": False,
                    "resoaning": data.reasoning
                }

            # Se exige decomposição e possui subquestions válidas
            if data.requires_decomposition and len(data.sub_questions) > 0:
                sub_questions_formatted = "\n".join([f"   {i+1}. {q}" for i, q in enumerate(data.sub_questions)])
                logger.info(f"📊 Complex query - {len(data.sub_questions)} steps:\n{sub_questions_formatted}")

                # Atualiza o estado iniciando o fluxo Multi-step (Zera resultados anteriores se houver)
                return {
                    "is_multistep": True,
                    "sub_questions": data.sub_questions,
                    "current_step": 0,
                    "sub_queries": [],
                    "sub_results": []
                }

            # Cenário simples (sem decomposição)
            logger.info("📊 Simple query - 1 step.")
            return {
                "is_multistep": False,
                "resoaning": data.reasoning
            }

        except Exception as e:
            logger.error(f"❌ Erro crítico analisando query: {str(e)}")
            return {
                "is_multistep": False
            }

    return query_planner_node