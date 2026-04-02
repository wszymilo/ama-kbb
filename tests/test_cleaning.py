import unittest

from kbb.schemas.models import ScrapedDocument
from kbb.tools.cleaning import DocumentCleaner


class TestDocumentCleaner(unittest.TestCase):
    """Unit tests for DocumentCleaner class."""

    def setUp(self):
        self.cleaner = DocumentCleaner()

    def test_clean_success_with_valid_content(self):
        doc = ScrapedDocument(
            source_url="https://example.com",
            title="Test Article",
            fetch_status="success",
            content="This is valid content with enough length to pass the minimum content length requirement for cleaning.",
        )
        result = self.cleaner.clean(doc)

        self.assertEqual(result.status, "cleaned")
        self.assertEqual(result.source_url, "https://example.com")
        self.assertEqual(result.title, "Test Article")
        self.assertIn("valid content", result.cleaned_text)
        self.assertIsNone(result.filter_reason)

    def test_clean_filter_fetch_failed(self):
        doc = ScrapedDocument(
            source_url="https://example.com",
            title="Test",
            fetch_status="failed",
            content="Some content",
        )
        result = self.cleaner.clean(doc)

        self.assertEqual(result.status, "filtered")
        self.assertEqual(result.filter_reason, "fetch_failed")
        self.assertEqual(result.cleaned_text, "")

    def test_clean_filter_empty_content(self):
        doc = ScrapedDocument(
            source_url="https://example.com",
            title="Test",
            fetch_status="success",
            content="",
        )
        result = self.cleaner.clean(doc)

        self.assertEqual(result.status, "filtered")
        self.assertEqual(result.filter_reason, "empty_content")

    def test_clean_filter_insufficient_content(self):
        doc = ScrapedDocument(
            source_url="https://example.com",
            title="Test",
            fetch_status="success",
            content="Short content",
        )
        result = self.cleaner.clean(doc)

        self.assertEqual(result.status, "filtered")
        self.assertEqual(result.filter_reason, "insufficient_content")

    def test_clean_whitespace_normalized(self):
        doc = ScrapedDocument(
            source_url="https://example.com",
            title="Test",
            fetch_status="success",
            content="Line1 with content here  \n\n\n\n  Line2 with more content here\r\n\r\n   Line3 has even more content and makes this longer than one hundred characters.",
        )
        result = self.cleaner.clean(doc)

        self.assertEqual(result.status, "cleaned")
        self.assertNotIn("  ", result.cleaned_text)
        self.assertNotIn("\n\n\n", result.cleaned_text)

    def test_clean_strips_boilerplate(self):
        content = """Article Title
This is the main content of the article.
It contains useful information about various topics.
This section provides additional details and context.

Copyright 2024
Privacy Policy
Terms of Service
All rights reserved.
"""
        doc = ScrapedDocument(
            source_url="https://example.com",
            title="Test",
            fetch_status="success",
            content=content,
        )
        result = self.cleaner.clean(doc)

        self.assertEqual(result.status, "cleaned")
        self.assertNotIn("Copyright", result.cleaned_text)
        self.assertNotIn("Privacy Policy", result.cleaned_text)
        self.assertIn("main content", result.cleaned_text)

    def test_clean_preserves_title_and_url(self):
        doc = ScrapedDocument(
            source_url="https://example.com/article",
            title="My Article",
            fetch_status="success",
            content="This is some content that is long enough to pass the minimum length check for cleaning.",
        )
        result = self.cleaner.clean(doc)

        self.assertEqual(result.source_url, "https://example.com/article")
        self.assertEqual(result.title, "My Article")

    def test_clean_custom_min_length(self):
        cleaner = DocumentCleaner(min_content_length=200)
        doc = ScrapedDocument(
            source_url="https://example.com",
            title="Test",
            fetch_status="success",
            content="A" * 150,
        )
        result = cleaner.clean(doc)

        self.assertEqual(result.status, "filtered")
        self.assertEqual(result.filter_reason, "insufficient_content")

    def test_clean_filter_after_boilerplate_removal(self):
        content = "X" * 80 + "\n\nPrivacy Policy\nTerms of Service\n"
        doc = ScrapedDocument(
            source_url="https://example.com",
            title="Test",
            fetch_status="success",
            content=content,
        )
        result = self.cleaner.clean(doc)

        self.assertEqual(result.status, "filtered")
        self.assertEqual(result.filter_reason, "insufficient_content_after_cleaning")


if __name__ == "__main__":
    unittest.main()
