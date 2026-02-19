"""
RAG (Retrieval Augmented Generation) System
HSG245 Knowledge Base Integration with PostgreSQL + pgvector
Uses OpenAI Embeddings (lightweight, no heavy model files)
"""

import os
from typing import List, Dict, Optional
import psycopg2
from psycopg2.extras import execute_values
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI
from pathlib import Path

class HSG245RAGSystem:
    """
    RAG system for HSG245 incident investigation
    Stores and retrieves relevant safety knowledge using PostgreSQL + pgvector/mongodb can be used as well or any vector databases
    Uses OpenAI Embeddings API (lightweight, no model downloads)
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize RAG system with PostgreSQL + pgvector"""
        
        # Get DATABASE_URL from environment or parameter
        self.database_url = database_url or os.getenv("DATABASE_URL")
        
        if not self.database_url:
            raise ValueError("DATABASE_URL not found in environment variables")
        
        # Initialize OpenAI client for embeddings
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embedding_model = "text-embedding-3-small"  # OpenAI's efficient embedding model
        self.embedding_dim = 1536  # text-embedding-3-small dimension
        
        # Initialize database connection
        self.conn = psycopg2.connect(self.database_url)
        self.conn.autocommit = True
        
        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # 500 characters per chunk
            chunk_overlap=50,  # 50 characters overlap
            separators=["\n\n", "\n", ". ", " "]
        )
        
        # Initialize database schema
        self._setup_database()
        
        doc_count = self._get_document_count()
        print(f" RAG System initialized with {doc_count} documents")
    
    def _setup_database(self):
        """Setup PostgreSQL database with pgvector extension"""
        with self.conn.cursor() as cur:
            # Enable pgvector extension
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Create knowledge table
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS hsg245_knowledge (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    embedding vector({self.embedding_dim}),
                    source TEXT,
                    chunk_index INTEGER,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create index for vector similarity search
            cur.execute("""
                CREATE INDEX IF NOT EXISTS hsg245_knowledge_embedding_idx 
                ON hsg245_knowledge 
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100);
            """)
            
        print("Database schema initialized")
    
    def _get_document_count(self) -> int:
        """Get total number of documents"""
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM hsg245_knowledge;")
            return cur.fetchone()[0]
    
    def add_text(self, text: str, source: str = "manual_upload", metadata: Optional[Dict] = None):
        """
        Add text to knowledge base
        
        Args:
            text: Text content to add
            source: Source identifier (e.g., "hsg245_regulations", "riddor_2013")
            metadata: Additional metadata (optional)
        """
        # Split text into chunks
        chunks = self.text_splitter.split_text(text)
        
        print(f" Processing {len(chunks)} chunks from {source}...")
        
        # Generate embeddings using OpenAI API
        embeddings = []
        for chunk in chunks:
            response = self.openai_client.embeddings.create(
                input=chunk,
                model=self.embedding_model
            )
            embeddings.append(response.data[0].embedding)
        
        # Insert into database
        with self.conn.cursor() as cur:
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_metadata = {
                    "source": source,
                    "chunk_index": i,
                    "chunk_size": len(chunk)
                }
                if metadata:
                    chunk_metadata.update(metadata)
                
                cur.execute("""
                    INSERT INTO hsg245_knowledge (content, embedding, source, chunk_index, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                """, (chunk, embedding, source, i, psycopg2.extras.Json(chunk_metadata)))
        
        print(f" Added {len(chunks)} chunks to knowledge base")
        return len(chunks)
    
    def add_from_file(self, file_path: str):
        """
        Add text from file
        
        Args:
            file_path: Path to text file
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Add to knowledge base
        source = path.stem  # Filename without extension
        return self.add_text(text, source=source)
    
    def query(self, query_text: str, n_results: int = 3) -> List[Dict]:
        """
        Query knowledge base for relevant documents
        
        Args:
            query_text: Query text (e.g., incident description)
            n_results: Number of results to return
            
        Returns:
            List of relevant documents with metadata
        """
        # Generate query embedding using OpenAI API
        response = self.openai_client.embeddings.create(
            input=query_text,
            model=self.embedding_model
        )
        query_embedding = response.data[0].embedding
        
        # Query PostgreSQL with cosine similarity
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    content,
                    source,
                    metadata,
                    1 - (embedding <=> %s::vector) as similarity
                FROM hsg245_knowledge
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (query_embedding, query_embedding, n_results))
            
            results = cur.fetchall()
        
        # Format results
        formatted_results = [
            {
                'text': row[0],
                'source': row[1],
                'metadata': row[2],
                'similarity': float(row[3])
            }
            for row in results
        ]
        
        return formatted_results
    
    def get_context_for_incident(self, incident_description: str, n_results: int = 5) -> str:
        """
        Get relevant context for incident analysis
        
        Args:
            incident_description: Description of incident
            n_results: Number of relevant chunks to retrieve
            
        Returns:
            Formatted context string for LLM
        """
        results = self.query(incident_description, n_results=n_results)
        
        context = "=== RELEVANT HSG245 KNOWLEDGE ===\n\n"
        
        for i, result in enumerate(results, 1):
            context += f"[Source: {result['source']} | Similarity: {result['similarity']:.2%}]\n"
            context += f"{result['text']}\n\n"
        
        return context
    
    def reset(self):
        """Clear all documents from knowledge base"""
        with self.conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE hsg245_knowledge;")
        print(" Knowledge base cleared")
    
    def stats(self) -> Dict:
        """Get knowledge base statistics"""
        with self.conn.cursor() as cur:
            # Total count
            cur.execute("SELECT COUNT(*) FROM hsg245_knowledge;")
            total_count = cur.fetchone()[0]
            
            # Get unique sources
            cur.execute("SELECT DISTINCT source FROM hsg245_knowledge;")
            sources = [row[0] for row in cur.fetchall()]
            
            return {
                'total_chunks': total_count,
                'sources': sources,
                'source_count': len(sources)
            }
    
    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()


# Singleton instance
_rag_instance = None

def get_rag_system() -> HSG245RAGSystem:
    """Get or create RAG system singleton"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = HSG245RAGSystem()
    return _rag_instance
