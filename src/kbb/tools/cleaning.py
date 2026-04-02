import re

from kbb.schemas.models import CleanDocument, ScrapedDocument
from kbb.tools.utils import generate_document_id


BOILERPLATE_PATTERNS = [
    re.compile(r"^[\s]*Cookie\s*Notice[\s]*$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^[\s]*Cookie\s*Policy[\s]*$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^[\s]*Accept\s*Cookies?[\s]*$", re.IGNORECASE | re.MULTILINE),
    re.compile(
        r"^[\s]*Subscribe\s*to\s*our\s*newsletter[\s]*$", re.IGNORECASE | re.MULTILINE
    ),
    re.compile(r"^[\s]*Follow\s*us\s*on[\s]*$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^[\s]*Share\s*this[\s]*$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^[\s]*Back\s*to\s*top[\s]*$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^[\s]*Copyright\s*\d+[\s]*.*$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^[\s]*Privacy\s*Policy[\s]*$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^[\s]*Terms?\s*of\s*Service[\s]*$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^[\s]*All\s*rights?\s*reserved[\s]*$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^[\s]*Menu[\s]*$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^[\s]*Home[\s]*$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^[\s]*About[\s]*$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^[\s]*Contact[\s]*$", re.IGNORECASE | re.MULTILINE),
]

MIN_CONTENT_LENGTH = 100


class DocumentCleaner:
    """Deterministic document cleaning and normalization pipeline.

    Processes scraped documents to remove noise, normalize whitespace,
    and filter low-value content before chunking for RAG storage.
    """

    def __init__(self, min_content_length: int = MIN_CONTENT_LENGTH):
        self.min_content_length = min_content_length

    def clean(self, document: ScrapedDocument) -> CleanDocument:
        """Clean and normalize a scraped document.

        Args:
            document: The scraped document to clean.

        Returns:
            `CleanDocument` with cleaned text or filter reason if rejected.
        """
        if document.fetch_status != "success":
            return self._filtered_document(document, "fetch_failed")

        content = document.content
        if not content or not content.strip():
            return self._filtered_document(document, "empty_content")

        if len(content.strip()) < self.min_content_length:
            return self._filtered_document(document, "insufficient_content")

        cleaned = self._normalize_whitespace(content)
        cleaned = self._strip_boilerplate(cleaned)

        if not cleaned.strip() or len(cleaned.strip()) < self.min_content_length:
            return self._filtered_document(
                document, "insufficient_content_after_cleaning"
            )

        return CleanDocument(
            status="cleaned",
            source_url=document.source_url,
            title=document.title,
            document_id=generate_document_id(document.source_url),
            cleaned_text=cleaned,
            filter_reason=None,
        )

    def _filtered_document(
        self, document: ScrapedDocument, reason: str
    ) -> CleanDocument:
        """Create a filtered document with the given reason."""
        return CleanDocument(
            status="filtered",
            source_url=document.source_url,
            title=document.title,
            document_id=generate_document_id(document.source_url),
            cleaned_text="",
            filter_reason=reason,
        )

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text."""
        text = re.sub(r"\r\n", "\n", text)
        text = re.sub(r"\r", "\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _strip_boilerplate(self, text: str) -> str:
        """Remove common boilerplate lines from text."""
        lines = text.split("\n")
        cleaned_lines = [
            line
            for line in lines
            if not any(p.match(line.strip()) for p in BOILERPLATE_PATTERNS)
        ]
        return "\n".join(cleaned_lines).strip()
