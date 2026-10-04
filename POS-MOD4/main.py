# main.py
import asyncio
import uuid
import sys
from langchain_core.messages import HumanMessage
from graph.builder import build_graph, create_graph
from services.memory_service import MemoryService


async def main():
    print("==========================================================")
    print("🎵 RECOMENDADOR DE MÚSICAS - ASSISTENTE COM MEMÓRIA DUAL 🎵")
    print("==========================================================\n")

    user_id = input("Digite seu ID de usuário ou Nome (ex: erick): ").strip() or "erick_wendel"
    thread_id = str(uuid.uuid4())

    mem_service = MemoryService()
    #graph = await build_graph(memory_service=mem_service)
    graph = await create_graph(services={"memory_service": mem_service})
    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": user_id,
        }
    }

    print(f"\nSessão iniciada para o usuário '{user_id}'. Digite 'sair' para encerrar.\n")

    try:
        while True:
            user_input = input("Você: ").strip()
            if not user_input or user_input.lower() in ["sair", "exit", "quit"]:
                print("\nAté logo!")
                break

            input_state = {
                "messages": [HumanMessage(content=user_input)],
                "user_id": user_id,
            }

            # Invocação assíncrona do grafo preservando a thread
            final_state = await graph.ainvoke(input_state, config=config)

            # Exibe a resposta gerada
            last_message = final_state["messages"][-1].content if final_state.get("messages") else "Sem resposta."
            print(f"\nAssistente: {last_message}\n")

            # Feedback de depuração do estado ativo
            if final_state.get("conversation_summary"):
                print(f"💡 [Resumo Atualizado no SQLite]: {final_state['conversation_summary']}\n")

    finally:
        await mem_service.close()


if __name__ == "__main__":
    # Ajuste obrigatório para Psycopg 3 + Asyncio no Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())