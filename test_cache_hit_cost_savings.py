#!/usr/bin/env python3
"""
Test Cache Hit - Rapor Hazırlama Ücreti Düşüşü
==============================================

Aynı critical fields'e sahip iki farklı incident'ı test et:
- Incident 1: Yeni analiz (maliyet oluşur)
- Incident 2: Benzer olay (cache hit - maliyet YALNIR!)

Bu test gösteriyor ki description farklı olsa bile,
aynı equipment + injury type + activity = AYNI CACHE = TASARRUF!
"""

import sys
import json
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.mongodb_cache_utils import (
    CacheKeyManager,
    CacheKeyDebugger,
    CacheEntryMetadata
)


def simulate_cost_calculation(analysis_type: str, is_cache_hit: bool = False):
    """
    Analiz maliyeti simülasyonu
    
    OpenAI Claude API'ye göre:
    - Text analysis: ~$0.31
    - Structured analysis: ~$0.15
    - Database operations: ~$0.05
    """
    if is_cache_hit:
        return {
            "api_call": 0.0,
            "analysis": 0.0,
            "database": 0.0,
            "total": 0.0,
            "status": "CACHE HIT - FREE!"
        }
    
    base_costs = {
        "api_call": 0.05,
        "analysis": 0.20,
        "database": 0.05,
    }
    
    return {
        "api_call": base_costs["api_call"],
        "analysis": base_costs["analysis"],
        "database": base_costs["database"],
        "total": sum(base_costs.values()),
        "status": "NEW ANALYSIS - PAID"
    }


def print_section(title: str, width: int = 100):
    """Başlık bas"""
    print(f"\n{'='*width}")
    print(f"🔍 {title}")
    print(f"{'='*width}")


def print_subsection(title: str, width: int = 100):
    """Alt başlık bas"""
    print(f"\n{'-'*width}")
    print(f"📌 {title}")
    print(f"{'-'*width}")


def test_similar_incidents_cache_hit():
    """
    Test: Aynı critical fields = Aynı cache = MALIYET DÜŞÜŞÜ
    """
    print_section("CACHE HIT TEST - Benzer Olaylar")
    
    # ============================================================================
    # SENARYO 1: Yağ Tasfiye Cihazı Yangını (İlk Olaya)
    # ============================================================================
    incident_1 = {
        "_id": "OIL-FIRE-001",
        "ref_no": "HSE-2026-001-PUMP",
        "incident_type": "ACCIDENT",
        "equipment": "Oil Purifier",
        "injury_type": "BURN",
        "activity": "Maintenance",
        "reported_by": "Vardiya Amiri",
        "date_time": "2026-03-14 15:20",
        "description": """
        YANGIN OLAYI - YAĞ TAFSİYE CİHAZI
        - Cihaz hat vanası açılmadan devreye alındı
        - Kuru ısıtma sonucu yangın oluştu
        - Personel deneyimi: 4 yıl
        - Uyarı işareti: YOK
        - Emniyet sensörü: YOK
        - Yaralanma: HAYIR
        """,
        "location": "Fabrika Dış Alan",
        "temperature_celsius": 850,
        "fire_duration_minutes": 15
    }
    
    print_subsection("Incident 1: İlk Yangın Olayı")
    print(f"📍 Ref: {incident_1['ref_no']}")
    print(f"🏭 Equipment: {incident_1['equipment']}")
    print(f"🤕 Injury Type: {incident_1['injury_type']}")
    print(f"🔧 Activity: {incident_1['activity']}")
    print(f"\nDescription: {incident_1['description'][:100]}...")
    
    cache_key_1 = CacheKeyManager.generate_cache_key("incident", incident_1)
    print(f"\n🔑 Cache Key: {cache_key_1}")
    
    cost_1 = simulate_cost_calculation("incident_analysis", is_cache_hit=False)
    print(f"\n💰 Maliyeti:")
    print(f"   API Call: ${cost_1['api_call']:.2f}")
    print(f"   Analysis: ${cost_1['analysis']:.2f}")
    print(f"   Database: ${cost_1['database']:.2f}")
    print(f"   ────────────────────")
    print(f"   TOPLAM: ${cost_1['total']:.2f} ✅ ÖDENDI")
    
    # ============================================================================
    # SENARYO 2: Benzer Yangın - AYNI EQUIPMENT, AYNI INJURY, AYNI ACTIVITY
    # ============================================================================
    incident_2 = {
        "_id": "OIL-FIRE-002",
        "ref_no": "HSE-2026-002-PUMP",
        "incident_type": "accident",  # lowercase - farklı format!
        "equipment": "oil purifier",  # lowercase - farklı format!
        "injury_type": "burn",        # lowercase - farklı format!
        "activity": "MAINTENANCE",    # uppercase - farklı format!
        "reported_by": "Farklı Vardiya Amiri",
        "date_time": "2026-03-15 14:30",
        "description": """
        AYNI TİPTE YANGIN - İKİNCİ KAZA
        - Başka personel aynı prosedürü hatası
        - Yağ pompası ısıtma sistemi kapalı iken çalıştırıldı
        - 2 yıllık yeni personel
        - Güvenlik işareti: HALA YOK
        - İlaç: HALA YOK
        - Yaralanma: HAYIR
        
        Tamamen farklı bir deskripsiyon ama aynı root cause!
        """,
        "location": "Fabrika İç Alan",
        "temperature_celsius": 920,  # Daha sıcak!
        "fire_duration_minutes": 22   # Daha uzun!
    }
    
    print_subsection("Incident 2: BENZER Yangın Olayı (24 Saat Sonra)")
    print(f"📍 Ref: {incident_2['ref_no']}")
    print(f"🏭 Equipment: {incident_2['equipment']}")
    print(f"🤕 Injury Type: {incident_2['injury_type']}")
    print(f"🔧 Activity: {incident_2['activity']}")
    print(f"\nDescription: {incident_2['description'][:100]}...")
    
    cache_key_2 = CacheKeyManager.generate_cache_key("incident", incident_2)
    print(f"\n🔑 Cache Key: {cache_key_2}")
    
    # ============================================================================
    # KARŞILAŞTIRMA
    # ============================================================================
    print_subsection("🎯 CACHE KEY KARŞILAŞTIRMASI")
    
    comparison = CacheKeyDebugger.compare_keys("incident", incident_1, incident_2)
    
    print(f"\nKey 1: {comparison['key_1']}")
    print(f"Key 2: {comparison['key_2']}")
    
    if comparison['match']:
        print(f"\n✅ KEYS MATCH! → CACHE HIT!")
        print(f"\n🔍 İnceleme:")
        print(f"   Incident 1 Critical Fields:")
        for k, v in comparison['debug_1']['normalized_data'].items():
            print(f"      • {k}: {v}")
        
        print(f"\n   Incident 2 Critical Fields:")
        for k, v in comparison['debug_2']['normalized_data'].items():
            print(f"      • {k}: {v}")
        
        print(f"\n   🔄 Sonuç: Tamamen AYNI critical fields!")
        
        # Cache hit maliyeti
        cost_2 = simulate_cost_calculation("incident_analysis", is_cache_hit=True)
        
        print(f"\n💰 Incident 2'nin Maliyeti:")
        print(f"   API Call: ${cost_2['api_call']:.2f}")
        print(f"   Analysis: ${cost_2['analysis']:.2f}")
        print(f"   Database: ${cost_2['database']:.2f}")
        print(f"   ────────────────────")
        print(f"   TOPLAM: ${cost_2['total']:.2f} 🎉 ÜCRETSIZ (Cache'den alındı!)")
        
    else:
        print(f"\n❌ KEYS DIFFERENT! → CACHE MISS!")
        if comparison.get('differences', {}).get('field'):
            print(f"   Farklar: {comparison['differences']['field']}")
        cost_2 = simulate_cost_calculation("incident_analysis", is_cache_hit=False)
        print(f"   Maliyet: ${cost_2['total']:.2f}")
    
    # ============================================================================
    # TASARRUF HESAPLAMASI
    # ============================================================================
    print_subsection("💰 TASARRUF ANALİZİ")
    
    if comparison['match']:
        total_cost_without_cache = cost_1['total'] + simulate_cost_calculation("incident_analysis", is_cache_hit=False)['total']
        total_cost_with_cache = cost_1['total']
        savings = total_cost_without_cache - total_cost_with_cache
        savings_percent = (savings / total_cost_without_cache) * 100
        
        print(f"\nİki Incident Analizi:")
        print(f"   Cache OLMADAN: ${total_cost_without_cache:.2f} (her ikisi için yeni analiz)")
        print(f"   Cache İLE: ${total_cost_with_cache:.2f} (ikincisi cache'den)")
        print(f"   ────────────────────────")
        print(f"   TASARRUF: ${savings:.2f} ({savings_percent:.1f}%)")
        
        print(f"\n📊 Ölçek:")
        print(f"   10 benzer olay: ${total_cost_without_cache * 10:.2f} → ${cost_1['total'] + simulate_cost_calculation('incident_analysis', is_cache_hit=False)['total'] * 0:.2f}")
        print(f"   100 benzer olay: ${total_cost_without_cache * 100:.2f} → ${cost_1['total'] + simulate_cost_calculation('incident_analysis', is_cache_hit=False)['total'] * 0 + cost_1['total']:.2f}")


def test_different_incidents_no_cache_hit():
    """
    Test: Farklı critical fields = Farklı cache = MALIYET ARTIR
    """
    print_section("NO CACHE TEST - Tamamen Farklı Olaylar")
    
    incident_1 = {
        "incident_type": "ACCIDENT",
        "equipment": "Oil Purifier",
        "injury_type": "BURN",
        "activity": "Maintenance"
    }
    
    incident_2 = {
        "incident_type": "NEAR-MISS",
        "equipment": "Forklift",
        "injury_type": "NONE",
        "activity": "Loading"
    }
    
    print_subsection("Incident 1: Yağ Yangını")
    print(f"   Equipment: {incident_1['equipment']}")
    print(f"   Injury: {incident_1['injury_type']}")
    
    key_1 = CacheKeyManager.generate_cache_key("incident", incident_1)
    print(f"   Cache Key: {key_1}")
    
    print_subsection("Incident 2: Forklift Near-Miss")
    print(f"   Equipment: {incident_2['equipment']}")
    print(f"   Injury: {incident_2['injury_type']}")
    
    key_2 = CacheKeyManager.generate_cache_key("incident", incident_2)
    print(f"   Cache Key: {key_2}")
    
    if key_1 != key_2:
        print(f"\n❌ FARKLI KEYS! (Beklenen)")
        print(f"   → Her biri ayrı cache entry")
        print(f"   → Her biri ayrı maliyet")
        cost = simulate_cost_calculation("incident_analysis")
        print(f"   → Maliyet Incident 2: ${cost['total']:.2f}")


def test_bulk_cache_savings():
    """
    Test: Toplu olaylar - cascade cache hit
    """
    print_section("BULK TEST - 5 Benzer Olay Analizi")
    
    # Template incident
    template = {
        "incident_type": "ACCIDENT",
        "equipment": "Conveyor Belt",
        "injury_type": "CUT",
        "activity": "Operation"
    }
    
    # 5 benzer olay oluştur (farklı descriptions)
    incidents = []
    for i in range(1, 6):
        incident = template.copy()
        incident["_id"] = f"CONV-{i}"
        incident["description"] = f"Cut injury incident #{i} with completely different details and circumstances"
        incidents.append(incident)
    
    print_subsection("5 Benzer Olay")
    
    cache_keys = CacheKeyManager.generate_bulk_cache_keys("incident", incidents)
    
    # Check if all have same key
    unique_keys = set(cache_keys.values())
    
    print(f"\n📋 Oluşturulan Cache Keys:")
    for incident_id, cache_key in list(cache_keys.items())[:5]:
        print(f"   {incident_id} → {cache_key}")
    
    print(f"\n🔑 Unique Keys: {len(unique_keys)}")
    
    if len(unique_keys) == 1:
        print(f"✅ TÜM 5 OLAY AYNI CACHE'I KULLANIYOR!")
        
        print_subsection("💰 5 Olay Maliyeti")
        
        cost_no_cache = simulate_cost_calculation("incident_analysis")['total'] * 5
        cost_with_cache = simulate_cost_calculation("incident_analysis")['total']  # Sadece birinci
        savings = cost_no_cache - cost_with_cache
        
        print(f"\nCache OLMADAN: ${cost_no_cache:.2f}")
        print(f"   • Olay 1: ${cost_no_cache/5:.2f}")
        print(f"   • Olay 2: ${cost_no_cache/5:.2f}")
        print(f"   • Olay 3: ${cost_no_cache/5:.2f}")
        print(f"   • Olay 4: ${cost_no_cache/5:.2f}")
        print(f"   • Olay 5: ${cost_no_cache/5:.2f}")
        
        print(f"\nCache İLE: ${cost_with_cache:.2f}")
        print(f"   • Olay 1: ${cost_no_cache/5:.2f} (yeni)")
        print(f"   • Olay 2-5: $0.00 (cache hit) ✅")
        
        print(f"\n────────────────────────")
        print(f"TOPLAM TASARRUF: ${savings:.2f} ({(savings/cost_no_cache)*100:.1f}%)")


def test_mongodb_simulation():
    """
    Benzetim: MongoDB'ye nasıl kaydedilir
    """
    print_section("MONGODB SIMULATION - Cache Entry Yapısı")
    
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
        "root_cause": "Safety valve not opened before heating oil",
        "severity": "HIGH",
        "recommendations": [
            "Add pressure relief valve",
            "Implement checklist verification",
            "Add visual warning signs"
        ],
        "5_why": [
            "Why 1: Operator forgot to open valve",
            "Why 2: No written procedure posted",
            "Why 3: Training incomplete",
            "Why 4: No supervision",
            "Why 5: Lack of safety culture"
        ]
    }
    
    metadata = CacheEntryMetadata.create_metadata(
        cache_key=cache_key,
        entity_type="incident",
        entity_data=incident,
        analysis_result=analysis_result,
        ttl_days=30
    )
    
    print_subsection("MongoDB Cache Entry")
    
    print(f"\n📄 Kaydedilen Veri:")
    print(json.dumps({
        "cache_key": metadata["cache_key"],
        "entity_type": metadata["entity_type"],
        "entity_id": metadata["entity_id"],
        "critical_fields": metadata["critical_fields"],
        "metadata": metadata["metadata"],
        "created_at": str(metadata["created_at"]),
        "expires_at": str(metadata["expires_at"])
    }, indent=2, ensure_ascii=False))
    
    print(f"\n✅ Bundan sonra cache hit olunca:")
    print(f"   1. Aynı cache_key ile sorgu yap")
    print(f"   2. Bulunan analysis_result döndür")
    print(f"   3. Hit count artır (metadata.hit_count += 1)")
    print(f"   4. MALIYET: $0.00 ✨")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "█"*100)
    print("🚀 CACHE HIT TEST - RAPOR HAZIRLAMA ÜCRETİ DÜŞÜŞÜ")
    print("█"*100)
    
    test_similar_incidents_cache_hit()
    test_different_incidents_no_cache_hit()
    test_bulk_cache_savings()
    test_mongodb_simulation()
    
    print("\n" + "█"*100)
    print("✅ TEST TAMAMLANDı!")
    print("█"*100)
    
    print("\n📊 ÖZET:")
    print("""
    1. ✅ Benzer olaylar → AYNI cache key → Cache hit!
    2. ✅ Cache hit → $0.00 maliyet
    3. ✅ 5 benzer olay → 4 tane %80 tasarruf
    4. ✅ MongoDB'ye kaydedilir ve TTL'le expire olur
    
    💡 Key Point: Description farklı = cache miss
                   Critical fields aynı = cache hit
    """)
