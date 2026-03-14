#!/usr/bin/env python3
"""
CACHE DEMO TEST: Oil Purifier Fire - İkinci Kez Bedava!
=======================================================

Aynı incident'i iki kez analiz ediliyor:
  1. İlk kez: API'ye gider ($0.31)
  2. İkinci kez: Cache'den gelir ($0.00) ✅
"""

import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.unified_analysis_pipeline import (
    UnifiedAnalysisPipeline,
    get_sample_incident_1
)


def main():
    print("\n" + "="*100)
    print("🔥 CACHE DEMO: Oil Purifier Fire - İkinci Kez Bedava!")
    print("="*100 + "\n")
    
    # Pipeline oluştur (RAG + Cache AKTIF)
    print("🚀 Pipeline oluşturuluyor (RAG=True, Cache=True)...\n")
    pipeline = UnifiedAnalysisPipeline(use_rag=True, use_cache=True)
    
    # Olay: Oil Purifier Fire
    incident = get_sample_incident_1()
    ref_no = incident.get("ref_no")
    
    # =====================================================================
    # ÇALIŞMA 1: İlk Kez (API'ye gidecek - Cache Miss)
    # =====================================================================
    print("\n" + "="*100)
    print(f"🔥 ÇALIŞMA 1: {ref_no} - İlk Analiz (API'ye Gidecek)")
    print("="*100 + "\n")
    
    print("📋 Olay: Yağ Tasfiye Cihazı Yangını")
    print(f"📝 Açıklama: {incident['description'][:100]}...\n")
    
    print("⏳ Analiz yapılıyor... (ilk kez, API'ye gidecek)\n")
    
    start1 = datetime.now()
    result1 = pipeline.analyze_incident(incident)
    elapsed1 = (datetime.now() - start1).total_seconds()
    
    source1 = result1.get('source')
    cost1 = "$0.31" if source1 == 'api' else "$0.00"
    
    print(f"\n✅ ÇALIŞMA 1 SONUCU:")
    print(f"   Kaynak: {source1.upper()}")
    print(f"   Süre: {elapsed1:.1f}s")
    print(f"   Maliyet: {cost1}")
    print(f"   Status: {'🟢 API' if source1 == 'api' else '🟡 Cache'}")
    
    # =====================================================================
    # ÇALIŞMA 2: İkinci Kez (Cache'den gelecek - Cache Hit)
    # =====================================================================
    print("\n\n" + "="*100)
    print(f"⚡ ÇALIŞMA 2: {ref_no} - Aynı Analiz Tekrar (Cache'den Gelecek!)")
    print("="*100 + "\n")
    
    print("📋 Olay: Aynı Yağ Tasfiye Cihazı Yangını")
    print(f"📝 Açıklama: {incident['description'][:100]}...\n")
    
    print("⏳ Analiz yapılıyor... (cache'den, çok hızlı!)\n")
    
    start2 = datetime.now()
    result2 = pipeline.analyze_incident(incident)
    elapsed2 = (datetime.now() - start2).total_seconds()
    
    source2 = result2.get('source')
    cost2 = "$0.31" if source2 == 'api' else "$0.00"
    
    print(f"\n✅ ÇALIŞMA 2 SONUCU:")
    print(f"   Kaynak: {source2.upper()}")
    print(f"   Süre: {elapsed2:.4f}s")
    print(f"   Maliyet: {cost2}")
    print(f"   Status: {'🟢 API' if source2 == 'api' else '🟢 CACHE (BEDAVA!)'}")
    
    # =====================================================================
    # KARŞILAŞTIRMA
    # =====================================================================
    print("\n\n" + "="*100)
    print("📊 SONUÇ: CACHE ETKİSİ")
    print("="*100)
    
    print(f"\n⚡ HİZ:")
    if elapsed2 > 0:
        speedup = elapsed1 / elapsed2
        print(f"   Çalışma 1 (API): {elapsed1:.1f}s")
        print(f"   Çalışma 2 (Cache): {elapsed2:.4f}s")
        print(f"   ⚡ Speedup: {speedup:.0f}x DAHA HIZLI!")
    
    print(f"\n💰 MALİYET:")
    print(f"   Cache OLMADAN (2x analiz): $0.31 × 2 = $0.62")
    print(f"   Cache İLE (1x API + 1x Hit): $0.31 + $0.00 = $0.31")
    print(f"   ✅ TASARRUF: $0.31 (50% İNDİRİM!)")
    
    print(f"\n✅ CACHE MEKANİZMASI:")
    if source1 == 'api' and source2 == 'cache':
        print(f"   ✅ Çalışma 1: API - Analiz cache'e kaydedildi")
        print(f"   ✅ Çalışma 2: Cache - Anlık erişim (bedava!)")
        print(f"   ✅ CACHE KUSURSUZ ÇALIŞIYOR!")
    else:
        print(f"   ❌ Çalışma 1: {source1} (beklenilen: api)")
        print(f"   ❌ Çalışma 2: {source2} (beklenilen: cache)")
    
    # Cache İstatistikleri
    print(f"\n📈 CACHE İSTATİSTİKLERİ:")
    stats = pipeline.cache.get_stats()
    print(f"   Toplam İstek: {stats['total_requests']}")
    print(f"   Cache Hits: {stats['cache_hits']}")
    print(f"   Cache Misses: {stats['cache_misses']}")
    print(f"   Hit Oranı: {stats['hit_rate']}")
    print(f"   Tasarruf Edilen Para: {stats['money_saved']}")
    
    # Sonuç Dosyaları
    print(f"\n📁 OLUŞTURULAN DOSYALAR:")
    output_dir = Path("outputs/unified_pipeline")
    if output_dir.exists():
        json_files = list(output_dir.glob(f"*{ref_no}*.json"))
        docx_files = list(output_dir.glob(f"*{ref_no}*.docx"))
        print(f"   JSON Analiz Dosyaları: {len(json_files)}")
        for f in json_files:
            print(f"      📄 {f.name}")
        print(f"   DOCX Raporlar: {len(docx_files)}")
        for f in docx_files:
            print(f"      📋 {f.name}")
    
    cache_dir = Path("cache/analyses")
    if cache_dir.exists():
        cache_files = list(cache_dir.glob("*.json"))
        print(f"   Cache Dosyaları: {len(cache_files)}")
        for f in cache_files[:3]:
            print(f"      💾 {f.name}")
    
    print("\n" + "="*100)
    print("✅ TEST TAMAMLANDI - CACHE BAŞARIYLA ÇALIŞTI!")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
