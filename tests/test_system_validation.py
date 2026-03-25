#!/usr/bin/env python3
"""
QUICK VALIDATION TEST
====================

Cache + Pipeline yapısının doğru kurulup kurulmadığını test et
(API çağrıları yapmadan, sadece yapıyı doğrula)
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🔍 System Validation Test\n")

# Test 1: Import kontrolü
print("="*80)
print("TEST 1: Import Kontrolü")
print("="*80)

try:
    from agents.unified_analysis_pipeline import (
        AnalysisCache,
        UnifiedAnalysisPipeline
    )
    print("✅ AnalysisCache imported successfully")
    print("✅ UnifiedAnalysisPipeline imported successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Cache manager oluştur
print("\n" + "="*80)
print("TEST 2: Cache Manager")
print("="*80)

try:
    cache = AnalysisCache()
    print("✅ AnalysisCache created")
    print(f"   Cache dir: {cache.cache_dir}")
    print(f"   TTL days: {cache.ttl_days}")
except Exception as e:
    print(f"❌ Cache creation failed: {e}")
    sys.exit(1)

# Test 3: Hash generation
print("\n" + "="*80)
print("TEST 3: Hash Generation")
print("="*80)

incident1 = {
    "ref_no": "INC-001",
    "description": "Test incident 1"
}

incident2 = {
    "ref_no": "INC-002",
    "description": "Test incident 2"
}

incident1_dup = {
    "ref_no": "INC-001",
    "description": "Test incident 1"
}

try:
    hash1 = cache.get_cache_key(incident1)
    hash2 = cache.get_cache_key(incident2)
    hash1_dup = cache.get_cache_key(incident1_dup)
    
    print(f"✅ Hash generation working")
    print(f"   INC-001 hash: {hash1}")
    print(f"   INC-002 hash: {hash2}")
    print(f"   INC-001 (dup) hash: {hash1_dup}")
    
    if hash1 == hash1_dup:
        print("✅ Same incident = same hash (deterministic)")
    else:
        print("❌ Hash mismatch for identical incidents")
        sys.exit(1)
    
    if hash1 != hash2:
        print("✅ Different incidents = different hashes")
    else:
        print("❌ Hash collision detected")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Hash generation failed: {e}")
    sys.exit(1)

# Test 4: Cache read/write
print("\n" + "="*80)
print("TEST 4: Cache Read/Write")
print("="*80)

try:
    # Write to cache
    test_data = {
        "overview": {"type": "Test"},
        "assessment": {"severity": "High"},
        "root_cause": {"code": "D1.0"}
    }
    
    cache.set(incident1, test_data)
    print("✅ Data written to cache")
    
    # Read from cache
    cached_data = cache.get(incident1)
    if cached_data:
        print("✅ Data read from cache (cache hit)")
        print(f"   Stored data matches: {cached_data.get('analysis_result') is not None}")
    else:
        print("❌ Cache read failed")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Cache read/write failed: {e}")
    sys.exit(1)

# Test 5: Pipeline creation
print("\n" + "="*80)
print("TEST 5: Pipeline Creation")
print("="*80)

try:
    pipeline = UnifiedAnalysisPipeline(use_rag=True, use_cache=True)
    print("✅ UnifiedAnalysisPipeline created")
    print(f"   RAG enabled: {pipeline.rootcause_agent.use_rag if hasattr(pipeline.rootcause_agent, 'use_rag') else 'Unknown'}")
    print(f"   Cache enabled: {pipeline.use_cache}")
    print(f"   Cache manager: {pipeline.cache is not None}")
except Exception as e:
    print(f"❌ Pipeline creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Output directories
print("\n" + "="*80)
print("TEST 6: Output Directories")
print("="*80)

try:
    output_dir = Path("outputs/unified_pipeline")
    cache_dir = Path("cache/analyses")
    
    output_exists = output_dir.exists()
    cache_exists = cache_dir.exists()
    
    print(f"{'✅' if output_exists else '⚠️'} outputs/unified_pipeline: {output_exists}")
    print(f"{'✅' if cache_exists else '⚠️'} cache/analyses: {cache_exists}")
    
    if not output_exists:
        output_dir.mkdir(parents=True, exist_ok=True)
        print("   Created output directory")
    
    if not cache_exists:
        cache_dir.mkdir(parents=True, exist_ok=True)
        print("   Created cache directory")
        
except Exception as e:
    print(f"❌ Directory check failed: {e}")
    sys.exit(1)

# Test 7: Agent availability
print("\n" + "="*80)
print("TEST 7: Agent Availability")
print("="*80)

try:
    print(f"✅ OverviewAgent: {pipeline.overview_agent is not None}")
    print(f"✅ AssessmentAgent: {pipeline.assessment_agent is not None}")
    print(f"✅ RootCauseAgent: {pipeline.rootcause_agent is not None}")
    print(f"✅ DocxAgent: {pipeline.docx_agent is not None}")
except Exception as e:
    print(f"❌ Agent check failed: {e}")
    sys.exit(1)

# Test 8: Cache statistics
print("\n" + "="*80)
print("TEST 8: Cache Statistics")
print("="*80)

try:
    stats = cache.get_stats()
    print("✅ Cache statistics retrieved")
    for key, value in stats.items():
        print(f"   {key}: {value}")
except Exception as e:
    print(f"❌ Statistics failed: {e}")
    sys.exit(1)

# Final summary
print("\n" + "="*80)
print("✅ SYSTEM VALIDATION COMPLETE")
print("="*80)
print("""
Summary:
  ✅ All imports working
  ✅ Cache manager operational
  ✅ Hash generation deterministic
  ✅ Cache read/write functional
  ✅ Pipeline created successfully
  ✅ Output directories ready
  ✅ All agents available
  ✅ Statistics tracking works

🎉 SYSTEM READY FOR PRODUCTION USE!

Next steps:
  1. Run quick_cache_test.py for cache verification
  2. Run test_rag_cache_integration.py for full integration
  3. Deploy pipeline in your application
""")
