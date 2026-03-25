"""
TEST SCRIPT: Unified Analysis Pipeline with Caching
=====================================================

Kullanım:
  python test_unified_pipeline.py single    # Tek olay testi
  python test_unified_pipeline.py batch     # Batch test (cache test)
  python test_unified_pipeline.py cache     # Cache hit/miss testi
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.unified_analysis_pipeline import (
    UnifiedAnalysisPipeline,
    get_sample_incident_1,
    get_sample_incident_2
)


def test_single_incident():
    """
    TEST 1: Tek olay analizi
    - Yeni analiz yapılır (API'ye gider)
    - JSON sonucu kaydedilir
    - DOCX raporu üretilir
    """
    
    print("\n" + "="*100)
    print("🧪 TEST 1: SINGLE INCIDENT ANALYSIS (WITH RAG + CACHE)")
    print("="*100 + "\n")
    
    pipeline = UnifiedAnalysisPipeline(use_rag=True, use_cache=True)
    
    incident = get_sample_incident_1()
    
    print(f"📋 Incident: {incident.get('ref_no')}")
    print(f"📝 Description: {incident.get('description')[:100]}...\n")
    
    result = pipeline.analyze_incident(incident)
    
    print("\n" + "="*100)
    print("✅ ANALYSIS COMPLETE")
    print("="*100)
    print(f"Source: {result.get('source')}")
    print(f"Timestamp: {result.get('timestamp')}")
    print()


def test_cache_hit_miss():
    """
    TEST 2: Cache Hit/Miss testi
    - Aynı olay 2x analiz ediliyor
    - İlki: API'ye gider (miss)
    - İkinci: Cache'den gelir (hit)
    """
    
    print("\n" + "="*100)
    print("🧪 TEST 2: CACHE HIT/MISS TEST (WITH RAG)")
    print("="*100 + "\n")
    
    pipeline = UnifiedAnalysisPipeline(use_rag=True, use_cache=True)
    
    incident = get_sample_incident_1()
    
    # İlk çalıştırma
    print("🔄 FIRST RUN (Expected: Miss → API)")
    print("─"*100)
    result1 = pipeline.analyze_incident(incident)
    source1 = result1.get('source')
    print(f"Result Source: {source1}\n")
    
    # İkinci çalıştırma (AYNI olay)
    print("\n🔄 SECOND RUN (Expected: Hit → Cache)")
    print("─"*100)
    result2 = pipeline.analyze_incident(incident)
    source2 = result2.get('source')
    print(f"Result Source: {source2}\n")
    
    # Doğrulama
    print("\n" + "="*100)
    print("✅ CACHE TEST RESULT")
    print("="*100)
    
    if source1 == 'api' and source2 == 'cache':
        print("✅ CACHE WORKS CORRECTLY!")
        print("   First run: API (miss)")
        print("   Second run: Cache (hit)")
        print(f"   Cost saved: $0.31")
    else:
        print("❌ CACHE TEST FAILED!")
        print(f"   First run: {source1} (expected: api)")
        print(f"   Second run: {source2} (expected: cache)")
    
    print()


def test_batch_with_repeats():
    """
    TEST 3: Batch analiz - Cache hit oranını test et
    - 3 olay analiz edilir
    - 2 yeni + 1 tekrar (cache hit test)
    """
    
    print("\n" + "="*100)
    print("🧪 TEST 3: BATCH ANALYSIS WITH CACHE HITS (WITH RAG)")
    print("="*100 + "\n")
    
    pipeline = UnifiedAnalysisPipeline(use_rag=True, use_cache=True)
    
    incident1 = get_sample_incident_1()
    incident2 = get_sample_incident_2()
    
    # Batch: [Yeni, Yeni, Tekrar]
    incidents = [
        incident1,                      # Yeni
        incident2,                      # Yeni
        incident1,                      # Tekrar! (cache hit beklentisi)
    ]
    
    results = pipeline.batch_analyze(incidents)
    
    print("\n" + "="*100)
    print("📊 BATCH RESULTS ANALYSIS")
    print("="*100 + "\n")
    
    for i, result in enumerate(results, 1):
        ref = result.get('incident_ref', f'Incident {i}')
        source = result.get('source', 'unknown')
        cached = result.get('cached', False)
        print(f"Incident {i}: {ref}")
        print(f"  Source: {source}")
        print(f"  Cached: {cached}")
        print()


def main():
    """
    Ana test fonksiyonu
    """
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == 'single':
            test_single_incident()
        elif test_type == 'cache':
            test_cache_hit_miss()
        elif test_type == 'batch':
            test_batch_with_repeats()
        else:
            print(f"Unknown test type: {test_type}")
            print("Valid options: single, cache, batch")
    else:
        # Varsayılan: Hepsi çalıştır
        test_single_incident()
        test_cache_hit_miss()
        test_batch_with_repeats()


if __name__ == "__main__":
    main()
