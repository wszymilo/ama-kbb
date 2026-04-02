# Current State Analysis - AMA-KBB Project

Generated: 2026-04-02

## What's Already Built

### 1. Project Structure
```
ama-kbb/
├── README.md (comprehensive documentation)
├── AGENTS.md (CrewAI reference guide)
├── main.py (PLACEHOLDER - empty)
├── rag_query.py (PLACEHOLDER - empty)
├── requirements.txt (complete dependency list)
├── pyproject.toml (project config)
├── env.example (environment template)
├── knowledge/user_preference.txt (sample user data)
└── src/kbb/
    ├── main.py (basic crew runner with CLI stubs)
    ├── crew.py (basic CrewAI setup with 2 agents)
    ├── config/
    │   ├── agents.yaml (2 agents: researcher, reporting_analyst)
    │   └── tasks.yaml (2 tasks: research_task, reporting_task)
    └── tools/
        └── custom_tool.py (example tool template)
```

### 2. Dependencies Installed
✅ Core frameworks:
- crewai==1.12.2
- litellm==1.82.6
- fastmcp==3.2.0
- chromadb==1.1.1
- openai==2.30.0
- pydantic==2.11.10
- huggingface-hub==1.8.0

### 3. Existing Code

#### crew.py (Basic Setup)
- Uses @CrewBase decorator pattern
- Has 2 agents defined:
  - `researcher`: Basic research agent
  - `reporting_analyst`: Report generation agent
- Has 2 tasks:
  - `research_task`: Conduct research on topic
  - `reporting_task`: Create detailed reports
- Process: Sequential
- Output: report.md file

#### src/kbb/main.py (Runner Functions)
- `run()`: Basic crew execution with hardcoded inputs (topic: "AI LLMs")
- `train()`: Training functionality
- `replay()`: Replay functionality
- `test()`: Testing functionality
- `run_with_trigger()`: Webhook/trigger support

#### agents.yaml & tasks.yaml
- Basic configurations for researcher and reporting_analyst
- Generic roles, not aligned with project requirements yet

### 4. What's NOT Built Yet

#### Missing Core Components (from README requirements):

**Agents (4 required):**
- ❌ Researcher (needs updating to match spec)
- ❌ SME (Subject Matter Expert) - NOT IMPLEMENTED
- ❌ Scraper - NOT IMPLEMENTED
- ❌ Data Scientist - NOT IMPLEMENTED

**Tools:**
- ❌ MCP-based search tool
- ❌ MCP-based fetch/scraping tool
- ❌ Embedding generation (nomic-ai/nomic-embed-text-v1.5)
- ❌ ChromaDB storage interface

**Pipeline Components:**
- ❌ Document cleaning/normalization
- ❌ Chunking for RAG
- ❌ Embedding generation
- ❌ ChromaDB integration
- ❌ Source validation logic

**Schemas:**
- ❌ ResearchPlan
- ❌ SourceCandidate
- ❌ SourceReview
- ❌ ScrapedDocument
- ❌ CleanChunk
- ❌ PipelineRunSummary

**Rubrics:**
- ❌ Domain-specific rubric format
- ❌ Sample rubrics (quantum_error_correction, sustainable_packaging)

**CLI:**
- ❌ main.py (top-level CLI entrypoint)
- ❌ rag_query.py (query interface)
- ❌ Argument parsing for topic, rubric, collection, etc.

**Artifacts & Outputs:**
- ❌ Artifact storage directory
- ❌ Run summary generation
- ❌ Intermediate outputs logging

**Tests:**
- ❌ No tests directory or test files

**Documentation:**
- ❌ Setup docs need updating per Issue #21

## Issues Assigned to MmaitsiMwale

### HIGH PRIORITY (Core Functionality)
1. **Issue #10**: Implement Scraper agent for approved source retrieval
2. **Issue #15**: Implement Data Scientist agent for corpus inclusion summary
3. **Issue #18**: Add query CLI for retrieving chunks from generated ChromaDB collection

### MEDIUM PRIORITY (Infrastructure)
4. **Issue #19**: Save run artifacts and final summary for demo/debugging
5. **Issue #22**: Prepare final demo script, sample topics, and fallback artifacts

### DOCUMENTATION & TESTING
6. **Issue #20**: Add minimal test coverage for deterministic modules
7. **Issue #21**: Update README and setup docs to match actual implementation

### ENHANCEMENTS
8. **Issue #23**: Discussion: Return both Markdown and VectorDB
9. **Issue #24**: Gradio UI

## Recommended Starting Point

### Phase 1: Core Infrastructure (Start Here)
1. **Issue #18** - Query CLI
   - Relatively independent
   - Tests ChromaDB integration
   - Provides foundation for testing

2. **Issue #19** - Artifact Saving
   - Needed for debugging all agents
   - Simple to implement
   - High value for development

### Phase 2: Agent Implementation
3. **Issue #10** - Scraper Agent
   - Fetch content from approved sources
   - Depends on MCP tools (Issue #8, #9 - assigned to others)

4. **Issue #15** - Data Scientist Agent
   - Cleaning, chunking, embedding, storage
   - Core RAG pipeline component

### Phase 3: Polish & Demo
5. **Issue #22** - Demo Preparation
6. **Issue #20** - Tests
7. **Issue #21** - Documentation Updates

### Phase 4: Enhancements (If Time Permits)
8. **Issue #23** - Dual Output Discussion
9. **Issue #24** - Gradio UI

## Dependencies Between Issues

```
Issue #10 (Scraper) depends on:
  - Issue #8 (MCP servers - MostafaKashwaa)
  - Issue #9 (Tool wrappers - MostafaKashwaa)

Issue #15 (Data Scientist) depends on:
  - Issue #12 (Chunking - wszymilo)
  - Issue #13 (Embeddings - wszymilo)
  - Issue #14 (ChromaDB - wszymilo)

Issue #18 (Query CLI) depends on:
  - Issue #14 (ChromaDB - wszymilo)

Issue #22 (Demo) depends on:
  - Most other issues being complete
```

## Next Steps

1. ✅ Repository cloned and explored
2. ⏭️ Set up development environment (.env file)
3. ⏭️ Start with Issue #18 or #19 (independent, foundational)
4. ⏭️ Coordinate with team on dependencies
5. ⏭️ Implement core agents (#10, #15)
6. ⏭️ Polish and demo preparation
