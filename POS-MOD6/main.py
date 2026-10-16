# main.py
import asyncio
import logging
from langchain_core.messages import HumanMessage
from services.llm_service import LLMService
from services.neo4j_service import Neo4jService
from graph.builder import build_sales_qa_graph

# Configuração limpa de log para visualizarmos a orquestração
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("SalesAgent")

def display_banner():
    print("═" * 70)
    print("  🧠 Agente Analítico de Vendas (RAG Avançado com Neo4j)  ")
    print("═" * 70)
    print("Digite 'sair' a qualquer momento para encerrar.\n")

async def main():
    display_banner()
    
    # 1. Inicializa Serviços
    llm_service = LLMService()
    neo4j_service = Neo4jService()
    
    # 2. Compila o Grafo
    graph = build_sales_qa_graph(llm_service, neo4j_service)

    try:
        while True:
            user_input = input("\n👤 Você: ")
            if user_input.lower() in ['sair', 'exit', 'quit']:
                break
                
            if not user_input.strip():
                continue

            print("\n" + "─" * 70)
            
            # 3. Invoca o grafo com a mensagem inicial
            initial_state = {
                "messages": [HumanMessage(content=user_input)]
            }

            # Executa o pipeline inteiro
            result = await graph.ainvoke(initial_state)

            print("─" * 70 + "\n")
            
            # 4. Exibe a resposta final do agente (A Analytical Response)
            final_messages = result.get("messages", [])
            if final_messages:
                print(f"🤖 Agente: {final_messages[-1].content}")
            
            # 5. Exibe os follow-ups sugeridos
            follow_ups = result.get("follow_up_questions")
            if follow_ups:
                print("\n💡 Sugestões de próximas perguntas:")
                for i, fq in enumerate(follow_ups):
                    print(f"   {i+1}. {fq}")

    except KeyboardInterrupt:
        print("\n\nSaindo...")
    finally:
        print("Encerrando conexão com o banco de dados...")
        neo4j_service.graph.close()

if __name__ == "__main__":
    asyncio.run(main())