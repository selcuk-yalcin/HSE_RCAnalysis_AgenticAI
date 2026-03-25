#!/usr/bin/env python3
"""
Test MongoDB Cache Configuration
================================
Verify cache collection in rca_database
"""

import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment
from dotenv import load_dotenv
load_dotenv()

mongo_uri = os.getenv("MONGODB_URI")
mongo_rca_db = os.getenv("MONGODB_RCA_DB")
mongo_cache_collection = os.getenv("MONGODB_CACHE_COLLECTION")

print("🔧 MongoDB Cache Configuration:")
print(f"  ✅ URI: {mongo_uri[:60]}...")
print(f"  ✅ Database: {mongo_rca_db}")
print(f"  ✅ Cache Collection: {mongo_cache_collection}")
print()

# Test connection
try:
    from pymongo import MongoClient
    print("🔍 Connecting to MongoDB Atlas...")
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
    client.admin.command('ping')
    print("✅ Connection successful!")
    
    # Get database
    db = client[mongo_rca_db]
    print(f"\n📦 Database: {mongo_rca_db}")
    
    # List collections
    collections = db.list_collection_names()
    print(f"   Collections: {collections}")
    
    # Check cache collection
    cache_col = db[mongo_cache_collection]
    cache_count = cache_col.count_documents({})
    print(f"\n📋 Cache Collection ({mongo_cache_collection}):")
    print(f"   Documents: {cache_count}")
    
    if cache_count > 0:
        sample = cache_col.find_one({})
        print(f"   Sample:")
        print(f"     - cache_key: {str(sample.get('cache_key', 'N/A'))[:20]}...")
        print(f"     - incident_ref: {sample.get('incident_ref', 'N/A')}")
        print(f"     - created_at: {sample.get('created_at', 'N/A')}")
    
    print("\n✅ MongoDB Cache is ready!")
    print("\n💡 Structure:")
    print(f"   mevzuatdb (cluster)")
    print(f"   └── {mongo_rca_db} (database)")
    print(f"       ├── taxonomy (collection - Mevzuat)")
    print(f"       ├── vector_search (collection - RAG)")
    print(f"       └── {mongo_cache_collection} (collection) ← Cache!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
