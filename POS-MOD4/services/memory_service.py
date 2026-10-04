# services/memory_service.py
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
from config import settings


class MemoryService:
    def __init__(self, postgres_uri: str = settings.postgres_url):
        self.postgres_uri = postgres_uri
        self.pool = None
        self.checkpointer = None

    async def setup(self):
        """Inicializa a pool de conexões e cria as tabelas de checkpoint no Postgres."""
        # open=False evita o aviso de depreciação no construtor
        self.pool = AsyncConnectionPool(
            conninfo=self.postgres_uri,
            max_size=20,
            kwargs={"autocommit": True},
            open=False
        )
        await self.pool.open()

        self.checkpointer = AsyncPostgresSaver(self.pool)
        await self.checkpointer.setup()
        return self.checkpointer

    async def close(self):
        if self.pool:
            await self.pool.close()