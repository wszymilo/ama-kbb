"""Canonical CrewAI scraper tool using httpx and html2text."""

from datetime import datetime
import html2text
import httpx

from crewai.tools import tool


@tool("scrape_urls")
def scrape_urls(urls: list[str], max_length: int = 50000) -> str:
    """
    Fetch content from a list of URLs and return as markdown.

    Args:
        urls: List of URLs to fetch.
        max_length: Maximum characters per page (default: 50000).

    Returns:
        JSON string of ScrapedDocument list with markdown content.
    """
    import json

    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.ignore_emphasis = False
    h.body_width = 0

    results = []

    for url in urls:
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, follow_redirects=True)

                if response.status_code != 200:
                    results.append(
                        {
                            "source_url": url,
                            "title": None,
                            "fetch_status": "failed",
                            "content": f"HTTP {response.status_code}",
                            "fetched_at": datetime.now().isoformat(),
                        }
                    )
                    continue

                html_content = response.text
                content = h.handle(html_content)

                if len(content) > max_length:
                    content = content[:max_length] + "\n\n[truncated]"

                title = _extract_title(html_content) or url

                results.append(
                    {
                        "source_url": url,
                        "title": title,
                        "fetch_status": "success",
                        "content": content,
                        "fetched_at": datetime.now().isoformat(),
                    }
                )

        except httpx.TimeoutException:
            results.append(
                {
                    "source_url": url,
                    "title": None,
                    "fetch_status": "failed",
                    "content": "Request timed out",
                    "fetched_at": datetime.now().isoformat(),
                }
            )
        except Exception as e:
            results.append(
                {
                    "source_url": url,
                    "title": None,
                    "fetch_status": "failed",
                    "content": f"Error: {str(e)}",
                    "fetched_at": datetime.now().isoformat(),
                }
            )

    return json.dumps(results, indent=2)


def _extract_title(html: str) -> str | None:
    """Extract title from HTML."""
    import re

    match = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    match = re.search(r"<h1[^>]*>([^<]+)</h1>", html, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    return None
