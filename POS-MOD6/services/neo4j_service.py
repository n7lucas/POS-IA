import logging
import asyncio
from typing import Any, List, Dict
from langchain_community.graphs import Neo4jGraph
from config import settings

logger = logging.getLogger(__name__)


class Neo4jService:
    def __init__(self):
        #Inicializa a conexão com o banco
        self.graph = Neo4jGraph(
            url=settings.neo4j_uri,
            username=settings.neo4j_user,
            password=settings.neo4j_password,
            enhanced_schema=False #Focado em um schema mais limpo para LLMS
        )


    async def get_schema(self) -> str:
        """Obtém o schema atualizado do banco para injetar no prompt"""
        try:
            await asyncio.to_thread(self.graph.refresh_schema)
            return self.graph.schema
        except Exception as e:
            logger.error(f"❌ Erro ao obter o schema")
            return ""


    async def validade_query(self, query: str) -> bool:
        """Usa o comando EXPLAIN para validar se a sintaxe da query está correta antes de executar."""
        try:
            await asyncio.to_thread(self.graph.query, f"EXPLAIN {query}")
            return True
        except Exception as e:
            logger.error(f"❌ Falha na validação da query: {e}")
            return False

    async def query(self, cypher_query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Executa a query de fato e retorna os dados."""
        try:
            params = parameters or {}
            result = await asyncio.to_thread(self.graph.query, cypher_query, params=params)
            return result
        except Exception as e:
            logger.error(f"❌ Erro executando a query: {e}")
            raise e