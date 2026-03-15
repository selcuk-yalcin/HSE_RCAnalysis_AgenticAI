#!/usr/bin/env python3
"""
Cache Key Debug Test
İkinci analiz neden cache hit olmadığını debug et
"""

import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from agents.unified_analysis_pipeline import UnifiedAnalysisPipeline, MongoDBCache

# Oil fire incident
oil_fire_incident = {
    "ref_no": "OIL-2026-002-FIRE",
    "reported_by": "Vardiya Amiri",
    "date_time": "15:20",
    "description": """
KAZA RAPORU - YAĞ TASFİYE CİHAZI YANMASI
- Yağcı, yağ tasfiye cihazını hat vanası açılmadan devreye aldı
- Cihaz yağ akışı olmadan ısıtılarak yangın oluşturdu
- Personel: 4 yıllık deneyimli, yazılı talimat: YOK
- Uyarıcı levha: YOK
- Emniyet sensörü: YOK
- Kişisel yaralanma: YOK, Ekipman hasarı: EVET
""",
    "injury_description": "Kişisel yaralanma yok",
    "equipment": "Yağ Tasfiye Cihazı"
}

print("\n" + "="*100)
print("🔍 CACHE KEY DEBUG TEST")
print("="*100)

# Cache key'i hesapla (MongoDBCache'ın yaptığı şey gibi)
print("\n1️⃣  Incident Data:")
print("─"*100)
print(json.dumps(oil_fire_incident, indent=2, ensure_ascii=False)[:200] + "...")

# MongoDBCache instance oluştur ve key'i hesapla
cache = MongoDBCache()
key1 = cache.get_cache_key(oil_fire_incident)

print(f"\n\n2️⃣  Cache Key (Calculation 1):")
print("─"*100)
print(f"   {key1}")

# Aynı incident'ı tekrar
key2 = cache.get_cache_key(oil_fire_incident)
print(f"\n3️⃣  Cache Key (Calculation 2):")
print("─"*100)
print(f"   {key2}")

if key1 == key2:
    print(f"\n   ✅ KEYS MATCH! Aynı incident aynı key üretiyor.")
else:
    print(f"\n   ❌ KEYS DIFFERENT! Bu neden cache hit olmadığını açıklıyor!")

# MongoDB'de şu key'i ara
print(f"\n\n4️⃣  MongoDB'de Cache Kaydı Kontrolü:")
print("─"*100)

try:
    found = cache.collection.find_one({"cache_key": key1})
    if found:
        print(f"   ✅ Cache kaydı bulundu!")
        print(f"   Document ID: {found.get('_id')}")
        print(f"   Incident Ref: {found.get('incident_ref')}")
        print(f"   Created: {found.get('created_at')}")
        print(f"   Expires: {found.get('expires_at')}")
    else:
        print(f"   ❌ Cache kaydı BULUNAMADI!")
        print(f"   MongoDB'de {key1} ile eşleşen kayıt yok")
        
        # Tüm records'ları listele
        all_records = list(cache.collection.find({}, {"cache_key": 1, "incident_ref": 1}))
        if all_records:
            print(f"\n   📋 MongoDB'de bulunan records:")
            for rec in all_records[:5]:
                print(f"      • {rec.get('incident_ref')} - {rec.get('cache_key', 'N/A')[:16]}...")
        else:
            print(f"\n   📭 MongoDB analysis_cache collection boş!")
            
except Exception as e:
    print(f"   ❌ MongoDB query hatası: {e}")

# Pipeline test
print(f"\n\n5️⃣  Pipeline Analysis Test:")
print("─"*100)

pipeline = UnifiedAnalysisPipeline(use_rag=False)

print(f"\n   📊 ANALYSIS 1 (İlk):")
start1 = datetime.now()
result1 = pipeline.analyze_incident(oil_fire_incident)
end1 = datetime.now()

print(f"      Source: {result1.get('source')}")
print(f"      Cached: {result1.get('cached')}")
print(f"      Duration: {(end1-start1).total_seconds():.1f}s")

print(f"\n   📊 ANALYSIS 2 (Tekrar):")
start2 = datetime.now()
result2 = pipeline.analyze_incident(oil_fire_incident)
end2 = datetime.now()

print(f"      Source: {result2.get('source')}")
print(f"      Cached: {result2.get('cached')}")
print(f"      Duration: {(end2-start2).total_seconds():.1f}s")

if result2.get('cached'):
    print(f"\n   ✅ CACHE HIT SUCCESSFUL!")
else:
    print(f"\n   ❌ CACHE HIT FAILED - API çağrısı yapıldı")

print("\n" + "="*100 + "\n")
