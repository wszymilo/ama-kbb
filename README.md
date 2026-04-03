# AMA-KBB - Autonomous Multi-Agent Knowledge Base Builder

AMA-KBB is an autonomous multi-agent system that builds RAG-ready knowledge bases from a user-provided topic. It combines LLM-powered research agents with deterministic document processing to produce clean, chunked, and embedded content stored in ChromaDB.

## Architecture

The pipeline consists of two distinct phases:

### Phase 1: LLM-Powered Research

```
topic + rubric
    |
    v
Researcher Agent --> ResearchPlan (objectives, subtopics, search queries)
    |
    v
Scraper Agent --> Fetches content from search query URLs
    |
    v
Plan Reviewer (SME) --> Validates plan against rubric
    |
    v
Research Agent --> Finds candidate sources via search tool
    |
    v
Source Reviewer (SME) --> Filters sources against rubric
```

### Phase 2: Deterministic Processing

```
ScrapedDocument (from Phase 1)
    |
    v
Document Cleaner --> Removes boilerplate, normalizes whitespace
    |
    v
Document Chunker --> Splits into RAG-ready chunks (MarkdownHeaderTextSplitter)
    |
    v
Embedding Generator --> Generates vectors (nomic-ai/nomic-embed-text-v1.5)
    |
    v
ChromaDB Storage --> Stores chunks with metadata
    |
    v
Run Summary --> JSON with metrics + markdown files
```

## CLI Usage

```bash
# Navigate to project directory
cd /home/wszymilo/code/PY/andela/group-projects/ama-kbb/kbb

# Basic run
uv run kbb run --topic "quantum computing"

# With rubric for domain-specific validation
uv run kbb run --topic "quantum error correction" --rubric rubrics/quantum_error_correction.yaml

# With custom year
uv run kbb run --topic "AI trends" --current-year 2026
```

## Output Artifacts

Each run creates a timestamped directory under `artifacts/`:

```
artifacts/run_20260403_151104/
├── documents/           # Cleaned markdown files (one per source)
│   ├── arxiv.org-abs-2205.01715.md
│   └── www.nature.com-articles-s41586-019-1771-3.md
├── chroma.db/           # ChromaDB vector store for this run
│   └── chroma.sqlite3
└── summary.json         # Run metrics
```

Example `summary.json`:
```json
{
  "run_id": "run_20260403_151104",
  "topic": "quantum computing",
  "metrics": {
    "documents_scraped": 8,
    "documents_cleaned": 8,
    "documents_filtered": 0,
    "chunks_created": 8,
    "chunks_stored": 8,
    "markdown_files_saved": 8
  }
}
```

## Key Components

| Component | File | Description |
|-----------|------|-------------|
| Workflow | `src/kbb/crew.py` | KbbWorkflow class with LLM and deterministic phases |
| CLI | `src/kbb/main.py` | Typer-based command interface |
| Config | `src/kbb/config.py` | Configuration dataclass |
| Schemas | `src/kbb/schemas/models.py` | Pydantic models for agent outputs |
| Search Tool | `src/kbb/tools/search.py` | Serper-based web search |
| Scrape Tool | `src/kbb/tools/scrape.py` | URL content fetching with html2text |
| Document Cleaner | `src/kbb/tools/cleaning.py` | Removes boilerplate, normalizes text |
| Document Chunking | `src/kbb/tools/chunking.py` | Markdown-aware text splitting |
| ChromaDB Storage | `src/kbb/storage/chroma_store.py` | Vector store interface |

## Agent Configuration

Agents and tasks are defined in YAML:

- `src/kbb/config/agents.yaml` - Agent role, goal, backstory, tools
- `src/kbb/config/tasks.yaml` - Task description, expected output, output schema

## Dependencies

Core dependencies in `pyproject.toml`:

- `crewai[tools]` - Agent orchestration
- `litellm` - Multi-provider LLM access
- `chromadb` - Vector database
- `sentence-transformers` - Embedding model (nomic-ai/nomic-embed-text-v1.5)
- `langchain-text-splitters` - Text chunking
- `html2text` - HTML to markdown conversion
- `httpx` - HTTP client for fetching

## Environment Variables

Create a `.env` file:

```
OPENAI_API_KEY=sk-your-key
SERPER_API_KEY=your-serper-key
MODEL=openai/gpt-4o-mini
EMBEDDING_MODEL=nomic-ai/nomic-embed-text-v1.5
CHROMA_DIR=./artifacts/chroma.db
COLLECTION_NAME=kbb
```

## Testing

```bash
cd /home/wszymilo/code/PY/andela/group-projects/ama-kbb/kbb

# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_chunking.py -v

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing
```

## Linting

```bash
cd /home/wszymilo/code/PY/andela/group-projects/ama-kbb/kbb

# Ruff linting
uv run ruff check src/
uv run ruff format src/

# Type checking
uv run mypy src/
```

## Limitations

1. **Content Fetching**: The scraper fetches publicly available content. Academic publishers (Nature, ScienceDirect, etc.) typically only expose abstracts to unauthenticated users. Full PDF fetching is not currently implemented.

2. **Search**: Uses Serper for web search. Requires SERPER_API_KEY.

3. **Rubrics**: Domain-specific rubrics must be provided as YAML files with specific structure (see `rubrics/` for examples).

## Project Structure

```
kbb/
├── src/kbb/
│   ├── crew.py              # Main workflow orchestration
│   ├── main.py              # CLI entry point
│   ├── config.py            # Configuration management
│   ├── state.py             # Workflow state
│   ├── config/              # YAML configs
│   │   ├── agents.yaml
│   │   └── tasks.yaml
│   ├── tools/               # Custom tools
│   │   ├── search.py
│   │   ├── scrape.py
│   │   ├── cleaning.py
│   │   ├── chunking.py
│   │   └── rubric_loader.py
│   ├── storage/             # Storage interfaces
│   │   └── chroma_store.py
│   └── schemas/             # Pydantic models
│       └── models.py
├── rubrics/                 # Domain rubrics
│   ├── quantum_error_correction.yaml
│   └── sustainable_packaging.yaml
├── artifacts/               # Run outputs
│   └── run_*/
├── tests/                   # Unit tests
├── pyproject.toml           # Project config
└── uv.lock                  # Dependency lock
```
