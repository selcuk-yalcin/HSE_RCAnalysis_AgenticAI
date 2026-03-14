#!/usr/bin/env python3
"""
Local Disk Cache Test
Cache'i disk'te sakla, sonra MongoDB'de de saklanacak
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))

print("""
╔════════════════════════════════════════════════════╗
║     Local Disk Cache Test (Development Mode)      ║
║     Production'da MongoDB kullanılacak             ║
╚════════════════════════════════════════════════════╝
""")

print("""
📌 Cache Architecture:
   🖥️  Local Development: Disk Cache (fast, no network needed)
   ☁️  Production (Railway): MongoDB Cache (persistent)
   
   Attachment'ta görülen collection:
   └── rca_database
       ├── taxonomy
       ├── vector_search  
       └── analysis_cache ← Production'da kullanılacak
""")

incident_data = {
    "ref_no": "INC-2026-001",
    "description": "Worker slipped on wet floor in manufacturing area",
    "location": "Manufacturing Floor"
}

analysis_result = {
    "overview": "Slip and fall incident",
    "severity": "High",
    "root_causes": ["Inadequate floor maintenance", "Lack of warning signs"],
    "recommendations": ["Daily floor cleaning", "Non-slip flooring"],
    "cost": "$15,000"
}

try:
    # Import local cache
    from agents.unified_analysis_pipeline import AnalysisCache
    
    print("\n1️⃣  Creating Local Disk Cache...")
    cache = AnalysisCache(ttl_days=30)
    print(f"   ✅ Cache directory: {cache.cache_dir}")
    print()
    
    print("2️⃣  Cache Operations Test:")
    print("   a) First check - MISS (not cached)")
    
    # First check
    cached = cache.get(incident_data)
    if cached:
        print("      ⚠️  Found (unexpected)")
    else:
        print("      ✅ Cache miss (expected)")
    
    print("   b) Writing to disk cache...")
    cache.set(incident_data, analysis_result)
    print("      ✅ Written to disk")
    
    # Show cache file
    import hashlib
    ref = incident_data.get("ref_no", "")
    desc = incident_data.get("description", "").lower().strip()
    normalized = f"{ref}:{desc}".lower().strip()
    normalized = " ".join(normalized.split())
    cache_key = hashlib.md5(normalized.encode()).hexdigest()
    cache_file = cache.cache_dir / f"{cache_key}.json"
    
    if cache_file.exists():
        print(f"      📁 Cache file: {cache_file.name}")
        print(f"      📏 Size: {cache_file.stat().st_size} bytes")
    
    print("   c) Second check - HIT (cached)")
    # Second check
    cached = cache.get(incident_data)
    if cached:
        print("      ✅ Cache HIT!")
        print(f"         Severity: {cached.get('severity')}")
    else:
        print("      ⚠️  Not found")
    
    print()
    print("3️⃣  Cache Statistics:")
    stats = cache.get_stats()
    print(f"   Hits: {stats['hits']}")
    print(f"   Misses: {stats['misses']}")
    print(f"   Saved Cost: ${stats['saved_cost']:.2f}")
    
    print()
    print("4️⃣  List Cached Items:")
    cache_files = list(cache.cache_dir.glob("*.json"))
    print(f"   Total cached: {len(cache_files)} item(s)")
    for cf in cache_files[:5]:
        size_kb = cf.stat().st_size / 1024
        print(f"      • {cf.name} ({size_kb:.1f} KB)")
    
    print()
    print("✅ Disk Cache Test Completed!")
    print()
    print("📝 Notes:")
    print("   • Local: Cache → disk (.cache/ folder)")
    print("   • Production: Cache → MongoDB (rca_database.analysis_cache)")
    print("   • Same interface, different backend")
    print()
    print("🚀 To use MongoDB in production:")
    print("   • Set environment: use_mongodb_cache=True")
    print("   • MongoDB bağlantısı yapılacak (network timeout çözülünce)")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
