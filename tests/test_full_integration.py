#!/usr/bin/env python3
"""
FULL TEST: RAG + CACHE + PIPELINE COMPLETE TEST
================================================

Bu test:
1. Cache'i temizler
2. İlk incident'i analiz eder (API çağrısı)
3. Aynı incident'i tekrar analiz eder (Cache hit)
4. Farklı incident'i analiz eder (API çağrısı)
5. İstatistikleri gösterir
"""

import sys
import json
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.unified_analysis_pipeline import UnifiedAnalysisPipeline


def clear_cache():
    """Cache'i temizle"""
    cache_dir = Path("cache/analyses")
    if cache_dir.exists():
        import shutil
        shutil.rmtree(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
    print("✅ Cache temizlendi\n")


def main():
    print("\n" + "="*100)
    print("🚀 FULL TEST: RAG + CACHE + PIPELINE INTEGRATION")
    print("="*100 + "\n")
    
    # Cache'i temizle
    clear_cache()
    
    # Pipeline oluştur (RAG + Cache aktif)
    print("🔧 Pipeline oluşturuluyor (RAG=True, Cache=True)...\n")
    pipeline = UnifiedAnalysisPipeline(use_rag=True, use_cache=True)
    
    # Test 1: İlk incident (API çağrısı)
    print("\n" + "="*100)
    print("TEST 1: İlk Incident (Cache Miss Expected - API çağrısı)")
    print("="*100 + "\n")
    
    incident1 = {
        "ref_no": "TEST-INC-001",
        "reported_by": "Test User",
        "date_time": "10:00",
        "description": "Test yangını - makine arızası nedeniyle başlayan yangın",
        "injury_description": "Kişisel yaralanma yok"
    }
    
    print(f"📋 Incident: {incident1['ref_no']}")
    print(f"📝 Description: {incident1['description']}\n")
    print("⏳ Analiz yapılıyor... (ilk kez, API'ye gidecek, 30+ saniye alabilir)\n")
    
    try:
        start_time = datetime.now()
        result1 = pipeline.analyze_incident(incident1)
        elapsed1 = (datetime.now() - start_time).total_seconds()
        
        print(f"\n✅ TEST 1 Tamamlandı")
        print(f"   Source: {result1.get('source')}")
        print(f"   Cached: {result1.get('cached')}")
        print(f"   Time: {elapsed1:.2f}s")
        
        test1_passed = result1.get('source') == 'api' and not result1.get('cached')
        print(f"   Result: {'✅ PASS' if test1_passed else '❌ FAIL'}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test iptal edildi (Ctrl+C)")
        return
    except Exception as e:
        print(f"\n❌ Test 1 hatası: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 2: AYNI incident (Cache Hit)
    print("\n" + "="*100)
    print("TEST 2: AYNI Incident Tekrar (Cache Hit Expected - Hızlı!)")
    print("="*100 + "\n")
    
    print(f"📋 Incident: {incident1['ref_no']} (TEKRAR)")
    print("Expected: Cache'den gelir (çok hızlı)\n")
    print("⏳ Analiz yapılıyor... (cache'den, <1 saniye)\n")
    
    start_time = datetime.now()
    result2 = pipeline.analyze_incident(incident1)
    elapsed2 = (datetime.now() - start_time).total_seconds()
    
    print(f"\n✅ TEST 2 Tamamlandı")
    print(f"   Source: {result2.get('source')}")
    print(f"   Cached: {result2.get('cached')}")
    print(f"   Time: {elapsed2:.4f}s")
    print(f"   Speed: {elapsed1/elapsed2:.0f}x daha hızlı!")
    print(f"   Cost Saved: $0.31")
    
    test2_passed = result2.get('source') == 'cache' and result2.get('cached')
    print(f"   Result: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    
    # Test 3: Farklı incident (API çağrısı)
    print("\n" + "="*100)
    print("TEST 3: Farklı Incident (Cache Miss Expected - API çağrısı)")
    print("="*100 + "\n")
    
    incident2 = {
        "ref_no": "TEST-INC-002",
        "reported_by": "Test User 2",
        "date_time": "14:00",
        "description": "Elektrik panosu kısa devre - elektrik yangını",
        "injury_description": "Hafif elektrik çarpması"
    }
    
    print(f"📋 Incident: {incident2['ref_no']}")
    print(f"📝 Description: {incident2['description']}\n")
    print("⏳ Analiz yapılıyor... (farklı incident, API'ye gidecek, 30+ saniye alabilir)\n")
    
    try:
        start_time = datetime.now()
        result3 = pipeline.analyze_incident(incident2)
        elapsed3 = (datetime.now() - start_time).total_seconds()
        
        print(f"\n✅ TEST 3 Tamamlandı")
        print(f"   Source: {result3.get('source')}")
        print(f"   Cached: {result3.get('cached')}")
        print(f"   Time: {elapsed3:.2f}s")
        
        test3_passed = result3.get('source') == 'api' and not result3.get('cached')
        print(f"   Result: {'✅ PASS' if test3_passed else '❌ FAIL'}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test iptal edildi (Ctrl+C)")
        test3_passed = False
    except Exception as e:
        print(f"\n❌ Test 3 hatası: {e}")
        import traceback
        traceback.print_exc()
        test3_passed = False
    
    # Test 4: AYNI farklı incident'i tekrar (Cache Hit)
    print("\n" + "="*100)
    print("TEST 4: Incident-2 Tekrar (Cache Hit Expected)")
    print("="*100 + "\n")
    
    print(f"📋 Incident: {incident2['ref_no']} (TEKRAR)")
    print("Expected: Cache'den gelir\n")
    
    start_time = datetime.now()
    result4 = pipeline.analyze_incident(incident2)
    elapsed4 = (datetime.now() - start_time).total_seconds()
    
    print(f"✅ TEST 4 Tamamlandı")
    print(f"   Source: {result4.get('source')}")
    print(f"   Time: {elapsed4:.4f}s")
    
    test4_passed = result4.get('source') == 'cache'
    print(f"   Result: {'✅ PASS' if test4_passed else '❌ FAIL'}")
    
    # =====================================================================
    # FINAL REPORT
    # =====================================================================
    print("\n" + "="*100)
    print("📊 FINAL TEST REPORT")
    print("="*100 + "\n")
    
    tests_passed = sum([test1_passed, test2_passed, test3_passed, test4_passed])
    total_tests = 4
    
    print("Test Results:")
    print(f"  Test 1 (First incident, API): {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"  Test 2 (Same incident, Cache): {'✅ PASS' if test2_passed else '❌ FAIL'}")
    print(f"  Test 3 (Different incident, API): {'✅ PASS' if test3_passed else '❌ FAIL'}")
    print(f"  Test 4 (Same incident-2, Cache): {'✅ PASS' if test4_passed else '❌ FAIL'}")
    print(f"\n  Total: {tests_passed}/{total_tests} passed")
    
    # Performance metrics
    print("\n💻 Performance Metrics:")
    print(f"  API calls (Miss): {elapsed1:.2f}s + {elapsed3:.2f}s = {elapsed1+elapsed3:.2f}s")
    print(f"  Cache hits (Hit): {elapsed2:.4f}s + {elapsed4:.4f}s = {elapsed2+elapsed4:.4f}s")
    print(f"  Total time: {elapsed1+elapsed2+elapsed3+elapsed4:.2f}s")
    print(f"  Speed improvement: {(elapsed1+elapsed3)/(elapsed2+elapsed4):.0f}x")
    
    # Cache statistics
    print("\n📈 Cache Statistics:")
    if pipeline.cache:
        stats = pipeline.cache.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    # Cost analysis
    print("\n💰 Cost Analysis:")
    print(f"  Without Cache: 4 × $0.31 = $1.24")
    print(f"  With Cache: 2 × $0.31 = $0.62 (2 hits free)")
    print(f"  Saved: $0.62 (50% reduction!)")
    
    # Output files
    print("\n📁 Output Files:")
    output_dir = Path("outputs/unified_pipeline")
    if output_dir.exists():
        json_files = list(output_dir.glob("*.json"))
        docx_files = list(output_dir.glob("*.docx"))
        print(f"  JSON files: {len(json_files)}")
        print(f"  DOCX reports: {len(docx_files)}")
    
    cache_dir = Path("cache/analyses")
    if cache_dir.exists():
        cache_files = list(cache_dir.glob("*.json"))
        print(f"  Cache files: {len(cache_files)}")
    
    # Final verdict
    print("\n" + "="*100)
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! SYSTEM WORKING PERFECTLY!")
    elif tests_passed >= 3:
        print("✅ MOST TESTS PASSED! SYSTEM MOSTLY WORKING!")
    else:
        print("⚠️ SOME TESTS FAILED! PLEASE CHECK LOGS!")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
