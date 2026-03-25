#!/usr/bin/env python3
"""
QUICK CACHE TEST - RAG + Cache
==============================
Sadece cache mekanizmasını test et.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.unified_analysis_pipeline import AnalysisCache

# Test incident
incident = {
    "ref_no": "TEST-001",
    "description": "Test cache mechanism with RAG"
}

print("="*100)
print("🧪 CACHE TEST: RAG + Cache Mekanizması")
print("="*100)

# Cache manager oluştur
cache = AnalysisCache()
print("\n✅ Cache manager oluşturuldu")
print(f"   Cache dir: {cache.cache_dir}\n")

# Test 1: Cache'de yoksa
print("TEST 1: Cache'de YOK (Miss Expected)")
print("─"*100)
result = cache.get(incident)
if result is None:
    print("✅ Expected: Cache miss → result is None")
else:
    print("❌ Unexpected: Cache hit")

print(f"\nCache stats: {cache.get_stats()}\n")

# Test 2: Cache'e kaydet
print("TEST 2: Cache'e Kaydet")
print("─"*100)
dummy_analysis = {
    "overview": {"incident_type": "Equipment Damage"},
    "assessment": {"severity": "High"},
    "root_cause": {"code": "D5.7", "name": "HAZOP Eksik"}
}

success = cache.set(incident, dummy_analysis)
if success:
    print("✅ Analiz cache'e kaydedildi")
else:
    print("❌ Cache yazma başarısız")

print(f"\nCache stats: {cache.get_stats()}\n")

# Test 3: Cache'den oku (Hit Expected)
print("TEST 3: Cache'den Oku (Hit Expected)")
print("─"*100)
result = cache.get(incident)
if result is not None:
    print("✅ Cache hit! Sonuç cache'den alındı")
    print(f"   Timestamp: {result.get('timestamp')}")
    print(f"   Incident: {result.get('incident_ref')}")
else:
    print("❌ Unexpected: Cache miss")

print(f"\nCache stats: {cache.get_stats()}\n")

# Test 4: Farklı incident (Miss Expected)
print("TEST 4: Farklı Incident (Miss Expected)")
print("─"*100)
different_incident = {
    "ref_no": "TEST-002",
    "description": "Different incident to test hash differentiation"
}

result = cache.get(different_incident)
if result is None:
    print("✅ Expected: Cache miss → Different incident, different hash")
else:
    print("❌ Unexpected: Cache hit")

print(f"\nCache stats: {cache.get_stats()}\n")

# Final stats
print("="*100)
print("📊 FINAL CACHE STATISTICS")
print("="*100)
final_stats = cache.get_stats()
for key, value in final_stats.items():
    print(f"{key:20s}: {value}")

print("\n" + "="*100)
print("✅ CACHE TEST TAMAMLANDI")
print("="*100)
