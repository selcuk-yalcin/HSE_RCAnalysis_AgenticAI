#!/usr/bin/env python3
"""
Cache HIT Test - Aynı incident'ı 2 kere analiz et
İkinci kez CACHE'DEN gelmelidir (API çağrısı yok, ödeme yok!)
"""

import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from agents.unified_analysis_pipeline import UnifiedAnalysisPipeline

# Oil fire incident'ı
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

# Pipeline başlat
pipeline = UnifiedAnalysisPipeline(use_rag=False, use_cache=True, use_mongodb_cache=True)

print("\n" + "="*100)
print("🧪 CACHE HIT TEST - OIL FIRE INCIDENT")
print("="*100)

# ============================================================
# ANALYSIS 1: İLK ANALIZ (YENI - API CALL)
# ============================================================
print("\n📊 ANALYSIS 1: İlk Analiz (MongoDB'ye yazılacak)")
print("─"*100)

start1 = datetime.now()
result1 = pipeline.analyze_incident(oil_fire_incident)
end1 = datetime.now()

print(f"\n   ✅ Analiz tamamlandı!")
print(f"   Source: {result1.get('source')}")
print(f"   Cached: {result1.get('cached')}")
print(f"   Duration: {(end1-start1).total_seconds():.1f}s")
print(f"   💰 Maliyeti: $0.31 (API çağrısı yapıldı)")

# ============================================================
# ANALYSIS 2: İKİNCİ ANALIZ (CACHE HIT - PARA YOK!)
# ============================================================
print("\n\n📊 ANALYSIS 2: Tekrar Analiz (Cache'den gelecek)")
print("─"*100)

start2 = datetime.now()
result2 = pipeline.analyze_incident(oil_fire_incident)
end2 = datetime.now()

print(f"\n   ✅ Analiz tamamlandı!")
print(f"   Source: {result2.get('source')}")
print(f"   Cached: {result2.get('cached')}")
print(f"   Duration: {(end2-start2).total_seconds():.1f}s")

if result2.get('cached'):
    print(f"   ✅ CACHE HIT! Maliyeti: $0.00 (Para ödenmedi!)")
else:
    print(f"   ❌ Cache miss oldu - API çağrısı yapıldı")

# ============================================================
# SONUÇ
# ============================================================
print("\n\n" + "="*100)
print("💰 COST ANALYSIS")
print("="*100)

analysis1_cost = 0.31
analysis2_cost = 0.0 if result2.get('cached') else 0.31

total_cost = analysis1_cost + analysis2_cost
saved = 0.31 if result2.get('cached') else 0.0

print(f"\n   Analysis 1 (İlk - API Çağrısı): ${analysis1_cost:.2f}")
print(f"   Analysis 2 (Tekrar - Cache): ${analysis2_cost:.2f}")
print(f"   ─────────────────────────────────────────")
print(f"   Total Cost: ${total_cost:.2f}")
print(f"   Tasarruf Edilen: ${saved:.2f}")

if result2.get('cached'):
    print(f"   💡 İkinci analiz cache'den geldi - %100 para tasarrufu!")
else:
    print(f"   ⚠️  İkinci analiz API'den çekildi")

# ============================================================
# Speed Comparison
# ============================================================
print(f"\n\n⏱️  SPEED COMPARISON")
print("─"*100)
time1 = (end1-start1).total_seconds()
time2 = (end2-start2).total_seconds()
speedup = time1 / time2 if time2 > 0 else 1

print(f"\n   İlk Analiz (API): {time1:.1f}s")
print(f"   Tekrar Analiz (Cache): {time2:.1f}s")
print(f"   Hızlanma: {speedup:.0f}x daha hızlı!")

print("\n" + "="*100 + "\n")
