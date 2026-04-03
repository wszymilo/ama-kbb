from abc import ABC, abstractmethod

from pydantic import BaseModel

from kbb.schemas.models import ScrapedDocument


class SearchResult(BaseModel):
    ''' Represents a single search result. '''
    title: str
    url: str
    snippet: str

class SearchTool(ABC):
    ''' Abstract interface for web search tools. '''
    @abstractmethod
    async def search(self, query: str, num_results: int) -> list[SearchResult]:
        ''' Search the web for the given query and return a list of SearchResult objects. '''
        pass

class FetchTool(ABC):
    ''' Abstract interface for fetching and cleaning web content. '''
    @abstractmethod
    async def fetch(self, url: str, max_length: int) -> list[ScrapedDocument]:
        ''' Fetch a URL and return a clean markdown string of the content. '''
