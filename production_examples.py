#!/usr/bin/env python3
"""
PRODUCTION EXAMPLE: Unified Pipeline Kullanımı
==============================================

Bu örnek, Unified Pipeline'ı gerçek kodda nasıl kullanacağınızı gösterir.
"""

import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.unified_analysis_pipeline import UnifiedAnalysisPipeline


def example_1_single_incident():
    """
    Örnek 1: Tek incident analiz
    """
    print("\n" + "="*100)
    print("ÖRNEK 1: Tek Incident Analiz")
    print("="*100 + "\n")
    
    # Pipeline oluştur
    pipeline = UnifiedAnalysisPipeline(use_rag=True, use_cache=True)
    
    # Incident data
    incident = {
        "ref_no": "PRD-INC-2026-001",
        "reported_by": "Operator Ali",
        "date_time": "10:30",
        "description": """
KAZA RAPORU - MAKİNE ARIZASI VE YANGINI
=======================================

Saat 10:30'da elektrik motor arızası nedeniyle makine yanmaya başlamıştır.
Personel motor soğutma sisteminin arızalı olduğunu fark etmiş, hızlıca sistem
kapatmış ve söndürme tozu kullanarak yangını kontrol altına almıştır.

Hasarlar:
- Motor başarısız
- Koruma korkuluğu kısmen hasar gördü
- Elektrik kabloları erimiş
""",
        "injury_description": "Kişisel yaralanma yok, ekipman hasarı"
    }
    
    print(f"📋 Incident: {incident['ref_no']}")
    print(f"👤 Reported by: {incident['reported_by']}")
    print(f"🕐 Time: {incident['date_time']}\n")
    
    # Analiz yap
    print("⏳ Analyzing... (ilk kez API'ye gidecek)")
    result = pipeline.analyze_incident(incident)
    
    # Sonuçları göster
    print(f"\n✅ Analysis Complete")
    print(f"   Source: {result.get('source')} (API from OpenRouter)")
    print(f"   Cached: {result.get('cached')}")
    print(f"   Timestamp: {result.get('timestamp')}")
    
    # Çıktı dosyaları
    print(f"\n📁 Generated Files:")
    output_dir = Path("outputs/unified_pipeline")
    if output_dir.exists():
        for f in sorted(output_dir.glob(f"*{incident['ref_no']}*"))[:2]:
            print(f"   ✅ {f.name}")


def example_2_batch_processing():
    """
    Örnek 2: Batch processing (haftalık incidents)
    """
    print("\n" + "="*100)
    print("ÖRNEK 2: Batch Processing (Haftalık Incidents)")
    print("="*100 + "\n")
    
    # Pipeline oluştur
    pipeline = UnifiedAnalysisPipeline(use_rag=True, use_cache=True)
    
    # Hafta boyunca alınan incidents
    incidents = [
        {
            "ref_no": "WEEK-MON-001",
            "reported_by": "Vardiya 1",
            "description": "Pompa arızası - yağ sızıntısı nedeniyle yangın",
            "injury_description": "Hafif yanık - ilk yardım uygulandı"
        },
        {
            "ref_no": "WEEK-MON-002",
            "reported_by": "Vardiya 1",
            "description": "Elektrik panosu kısa devre - elektrik yangını",
            "injury_description": "Kişisel yaralanma yok"
        },
        {
            "ref_no": "WEEK-TUE-001",
            "reported_by": "Vardiya 2",
            "description": "Pompa arızası - yağ sızıntısı nedeniyle yangın",  # TEKRAR!
            "injury_description": "Hafif yanık - ilk yardım uygulandı"
        },
        {
            "ref_no": "WEEK-THU-001",
            "reported_by": "Vardiya 3",
            "description": "Elektrik panosu kısa devre - elektrik yangını",  # TEKRAR!
            "injury_description": "Kişisel yaralanma yok"
        }
    ]
    
    print(f"📋 Processing {len(incidents)} incidents from the week\n")
    
    results = []
    for i, incident in enumerate(incidents, 1):
        print(f"[{i}/{len(incidents)}] {incident['ref_no']}", end="")
        
        # Analiz yap (cache otomatik çalışacak)
        result = pipeline.analyze_incident(incident)
        results.append(result)
        
        source = result.get('source')
        print(f" → {source.upper()}")
    
    # İstatistikler
    print(f"\n📊 Statistics:")
    cache_hits = sum(1 for r in results if r.get('cached'))
    cache_misses = len(results) - cache_hits
    
    print(f"   Total: {len(results)}")
    print(f"   Cache Hits: {cache_hits}")
    print(f"   Cache Misses: {cache_misses}")
    print(f"   Hit Rate: {cache_hits/len(results)*100:.1f}%")
    
    # Maliyet
    print(f"\n💰 Cost Analysis:")
    normal_cost = len(results) * 0.31
    cache_cost = cache_misses * 0.31
    saved = normal_cost - cache_cost
    
    print(f"   Without Cache: {len(results)} × $0.31 = ${normal_cost:.2f}")
    print(f"   With Cache: {cache_misses} × $0.31 = ${cache_cost:.2f}")
    print(f"   Saved: ${saved:.2f} ({saved/normal_cost*100:.0f}%)")


def example_3_custom_usage():
    """
    Örnek 3: Özel kullanım - Cache statistics'i takip et
    """
    print("\n" + "="*100)
    print("ÖRNEK 3: Cache Statistics Takibi")
    print("="*100 + "\n")
    
    # Pipeline oluştur
    pipeline = UnifiedAnalysisPipeline(use_rag=True, use_cache=True)
    
    # İstatistikleri başlangıçta al
    print("📈 Starting cache stats:")
    stats_before = pipeline.cache.get_stats()
    for key, value in stats_before.items():
        print(f"   {key}: {value}")
    
    # Birkaç test incident
    test_incidents = [
        {"ref_no": "STAT-001", "description": "Test incident 1"},
        {"ref_no": "STAT-002", "description": "Test incident 2"},
        {"ref_no": "STAT-001", "description": "Test incident 1"},  # TEKRAR
    ]
    
    print(f"\n🔄 Processing {len(test_incidents)} incidents:\n")
    
    for incident in test_incidents:
        print(f"Processing {incident['ref_no']}...", end="")
        result = pipeline.analyze_incident(incident)
        source = result.get('source')
        cached = result.get('cached')
        
        if cached:
            print(f" ✅ CACHE HIT (${0.31} saved)")
        else:
            print(f" → API")
    
    # İstatistikleri sonra al
    print(f"\n📈 Final cache stats:")
    stats_after = pipeline.cache.get_stats()
    for key, value in stats_after.items():
        print(f"   {key}: {value}")
    
    # Farklılık göster
    print(f"\n📊 Improvement:")
    hits_before = int(stats_before['cache_hits'].split()[0]) if isinstance(stats_before['cache_hits'], str) else 0
    hits_after = stats_after['cache_hits']
    print(f"   New cache hits: {hits_after - hits_before}")
    print(f"   Total money saved: {stats_after['money_saved']}")


def example_4_error_handling():
    """
    Örnek 4: Error handling
    """
    print("\n" + "="*100)
    print("ÖRNEK 4: Error Handling")
    print("="*100 + "\n")
    
    # Pipeline oluştur
    pipeline = UnifiedAnalysisPipeline(use_rag=True, use_cache=True)
    
    # Test 1: Empty incident
    print("Test 1: Empty incident")
    try:
        result = pipeline.analyze_incident({})
        if "error" in result:
            print(f"   ✅ Handled gracefully: {result.get('error')}")
    except Exception as e:
        print(f"   ⚠️ Exception caught: {e}")
    
    # Test 2: Missing fields
    print("\nTest 2: Minimal incident (missing fields)")
    try:
        result = pipeline.analyze_incident({"ref_no": "MIN-001"})
        if "error" in result:
            print(f"   ✅ Handled: {result.get('error')}")
    except Exception as e:
        print(f"   ⚠️ Exception caught: {e}")
    
    # Test 3: Valid incident
    print("\nTest 3: Valid incident (should work)")
    try:
        result = pipeline.analyze_incident({
            "ref_no": "VALID-001",
            "description": "Valid incident for testing"
        })
        print(f"   ✅ Analysis result: {result.get('source', 'unknown')}")
    except Exception as e:
        print(f"   ⚠️ Exception caught: {e}")


def main():
    """
    Production examples
    """
    print("\n" + "="*100)
    print("🚀 UNIFIED PIPELINE PRODUCTION EXAMPLES")
    print("="*100)
    
    print("""
Bu örnekler, Unified Pipeline'ı gerçek dünya senaryolarında 
nasıl kullanacağınızı gösterir.

Tamamlanan örnekler:
1. Tek incident analizi
2. Batch processing (haftalık)
3. Cache statistics takibi
4. Error handling
    """)
    
    input_choice = input("Çalıştırmak istediğiniz örneği seçin (1-4 veya 'all'): ").strip().lower()
    
    if input_choice == '1' or input_choice == 'all':
        try:
            example_1_single_incident()
        except KeyboardInterrupt:
            print("\n⏹️ Example 1 cancelled")
        except Exception as e:
            print(f"\n❌ Example 1 error: {e}")
            import traceback
            traceback.print_exc()
    
    if input_choice == '2' or input_choice == 'all':
        example_2_batch_processing()
    
    if input_choice == '3' or input_choice == 'all':
        example_3_custom_usage()
    
    if input_choice == '4' or input_choice == 'all':
        example_4_error_handling()
    
    print("\n" + "="*100)
    print("✅ Examples Complete!")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
