import unittest
from unittest.mock import patch

from kbb.schemas.models import CleanDocument
from kbb.tools.chunking import DocumentChunker
from kbb.tools.utils import generate_document_id


class TestDocumentChunker(unittest.TestCase):
    """Unit tests for DocumentChunker class."""

    def setUp(self):
        self.chunker = DocumentChunker()

    @patch("kbb.tools.chunking.get_config")
    def test_chunk_produces_records_from_cleaned_doc(self, mock_config):
        mock_config.return_value.COLLECTION_NAME = "test_collection"
        doc = CleanDocument(
            status="cleaned",
            source_url="https://example.com/article",
            title="Test Article",
            document_id="example-com-article",
            cleaned_text="# Header\n\nThis is some content.",
            filter_reason=None,
        )
        result = self.chunker.chunk([doc])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].document_id, "example-com-article_ch_0")
        self.assertIn("This is some content", result[0].chunk_text)

    @patch("kbb.tools.chunking.get_config")
    def test_chunk_skips_filtered_doc(self, mock_config):
        mock_config.return_value.COLLECTION_NAME = "test_collection"
        doc = CleanDocument(
            status="filtered",
            source_url="https://example.com",
            title="Test",
            document_id="example-com",
            cleaned_text="",
            filter_reason="insufficient_content",
        )
        result = self.chunker.chunk([doc])

        self.assertEqual(len(result), 0)

    @patch("kbb.tools.chunking.get_config")
    def test_chunk_skips_empty_text(self, mock_config):
        mock_config.return_value.COLLECTION_NAME = "test_collection"
        doc = CleanDocument(
            status="cleaned",
            source_url="https://example.com",
            title="Test",
            document_id="example-com",
            cleaned_text="",
            filter_reason=None,
        )
        result = self.chunker.chunk([doc])

        self.assertEqual(len(result), 0)

    @patch("kbb.tools.chunking.get_config")
    def test_chunk_index_format_zero_based(self, mock_config):
        mock_config.return_value.COLLECTION_NAME = "test_collection"
        doc = CleanDocument(
            status="cleaned",
            source_url="https://example.com/article",
            title="Test",
            document_id="example-com-article",
            cleaned_text="# H1\nContent 1\n\n## H2\nContent 2\n\n### H3\nContent 3",
            filter_reason=None,
        )
        result = self.chunker.chunk([doc])

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].metadata["chunk_index"], "ch_0")
        self.assertEqual(result[1].metadata["chunk_index"], "ch_1")
        self.assertEqual(result[2].metadata["chunk_index"], "ch_2")

    @patch("kbb.tools.chunking.get_config")
    def test_chunk_preserves_metadata(self, mock_config):
        mock_config.return_value.COLLECTION_NAME = "test_collection"
        doc = CleanDocument(
            status="cleaned",
            source_url="https://example.com/article",
            title="Test Article Title",
            document_id="example-com-article",
            cleaned_text="# Header\nContent here",
            filter_reason=None,
        )
        result = self.chunker.chunk([doc])

        self.assertEqual(
            result[0].metadata["source_url"], "https://example.com/article"
        )
        self.assertEqual(result[0].metadata["title"], "Test Article Title")

    @patch("kbb.tools.chunking.get_config")
    def test_custom_headers(self, mock_config):
        mock_config.return_value.COLLECTION_NAME = "test_collection"
        custom_headers = [("#", "Header1"), ("##", "Header2")]
        chunker = DocumentChunker(headers_to_split_on=custom_headers)
        doc = CleanDocument(
            status="cleaned",
            source_url="https://example.com",
            title="Test",
            document_id="example-com",
            cleaned_text="# H1\nContent 1\n\n## H2\nContent 2\n\n### H3\nContent 3",
            filter_reason=None,
        )
        result = chunker.chunk([doc])

        self.assertEqual(len(result), 2)

    @patch("kbb.tools.chunking.get_config")
    def test_custom_overlap(self, mock_config):
        mock_config.return_value.COLLECTION_NAME = "test_collection"
        chunker = DocumentChunker(overlap_tokens=50)
        doc = CleanDocument(
            status="cleaned",
            source_url="https://example.com",
            title="Test",
            document_id="example-com",
            cleaned_text="# H1\nFirst chunk content here\n\n## H2\nSecond chunk content here",
            filter_reason=None,
        )
        result = chunker.chunk([doc])

        self.assertEqual(len(result), 2)

    @patch("kbb.tools.chunking.get_config")
    def test_collection_name_from_config(self, mock_config):
        mock_config.return_value.COLLECTION_NAME = "my_knowledge_base"
        doc = CleanDocument(
            status="cleaned",
            source_url="https://example.com",
            title="Test",
            document_id="example-com",
            cleaned_text="# Header\nContent",
            filter_reason=None,
        )
        result = self.chunker.chunk([doc])

        self.assertEqual(result[0].collection_name, "my_knowledge_base")

    @patch("kbb.tools.chunking.get_config")
    def test_generates_document_id_from_url(self, mock_config):
        mock_config.return_value.COLLECTION_NAME = "test_collection"
        chunker = DocumentChunker()
        doc = CleanDocument(
            status="cleaned",
            source_url="https://example.com/path/to/page",
            title="Test",
            document_id=None,
            cleaned_text="# Header\nContent",
            filter_reason=None,
        )
        result = chunker.chunk([doc])

        self.assertEqual(result[0].document_id, "example.com-path-to-page_ch_0")

    @patch("kbb.tools.chunking.get_config")
    def test_uses_provided_document_id(self, mock_config):
        mock_config.return_value.COLLECTION_NAME = "test_collection"
        doc = CleanDocument(
            status="cleaned",
            source_url="https://example.com",
            title="Test",
            document_id="custom-doc-id",
            cleaned_text="# Header\nContent",
            filter_reason=None,
        )
        result = self.chunker.chunk([doc])

        self.assertEqual(result[0].document_id, "custom-doc-id_ch_0")

    @patch("kbb.tools.chunking.get_config")
    def test_multiple_documents(self, mock_config):
        mock_config.return_value.COLLECTION_NAME = "test_collection"
        doc1 = CleanDocument(
            status="cleaned",
            source_url="https://example.com/1",
            title="Doc 1",
            document_id="doc-1",
            cleaned_text="# H1\nContent 1",
            filter_reason=None,
        )
        doc2 = CleanDocument(
            status="cleaned",
            source_url="https://example.com/2",
            title="Doc 2",
            document_id="doc-2",
            cleaned_text="# H1\nContent 2",
            filter_reason=None,
        )
        result = self.chunker.chunk([doc1, doc2])

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].document_id, "doc-1_ch_0")
        self.assertEqual(result[1].document_id, "doc-2_ch_0")

    @patch("kbb.tools.chunking.get_config")
    def test_zero_overlap_no_overlap_applied(self, mock_config):
        mock_config.return_value.COLLECTION_NAME = "test_collection"
        chunker = DocumentChunker(overlap_tokens=0)
        doc = CleanDocument(
            status="cleaned",
            source_url="https://example.com",
            title="Test",
            document_id="doc-1",
            cleaned_text="# H1\nFirst\n\n## H2\nSecond",
            filter_reason=None,
        )
        result = chunker.chunk([doc])

        self.assertEqual(len(result), 2)
        self.assertNotIn("First", result[1].chunk_text)

    @patch("kbb.tools.chunking.get_config")
    def test_single_chunk_no_overlap_needed(self, mock_config):
        mock_config.return_value.COLLECTION_NAME = "test_collection"
        chunker = DocumentChunker(overlap_tokens=100)
        doc = CleanDocument(
            status="cleaned",
            source_url="https://example.com",
            title="Test",
            document_id="doc-1",
            cleaned_text="# Header\nContent only",
            filter_reason=None,
        )
        result = chunker.chunk([doc])

        self.assertEqual(len(result), 1)


class TestGenerateDocumentId(unittest.TestCase):
    """Unit tests for generate_document_id utility."""

    def test_generates_id_with_path(self):
        result = generate_document_id("https://example.com/path/to/page")
        self.assertEqual(result, "example.com-path-to-page")

    def test_generates_id_without_path(self):
        result = generate_document_id("https://example.com")
        self.assertEqual(result, "example.com")

    def test_generates_id_with_trailing_slash(self):
        result = generate_document_id("https://example.com/")
        self.assertEqual(result, "example.com")


if __name__ == "__main__":
    unittest.main()
