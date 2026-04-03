#!/usr/bin/env python
"""
Gradio UI for querying the ChromaDB knowledge base.
Based on the CLI from Issue #18.

**DEPENDENCY:** Requires storage module from Issues #18/19 (PR #32).
Ensure PR #32 is merged to development before using this UI.

Usage:
    python gradio_ui.py
    python gradio_ui.py --persist-dir ./my_chroma_db --port 7860
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List, Tuple, Optional

import gradio as gr

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from kbb.storage.chroma_store import ChromaKBStore

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GradioKBInterface:
    """Gradio interface for querying the knowledge base."""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize Gradio interface.
        
        Args:
            persist_directory: ChromaDB persist directory
        """
        self.persist_directory = persist_directory
        logger.info(f"Initialized Gradio interface with persist_dir: {persist_directory}")
    
    def list_collections(self) -> str:
        """
        List all available collections.
        
        Returns:
            Formatted string of collections
        """
        try:
            import chromadb
            from chromadb.config import Settings
            
            client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            collections = client.list_collections()
            
            if not collections:
                return "No collections found."
            
            result = "📚 Available Collections:\n\n"
            for coll in collections:
                count = coll.count()
                result += f"  • {coll.name} ({count} chunks)\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return f"❌ Error: {str(e)}"
    
    def query_knowledge_base(
        self,
        collection_name: str,
        question: str,
        top_k: int = 5,
        show_full_content: bool = False
    ) -> Tuple[str, str]:
        """
        Query the knowledge base.
        
        Args:
            collection_name: ChromaDB collection name
            question: Question to ask
            top_k: Number of results to return
            show_full_content: Whether to show full content or preview
            
        Returns:
            Tuple of (status_message, results_markdown)
        """
        if not collection_name or not question:
            return "⚠️ Please provide both collection name and question.", ""
        
        try:
            # Initialize ChromaDB store
            store = ChromaKBStore(
                persist_directory=self.persist_directory,
                collection_name=collection_name
            )
            
            # Get collection stats
            stats = store.get_collection_stats()
            total_chunks = stats.get('total_chunks', 0)
            
            if total_chunks == 0:
                return f"⚠️ Collection '{collection_name}' is empty or doesn't exist.", ""
            
            # Query the store
            results = store.query(query_text=question, n_results=top_k)
            
            if not results:
                return f"✓ Query completed but no results found in '{collection_name}'.", ""
            
            # Format results as markdown
            results_md = f"# Query Results\n\n"
            results_md += f"**Collection:** {collection_name} ({total_chunks} total chunks)\n\n"
            results_md += f"**Question:** {question}\n\n"
            results_md += f"**Results:** {len(results)}/{top_k}\n\n"
            results_md += "---\n\n"
            
            for result in results:
                rank = result['rank']
                chunk_id = result['id']
                content = result['document']
                distance = result['distance']
                metadata = result['metadata']
                
                results_md += f"## Result {rank}\n\n"
                results_md += f"**Chunk ID:** `{chunk_id}`\n\n"
                results_md += f"**Similarity Score:** {1 - distance:.4f} (distance: {distance:.4f})\n\n"
                results_md += f"**Source:** {metadata.get('source_url', 'N/A')}\n\n"
                
                if show_full_content:
                    results_md += f"**Content:**\n\n```\n{content}\n```\n\n"
                else:
                    # Preview first 300 chars
                    preview = content[:300] + "..." if len(content) > 300 else content
                    results_md += f"**Preview:**\n\n{preview}\n\n"
                
                results_md += "---\n\n"
            
            status = f"✓ Found {len(results)} relevant chunks in '{collection_name}'"
            return status, results_md
            
        except Exception as e:
            logger.error(f"Query failed: {e}", exc_info=True)
            return f"❌ Error: {str(e)}", ""


def create_interface(persist_directory: str = "./chroma_db") -> gr.Blocks:
    """
    Create the Gradio interface.
    
    Args:
        persist_directory: ChromaDB persist directory
        
    Returns:
        Gradio Blocks interface
    """
    kb_interface = GradioKBInterface(persist_directory=persist_directory)
    
    with gr.Blocks(title="Knowledge Base Query Interface", theme=gr.themes.Soft()) as interface:
        gr.Markdown(
            """
            # 🔍 Knowledge Base Query Interface
            
            Query your ChromaDB knowledge base using natural language.
            Built on the CLI from [Issue #18](https://github.com/wszymilo/ama-kbb/issues/18).
            """
        )
        
        with gr.Tab("Query"):
            with gr.Row():
                with gr.Column(scale=2):
                    collection_input = gr.Textbox(
                        label="Collection Name",
                        placeholder="kb_poc",
                        value="kb_poc",
                        info="Name of the ChromaDB collection to query"
                    )
                    
                    question_input = gr.Textbox(
                        label="Question",
                        placeholder="What is quantum error correction?",
                        lines=3,
                        info="Ask a question in natural language"
                    )
                    
                    with gr.Row():
                        top_k_slider = gr.Slider(
                            minimum=1,
                            maximum=20,
                            value=5,
                            step=1,
                            label="Number of Results",
                            info="How many relevant chunks to retrieve"
                        )
                        
                        show_full_toggle = gr.Checkbox(
                            label="Show Full Content",
                            value=False,
                            info="Show complete chunk content (not just preview)"
                        )
                    
                    query_button = gr.Button("🔍 Search", variant="primary", size="lg")
                
                with gr.Column(scale=1):
                    gr.Markdown("### Quick Actions")
                    list_collections_button = gr.Button("📚 List Collections", size="sm")
                    collections_output = gr.Textbox(
                        label="Available Collections",
                        lines=8,
                        interactive=False
                    )
            
            with gr.Row():
                status_output = gr.Textbox(label="Status", interactive=False)
            
            with gr.Row():
                results_output = gr.Markdown(label="Results")
            
            # Event handlers
            query_button.click(
                fn=kb_interface.query_knowledge_base,
                inputs=[collection_input, question_input, top_k_slider, show_full_toggle],
                outputs=[status_output, results_output]
            )
            
            list_collections_button.click(
                fn=kb_interface.list_collections,
                inputs=[],
                outputs=[collections_output]
            )
        
        with gr.Tab("About"):
            gr.Markdown(
                """
                ## About This Interface
                
                This Gradio UI provides a web interface for querying the AMA-KBB knowledge base.
                
                ### Features
                - 🔍 Natural language querying using nomic-embed-text-v1.5 embeddings
                - 📊 Adjustable number of results (top-k)
                - 📄 Preview or full content view
                - 📚 Collection listing and statistics
                
                ### How It Works
                1. Select a ChromaDB collection
                2. Enter your question in natural language
                3. Adjust the number of results if needed
                4. Click "Search" to get relevant chunks
                
                ### Technical Details
                - **Embedding Model:** nomic-ai/nomic-embed-text-v1.5
                - **Vector Store:** ChromaDB with cosine similarity
                - **Query Prefix:** `search_query:` (for nomic embedder)
                - **Index Prefix:** `search_document:` (for nomic embedder)
                
                ### Related Issues
                - [Issue #18](https://github.com/wszymilo/ama-kbb/issues/18): Query CLI implementation
                - [Issue #19](https://github.com/wszymilo/ama-kbb/issues/19): Artifact storage
                - [Issue #24](https://github.com/wszymilo/ama-kbb/issues/24): This Gradio UI
                """
            )
        
        with gr.Tab("Examples"):
            gr.Markdown(
                """
                ## Example Queries
                
                Try these sample questions (adjust collection name as needed):
                
                ### Quantum Computing
                - "What is quantum error correction?"
                - "Explain surface codes"
                - "How do topological codes work?"
                - "What are the main challenges in fault-tolerant quantum computing?"
                
                ### General
                - "Summarize the main concepts"
                - "What are the key takeaways?"
                - "Explain the technical approach"
                
                ### Tips
                - Be specific in your questions
                - Use natural language (no need for keywords)
                - Increase top-k for broader coverage
                - Enable "Show Full Content" for detailed reading
                """
            )
    
    return interface


def main():
    """Main entry point for the Gradio UI."""
    parser = argparse.ArgumentParser(
        description="Launch Gradio UI for knowledge base queries",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--persist-dir',
        type=str,
        default='./chroma_db',
        help='ChromaDB persist directory (default: ./chroma_db)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=7860,
        help='Port to run Gradio server (default: 7860)'
    )
    
    parser.add_argument(
        '--share',
        action='store_true',
        help='Create a public shareable link'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and launch interface
    interface = create_interface(persist_directory=args.persist_dir)
    
    logger.info(f"Launching Gradio UI on port {args.port}...")
    logger.info(f"ChromaDB directory: {args.persist_dir}")
    
    interface.launch(
        server_port=args.port,
        share=args.share,
        show_error=True
    )


if __name__ == "__main__":
    main()
