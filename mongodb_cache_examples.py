#!/usr/bin/env python3
"""
MongoDB Cache Usage Examples
============================
Farklı senaryolarda MongoDB cache nasıl kullanılır?
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agents.unified_analysis_pipeline import UnifiedAnalysisPipeline, MongoDBCache, AnalysisCache


# Example incident data
SAMPLE_INCIDENT = {
    "ref_no": "INC-001",
    "description": "Worker slipped on wet floor, broke arm",
    "location": "Factory Floor",
    "date": "2026-03-14",
    "severity": "High"
}


# ============================================================================
# EXAMPLE 1: Local Development (Disk Cache)
# ============================================================================

def example_1_local_development():
    """Local'de disk cache kullan"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Local Development with Disk Cache")
    print("=" * 70)
    
    pipeline = UnifiedAnalysisPipeline(
        use_rag=False,
        use_cache=True,
        use_mongodb_cache=False  # Force disk cache
    )
    
    print("\n1️⃣ First analysis (disk cache miss)")
    result_1 = pipeline.analyze_incident(SAMPLE_INCIDENT)
    stats = pipeline.cache.get_stats()
    print(f"   Cache stats: {stats}")
    
    print("\n2️⃣ Second analysis (disk cache hit)")
    result_2 = pipeline.analyze_incident(SAMPLE_INCIDENT)
    stats = pipeline.cache.get_stats()
    print(f"   Cache stats: {stats}")
    print(f"   ✅ Disk cache working! Hit rate: {stats['hit_rate']}")


# ============================================================================
# EXAMPLE 2: Production (MongoDB Cache)
# ============================================================================

def example_2_production_mongodb():
    """Railway production'da MongoDB cache kullan"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Production with MongoDB Cache")
    print("=" * 70)
    
    # Check MongoDB URI
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        print("⚠️ MONGODB_URI not set. Skipping example...")
        print("   Set in .env: MONGODB_URI=mongodb+srv://...")
        return
    
    try:
        pipeline = UnifiedAnalysisPipeline(
            use_rag=False,
            use_cache=True,
            use_mongodb_cache=True  # Force MongoDB cache
        )
        
        print("\n1️⃣ First analysis (MongoDB cache miss)")
        result_1 = pipeline.analyze_incident(SAMPLE_INCIDENT)
        stats = pipeline.cache.get_stats()
        print(f"   Cache stats: {stats}")
        
        print("\n2️⃣ Second analysis (MongoDB cache hit)")
        result_2 = pipeline.analyze_incident(SAMPLE_INCIDENT)
        stats = pipeline.cache.get_stats()
        print(f"   Cache stats: {stats}")
        print(f"   ✅ MongoDB cache working! Hit rate: {stats['hit_rate']}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


# ============================================================================
# EXAMPLE 3: Auto-Detection
# ============================================================================

def example_3_auto_detection():
    """Ortama göre otomatik seçim"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Auto-Detection (Local or Production)")
    print("=" * 70)
    
    # No use_mongodb_cache specified - auto-detect!
    pipeline = UnifiedAnalysisPipeline(
        use_rag=False,
        use_cache=True
        # use_mongodb_cache not specified - will auto-detect
    )
    
    print("\n🔍 Pipeline initialized:")
    cache_type = "MongoDB" if hasattr(pipeline.cache, 'collection') else "Disk"
    print(f"   Cache type: {cache_type}")
    
    print("\n1️⃣ Analyzing incident...")
    result = pipeline.analyze_incident(SAMPLE_INCIDENT)
    stats = pipeline.cache.get_stats()
    print(f"   Cache stats: {stats}")


# ============================================================================
# EXAMPLE 4: Direct MongoDB Cache Usage
# ============================================================================

def example_4_direct_mongodb():
    """MongoDB cache'i doğrudan kullan"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Direct MongoDB Cache Usage")
    print("=" * 70)
    
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        print("⚠️ MONGODB_URI not set. Skipping example...")
        return
    
    try:
        # MongoDB cache'i oluştur
        cache = MongoDBCache(
            db_name="rca_database",
            collection_name="analysis_cache",
            ttl_days=30
        )
        
        print("\n1️⃣ Get cache key")
        key = cache.get_cache_key(SAMPLE_INCIDENT)
        print(f"   Key: {key}")
        
        print("\n2️⃣ Set cache")
        result_data = {"overview": "Test analysis", "status": "ok"}
        cache.set(SAMPLE_INCIDENT, result_data)
        print(f"   ✅ Cached result")
        
        print("\n3️⃣ Get from cache")
        cached = cache.get(SAMPLE_INCIDENT)
        if cached:
            print(f"   ✅ Found in cache!")
            print(f"   Data: {cached['analysis_result']}")
        
        print("\n4️⃣ View statistics")
        stats = cache.get_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n5️⃣ Clear cache")
        cache.clear()
        print(f"   ✅ Cache cleared")
    
    except Exception as e:
        print(f"❌ Error: {e}")


# ============================================================================
# EXAMPLE 5: Batch Processing with Cache
# ============================================================================

def example_5_batch_with_cache():
    """Batch incident'lar cache ile işle"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Batch Processing with Cache Optimization")
    print("=" * 70)
    
    # Incidents: 2 unique + 2 repeats = 4 total
    incidents = [
        {"ref_no": "A1", "description": "Incident A"},
        {"ref_no": "B1", "description": "Incident B"},
        {"ref_no": "A1", "description": "Incident A"},  # Repeat - cache hit
        {"ref_no": "B1", "description": "Incident B"},  # Repeat - cache hit
    ]
    
    pipeline = UnifiedAnalysisPipeline(
        use_rag=False,
        use_cache=True
    )
    
    print(f"\nProcessing {len(incidents)} incidents...")
    for i, incident in enumerate(incidents, 1):
        print(f"\n{i}. Processing {incident['ref_no']}...")
        try:
            result = pipeline.analyze_incident(incident)
            print(f"   ✅ Completed")
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
    
    stats = pipeline.cache.get_stats()
    print(f"\n📊 Final Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print(f"\n💡 Savings: {stats['money_saved']} with {stats['hit_rate']} hit rate!")


# ============================================================================
# EXAMPLE 6: Cache Clearing
# ============================================================================

def example_6_cache_management():
    """Cache yönetimi"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Cache Management")
    print("=" * 70)
    
    pipeline = UnifiedAnalysisPipeline(
        use_rag=False,
        use_cache=True
    )
    
    print("\n1️⃣ Add some data to cache...")
    result = pipeline.analyze_incident(SAMPLE_INCIDENT)
    stats_before = pipeline.cache.get_stats()
    print(f"   Before: {stats_before['total_requests']} requests")
    
    print("\n2️⃣ Clear cache")
    pipeline.cache.clear()
    print(f"   ✅ Cache cleared")
    
    print("\n3️⃣ Add data again (cache is now empty)")
    result = pipeline.analyze_incident(SAMPLE_INCIDENT)
    stats_after = pipeline.cache.get_stats()
    print(f"   After: {stats_after['cache_misses']} misses (cache was cleared)")


# ============================================================================
# EXAMPLE 7: Error Handling
# ============================================================================

def example_7_error_handling():
    """Hata yönetimi"""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Error Handling & Fallback")
    print("=" * 70)
    
    try:
        # MongoDB olmadığında fallback
        pipeline = UnifiedAnalysisPipeline(
            use_rag=False,
            use_cache=True,
            use_mongodb_cache=True  # Try MongoDB
        )
        print("✅ MongoDB cache initialized")
    except Exception as e:
        print(f"⚠️ MongoDB failed: {e}")
        print("   Falling back to disk cache...")
        pipeline = UnifiedAnalysisPipeline(
            use_rag=False,
            use_cache=True,
            use_mongodb_cache=False
        )
        print("✅ Disk cache initialized")
    
    result = pipeline.analyze_incident(SAMPLE_INCIDENT)
    print("✅ Analysis completed with fallback cache")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("""
    🚀 MongoDB Cache Usage Examples
    ================================
    
    Çalıştırılacak örnek seçin (1-7):
    """)
    
    examples = {
        "1": ("Local Development (Disk Cache)", example_1_local_development),
        "2": ("Production (MongoDB Cache)", example_2_production_mongodb),
        "3": ("Auto-Detection", example_3_auto_detection),
        "4": ("Direct MongoDB Cache", example_4_direct_mongodb),
        "5": ("Batch Processing", example_5_batch_with_cache),
        "6": ("Cache Management", example_6_cache_management),
        "7": ("Error Handling", example_7_error_handling),
    }
    
    for key, (name, _) in examples.items():
        print(f"   {key}. {name}")
    
    choice = input("\nSeçim (1-7) veya 'all' (tümü): ").strip()
    
    if choice == "all":
        for example_func in [func for _, func in examples.values()]:
            try:
                example_func()
            except Exception as e:
                print(f"⚠️ Error in example: {e}")
    elif choice in examples:
        try:
            examples[choice][1]()
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ Invalid choice")
    
    print("\n✅ Examples completed!")
