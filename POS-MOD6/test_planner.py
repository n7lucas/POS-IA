import asyncio
import logging
from services.llm_service import LLMService
from graph.nodes.query_planner import create_query_planner_node


# Configura o log para aparecer no terminal de forma clara
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


async def main():
    print("🤖 1. Inicializando LLM Service...")
    llm_service = LLMService()

    print("⚙️ 2. Criando o nó do Planner...")
    planner_node = create_query_planner_node(llm_service)

    #==========================================
    # TESTE 1: Pergunta Simples
    # ==========================================
    print("\n--- INICIANDO TESTE 1: SIMPLES ---")
    state_simples = {"question": "Quais são os cursos disponíveis? "}

    #Executa o no passando o estado
    novo_estado_simples = await planner_node(state_simples)

    print("\n✅ Resultado retornado para o estado (Simples):")
    print(novo_estado_simples)


    # ==========================================
    # TESTE 2: Pergunta Complexa
    # ==========================================
    print("\n--- INICIANDO TESTE 2: COMPLEXA ---")
    state_complexo = {"question": "Compare a receita dos cursos de alta taxa de conclusão com os de baixa taxa."}

    # Executa o nó passando o estado
    novo_estado_complexo = await planner_node(state_complexo)

    print("\n✅ Resultado retornado para o estado (Complexa):")
    print(novo_estado_complexo)

if __name__ == "__main__":
    asyncio.run(main())

