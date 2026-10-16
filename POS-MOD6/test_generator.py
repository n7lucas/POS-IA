import asyncio
import logging
from services.llm_service import LLMService
from services.neo4j_service import Neo4jService
from graph.nodes.cypher_generator import create_cypher_generator_node

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

async def main():
    print("🤖 1. Inicializando Serviços (LLM e Neo4j)...")
    llm_service = LLMService()
    # ATENÇÃO: Para rodar este teste, você precisa ter um banco Neo4j rodando 
    # (pode ser o container Docker do projeto original do professor)
    neo4j_service = Neo4jService()

    print("⚙️ 2. Criando o nó Gerador de Cypher...")
    generator_node = create_cypher_generator_node(llm_service, neo4j_service)

    # Vamos simular um estado que já passou pelo Query Planner (Pergunta Simples)
    state = {
        "question": "Quais são todos os cursos cadastrados?",
        "is_multistep": False
    }

    print("\n-- INICIANDO TESTE DO GERADOR ---")
    novo_estado = await generator_node(state)

    print("\n✅ Estado Atualizado com a Query:")
    print(novo_estado)

if __name__ == "__main__":
    asyncio.run(main())