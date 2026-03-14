#!/usr/bin/env python3
"""
MongoDB Cache'i Test Et
Cache'i rca_database.analysis_cache'e yaz
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Add agents to path
sys.path.insert(0, str(Path(__file__).parent))

print("""
╔════════════════════════════════════════════════════╗
║  MongoDB Cache Test - rca_database.analysis_cache ║
╚════════════════════════════════════════════════════╝
""")

# Test incident data
incident_data = {
    "ref_no": "TEST-CACHE-2026-001",
    "description": "Worker slipped on wet floor in manufacturing area - hazard scenario",
    "location": "Manufacturing Floor",
    "incident_type": "Slip and Fall"
}

analysis_result = {
    "overview": "Slip and fall incident on wet manufacturing floor",
    "severity": "High",
    "root_causes": [
        "Inadequate floor maintenance",
        "Lack of warning signs",
        "Poor drainage system"
    ],
    "recommendations": [
        "Implement daily floor cleaning schedule",
        "Install non-slip flooring",
        "Add warning signs for wet areas"
    ],
    "cost_estimate": "$15,000"
}

print("📋 Test Scenario:")
print(f"   Ref No: {incident_data['ref_no']}")
print(f"   Description: {incident_data['description'][:60]}...")
print()

try:
    # Import MongoDB cache
    from agents.unified_analysis_pipeline import MongoDBCache
    
    print("1️⃣  Creating MongoDB Cache instance...")
    cache = MongoDBCache(ttl_days=30)
    print()
    
    print("2️⃣  Testing Cache Operations:")
    print("   a) First call - should MISS (not in cache)")
    
    # First call - miss
    cached_result = cache.get(incident_data)
    if cached_result:
        print("      ✅ Found in cache (unexpected)")
    else:
        print("      ✅ Cache miss (expected)")
    
    print("   b) Writing to cache...")
    cache.set(incident_data, analysis_result)
    print("      ✅ Written to MongoDB")
    
    print("   c) Second call - should HIT (in cache)")
    # Second call - hit
    cached_result = cache.get(incident_data)
    if cached_result:
        print("      ✅ Cache HIT! Found in cache")
        print(f"         Severity: {cached_result.get('severity')}")
    else:
        print("      ⚠️  No cache hit")
    
    print()
    print("3️⃣  Cache Statistics:")
    stats = cache.get_stats()
    print(f"   Hits: {stats['hits']}")
    print(f"   Misses: {stats['misses']}")
    print(f"   Saved Cost: ${stats['saved_cost']:.2f}")
    
    print()
    print("✅ MongoDB Cache Test Completed!")
    print()
    print("📍 Data Location:")
    print("   Cluster: mevzuatdb.qqpyi1b.mongodb.net")
    print("   Database: rca_database")
    print("   Collection: analysis_cache ← Cache here!")
    print()
    print("🔗 View in MongoDB Atlas:")
    print("   https://cloud.mongodb.com/v2/")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
