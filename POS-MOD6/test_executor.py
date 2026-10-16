import asyncio
import logging
from services.neo4j_service import Neo4jService
from graph.nodes.cypher_executor import create_cypher_executor_node

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

async def main():
    print(" 1. Inicializando Servico Neo4j...")
    neo4j_service = Neo4jService()

    print(" 2. Criando o nó executor de Cypher...")
    executor_node = create_cypher_executor_node(neo4j_service)

    # ==========================================
    # TESTE 1: Query Válida
    # ==========================================
    print("\n--- INICIANDO TESTE 1: EXECUÇÃO DE SUCESSO ---")
    state_sucesso = {
        "query": "MATCH (n) RETURN COUNT(n) AS total_nodes",
        "is_multistep": False
    }

    novo_estado_sucesso = await executor_node(state_sucesso)
    print("\n✅ Estado Atualizado (Sucesso):")
    print(novo_estado_sucesso)

    # ==========================================
    # TESTE 2: Query Inválida (Simulando erro de sintaxe)
    # ==========================================

    print("\n--- INICIANDO TESTE 2: ERRO DE SINTAXE (NEEDS CORRECTION) ---")
    state_erro = {
        "query": "MATCH (n) RETURNNNN n", # 'RETURNNNN' está errado de propósito
        "is_multistep": False,
        "correction_attempts": 0
    }

    novo_estado_erro = await executor_node(state_erro)
    print("\n⚠️ Estado Atualizado (Erro/Correção):")
    print(novo_estado_erro)


    # ==========================================
    # TESTE 3: Cenário Multi-step (Simulando o Passo 0)
    # ==========================================
    print("\n--- INICIANDO TESTE 3: MULTI-STEP (PASSO 0) ---")
    state_multistep = {
        "query": "MATCH (c:Course) RETURN COUNT(c) AS total_cursos", # Query do passo atual
        "is_multistep": True,
        "sub_questions": [
            "Quantos cursos existem?", 
            "Qual o curso mais caro?"
        ],
        "current_step": 0, # Estamos executando a query da primeira sub-pergunta
        "sub_results": []  # Ainda não temos resultados acumulados
    }
    
    novo_estado_multistep = await executor_node(state_multistep)
    print("\n🔄 Estado Atualizado (Multi-step - Preparando para o Passo 1):")
    print(novo_estado_multistep)
if __name__ == "__main__":
    asyncio.run(main())