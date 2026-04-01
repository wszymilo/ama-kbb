md

# Autonomous Multi-Agent Knowledge Base Builder for RAG Systems

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)

## Overview

Autonomous multi-agent system that builds a trustworthy knowledge base for RAG systems from a user-provided topic.

The system uses 4 specialized AI agents that collaborate like a research team:

- **Researcher** — creates and revises the research plan
- **SME [Subject Matter Expect]** — validates plans and sources using domain-specific rubrics
- **Scraper** — collects approved source content using external tools
- **Data Scientist** — cleans, chunks, embeds, and stores the final corpus in ChromaDB

This project is being built as a **3-day proof of concept (POC)** by a team of 5 developers. The goal is to deliver a working end-to-end pipeline, not a production-ready platform.

## Problem Solved

Manual knowledge base creation for RAG is:

- slow
- inconsistent
- difficult to scale
- hard to audit
- often dependent on domain experts

This project automates the pipeline while preserving quality gates, source review, and traceable processing steps.

## POC Goals

The POC is successful if it can:

- accept a topic from the user
- generate a structured research plan
- discover candidate sources
- reject at least some low-quality or irrelevant sources
- fetch content from approved sources
- clean and chunk documents
- generate embeddings
- store chunks in ChromaDB
- support basic retrieval against the generated KB

## Scope for This POC

### In scope

- CLI workflow
- CrewAI-based multi-agent orchestration
- LiteLLM for model access
- MCP-based external tools for search/fetch where practical
- domain-specific SME review rubrics
- ChromaDB vector storage
- embeddings with `nomic-ai/nomic-embed-text-v1.5`
- auditable intermediate outputs
- one working end-to-end happy path

### Out of scope

- production deployment
- web UI by default
- advanced retry/recovery
- large-scale crawling
- full benchmark suite
- enterprise security/auth
- sophisticated long-term memory
- multi-tenant usage

## Architecture

### Core stack

| Category | Technology |
|----------|------------|
| Language | Python 3.10+ |
| Agent orchestration | CrewAI |
| Model access | LiteLLM |
| Tooling integration | MCP-compatible public servers where suitable |
| Web search / fetch | MCP tools and/or direct fallback integrations |
| Vector DB | ChromaDB |
| Embedding model | `nomic-ai/nomic-embed-text-v1.5`|
| Embedding runtime | Hugging Face tooling |
| Interface | CLI |


## Agent Roles

### 1. Researcher

Responsible for:

- understanding the user topic
- breaking it into subtopics
- proposing search queries
- drafting a research plan
- updating the plan based on SME feedback

### 2. SME

Responsible for:

- validating the research plan
- applying domain-specific evaluation rubrics
- reviewing candidate sources
- rejecting low-quality, untrustworthy, or off-scope sources
- documenting acceptance/rejection rationale

### 3. Scraper

Responsible for:

- using approved tools to retrieve source content
- collecting source metadata
- returning raw scraped documents for processing

### 4. Data Scientist

Responsible for:

- cleaning and normalizing fetched content
- chunking documents for retrieval
- generating embeddings
- storing chunks and metadata in ChromaDB
- producing a summary of the resulting KB

## Workflow


User Topic
  -> Researcher creates research plan
  -> SME reviews plan using domain rubric
  -> Search tool finds candidate sources
  -> SME reviews and filters sources
  -> Scraper fetches approved pages
  -> Data Scientist cleans and chunks content
  -> Data Scientist embeds chunks with nomic-embed-text-v1.5
  -> ChromaDB stores final KB
  -> User queries the resulting knowledge base

Quality gates

    SME can reject the plan
    SME can reject sources
    low-content or malformed pages can be filtered out
    final KB only includes approved and processable content

MCP Strategy

This project intends to use public MCP servers for external capabilities where possible, especially for:

    web search
    webpage fetching / content extraction
    possibly filesystem or utility tools

Important POC note

For this 3-day POC, the most practical architecture is:

    use MCP servers for external tools
    use local/application-managed embeddings via Hugging Face for nomic-ai/nomic-embed-text-v1.5

This is intentional because embedding through a public MCP server is less standard and would add unnecessary integration risk for a short delivery timeline.
MCP server selection criteria

We will select public MCP servers that are:

    publicly available
    simple to integrate from Python
    reliable enough for a demo
    easy to replace if unstable

Fallback policy

If a chosen MCP server is unreliable during implementation, we may use a direct Python integration for that specific capability while preserving the same tool abstraction in code.
Embeddings

This project uses:

    Model: nomic-ai/nomic-embed-text-v1.5
    Access path: Hugging Face tooling
    Usage: generate embeddings for cleaned text chunks before storing them in ChromaDB

Why this model

    strong quality for retrieval use cases
    good open model choice for RAG pipelines
    practical for a POC without locking into a proprietary embedding API

Embedding design

Each chunk will be embedded with metadata such as:

    topic
    source URL
    document title
    document ID
    chunk index
    collection name / namespace

Domain-Specific SME Rubrics

A key feature of this project is that the SME is domain-specific.

Instead of using a generic reviewer only, the SME should receive a rubric describing:

    trusted source types for the domain
    preferred institutions or publishers
    unacceptable source patterns
    recency expectations
    terminology and scope boundaries
    evidence requirements

Example rubric dimensions

    Authority — Is the source from a recognized authority in the field?
    Relevance — Does the source directly address the target topic/subtopic?
    Reliability — Is the source factual, non-promotional, and sufficiently detailed?
    Recency — Is the source recent enough for the domain?
    Completeness — Does the source provide enough substance for KB inclusion?

Example domains

    quantum error correction
    sustainable packaging materials
    any domain where the rubric can be defined clearly

Planned Repository Structure

```text
.
├── README.md
├── LICENSE
├── .env.example
├── requirements.txt
├── main.py
├── rag_query.py
├── src/
│   ├── agents/
│   │   ├── researcher.py
│   │   ├── sme.py
│   │   ├── scraper.py
│   │   └── data_scientist.py
│   ├── tasks/
│   ├── tools/
│   │   ├── mcp_search.py
│   │   ├── mcp_fetch.py
│   │   └── embeddings.py
│   ├── pipeline/
│   │   ├── orchestration.py
│   │   ├── cleaning.py
│   │   └── chunking.py
│   ├── storage/
│   │   └── chroma_store.py
│   ├── config/
│   │   └── settings.py
│   ├── schemas/
│   │   └── models.py
│   └── utils/
├── rubrics/
│   ├── quantum_error_correction.yaml
│   └── sustainable_packaging.yaml
├── artifacts/
└── tests/
```

Typed Handoffs

To keep the workflow auditable and robust, agent communication should use structured schemas.

Examples:

    ResearchPlan
    SourceCandidate
    SourceReview
    ScrapedDocument
    CleanChunk
    PipelineRunSummary

This makes the pipeline easier to debug and demo.
Quick Start

    The exact dependency list may evolve during implementation, but this is the intended setup.

1. Clone the repo

```bash

git clone <your-repo-url>
cd <your-repo-name>
```
2. Create environment

```bash

python -m venv .venv
source .venv/bin/activate
```
3. Install dependencies

```bash

pip install -r requirements.txt
```
Expected dependency categories include:

    crewai
    litellm
    chromadb
    python-dotenv
    pydantic
    sentence-transformers and/or transformers
    any MCP client/runtime package selected during implementation

4. Configure environment

```bash

cp .env.example .env
```
Add the required keys and settings to .env.

Possible variables:

```bash

LITELLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=...
CHROMA_PERSIST_DIR=./chroma_db
DEFAULT_COLLECTION=kb_poc
HF_MODEL_NAME=nomic-ai/nomic-embed-text-v1.5
MCP_SEARCH_SERVER=...
MCP_FETCH_SERVER=...
```
5. Run the pipeline

```bash

python main.py --topic "quantum error correction" --rubric rubrics/quantum_error_correction.yaml
```
6. Query the built KB

```bash

python rag_query.py --collection kb_poc --question "What are the main error correction codes?"
```
CLI Usage
Build a knowledge base

```bash

python main.py \
  --topic "sustainable packaging materials" \
  --rubric rubrics/sustainable_packaging.yaml \
  --collection sustainable_packaging_kb \
  --max-sources 10
```
Query a knowledge base

```bash

python rag_query.py \
  --collection sustainable_packaging_kb \
  --question "What are common biodegradable packaging materials?"
```
Planned CLI arguments
main.py

    --topic
    --rubric
    --collection
    --max-sources
    --verbose

rag_query.py

    --collection
    --question
    --top-k

Example End-to-End Run

Input:

```bash

python main.py --topic "quantum error correction" --rubric rubrics/quantum_error_correction.yaml
```
Expected high-level result:

    Research plan generated
    SME approves/revises plan
    candidate sources found
    SME rejects weak sources
    approved pages fetched
    documents chunked and embedded
    ChromaDB collection created
    retrieval query succeeds against resulting collection

Evaluation Criteria

The POC will be considered successful if the following are demonstrated:

    Fully automated happy-path KB generation
    SME applies a domain-specific rubric
    SME rejects at least one unreliable or low-value source
    Source content is fetched and processed successfully
    Chunks are embedded with nomic-ai/nomic-embed-text-v1.5
    Chunks are stored in ChromaDB
    Resulting knowledge base is queryable
    Retrieval returns source-linked chunks

Development Plan

This project has a hard 3-day delivery window and will be executed as a POC.
Day 1 — Foundation

    repository setup
    config and schemas
    LiteLLM integration
    Researcher + SME agent stubs
    decide MCP servers for search/fetch
    initial tool wrappers

Day 2 — Pipeline

    Scraper integration
    document fetch path working
    cleaning and chunking
    embeddings with Nomic model
    ChromaDB persistence
    first end-to-end happy path

Day 3 — Demo readiness

    stabilize orchestration
    improve SME rubric handling
    add query script
    add minimal tests
    improve README
    prepare demo topics and fallback artifacts

Team Model

5 developers with mixed experience.

Suggested implementation strategy:

    stronger developers own orchestration/integration
    junior developers own bounded modules like schemas, config, chunking, CLI, docs, and tests
    keep all interfaces simple and explicit

Known Risks

    public MCP server reliability may vary
    some source pages may be difficult to extract cleanly
    embedding/runtime setup may require local model tuning
    CrewAI + tool integration may require simplification for the POC
    domain rubrics may need manual tuning to avoid over-rejection or weak filtering

Risk mitigation

    abstract search/fetch behind simple wrappers
    allow direct fallback integrations if MCP is unstable
    keep one shallow feedback loop only
    prioritize one deterministic happy path over broad feature coverage

Future Extensions

If time permits or after the POC, we may add:

    lightweight web UI
    richer source credibility heuristics
    support for multiple rubrics per domain
    citation-aware answer generation
    asynchronous scraping
    better deduplication
    evaluation harness
    artifact viewer / run dashboard
    support for multiple embedding backends
    support for multiple MCP providers behind a common interface

Contributing

    Fork the repo
    Create a branch

```bash

git checkout -b feature/my-change
```
    Commit changes

```bash

git commit -m "Add feature"
```
    Push and open PR

License

This project is MIT licensed.
Acknowledgments

Built as a rapid POC for autonomous knowledge base creation for RAG systems. Built for fast iteration, clear quality gates, and a working retrieval demo.
