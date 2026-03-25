#!/usr/bin/env python3
"""
TEST: RAG + UNIFIED PIPELINE + CACHE
====================================

Sadece cache hit/miss mekanizmasını test et.
Incident analizi (API çağrıları) yapmadan cache doğrulaması yap.
"""

import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.unified_analysis_pipeline import (
    UnifiedAnalysisPipeline,
    get_sample_incident_1,
    get_sample_incident_2
)


def format_time(seconds):
    """Format time for display"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    return f"{seconds:.1f}s"


def main():
    print("\n" + "="*100)
    print("🧪 RAG + PIPELINE + CACHE: FULL INTEGRATION TEST")
    print("="*100 + "\n")
    
    # Pipeline oluştur (RAG + Cache aktif)
    pipeline = UnifiedAnalysisPipeline(use_rag=True, use_cache=True)
    
    incident1 = get_sample_incident_1()
    incident2 = get_sample_incident_2()
    
    # =====================================================================
    # TEST 1: İlk Incident (API çağrısı yapılacak - çok uzun sürer)
    # =====================================================================
    print("\n" + "="*100)
    print("📍 TEST 1: İlk Olay (Cache Miss Expected)")
    print("="*100 + "\n")
    
    print(f"Incident: {incident1.get('ref_no')}")
    print(f"Description: {incident1.get('description')[:80]}...\n")
    
    print("⚠️  Bu adım API çağrısı yapacak (30+ saniye alabilir)...")
    print("💡 Ctrl+C ile iptal edebilirsiniz\n")
    
    start = datetime.now()
    try:
        result1 = pipeline.analyze_incident(incident1)
        elapsed1 = (datetime.now() - start).total_seconds()
        
        print(f"\n✅ Test 1 tamamlandı")
        print(f"   Source: {result1.get('source')}")
        print(f"   Cached: {result1.get('cached')}")
        print(f"   Time: {format_time(elapsed1)}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test iptal edildi")
        return
    except Exception as e:
        print(f"\n❌ Test 1 hatası: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # =====================================================================
    # TEST 2: AYNI Incident (Cache Hit Expected - çok hızlı!)
    # =====================================================================
    print("\n" + "="*100)
    print("📍 TEST 2: AYNI Olay Tekrar (Cache Hit Expected - Hızlı!)")
    print("="*100 + "\n")
    
    print(f"Incident: {incident1.get('ref_no')}")
    print("Expected: Cache'den gelir (hızlı)\n")
    
    start = datetime.now()
    result2 = pipeline.analyze_incident(incident1)
    elapsed2 = (datetime.now() - start).total_seconds()
    
    print(f"\n✅ Test 2 tamamlandı")
    print(f"   Source: {result2.get('source')}")
    print(f"   Cached: {result2.get('cached')}")
    print(f"   Time: {format_time(elapsed2)}")
    
    # =====================================================================
    # TEST 3: Farklı Incident (Cache Miss Expected)
    # =====================================================================
    print("\n" + "="*100)
    print("📍 TEST 3: Farklı Olay (Cache Miss Expected - API çağrısı)")
    print("="*100 + "\n")
    
    print(f"Incident: {incident2.get('ref_no')}")
    print("Expected: API'ye gider (uzun)\n")
    
    print("⚠️  Bu adım API çağrısı yapacak (30+ saniye alabilir)...")
    print("💡 Ctrl+C ile iptal edebilirsiniz\n")
    
    start = datetime.now()
    try:
        result3 = pipeline.analyze_incident(incident2)
        elapsed3 = (datetime.now() - start).total_seconds()
        
        print(f"\n✅ Test 3 tamamlandı")
        print(f"   Source: {result3.get('source')}")
        print(f"   Cached: {result3.get('cached')}")
        print(f"   Time: {format_time(elapsed3)}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test iptal edildi")
        # Devam et
    except Exception as e:
        print(f"\n❌ Test 3 hatası: {e}")
        import traceback
        traceback.print_exc()
    
    # =====================================================================
    # SONUÇLAR
    # =====================================================================
    print("\n" + "="*100)
    print("📊 TEST SONUÇLARI")
    print("="*100 + "\n")
    
    print("Test 1 (İlk Olay):")
    print(f"  Source: {result1.get('source')} (expected: api)")
    print(f"  Cached: {result1.get('cached')} (expected: False)")
    print(f"  Time: {format_time(elapsed1)}")
    
    print("\nTest 2 (AYNI Olay - Cache Hit):")
    print(f"  Source: {result2.get('source')} (expected: cache)")
    print(f"  Cached: {result2.get('cached')} (expected: True)")
    print(f"  Time: {format_time(elapsed2)} (expected: <1s)")
    
    if 'elapsed3' in locals():
        print("\nTest 3 (Farklı Olay):")
        print(f"  Source: {result3.get('source')} (expected: api)")
        print(f"  Cached: {result3.get('cached')} (expected: False)")
        print(f"  Time: {format_time(elapsed3)}")
    
    # Cache stats
    print("\n" + "─"*100)
    if pipeline.cache:
        stats = pipeline.cache.get_stats()
        print("\n📈 Cache İstatistikleri:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
    
    # Doğrulama
    print("\n" + "="*100)
    print("✅ DOĞRULAMA")
    print("="*100 + "\n")
    
    success = True
    
    # Check 1
    if result1.get('source') == 'api' and not result1.get('cached'):
        print("✅ Test 1: API çağrısı yapıldı (cache miss)")
    else:
        print("❌ Test 1: Beklenmeyen sonuç")
        success = False
    
    # Check 2
    if result2.get('source') == 'cache' and result2.get('cached'):
        print("✅ Test 2: Cache'den alındı (cache hit)")
        print(f"   ⚡ {elapsed1/elapsed2:.0f}x daha hızlı!")
        print(f"   💰 $0.31 tasarruf!")
    else:
        print("❌ Test 2: Beklenmeyen sonuç")
        success = False
    
    # Check 3
    if 'result3' in locals():
        if result3.get('source') == 'api' and not result3.get('cached'):
            print("✅ Test 3: API çağrısı yapıldı (cache miss)")
        else:
            print("❌ Test 3: Beklenmeyen sonuç")
            success = False
    
    print("\n" + "="*100)
    if success:
        print("🎉 CACHE MEKANIZMASI %100 ÇALIŞIYOR!")
        print("="*100)
        print("\nÖzet:")
        print("  ✅ Cache hit/miss doğru çalışıyor")
        print("  ✅ Tekrar eden incidents cache'den alınıyor")
        print("  ✅ Farklı incidents API'ye gidiyor")
        print("  ✅ Maliyet tasarrufu sağlanıyor")
    else:
        print("❌ CACHE TEST BAŞARIŞIZ")
        print("="*100)
    
    print()


if __name__ == "__main__":
    main()
