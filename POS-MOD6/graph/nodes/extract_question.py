import logging
from graph.state import GraphState


logger = logging.getLogger(__name__)

async def extract_question_node(state: GraphState) -> dict:
    try:
        messages = state.get("messages", [])
        if not messages:
            logger.error("Sem mensagens no estado")
            return {"error": "Nenhuma mensagem fornecida"}
        # Pega o conteudo da última mensagem
        last_message = messages[-1]
        question = str(last_message.content).strip()

        if not question:
            logger.error("A pergunta extraida está vazia.")
            return {"error" : "Nenhuma mensagem fornecida"}

        logger.info(f" Pergunta extraida: `{question}`")


        return {"question": question}

    except Exception as e:
        logger.error(f"Erro ao extrair a pergunta: {str(e)}")
        return {"error": f"Falha ao extrair a pergunta: {str(e)}"}

            # Pega o conteudo da ultima mensage
#extrair mensagem do usuario ->