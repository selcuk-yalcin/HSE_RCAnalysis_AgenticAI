"""
Knowledge Base Loader
Load HSG245 text documents into RAG system
"""

import sys
from pathlib import Path
from shared.rag_system import get_rag_system

def load_text_file(file_path: str):
    """Load a single text file into knowledge base"""
    rag = get_rag_system()
    
    print(f"\n Loading: {file_path}")
    chunks_added = rag.add_from_file(file_path)
    
    print(f" Successfully loaded {chunks_added} chunks")
    
    # Show stats
    stats = rag.stats()
    print(f"\n Knowledge Base Stats:")
    print(f"   Total chunks: {stats['total_chunks']}")
    print(f"   Sources: {stats['source_count']}")
    for source in stats['sources']:
        print(f"   - {source}")

def load_text_string(text: str, source_name: str):
    """Load text from string"""
    rag = get_rag_system()
    
    print(f"\n Loading text from: {source_name}")
    chunks_added = rag.add_text(text, source=source_name)
    
    print(f" Successfully loaded {chunks_added} chunks")
    
    # Show stats
    stats = rag.stats()
    print(f"\n Knowledge Base Stats:")
    print(f"   Total chunks: {stats['total_chunks']}")
    print(f"   Sources: {stats['source_count']}")

def load_multiple_files(directory: str):
    """Load all .txt files from directory"""
    rag = get_rag_system()
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f" Directory not found: {directory}")
        return
    
    txt_files = list(dir_path.glob("*.txt"))
    
    if not txt_files:
        print(f" No .txt files found in {directory}")
        return
    
    print(f"\n Found {len(txt_files)} text files in {directory}")
    
    total_chunks = 0
    for file_path in txt_files:
        print(f"\n   Loading: {file_path.name}")
        chunks = rag.add_from_file(str(file_path))
        total_chunks += chunks
    
    print(f"\n Loaded {total_chunks} total chunks from {len(txt_files)} files")
    
    # Show stats
    stats = rag.stats()
    print(f"\n Knowledge Base Stats:")
    print(f"   Total chunks: {stats['total_chunks']}")
    print(f"   Sources: {stats['source_count']}")

def test_query(query: str):
    """Test query on knowledge base"""
    rag = get_rag_system()
    
    print(f"\n Testing query: {query}")
    results = rag.query(query, n_results=3)
    
    print(f"\n Top 3 Results:")
    for i, result in enumerate(results, 1):
        print(f"\n   Result {i} [Source: {result['metadata']['source']}]:")
        print(f"   {result['text'][:200]}...")

if __name__ == "__main__":
    print("=" * 60)
    print("HSG245 Knowledge Base Loader")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python load_knowledge.py <file_path>        # Load single file")
        print("  python load_knowledge.py --dir <directory>  # Load all .txt files")
        print("  python load_knowledge.py --test <query>     # Test query")
        print("\nExample:")
        print("  python load_knowledge.py hsg245_regulations.txt")
        print("  python load_knowledge.py --dir ./knowledge_docs")
        print("  python load_knowledge.py --test 'workplace accident investigation'")
        sys.exit(1)
    
    if sys.argv[1] == "--dir":
        if len(sys.argv) < 3:
            print(" Please provide directory path")
            sys.exit(1)
        load_multiple_files(sys.argv[2])
    
    elif sys.argv[1] == "--test":
        if len(sys.argv) < 3:
            print(" Please provide query text")
            sys.exit(1)
        query = " ".join(sys.argv[2:])
        test_query(query)
    
    else:
        # Single file mode
        load_text_file(sys.argv[1])
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)
