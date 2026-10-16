# services/mcp_service.py
import os
import asyncio
import logging
from typing import List
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

logger = logging.getLogger(__name__)


class McpService:
    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)
        self.client: MultiServerMCPClient = None
        self._tools_cache: List[BaseTool] = []

    def _init_mcp_client(self) -> MultiServerMCPClient:
        return MultiServerMCPClient({
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", self.root_dir],
                "transport": "stdio",
            }
        })

    async def get_tools(self) -> List[BaseTool]:
        """Obtém as ferramentas do MCP Server sem bloquear o loop de eventos."""
        if not self.client:
            self.client = await asyncio.to_thread(self._init_mcp_client)
            self._tools_cache = await self.client.get_tools()
        return self._tools_cache

    async def close(self):
        if self.client:
            await self.client.close()
            self.client = None