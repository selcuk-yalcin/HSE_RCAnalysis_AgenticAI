#!/usr/bin/env python3
"""
Test MongoDB Cache - Write Sample Data
======================================
MongoDB Atlas'ta cache'leri test et
"""

import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

# Test data
incident = {
    "ref_no": "TEST-CACHE-001",
    "description": "Worker slipped on wet floor in manufacturing area"
}

analysis_result = {
    "source": "api",
    "overview": "Industrial slip and fall incident",
    "assessment": "High risk environment",
    "root_cause": "Inadequate floor maintenance",
    "recommendations": ["Improve floor cleaning", "Add warning signs"]
}

print("""
╔═══════════════════════════════════════════════════╗
║   MongoDB Cache Write Test                        ║
╚═══════════════════════════════════════════════════╝
""")

# Check env
mongo_uri = os.getenv("MONGODB_URI")
mongo_rca_db = os.getenv("MONGODB_RCA_DB")
mongo_cache_col = os.getenv("MONGODB_CACHE_COLLECTION")

if not mongo_uri:
    print("❌ MONGODB_URI not set in .env")
    sys.exit(1)

print(f"✅ Configuration loaded:")
print(f"   URI: {mongo_uri[:60]}...")
print(f"   Database: {mongo_rca_db}")
print(f"   Collection: {mongo_cache_col}")
print()

# Try to write to MongoDB
try:
    from pymongo import MongoClient
    import hashlib
    
    print("🔍 Connecting to MongoDB Atlas...")
    # Remove quotes if present
    if mongo_uri.startswith('"') and mongo_uri.endswith('"'):
        mongo_uri = mongo_uri[1:-1]
    
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=15000)
    client.admin.command('ping')
    print("✅ Connected!")
    
    # Get database and collection
    db = client[mongo_rca_db]
    collection = db[mongo_cache_col]
    
    # Generate cache key
    normalized = f"{incident['ref_no']}:{incident['description']}".strip().lower()
    normalized = " ".join(normalized.split())
    cache_key = hashlib.md5(normalized.encode()).hexdigest()
    
    print(f"\n📝 Writing to cache:")
    print(f"   Incident: {incident['ref_no']}")
    print(f"   Cache key: {cache_key[:16]}...")
    
    # Write to MongoDB
    doc = {
        "cache_key": cache_key,
        "incident_ref": incident['ref_no'],
        "analysis_result": analysis_result,
        "created_at": datetime.now(),
        "expires_at": datetime.now()  # For TTL index
    }
    
    result = collection.insert_one(doc)
    print(f"✅ Written! ID: {result.inserted_id}")
    
    # Verify write
    print(f"\n🔍 Verifying...")
    found = collection.find_one({"cache_key": cache_key})
    if found:
        print(f"✅ Found in database!")
        print(f"   Cache key: {found['cache_key'][:16]}...")
        print(f"   Incident: {found['incident_ref']}")
        print(f"   Created: {found['created_at']}")
    else:
        print(f"❌ Not found in database")
    
    # Show collection stats
    print(f"\n📊 Collection stats:")
    total = collection.count_documents({})
    print(f"   Total documents: {total}")
    
    # List all in collection
    if total > 0:
        print(f"\n📋 All cached incidents:")
        for doc in collection.find():
            print(f"   • {doc.get('incident_ref')} (cached: {doc.get('created_at')})")
    
    print(f"\n✅ MongoDB Cache test completed successfully!")
    print(f"\n💡 Structure in MongoDB Atlas:")
    print(f"   mevzuatdb (cluster)")
    print(f"   └── {mongo_rca_db} (database)")
    print(f"       ├── taxonomy")
    print(f"       ├── vector_search")
    print(f"       └── {mongo_cache_col} ← Cache here!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
