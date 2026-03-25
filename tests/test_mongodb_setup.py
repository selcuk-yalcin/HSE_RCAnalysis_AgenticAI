#!/usr/bin/env python3
"""
Simple MongoDB Cache Test - No External MongoDB Needed
======================================================
SQLite yerine MongoDB'ye cache kaydet (mock test)
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("""
╔════════════════════════════════════════════════════════════════╗
║   MongoDB Cache System - Setup & Testing Guide              ║
╚════════════════════════════════════════════════════════════════╝
""")

# Check MongoDB URI
mongo_uri = os.getenv("MONGODB_URI")

if not mongo_uri:
    print("""
❌ MONGODB_URI not configured

For Local Testing, choose one option:

Option 1: MongoDB Community (Recommended)
─────────────────────────────────────────
macOS:
  brew install mongodb-community
  brew services start mongodb-community
  
Linux (Ubuntu/Debian):
  sudo apt-get install mongodb
  sudo systemctl start mongodb
  
Then set:
  export MONGODB_URI=mongodb://localhost:27017/

Option 2: MongoDB with Docker
──────────────────────────────
  docker run -d -p 27017:27017 --name mongodb mongo:latest
  
Then set:
  export MONGODB_URI=mongodb://localhost:27017/

Option 3: MongoDB Atlas Cloud (Production)
──────────────────────────────────────────
  1. Create cluster at https://www.mongodb.com/cloud/atlas
  2. Get connection string
  3. Set:
     export MONGODB_URI=mongodb+srv://user:password@cluster...

Option 4: For Railway Production
────────────────────────────────
  1. Go to Railway Dashboard
  2. Project → Add → MongoDB
  3. Auto-injects MONGODB_URI

═════════════════════════════════════════════════════════════════
""")
    sys.exit(1)

print(f"✅ MONGODB_URI configured!")
print(f"   Connection: {mongo_uri[:50]}...")

# Test MongoDB connection
print("\n🔍 Testing MongoDB connection...")

try:
    from pymongo import MongoClient
    
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    
    # Test connection
    client.admin.command('ping')
    print("✅ MongoDB connection successful!")
    
    # Show database info
    db = client['rca_database']
    collections = db.list_collection_names()
    print(f"   Database: rca_database")
    print(f"   Collections: {collections if collections else 'empty'}")
    
    # Check cache collection
    cache_collection = db['analysis_cache']
    cache_count = cache_collection.count_documents({})
    print(f"   Cache documents: {cache_count}")
    
    if cache_count > 0:
        print(f"\n   📊 Sample cache entry:")
        sample = cache_collection.find_one({})
        print(f"      - cache_key: {sample.get('cache_key', 'N/A')[:16]}...")
        print(f"      - incident_ref: {sample.get('incident_ref', 'N/A')}")
        print(f"      - created_at: {sample.get('created_at', 'N/A')}")
    
    print("""
════════════════════════════════════════════════════════════════

✅ MongoDB is ready for caching!

Next Steps:
──────────

1. Test Disk Cache (no MongoDB needed):
   python3 quick_cache_test.py

2. Test Full Pipeline with Disk Cache:
   python3 test_unified_pipeline.py

3. Use MongoDB Cache in code:
   from agents.unified_analysis_pipeline import UnifiedAnalysisPipeline
   
   pipeline = UnifiedAnalysisPipeline(
       use_cache=True,
       use_mongodb_cache=True  # Force MongoDB
   )
   
   result = pipeline.analyze_incident(incident_data)
   
   # Check stats
   stats = pipeline.cache.get_stats()
   print(f"Hit rate: {stats['hit_rate']}")
   print(f"Saved: {stats['money_saved']}")

4. Production Deploy to Railway:
   - Add MongoDB service in Railway Dashboard
   - Push code
   - Done! 🚀

════════════════════════════════════════════════════════════════
""")
    
except ImportError:
    print("❌ pymongo not installed")
    print("   pip install pymongo")
    sys.exit(1)
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("""
This could mean:
1. MongoDB service not running
2. Invalid connection string
3. Network connectivity issue

Try:
- For local: mongosh "mongodb://localhost:27017/"
- Check MongoDB logs
- Verify MONGODB_URI syntax
""")
    sys.exit(1)
