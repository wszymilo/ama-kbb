# Implementation Notes - Issues #18 and #19

## Completed Work

### Issue #19: Save run artifacts and final summary for demo/debugging
✅ **COMPLETED**

#### Implementation:
- Created `src/kbb/storage/artifact_store.py` - Complete artifact management system
- Created `src/kbb/schemas/models.py` - Typed schemas for all pipeline artifacts

#### Features:
1. **Artifact Storage Structure**
   - Organized by run_id with subdirectories: research/, sources/, documents/, chunks/
   - JSON metadata + separate content files for readability
   - Human-readable summaries alongside machine-readable JSON

2. **What Gets Saved**
   - Research plans (versioned)
   - Source candidates (all discovered sources)
   - Source reviews (SME evaluations with scores and rationale)
   - Scraped documents (content + metadata)
   - Cleaned chunks (with/without embeddings)
   - Run summaries (complete pipeline statistics)

3. **Schemas Created**
   - `ResearchPlan` - Research plan structure
   - `SourceCandidate` - Discovered sources
   - `SourceReview` - SME evaluations
   - `ScrapedDocument` - Scraped content
   - `CleanChunk` - Processed chunks with embeddings
   - `PipelineRunSummary` - Complete run statistics and timing

#### Usage Example:
```python
from kbb.storage import ArtifactStore
from kbb.schemas.models import PipelineRunSummary

store = ArtifactStore(base_dir="./artifacts")
run_dir = store.create_run_directory("run_20260402_120000")

# Save artifacts throughout pipeline
store.save_research_plan(run_id, plan)
store.save_source_reviews(run_id, reviews)
store.save_scraped_documents(run_id, documents)
store.save_chunks(run_id, chunks)

# Save final summary
summary = PipelineRunSummary(
    run_id=run_id,
    topic="quantum error correction",
    sources_discovered=10,
    sources_approved=7,
    chunks_stored=150
)
summary.mark_completed()
store.save_run_summary(summary)
```

### Issue #18: Add query CLI for retrieving chunks from generated ChromaDB collection
✅ **COMPLETED**

#### Implementation:
- Created `rag_query.py` - Complete query CLI tool
- Created `src/kbb/storage/chroma_store.py` - ChromaDB interface
- Added `QueryResult` schema for structured query responses

#### Features:
1. **Query CLI (`rag_query.py`)**
   - Query by natural language question
   - Configurable top-k results
   - List all collections
   - Verbose mode (full content) or preview mode
   - Uses nomic-embed-text-v1.5 for query embeddings

2. **ChromaDB Interface**
   - Store chunks with embeddings
   - Query with metadata filtering
   - Collection statistics
   - Persistent storage

#### Usage:
```bash
# Query a collection
python rag_query.py --collection kb_poc --question "What is quantum error correction?"

# Get more results
python rag_query.py -c kb_poc -q "surface codes" --top-k 10

# Verbose output with full content
python rag_query.py -c kb_poc -q "topological codes" -v

# List all collections
python rag_query.py --list-collections

# Use custom ChromaDB directory
python rag_query.py -c kb_poc -q "error rates" --persist-dir ./my_chroma_db
```

## Testing

### Test Script: `test_artifacts_query.py`
Comprehensive test demonstrating both issues:
```bash
python test_artifacts_query.py
```

This script:
1. Creates a test run with all artifact types
2. Saves artifacts to `./artifacts/`
3. Stores chunks in ChromaDB (`./test_chroma_db`)
4. Queries ChromaDB
5. Validates all functionality

## Dependencies Added
- `sentence-transformers>=2.2.0` (for nomic-embed-text-v1.5)

## File Structure Created
```
src/kbb/
├── schemas/
│   ├── __init__.py
│   └── models.py (7 Pydantic models)
└── storage/
    ├── __init__.py
    ├── artifact_store.py (complete artifact management)
    └── chroma_store.py (ChromaDB interface)

rag_query.py (CLI tool)
test_artifacts_query.py (comprehensive test)
artifacts/ (created at runtime)
```

## Integration Points

### For Other Team Members

**Researcher Agent (Issue #6 - seun-ja):**
```python
from kbb.storage import ArtifactStore
from kbb.schemas.models import ResearchPlan

# Create and save research plan
plan = ResearchPlan(topic=user_topic, subtopics=[...], ...)
artifact_store.save_research_plan(run_id, plan)
```

**SME Agent (Issue #7 - mrpeski):**
```python
from kbb.schemas.models import SourceReview

# Review sources
review = SourceReview(
    source=candidate,
    approved=True,
    authority_score=4.5,
    rationale="..."
)
artifact_store.save_source_reviews(run_id, reviews)
```

**Scraper Agent (Issue #10 - MmaitsiMwale):**
```python
from kbb.schemas.models import ScrapedDocument

# Save scraped content
doc = ScrapedDocument(
    source_url=url,
    title=title,
    content=content,
    status="success"
)
artifact_store.save_scraped_documents(run_id, [doc])
```

**Data Scientist Agent (Issue #15 - MmaitsiMwale):**
```python
from kbb.storage import ChromaKBStore
from kbb.schemas.models import CleanChunk

# Store chunks with embeddings
store = ChromaKBStore(collection_name=collection)
chunks = [CleanChunk(chunk_id=..., content=..., embedding=[...])]
store.add_chunks(chunks)

# Save to artifacts
artifact_store.save_chunks(run_id, chunks)
```

**Main Pipeline (Issue #16 - wszymilo):**
```python
from kbb.storage import ArtifactStore
from kbb.schemas.models import PipelineRunSummary
import uuid

# Initialize at start
run_id = f"run_{uuid.uuid4().hex[:12]}"
artifact_store = ArtifactStore()
run_dir = artifact_store.create_run_directory(run_id)

summary = PipelineRunSummary(
    run_id=run_id,
    topic=topic,
    collection_name=collection
)

# Update throughout pipeline
summary.sources_discovered = len(candidates)
summary.sources_approved = len(approved)
# ...

# Save at end
summary.mark_completed()
artifact_store.save_run_summary(summary)
```

## Known Limitations

1. **Embedding Model**: Query CLI requires sentence-transformers package
   - Install: `pip install sentence-transformers`
   - Model loads on first query (may take a moment)

2. **Large Embeddings**: Full chunk files include embedding vectors (can be large)
   - Metadata files exclude embeddings for readability
   - Full files in `chunks_full.json` for potential reuse

3. **ChromaDB Setup**: Requires ChromaDB collection to exist before querying
   - Use `--list-collections` to see available collections

## Next Steps

1. **Integration**: Other agents should import and use these schemas/stores
2. **Testing**: Add unit tests for storage classes (Issue #20)
3. **Documentation**: Update README with query CLI usage (Issue #21)
4. **Demo**: Use artifacts for demo preparation (Issue #22)

## Branch
`feat/issue-18-19-artifacts-query-cli`

Ready for review and merge!
