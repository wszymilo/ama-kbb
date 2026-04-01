# Autonomous Multi-Agent Knowledge Base Builder for RAG Systems

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)

## Overview

Automated system that builds trustworthy knowledge bases for RAG systems using 4 specialized AI agents collaborating like a research team. No domain experts required!

**Agents:**
- **Researcher** - Creates & revises research plans
- **SME** - Validates plans & sources for credibility
- **Scraper** - Executes approved scraping with Serper
- **Data Scientist** - Cleans, chunks & stores in ChromaDB

## Problem Solved

Manual KB building is slow, inconsistent, and unscalable without domain experts. This system automates the entire pipeline with built-in quality gates.

## Tech Stack

| Category | Technology |
|----------|------------|
| Orchestration | OpenAI Agents SDK |
| Communication | MCP (Model Context Protocol) |
| Search | [Serper](https://serper.dev/) (Google Search API) |
| Vector DB | [ChromaDB](https://docs.trychroma.com/) |
| LLM | GPT-4o |

## Quick Start

### Prerequisites
```bash
pip install openai-agents chromadb serper python-dotenv
```

### 1. Setup
```bash
cp .env.example .env
# Add your API keys to .env
```

### 2. Run Demo
```bash
python main.py --topic "quantum error correction"
```

### 3. Query KB
```python
from rag_query import query_kb
results = query_kb("What are the main error correction codes?")
```

## Workflow
User Topic -> Researcher (Plan) -> SME (Review) -> Scraper (Data) -> SME (Validate) -> Data Scientist (KB) -> ChromaDB
                                         ^ Feedback loops ensure quality ^

**Key Features:**
- Typed message communication (auditable)
- SME rejects unreliable sources
- Automatic cleaning/deduplication
- Domain-agnostic (just change SME guidelines)

## Demo Domains Tested
- Quantum error correction
- Sustainable packaging materials

## Evaluation Criteria
- [ ] Fully autonomous KB generation
- [ ] SME rejects ≥1 unreliable source
- [ ] Queryable ChromaDB output
- [ ] RAG-ready chunks

## Development Roadmap

| Day | Milestone |
|-----|-----------|
| Day 1 | Environment + stubs |
| Day 2 | SME + Scraper |
| Day 3 | Data Scientist + E2E flow |
| Day 4 | Testing + Demo |


## Contributing
1. Fork the repo
2. Create feature branch (`git checkout -b feature/agent-enhancement`)
3. Commit changes (`git commit -m 'Add agent memory'`)
4. Push & PR

## License
This project is [MIT licensed](LICENSE).

## Acknowledgments
Built during [AI Bootcamp] - Special thanks to the agentic AI community!

---
*Built with love for autonomous RAG systems*
