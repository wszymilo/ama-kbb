"""Canonical CrewAI search tool using Serper."""

import os

from crewai.tools import tool


@tool("search")
def search(query: str, num_results: int = 10) -> str:
    """
    Search the web for information using Google search via Serper.

    Args:
        query: The search query string.
        num_results: Maximum number of results to return (default: 10).

    Returns:
        A formatted string containing search results with title, URL, and snippet.
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return "Error: SERPER_API_KEY environment variable not set"

    import httpx

    url = "https://google.serper.dev/search"
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }
    payload = {"q": query, "num": num_results}

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, headers=headers, json=payload)

            if response.status_code != 200:
                return f"Error: Serper API returned status {response.status_code}"

            data = response.json()
            organic = data.get("organic", [])

            if not organic:
                return f"No results found for query: {query}"

            results = []
            for item in organic:
                title = item.get("title", "")
                link = item.get("link", "")
                snippet = item.get("snippet", "")

                results.append(f"Title: {title}\nURL: {link}\nSnippet: {snippet}\n")

            return "\n---\n".join(results)

    except httpx.TimeoutException:
        return "Error: Serper API request timed out"
    except Exception as e:
        return f"Error: Failed to execute search - {str(e)}"
