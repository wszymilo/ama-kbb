from urllib.parse import urlparse


def generate_document_id(url: str) -> str:
    """Generate document_id from URL by slugifying."""
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "-")
    return f"{parsed.netloc}-{path}" if path else parsed.netloc
