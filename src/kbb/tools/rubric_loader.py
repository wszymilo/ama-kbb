"""Utility for loading and parsing domain rubric YAML files."""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)


class RubricLoader:
    """Load and parse rubric YAML files for SME review."""

    REQUIRED_FIELDS = ["domain"]

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def load_from_path(self, path: str) -> Dict[str, Any]:
        """
        Load and parse a rubric YAML file.

        Args:
            path: Path to the rubric YAML file

        Returns:
            Dictionary containing rubric criteria

        Raises:
            FileNotFoundError: If rubric file doesn't exist
            ValueError: If rubric file is invalid/missing required fields
        """
        if not path:
            return {}

        if path in self._cache:
            logger.debug(f"Returning cached rubric: {path}")
            return self._cache[path]

        rubric_path = Path(path)
        if not rubric_path.exists():
            raise FileNotFoundError(f"Rubric file not found: {path}")

        try:
            with open(rubric_path, "r") as f:
                rubric = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in rubric file: {e}")

        if not isinstance(rubric, dict):
            raise ValueError("Rubric file must contain a YAML dictionary")

        if not self.validate_rubric(rubric):
            raise ValueError(
                f"Rubric missing required fields. Required: {self.REQUIRED_FIELDS}"
            )

        self._cache[path] = rubric
        logger.info(f"Loaded rubric from {path}: {rubric.get('domain', 'unknown')}")
        return rubric

    def validate_rubric(self, rubric: Dict[str, Any]) -> bool:
        """
        Validate that rubric has required fields.

        Args:
            rubric: Rubric dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        for field in self.REQUIRED_FIELDS:
            if field not in rubric:
                return False
        return True

    def get_rubric_summary(self, rubric: Dict[str, Any]) -> str:
        """
        Create a formatted summary of rubric for agent context.

        Args:
            rubric: Rubric dictionary

        Returns:
            Formatted string summary
        """
        summary_parts = []

        if domain := rubric.get("domain"):
            summary_parts.append(f"Domain: {domain}")

        if trusted := rubric.get("trusted_source_types"):
            summary_parts.append(f"Trusted source types: {', '.join(trusted)}")

        if institutions := rubric.get("preferred_institutions_publishers"):
            summary_parts.append(
                f"Preferred institutions: {', '.join(institutions[:3])}..."
            )

        if disallowed := rubric.get("disallowed_source_patterns"):
            summary_parts.append(f"Disallowed patterns: {', '.join(disallowed)}")

        if recency := rubric.get("recency_expectations"):
            summary_parts.append(f"Recency: {recency}")

        if terminology := rubric.get("key_terminology"):
            summary_parts.append(f"Key terminology: {', '.join(terminology[:5])}...")

        if evidence := rubric.get("evidence_requirements"):
            summary_parts.append(f"Evidence requirements: {', '.join(evidence)}")

        return "\n".join(summary_parts)


# Singleton instance for reuse
_rubric_loader: Optional[RubricLoader] = None


def get_rubric_loader() -> RubricLoader:
    """Get or create the global RubricLoader instance."""
    global _rubric_loader
    if _rubric_loader is None:
        _rubric_loader = RubricLoader()
    return _rubric_loader
