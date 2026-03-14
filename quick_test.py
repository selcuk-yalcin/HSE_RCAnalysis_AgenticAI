#!/usr/bin/env python3
"""Hızlı test - Confined Space senaryosu"""

import sys
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
load_dotenv()

from agents.overview_agent import OverviewAgent
from agents.assessment_agent import AssessmentAgent
from agents.rootcause_agent_v2 import RootCauseAgentV2

print("\n" + "="*80)
print("🚀 QUICK TEST - CONFINED SPACE SENARYOSU")
print("="*80 + "\n")

incident = {
    "ref_no": "CS-2026-TEST",
    "reported_by": "Test User",
    "date_time": "12.03.2026 10:00",
    "description": """
CONFINED SPACE KAZASI - OKSİJEN EKSİKLİĞİ
==========================================
3 kişi atıksu tankına izinsiz girdi.
- Atmosfer testi yapılmadı
- Permit alınmadı  
- Gözcü yoktu
Sonuç: 3 kişi oksijen eksikliğinden bayıldı, yoğun bakıma kaldırıldı.
""",
    "injury_description": "3 kişi hipoksi, 2 kişi yoğun bakımda"
}

print("📋 STEP 1: Overview Agent başlatılıyor...")
print("-"*80)
overview = OverviewAgent()
part1 = overview.process_initial_report(incident)

print("\n✅ Part 1 tamamlandı!")
print(f"   Olay tipi: {part1.get('incident_type')}")

print("\n📋 STEP 2: Assessment Agent başlatılıyor...")  
print("-"*80)
assessment = AssessmentAgent()
part2 = assessment.assess_incident(part1, incident)

print("\n✅ Part 2 tamamlandı!")
print(f"   Ciddiyet: {part2.get('actual_potential_harm')}")

print("\n📋 STEP 3: Root Cause Agent başlatılıyor...")
print("-"*80)
rootcause = RootCauseAgentV2()
part3 = rootcause.analyze_root_causes(part1, part2, incident)

print("\n✅ Part 3 tamamlandı!")
print(f"   Kök neden sayısı: {len(part3.get('final_root_causes', []))}")

# DETAYLI RAPOR ÇIKTISI
print("\n" + "="*80)
print("📊 DETAYLI RAPOR")
print("="*80)

print("\n🔍 PART 1 - OVERVIEW:")
print("-"*80)
import json
print(json.dumps(part1, indent=2, ensure_ascii=False))

print("\n🔍 PART 2 - ASSESSMENT:")
print("-"*80)
print(json.dumps(part2, indent=2, ensure_ascii=False))

print("\n🔍 PART 3 - ROOT CAUSE ANALYSIS:")
print("-"*80)
print(json.dumps(part3, indent=2, ensure_ascii=False))

print("\n" + "="*80)
print("🎉 TEST BAŞARILI - TAM RAPOR GÖSTERILDI!")
print("="*80 + "\n")
