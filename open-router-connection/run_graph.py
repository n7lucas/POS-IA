# run_graph.py
import asyncio
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from graph import build_graph

# 1. Carrega as variáveis de ambiente (.env)
load_dotenv()


async def main():
    # 2. Compila o grafo
    graph = build_graph()

    # 3. Define a mensagem de entrada
    input_data = {
        "messages": [HumanMessage(content="Gostaria de agendar uma consulta médica para amanhã.")],
        "intent": "unknown",
        "action_result": "",
        "output": "",
    }

    print("🚀 Executando o grafo com a entrada do usuário...\n")

    # 4. Executa o grafo de forma assíncrona
    final_state = await graph.ainvoke(input_data)

    print("--------------------------------------------------")
    print(f"🎯 Intenção Identificada: {final_state.get('intent')}")
    print(f"⚙️  Resultado da Ação:     {final_state.get('action_result')}")
    print(f"🤖 Resposta do Agente:    {final_state.get('output')}")
    print("--------------------------------------------------")


if __name__ == "__main__":
    asyncio.run(main())