from datetime import datetime
import json
from mcp.types import TextContent
from .base import FetchTool
from .mcp_client_manager import MCPClientManager
from ..schemas.models import ScrapedDocument


class Fetch(FetchTool):
    def __init__(self, mcp_client_manager: MCPClientManager, server_name: str = "fetch"):
        self.mcp_client_manager = mcp_client_manager
        self.server_name = server_name

    async def fetch(self, url: str, max_length: int = 10000) -> list[ScrapedDocument]:
        result = await self.mcp_client_manager.call_tool(
            server_name=self.server_name,
            tool_name="fetch_url",
            arguments={"url": url, 'max_char': max_length},
        )

        if result.isError:
            if isinstance(result, TextContent):
                error_message = result.text
            else:
                error_message = str(result)
            raise Exception(f"Error fetching URL: {error_message}")

        text_content = [
            c.text for c in result.content if isinstance(c, TextContent)]

        docs: list[ScrapedDocument] = []
        try:
            for text in text_content:
                data = json.loads(text)
                docs.append(ScrapedDocument(
                    source_url=data.get("source_url", ""),
                    title=data.get("title", ""),
                    fetch_status='success',
                    content=data.get("content", ""),
                    fetched_at=datetime.now())
                )
            return docs
        except json.JSONDecodeError:
            raise Exception("Failed to parse JSON from the fetched content.")

        # if not text_content:
            # raise Exception("No text content found in the result.")

        # return "\n".join(text_content)
