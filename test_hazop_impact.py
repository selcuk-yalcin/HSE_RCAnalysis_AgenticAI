#!/usr/bin/env python3
"""
Hızlı Test: HAZOP yapılıp yapılmadığının kök nedene etkisini test et
Amaç: Sadece root cause kodlarını karşılaştır, rapor yazma
"""

import json
from pathlib import Path
from agents.rootcause_agent_v2 import RootCauseAgentV2
from agents.overview_agent import OverviewAgent
from agents.assessment_agent import AssessmentAgent

incident_summary = """
KAZA RAPORU - YAĞ TASFİYE CİHAZI YANMASI
==========================================

1. OLAY ÖZETİ
Saat 15:20'de görevli yağcı, yağ tasfiye cihazını "ON" konumuna alarak sistemi devreye sokmuştur. 
Ancak normal çalışma sırasına göre cihaz devreye alınmadan önce hat vanasının açılması gerekmekteyken, 
ilgili çalışan tarafından vana açılmadan cihaz çalıştırılmıştır. Çalışan, cihazı devreye aldıktan sonra 
hat vanasını açmadan alandan ayrılmıştır.

Yaklaşık 15–20 dakika sonra vardiya değişimi gerçekleşmiş, ilk yağcı vardiyadan ayrılmış ve yeni yağcı 
görev başı yapmıştır. Göreve başlayan yeni yağcı, yağ tasfiye cihazından duman çıktığını fark etmiş 
ve durumu derhal ilgili kişilere bildirmiştir. Yapılan bildirim üzerine cihaz kapatılmış ve güvenli 
müdahale amacıyla soğumaya bırakılmıştır. Olaydan yaklaşık 12 saat sonra cihaz sökülerek iç kısmında 
detaylı inceleme yapılmış, gerçekleştirilen kontrolde cihazın iç aksamında yanma meydana geldiği tespit edilmiştir.

2. BULGULAR
- Personel: 4 yıllık kıdemli ve tecrübeli personel
- Yazılı talimat: VERİLMEMİŞ
- Interlock/Sensör: YOK (bu cihazda)
- Diğer cihazlarda: VAR
- Uyarı levhası: YOK
- HAZOP yapılıp yapılmadığı: KONTROL ALTINDA
"""

def run_test(test_name, has_hazop=False):
    print(f"\n{'=' * 80}")
    print(f"🧪 TEST: {test_name}")
    print(f"{'=' * 80}")
    
    # Part 1: Overview
    overview_agent = OverviewAgent()
    overview_result = overview_agent.process_initial_report({
        "ref_no": f"TEST-HAZOP-{1 if has_hazop else 0}",
        "reported_by": "Test",
        "date_time": "15:20",
        "description": incident_summary,
        "injury_description": "Kişisel yaralanma yok. Ekipman hasarı: yanma"
    })
    
    # Part 2: Assessment
    assessment_agent = AssessmentAgent()
    assessment_result = assessment_agent.assess_incident(overview_result, {
        "description": incident_summary
    })
    
    # Part 3: Root Cause with HITL
    investigation_data = {
        "description": incident_summary,
    }
    
    # ✅ HAZOP yapıldı ise HITL cevabı ekle
    if has_hazop:
        investigation_data["five_why_answers"] = [
            {
                "question": "Bu cihazda neden interlock/sensör yok?",
                "answer": "HAZOP analizi yapıldığında bu cihazın 'yağ akışı olmadan ısıtma' riski tanımlanmıştır. Ancak retrofit edilmemiştir."
            },
            {
                "question": "Neden retrofit edilmemiştir?",
                "answer": "Maliyet gerekçesiyle retrofit ertelenmiştir. Bunun yerine operatörlere yazılı prosedür sağlanması planlanmıştır ama yapılmamıştır."
            }
        ]
    
    print(f"\n🔍 HITL Inputs:")
    if has_hazop:
        print(f"   ✅ HAZOP yapıldı (simule edildi)")
    else:
        print(f"   ❌ HAZOP yapılmadı")
    
    # Root Cause Analysis
    print(f"\n⏳ Analyzing...")
    rootcause_agent = RootCauseAgentV2(use_rag=False)  # Static KB for consistency
    
    root_cause_result = rootcause_agent.analyze_root_causes(
        overview_result,
        assessment_result,
        investigation_data
    )
    
    # Extract root causes
    print(f"\n📊 ROOT CAUSES IDENTIFIED:")
    print(f"{'─' * 80}")
    
    branches = root_cause_result.get('analysis_branches', [])
    root_causes = []
    
    for i, branch in enumerate(branches, 1):
        root_cause = branch.get('root_cause', {})
        code = root_cause.get('code', 'N/A')
        title = root_cause.get('standard_title_tr', 'N/A')
        
        root_causes.append(code)
        print(f"\n{i}. [{code}] {title}")
        print(f"   Category: {root_cause.get('category_type', 'N/A')}")
    
    rootcause_agent.cleanup()
    
    return sorted(root_causes)


# ============================================================================
# TEST ÇALIŞTIR
# ============================================================================

print("\n" + "🔬" * 40)
print("HAZOP ETKİ KARŞILAŞTIRMASI TESTİ")
print("🔬" * 40)

# Test 1: HAZOP yapılmadı
results_no_hazop = run_test(
    "HAZOP Yapılmadı (Orijinal Scenario)",
    has_hazop=False
)

# Test 2: HAZOP yapıldı (simule)
results_with_hazop = run_test(
    "HAZOP Yapıldı (Simule)",
    has_hazop=True
)

# ============================================================================
# SONUÇ KARŞILAŞTIRMASI
# ============================================================================

print(f"\n\n{'=' * 80}")
print("📈 SONUÇ KARŞILAŞTIRMASI")
print(f"{'=' * 80}")

print(f"\n❌ HAZOP Yapılmadı (Senaryo 1):")
print(f"   Root Cause Kodları: {results_no_hazop}")

print(f"\n✅ HAZOP Yapıldı (Senaryo 2):")
print(f"   Root Cause Kodları: {results_with_hazop}")

print(f"\n{'─' * 80}")

if results_no_hazop == results_with_hazop:
    print("⚠️  SONUÇ: Aynı kök nedenler çıktı (HITL henüz etkili değil)")
    print("   Bunun nedeni: _append_hitl_answers() metodu tamamlanmalı veya")
    print("                 Claude prompt'ta HITL cevapları kullanılmalı")
else:
    print("✅ SONUÇ: HAZOP bilgisi kök nedenleri değiştirdi!")
    print(f"   Fark: {set(results_no_hazop) ^ set(results_with_hazop)}")

print(f"\n{'=' * 80}\n")
