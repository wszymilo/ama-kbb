import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    EMBEDDING_MODEL: str = "nomic-ai/nomic-embed-text-v1.5"
    CHROMA_DIR: str = "./artifacts/chroma.db"
    COLLECTION_NAME: str = "kbb"
    MCP_URL: str | None = None


@lru_cache
def get_config() -> Config:
    return Config(
        EMBEDDING_MODEL=os.getenv("EMBEDDING_MODEL", "nomic-ai/nomic-embed-text-v1.5"),
        CHROMA_DIR=os.getenv("CHROMA_DIR", "./artifacts/chroma.db"),
        COLLECTION_NAME=os.getenv("COLLECTION_NAME", "kbb"),
        MCP_URL=os.getenv("MCP_URL") or None,
    )
