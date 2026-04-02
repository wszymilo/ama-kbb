import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    OPENAI_API_KEY: str
    MODEL: str
    EMBEDDING_MODEL: str = "nomic-ai/nomic-embed-text-v1.5"
    CHROMA_DIR: str = "./artifacts/chroma.db"
    COLLECTION_NAME: str = "kbb"
    MCP_URL: str | None = None

    def __post_init__(self):
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        if not self.MODEL:
            raise ValueError("MODEL is required")


@lru_cache
def get_config() -> Config:
    return Config(
        # TODO: #37 No need for this as we already can parse this via config file
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY", ""),
        MODEL=os.getenv("MODEL", ""),
        EMBEDDING_MODEL=os.getenv("EMBEDDING_MODEL", "nomic-ai/nomic-embed-text-v1.5"),
        CHROMA_DIR=os.getenv("CHROMA_DIR", "./artifacts/chroma.db"),
        COLLECTION_NAME=os.getenv("COLLECTION_NAME", "kbb"),
        MCP_URL=os.getenv("MCP_URL") or None,
    )
