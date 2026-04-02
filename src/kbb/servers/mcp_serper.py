import os
import re
import json
import logging
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(override=True)

mcp = FastMCP('mcp-serper')

@mcp.tool()
async def search_web(query: str, num_results: int = 5):
    '''
    Search the web for the given query and return top results.

    @param query: The search query string.
    @param num_results: The number of top results to return (default is 5).

    Returns a JSON string containing a list of search results, where each result includes the title, link, and snippet. If an error occurs during the web search, an appropriate error message is returned.
    '''
    serper_api_key = os.getenv('SERPER_API_KEY')
    if not serper_api_key:
        return json.dumps({'error': 'SERPER_API_KEY not set in environment variables'}, indent=2)

    api_url = 'https://google.serper.dev/search'
    headers = {
        'X-API-KEY': serper_api_key,
        'Content-Type': 'application/json'
    }
    payload = {
        'q': query,
        'num': num_results
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        results = [{
            'title': item.get('title', ''),
            'link': item.get('link', ''),
            'snippet': item.get('snippet', '')
        } for item in data.get('organic', [])[:num_results]]

        return json.dumps({'results': results}, indent=2)

    except httpx.TimeoutException as e:
        logging.error(f'Timeout error during web search: {e}')
        return json.dumps({'error': f'Timeout error during web search: {e}'}, indent=2)
    except httpx.HTTPStatusError as e:
        logging.error(f'HTTP error during web search: {e}')
        return json.dumps({'error': f'HTTP error during web search: {e}'}, indent=2)
    except Exception as e:
        logging.error(f'Unexpected error during web search: {e}')
        return json.dumps({'error': f'Unexpected error during web search: {e}'}, indent=2)


@mcp.tool()
async def fetch_url(url: str, max_char: int = 5000):
    '''
    Fetch and extract readable text from a URL.
    Returns JSON with the URL, status, content (plain text, stripped of HTML tags),
    and whether truncation occurred if content exceeds max_char limit.

    @param url: The URL to fetch.
    @param max_char: Maximum number of characters to return from the content (default is 5000).

    Returns a JSON string containing the final URL after redirects, HTTP status code, extracted content (plain text with HTML tags stripped), and a boolean indicating whether the content was truncated due to exceeding the max_char limit. If an error occurs during fetching or processing the URL, an appropriate error message is returned in JSON format.
    '''
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '')

            if 'text/html' in content_type:
                # Simple regex to strip HTML tags (for demonstration)
                text = re.sub(r'<style[^>]*>.*?</style>', ' ', response.text, flags=re.DOTALL | re.IGNORECASE)
                text = re.sub(r'<script[^>]*>.*?</script>', ' ', text, flags=re.DOTALL | re.IGNORECASE)
                # Remove remaining HTML tags
                text = re.sub(r'<[^>]+>', ' ', text)
                # Collapse multiple spaces
                text = re.sub(r'\s+', ' ', text).strip()
            else:
                text = response.text.strip()

        truncated = len(text) > max_char
        content = text[:max_char] + '... [truncated]' if truncated else text

        return json.dumps({
            'url': str(response.url),
            'status': response.status_code,
            'content': content,
            'truncated': truncated
        }, indent=2)

    except httpx.TimeoutException as e:
        logging.error(f'Timeout error fetching URL {url}: {e}')
        return json.dumps({'error': f'Timeout error fetching URL: {e}'}, indent=2)
    except httpx.ConnectError as e:
        logging.error(f'Connection error fetching URL {url}: {e}')
        return json.dumps({'error': f'Connection error fetching URL: {e}'}, indent=2)
    except httpx.HTTPStatusError as e:
        logging.error(f'HTTP error fetching URL {url}: {e}')
        return json.dumps({'error': f'HTTP error fetching URL: {e}'}, indent=2)
    except Exception as e:
        logging.error(f'Unexpected error fetching URL {url}: {e}')
        return json.dumps({'error': f'Unexpected error fetching URL: {e}'}, indent=2)

if __name__ == '__main__':
    mcp.run()
