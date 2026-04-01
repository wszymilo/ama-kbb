import os
import unittest
from unittest.mock import patch

from kbb.config import get_config


class TestConfig(unittest.TestCase):
    def setUp(self):
        get_config.cache_clear()

    @patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "test-key",
            "MODEL": "gpt-4o",
            "EMBEDDING_MODEL": "custom-embedding",
            "CHROMA_DIR": "./custom/chroma",
            "COLLECTION_NAME": "test_collection",
            "MCP_URL": "http://localhost:8000",
        },
    )
    def test_valid_config_with_all_fields(self):
        get_config.cache_clear()
        config = get_config()

        self.assertEqual(config.OPENAI_API_KEY, "test-key")
        self.assertEqual(config.MODEL, "gpt-4o")
        self.assertEqual(config.EMBEDDING_MODEL, "custom-embedding")
        self.assertEqual(config.CHROMA_DIR, "./custom/chroma")
        self.assertEqual(config.COLLECTION_NAME, "test_collection")
        self.assertEqual(config.MCP_URL, "http://localhost:8000")

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "MODEL": "gpt-4o"})
    def test_default_values_for_optional_fields(self):
        get_config.cache_clear()
        config = get_config()

        self.assertEqual(config.EMBEDDING_MODEL, "nomic-ai/nomic-embed-text-v1.5")
        self.assertEqual(config.CHROMA_DIR, "./artifacts/chroma.db")
        self.assertEqual(config.COLLECTION_NAME, "kbb")
        self.assertIsNone(config.MCP_URL)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "", "MODEL": "gpt-4o"})
    def test_missing_openai_api_key_raises_error(self):
        get_config.cache_clear()
        with self.assertRaises(ValueError) as ctx:
            get_config()
        self.assertEqual(str(ctx.exception), "OPENAI_API_KEY is required")

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "MODEL": ""})
    def test_missing_model_raises_error(self):
        get_config.cache_clear()
        with self.assertRaises(ValueError) as ctx:
            get_config()
        self.assertEqual(str(ctx.exception), "MODEL is required")

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "MODEL": "gpt-4o"})
    def test_config_caching(self):
        get_config.cache_clear()
        config1 = get_config()
        config2 = get_config()
        self.assertIs(config1, config2)

    @patch.dict(
        os.environ, {"OPENAI_API_KEY": "test-key", "MODEL": "gpt-4o", "MCP_URL": ""}
    )
    def test_mcp_url_empty_string_converted_to_none(self):
        get_config.cache_clear()
        config = get_config()
        self.assertIsNone(config.MCP_URL)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "MODEL": "gpt-4o"})
    def test_config_immutability(self):
        get_config.cache_clear()
        config = get_config()
        with self.assertRaises(Exception):
            config.OPENAI_API_KEY = "new-key"


if __name__ == "__main__":
    unittest.main()
