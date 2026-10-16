# graph/nodes/analytical_response.py
import json
import logging
from langchain_core.messages import AIMessage
from graph.state import GraphState
from services.llm_service import LLMService
from prompts.analytical_response import (
    AnalyticalResponseSchema, get_system_prompt, get_user_prompt, 
    get_error_prompt, get_no_results_prompt, get_multi_step_prompt
)

logger = logging.getLogger(__name__)

async def handle_error_response(state: GraphState, llm_service: LLMService) -> dict:
    system_prompt = get_system_prompt()
    user_prompt = get_error_prompt(state.get("error", ""), state.get("question", ""))
    
    data, error = await llm_service.generate_structured(system_prompt, user_prompt, AnalyticalResponseSchema)
    
    if error or not data:
        fallback = f"An error occurred: {error}"
        return {"messages": [AIMessage(content=fallback)], "error": error, "answer": fallback, "follow_up_questions": []}

    return {"messages": [AIMessage(content=data.answer)], "answer": data.answer, "follow_up_questions": data.follow_up_questions}

async def handle_no_results_response(state: GraphState, llm_service: LLMService) -> dict:
    logger.info("💬 Gerando resposta para 'sem resultados'...")
    system_prompt = get_system_prompt()
    user_prompt = get_no_results_prompt(state.get("question", "your query"), state.get("query", "N/A"))
    
    data, error = await llm_service.generate_structured(system_prompt, user_prompt, AnalyticalResponseSchema)
    
    if data:
        return {"messages": [AIMessage(content=data.answer)], "answer": data.answer, "follow_up_questions": data.follow_up_questions}

    fallback = "No data found matching your query."
    return {"messages": [AIMessage(content=fallback)], "error": error, "answer": fallback, "follow_up_questions": []}

async def handle_success_response(state: GraphState, llm_service: LLMService) -> dict:
    system_prompt = get_system_prompt()
    
    is_multi_step_valid = (
        state.get("is_multistep") and 
        state.get("sub_results") and 
        state.get("sub_questions") and 
        state.get("sub_queries")
    )
    
    if is_multi_step_valid:
        sub_results = state["sub_results"]
        logger.info(f"📊 Sintetizando resultados de {len(sub_results)} passos...")
        
        steps_data = []
        for i, results in enumerate(sub_results):
            steps_data.append({
                "stepNumber": i + 1,
                "question": state["sub_questions"][i],
                "query": state["sub_queries"][i],
                "results": json.dumps(results)
            })
        user_prompt = get_multi_step_prompt(state.get("question", ""), steps_data)
    else:
        user_prompt = get_user_prompt(
            state.get("question", ""), 
            state.get("query", ""), 
            json.dumps(state.get("db_results"))
        )

    data, error = await llm_service.generate_structured(system_prompt, user_prompt, AnalyticalResponseSchema)
    
    if error or not data:
        return {"error": f"Response generation failed: {error or 'Unknown error'}"}

    logger.info("✅ Resposta analítica gerada com sucesso.")
    return {"messages": [AIMessage(content=data.answer)], "answer": data.answer, "follow_up_questions": data.follow_up_questions}


def create_analytical_response_node(llm_service: LLMService):
    async def analytical_response_node(state: GraphState) -> dict:
        try:
            if state.get("error"):
                return await handle_error_response(state, llm_service)
                
            # Verifica se está vazio (tanto o db_results quanto o sub_results)
            db_res = state.get("db_results") or []
            sub_res = state.get("sub_results") or []
            
            if not db_res and not sub_res:
                return await handle_no_results_response(state, llm_service)

            return await handle_success_response(state, llm_service)

        except Exception as e:
            logger.error(f"Erro gerando resposta analítica: {str(e)}")
            return {"error": f"Response generation failed: {str(e)}"}

    return analytical_response_node