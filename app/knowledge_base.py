"""
Knowledge base module for Harri AI Assistant.
Handles loading markdown documentation and providing vector search capabilities.
"""

import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from loguru import logger
from chromadb.config import Settings
# from sentence_transformers import SentenceTransformer

# Get the directory of the current Python file
current_file_dir = os.path.dirname(os.path.abspath(__file__))

# Specify the target directory name that is in the same directory as the current file
target_dir_name = "kb"

# Construct the path to the target directory
kb_path = os.path.join(current_file_dir, target_dir_name)


class KnowledgeBase:
    """Knowledge base service for managing and searching documentation."""

    def __init__(self):
        """Initialize the knowledge base with vector database and embeddings."""
        self.kb_dir = Path(kb_path)
        self.documents: List[Dict[str, Any]] = []
        self.chroma_client = None
        self.embedding_model = None
        self.collection = None
        self._initialize_vector_db()
        self._load_documents()
        self._index_documents()

    def _initialize_vector_db(self) -> None:
        """Initialize ChromaDB client and embedding model."""
        try:
            self.chroma_client = chromadb.PersistentClient(
                path="./chroma_db",
                settings=Settings()
            )
            # self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embedding_model = None  # Use ChromaDB's default embeddings
            self.collection = self.chroma_client.get_or_create_collection(
                name="harri_knowledge_base",
                metadata={"description": "Harri internal documentation and knowledge base"}
            )
            logger.info("Vector database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing vector database: {e}")
            raise

    def _load_documents(self) -> None:
        """Load all markdown documents from the kb directory."""
        try:
            if not self.kb_dir.exists():
                logger.warning(f"Knowledge base directory {self.kb_dir} does not exist")
                return
            for md_file in self.kb_dir.glob("*.md"):
                self._load_single_document(md_file)
            logger.info(f"Loaded {len(self.documents)} documents from knowledge base")
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            raise

    def _load_single_document(self, file_path: Path) -> None:
        """Load a single markdown document and split it into chunks."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else file_path.stem
            chunks = self._split_document(content, file_path.name)
            for i, chunk in enumerate(chunks):
                document = {
                    "id": f"{file_path.stem}_{i}",
                    "title": title,
                    "filename": file_path.name,
                    "content": chunk,
                    "source": str(file_path)
                }
                self.documents.append(document)
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {e}")

    def _split_document(self, content: str, filename: str) -> List[str]:
        """
        Split document content into meaningful chunks for vector storage.
        
        This method intelligently splits markdown documents into chunks that preserve
        semantic meaning while being suitable for embedding and retrieval.
        Each chunk includes its immediate parent header for better context.
        
        Args:
            content: The full document content as a string
            filename: The name of the file being processed (for context)
            
        Returns:
            List of text chunks, each containing meaningful content units with parent header context
        """
        # Strategy 1: Split by markdown headings (## and ###) and include parent headers
        # This preserves document structure and keeps related content together
        # We need to find the parent header for each subsection
        
        # Step 1: Parse all headings to understand document hierarchy
        # This creates a map of heading positions and their levels for parent-child relationship analysis
        heading_pattern = r'^(#{1,3})\s+(.+)$'  # Matches #, ##, and ### headings
        headings = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            match = re.match(heading_pattern, line)
            if match:
                level = len(match.group(1))  # Count # symbols to determine heading level
                title = match.group(2).strip()  # Extract the heading text
                headings.append((i, level, title))  # Store: (line_number, level, title)
        
        # Step 2: Split content by subsection headings (## and ###)
        # This creates the individual chunks we'll process
        sections = re.split(r'^#{2,3}\s+', content, flags=re.MULTILINE)
        
        chunks = []
        section_index = 0  # Track which section we're processing
        
        for section in sections:
            if section.strip():  # Skip empty sections
                # Clean up excessive whitespace: replace 3+ consecutive newlines with 2
                # This maintains readability while reducing noise in embeddings
                section = re.sub(r'\n\s*\n\s*\n', '\n\n', section.strip())
                
                # Step 3: Find the appropriate parent header for this section
                # We need to identify which # heading (level 1) is the parent of this subsection
                parent_header = ""
                if section_index < len(headings):
                    # Iterate through all headings to find the correct parent
                    for i, (line_num, level, title) in enumerate(headings):
                        if level == 1:  # This is a # heading (potential parent)
                            # Check if this parent comes before our current section
                            # We need to ensure this parent is the most recent one before our section
                            if i < len(headings) - 1:
                                next_heading_line = headings[i + 1][0]
                                # If our section starts after this parent, use it as the parent
                                if section_index == 0 or line_num < next_heading_line:
                                    parent_header = title
                                    break
                
                # Step 4: Add parent header context to each chunk for better retrieval
                # This helps the AI understand the broader context when retrieving chunks
                if parent_header:
                    # Format: "Parent Header\n\nSubsection Content"
                    chunk_with_context = f"{parent_header}\n\n{section}"
                else:
                    # Fallback: use section as-is if no parent found
                    chunk_with_context = section
                
                chunks.append(chunk_with_context)
                section_index += 1

        # Strategy 2: Fallback to paragraph-based splitting
        # If no markdown headings found, split by paragraph breaks
        if not chunks:
            # Split on double newlines (paragraph boundaries)
            paragraphs = re.split(r'\n\s*\n', content)
            # Filter out empty paragraphs and strip whitespace
            chunks = [p.strip() for p in paragraphs if p.strip()]

        return chunks

    def _index_documents(self) -> None:
        """Index documents in the vector database."""
        try:
            if not self.documents:
                logger.warning("No documents to index")
                return

            # Prepare documents for indexing
            ids = [doc["id"] for doc in self.documents]
            texts = [doc["content"] for doc in self.documents]
            metadatas = [{"filename": doc["filename"], "title": doc["title"]} for doc in self.documents]

            # Add documents to collection
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Indexed {len(self.documents)} documents in vector database")
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
            raise

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents using vector similarity.

        Args:
            query: Search query
            top_k: Number of top results to return

        Returns:
            List of relevant documents with metadata
        """
        try:
            if not self.collection:
                logger.warning("Vector database not initialized")
                return []

            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )

            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                        "distance": results['distances'][0][i] if results['distances'] and results['distances'][0] else 0.0
                    })

            return formatted_results
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []


# Global knowledge base instance
knowledge_base = KnowledgeBase()
