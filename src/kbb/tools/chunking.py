from typing import List, Optional

from langchain_text_splitters import MarkdownHeaderTextSplitter

from kbb.schemas.models import CleanDocument, ChunkRecord
from kbb.config import get_config
from kbb.tools.utils import generate_document_id

DEFAULT_HEADERS = [
    ("#", "Header1"),
    ("##", "Header2"),
    ("###", "Header3"),
    ("####", "Header4"),
]
DEFAULT_OVERLAP_TOKENS = 100


class DocumentChunker:
    """Chunks cleaned documents into RAG-ready text units with metadata."""

    def __init__(
        self,
        headers_to_split_on: Optional[List[tuple]] = None,
        overlap_tokens: int = DEFAULT_OVERLAP_TOKENS,
    ):
        self.splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on or DEFAULT_HEADERS,
            strip_headers=True,
        )
        self.overlap_tokens = overlap_tokens

    def chunk(self, documents: List[CleanDocument]) -> List[ChunkRecord]:
        """Chunk a list of clean documents into ChunkRecords.

        Args:
            documents: List of CleanDocument objects (status='cleaned')

        Returns:
            List of ChunkRecord objects ready for embedding
        """
        config = get_config()
        chunks = []

        for doc in documents:
            if doc.status != "cleaned" or not doc.cleaned_text:
                continue

            doc_id = doc.document_id or generate_document_id(doc.source_url)
            langchain_docs = self.splitter.split_text(doc.cleaned_text)
            text_chunks = [doc.page_content for doc in langchain_docs]
            text_chunks = self._apply_overlap(text_chunks)

            for idx, chunk_text in enumerate(text_chunks):
                chunks.append(
                    ChunkRecord(
                        document_id=f"{doc_id}_ch_{idx}",
                        chunk_text=chunk_text,
                        metadata={
                            "source_url": doc.source_url,
                            "title": doc.title,
                            "chunk_index": f"ch_{idx}",
                        },
                        collection_name=config.COLLECTION_NAME,
                    )
                )

        return chunks

    def _apply_overlap(self, chunks: List[str]) -> List[str]:
        """Apply token-based overlap between chunks."""
        if self.overlap_tokens <= 0 or len(chunks) <= 1:
            return chunks

        result = [chunks[0]]
        for chunk in chunks[1:]:
            prev = result[-1]
            overlap_chars = self.overlap_tokens * 4
            if len(prev) > overlap_chars:
                overlap = prev[-overlap_chars:]
                chunk = overlap + "\n" + chunk
            result.append(chunk)
        return result
