from contextlib import AsyncExitStack
from typing import Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import CallToolResult
from pydantic import BaseModel


class MCPServerConfig(BaseModel):
    ''' Configuration for an MCP server connection. '''
    name: str
    command: str
    args: list[str] = []
    env: dict[str, str] = {}


class MCPClientManager:
    ''' Manages MCP server connections and provides tool calling '''

    def __init__(self, configs: dict[str, MCPServerConfig] = {}):
        self.configs: dict[str, MCPServerConfig] = configs 
        self.sessions: dict[str, ClientSession] = {}
        self._stack = AsyncExitStack()

    async def initialize(self) -> None:
        ''' Start all configured MCP servers and establish sessions.'''
        for name, config in self.configs.items():
            print(f"Initializing server '{name}' with command: {config.command} {config.args}")
            server_params = StdioServerParameters(
                command=config.command,
                args=config.args,
                env=config.env
            )
            try:
                read, write = await self._stack.enter_async_context(
                    stdio_client(server_params)
                )
                session = await self._stack.enter_async_context(
                    ClientSession(read, write)
                )
                await session.initialize()
                self.sessions[name] = session
            except Exception as e:
                raise RuntimeError(
                    f"Failed to initialize server '{name}': {e}")

    async def call_tool(self, server_name: str, tool_name: str, arguments: dict[str, Any]) -> CallToolResult:
        ''' Calls a tool on the specified server. '''
        session = self.sessions.get(server_name)
        if not session:
            raise ValueError(f"Server '{server_name}' is not initialized.")

        try:
            result = await session.call_tool(tool_name, arguments=arguments)
            return result
        except Exception as e:
            raise RuntimeError(
                f"Failed to call tool '{tool_name}' on server '{server_name}': {e}")


    async def cleanup(self) -> None:
        ''' Closes all server connections. '''
        await self._stack.aclose()

    async def __aenter__(self):
        await self.initialize()
        self.initialized = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
        self.initialized = False


