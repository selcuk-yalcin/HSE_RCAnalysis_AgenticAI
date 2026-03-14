#!/usr/bin/env python3
"""
Doğrudan MongoDB'ye Yazma (MongoClient'i test et)
"""
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

print("MongoDB Doğrudan Yazma Testi")
print("=" * 50)

# Get config
mongo_uri = os.getenv("MONGODB_URI", "").strip()
if mongo_uri.startswith('"') and mongo_uri.endswith('"'):
    mongo_uri = mongo_uri[1:-1]

db_name = os.getenv("MONGODB_RCA_DB", "rca_database")
col_name = os.getenv("MONGODB_CACHE_COLLECTION", "analysis_cache")

print(f"\n1. Configuration:")
print(f"   URI: {mongo_uri[:50]}...")
print(f"   DB: {db_name}")
print(f"   Collection: {col_name}")

# Try direct write
print(f"\n2. Attempting connection...")

try:
    from pymongo import MongoClient
    import hashlib
    
    # Connect with explicit timeouts
    print("   Creating client...")
    client = MongoClient(
        mongo_uri,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        retryWrites=True
    )
    
    print("   Pinging server...")
    client.admin.command('ping')
    print("   ✅ Connected!")
    
    # Get collection
    db = client[db_name]
    collection = db[col_name]
    
    # Test document
    test_doc = {
        "cache_key": hashlib.md5(b"test-incident").hexdigest(),
        "incident_ref": "TEST-001",
        "analysis_result": {"status": "test", "timestamp": datetime.now()},
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(days=30)
    }
    
    print(f"\n3. Writing document...")
    result = collection.insert_one(test_doc)
    print(f"   ✅ Inserted ID: {result.inserted_id}")
    
    # Read back
    print(f"\n4. Reading back...")
    found = collection.find_one({"_id": result.inserted_id})
    if found:
        print(f"   ✅ Document found!")
        print(f"      Incident: {found['incident_ref']}")
    
    # Count
    count = collection.count_documents({})
    print(f"\n5. Collection stats:")
    print(f"   Total documents: {count}")
    
    print(f"\n✅ SUCCESS! Cache yazılmış.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
