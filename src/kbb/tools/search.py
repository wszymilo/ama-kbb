import json

from mcp.types import TextContent
from .base import SearchTool, SearchResult 
from .mcp_client_manager import MCPClientManager


class SerperSearchTool(SearchTool):
    ''' Search tool using serper-toolkit MCP server. '''

    def __init__(self, mcp_client: MCPClientManager, server_name: str = 'serper'):
        self.client = mcp_client
        self.server_name = server_name

    async def search(self, query: str, num_results: int = 10) -> list[SearchResult]:
        ''' Execute search via serper-toolkit MCP server and return results. '''
        result = await self.client.call_tool(
            server_name=self.server_name,
            tool_name='search_web',
            arguments={
                'query': query,
                'search_num': num_results
            }
        )

        if result.isError:
            if isinstance(result, TextContent):
                error_text = result.text
            else:
                error_text = str(result)
            raise RuntimeError(f'Search tool call failed: {error_text}')

        text_content = [c.text for c in result.content if isinstance(c, TextContent)]
        if not text_content:
            raise RuntimeError(
                'Search results did not contain any text content.')

        data = json.loads(text_content[0])

        organic = data.get('results', [])

        return [
            SearchResult(
                title=item.get('title', ''),
                url=item.get('link', ''),
                snippet=item.get('snippet', None)
            ) for item in organic
        ]
