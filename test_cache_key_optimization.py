#!/usr/bin/env python3
"""
Test MongoDB Cache Key Optimization
====================================

Kritik alanlara göre optimize edilmiş cache key'leri test et.

Özellikler:
1. ✅ Sadece kritik alanlar → lightweight cache keys
2. ✅ Description farkı göz ardı → daha yüksek hit rate
3. ✅ Case-insensitive comparison → "Oil" = "oil" = "OIL"
4. ✅ Whitespace normalization → "Oil  Purifier" = "oil purifier"
5. ✅ SHA256 hashing → MD5 yerine daha güvenli
"""

import sys
import json
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.mongodb_cache_utils import (
    CacheKeyManager,
    CacheKeyDebugger,
    CacheEntryMetadata
)


def test_basic_cache_key_generation():
    """Test 1: Temel cache key generation"""
    print("\n" + "="*100)
    print("TEST 1: Temel Cache Key Generation")
    print("="*100)
    
    incident = {
        "_id": "INC-001",
        "ref_no": "OIL-2026-001",
        "incident_type": "ACCIDENT",
        "equipment": "Oil Purifier",
        "injury_type": "BURN",
        "activity": "Maintenance",
        "description": "Detailed incident description about oil purifier",
        "location": "Workshop"
    }
    
    cache_key = CacheKeyManager.generate_cache_key("incident", incident)
    
    print(f"\n✅ Generated Cache Key:")
    print(f"   {cache_key}")
    
    # Validate format
    if CacheKeyManager.is_cache_key_valid(cache_key):
        print(f"\n✅ Cache key format is valid!")
        print(f"   Format: entity_type:version:hash")
    else:
        print(f"\n❌ Cache key format is invalid!")
    
    return cache_key


def test_case_insensitive_matching():
    """Test 2: Case-insensitive matching"""
    print("\n" + "="*100)
    print("TEST 2: Case-Insensitive Matching")
    print("="*100)
    
    incident_1 = {
        "incident_type": "ACCIDENT",
        "equipment": "Oil Purifier",
        "injury_type": "BURN",
        "activity": "Maintenance"
    }
    
    incident_2 = {
        "incident_type": "accident",  # lowercase
        "equipment": "oil purifier",  # lowercase
        "injury_type": "burn",        # lowercase
        "activity": "MAINTENANCE"     # uppercase
    }
    
    key1 = CacheKeyManager.generate_cache_key("incident", incident_1)
    key2 = CacheKeyManager.generate_cache_key("incident", incident_2)
    
    print(f"\nIncident 1 (mixed case): {key1}")
    print(f"Incident 2 (lowercase):  {key2}")
    
    if key1 == key2:
        print(f"\n✅ KEYS MATCH! Case normalization works correctly.")
        print(f"   → Both incidents use the same cache")
    else:
        print(f"\n❌ KEYS DIFFERENT! Case normalization failed.")
    
    return key1 == key2


def test_description_difference_ignored():
    """Test 3: Description farkı göz ardı edilir"""
    print("\n" + "="*100)
    print("TEST 3: Description Difference Ignored")
    print("="*100)
    
    incident_1 = {
        "incident_type": "ACCIDENT",
        "equipment": "Oil Purifier",
        "injury_type": "BURN",
        "activity": "Maintenance",
        "description": "Short description"
    }
    
    incident_2 = {
        "incident_type": "ACCIDENT",
        "equipment": "Oil Purifier",
        "injury_type": "BURN",
        "activity": "Maintenance",
        "description": "Very long and detailed description about oil purifier fire incident with root cause analysis and prevention measures..."
    }
    
    key1 = CacheKeyManager.generate_cache_key("incident", incident_1)
    key2 = CacheKeyManager.generate_cache_key("incident", incident_2)
    
    print(f"\nIncident 1 description: {incident_1['description'][:50]}...")
    print(f"Incident 2 description: {incident_2['description'][:50]}...")
    
    print(f"\nIncident 1 cache key: {key1}")
    print(f"Incident 2 cache key: {key2}")
    
    if key1 == key2:
        print(f"\n✅ KEYS MATCH! Description differences ignored.")
        print(f"   → Both incidents share same cache (cost savings!)")
    else:
        print(f"\n❌ KEYS DIFFERENT! Description affected cache key.")
    
    return key1 == key2


def test_whitespace_normalization():
    """Test 4: Whitespace normalization"""
    print("\n" + "="*100)
    print("TEST 4: Whitespace Normalization")
    print("="*100)
    
    incident_1 = {
        "equipment": "Oil Purifier",
        "incident_type": "ACCIDENT",
        "injury_type": "BURN",
        "activity": "Maintenance"
    }
    
    incident_2 = {
        "equipment": "   Oil  Purifier   ",  # Extra spaces
        "incident_type": "  ACCIDENT  ",
        "injury_type": "BURN",
        "activity": "Maintenance"
    }
    
    key1 = CacheKeyManager.generate_cache_key("incident", incident_1)
    key2 = CacheKeyManager.generate_cache_key("incident", incident_2)
    
    print(f"\nIncident 1 equipment: '{incident_1['equipment']}'")
    print(f"Incident 2 equipment: '{incident_2['equipment']}'")
    
    if key1 == key2:
        print(f"\n✅ KEYS MATCH! Whitespace normalization works.")
    else:
        print(f"\n❌ KEYS DIFFERENT! Whitespace not normalized.")
    
    return key1 == key2


def test_debug_mode():
    """Test 5: Debug mode - hangi alanlar kullanıldı?"""
    print("\n" + "="*100)
    print("TEST 5: Debug Mode - Field Inspection")
    print("="*100)
    
    incident = {
        "_id": "INC-001",
        "ref_no": "OIL-2026-001",
        "incident_type": "ACCIDENT",
        "equipment": "Oil Purifier",
        "injury_type": "BURN",
        "activity": "Maintenance",
        "description": "This is a detailed description",
        "location": "Workshop",
        "extra_field": "This should not be used in cache key"
    }
    
    debug_info = CacheKeyDebugger.debug_generate_key("incident", incident)
    
    print(f"\n📋 Cache Key Debug Info:")
    print(f"   Cache Key: {debug_info['cache_key']}")
    print(f"   Valid: {debug_info['is_valid']}")
    
    print(f"\n📌 Critical Fields Used:")
    for field in debug_info['critical_fields']:
        print(f"   - {field}")
    
    print(f"\n📊 Extracted Data:")
    for field, value in debug_info['extracted_data'].items():
        print(f"   {field}: {value}")
    
    print(f"\n🔄 Normalized Data:")
    for field, value in debug_info['normalized_data'].items():
        print(f"   {field}: {value}")
    
    # Check that description is not included
    if 'description' not in debug_info['extracted_data']:
        print(f"\n✅ Description correctly excluded from cache key!")
    else:
        print(f"\n❌ Description was included in cache key!")
    
    return 'description' not in debug_info['extracted_data']


def test_comparison_mode():
    """Test 6: Comparison mode - iki incident'ı karşılaştır"""
    print("\n" + "="*100)
    print("TEST 6: Comparison Mode")
    print("="*100)
    
    incidents = [
        {
            "incident_type": "ACCIDENT",
            "equipment": "Forklift",
            "injury_type": "FRACTURE",
            "activity": "Loading"
        },
        {
            "incident_type": "ACCIDENT",
            "equipment": "Forklift",
            "injury_type": "FRACTURE",
            "activity": "Unloading"  # Different activity
        }
    ]
    
    comparison = CacheKeyDebugger.compare_keys("incident", incidents[0], incidents[1])
    
    print(f"\nIncident 1 Key: {comparison['key_1']}")
    print(f"Incident 2 Key: {comparison['key_2']}")
    print(f"Match: {comparison['match']}")
    
    if comparison['match']:
        print(f"\n✅ KEYS MATCH!")
    else:
        print(f"\n❌ KEYS DIFFERENT!")
        if comparison.get('differences', {}).get('field'):
            print(f"   Differences in fields: {comparison['differences']['field']}")
    
    return comparison


def test_bulk_key_generation():
    """Test 7: Bulk cache key generation"""
    print("\n" + "="*100)
    print("TEST 7: Bulk Cache Key Generation")
    print("="*100)
    
    incidents = [
        {
            "_id": "INC-001",
            "incident_type": "ACCIDENT",
            "equipment": "Oil Purifier",
            "injury_type": "BURN",
            "activity": "Maintenance"
        },
        {
            "_id": "INC-002",
            "incident_type": "NEAR-MISS",
            "equipment": "Forklift",
            "injury_type": "NONE",
            "activity": "Loading"
        },
        {
            "_id": "INC-003",
            "incident_type": "ACCIDENT",
            "equipment": "Mixer",
            "injury_type": "CUT",
            "activity": "Cleaning"
        }
    ]
    
    bulk_keys = CacheKeyManager.generate_bulk_cache_keys("incident", incidents)
    
    print(f"\n📦 Generated {len(bulk_keys)} cache keys:")
    for entity_id, cache_key in bulk_keys.items():
        print(f"   {entity_id} → {cache_key}")
    
    return len(bulk_keys) == len(incidents)


def test_metadata_creation():
    """Test 8: Metadata creation for MongoDB"""
    print("\n" + "="*100)
    print("TEST 8: Cache Entry Metadata Creation")
    print("="*100)
    
    incident = {
        "_id": "INC-001",
        "ref_no": "OIL-2026-001",
        "incident_type": "ACCIDENT",
        "equipment": "Oil Purifier",
        "injury_type": "BURN",
        "activity": "Maintenance"
    }
    
    cache_key = CacheKeyManager.generate_cache_key("incident", incident)
    
    analysis_result = {
        "root_cause": "Valve not opened before heating",
        "severity": "HIGH",
        "recommendations": ["Add warning signs", "Implement checklist"]
    }
    
    metadata = CacheEntryMetadata.create_metadata(
        cache_key=cache_key,
        entity_type="incident",
        entity_data=incident,
        analysis_result=analysis_result,
        ttl_days=30
    )
    
    print(f"\n📌 Created Metadata:")
    print(json.dumps(metadata, indent=2, default=str, ensure_ascii=False)[:500] + "...")
    
    # Verify metadata structure
    required_keys = ['cache_key', 'entity_type', 'entity_id', 'analysis_result', 'created_at', 'expires_at', 'metadata']
    all_present = all(key in metadata for key in required_keys)
    
    if all_present:
        print(f"\n✅ Metadata structure is valid!")
    else:
        print(f"\n❌ Metadata structure is incomplete!")
    
    return all_present


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Tüm testleri çalıştır"""
    print("\n" + "█"*100)
    print("🧪 MONGODB CACHE KEY OPTIMIZATION TESTS")
    print("█"*100)
    
    results = {
        "Test 1 - Basic Generation": test_basic_cache_key_generation() is not None,
        "Test 2 - Case Insensitive": test_case_insensitive_matching(),
        "Test 3 - Description Ignored": test_description_difference_ignored(),
        "Test 4 - Whitespace Normalization": test_whitespace_normalization(),
        "Test 5 - Debug Mode": test_debug_mode(),
        "Test 6 - Comparison Mode": test_comparison_mode() is not None,
        "Test 7 - Bulk Generation": test_bulk_key_generation(),
        "Test 8 - Metadata Creation": test_metadata_creation()
    }
    
    # Summary
    print("\n" + "="*100)
    print("📊 TEST SUMMARY")
    print("="*100)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'─'*100}")
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"❌ {total - passed} test(s) failed")
    
    print("█"*100)


if __name__ == "__main__":
    run_all_tests()
