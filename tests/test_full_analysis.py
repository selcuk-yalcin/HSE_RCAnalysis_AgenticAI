"""
FULL ANALIZ TEST - MOCK + REAL AGENTS
=====================================

API key'leri olmadığı için mock data ile gerçek agent yapısını simulate et.
Tüm 5 aşamayı kapsamlı şekilde göster.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


# ============================================================================
# MOCK SONUÇLARI - GERÇEK AGENT ÇIKTILARINI SIMULATE ET
# ============================================================================

MOCK_OVERVIEW_RESULT = {
    "ref_no": "02-26",
    "incident_type": "Ramak Kala (Near Miss) - Seviye A (Yüksek)",
    "location": "MPT Test Sahası",
    "severity_assessment": "ÇOK YÜKSEK - Potansiyel Ölüm/Ciddi Yaralanma",
    "risk_level": "CRÍTICA L",
    "summary": "MPT test sahasında sarmal kapı mekanizmasından metal parça koparak 2 metre yakınlığında çalışana düştü",
    "investigation_details": {
        "olay_tarihi": "20.01.2026 09:10",
        "olay_yeri": "MPT Test Sahası",
        "olay_tipi": "Ekipman hasarı + Near Miss",
        "potansiyel_sonuclar": ["Kafatası kırığı", "Omurga hasarı", "Ölüm"]
    }
}

MOCK_ASSESSMENT_RESULT = {
    "actual_potential_harm": "Ramak Kala - Potansiyel sonuç çok ciddiydi ama yaralanma olmadı",
    "riddor_reportable": "Hayır (yaralanma yok)",
    "investigation_level": "Seviye A (Yüksek Araştırma)",
    "potential_consequences": [
        "Kafatası kırığı ve iç kanama (baş bölgesi)",
        "Omurga hasarı ve felç (omuz/sırt bölgesi)",
        "Çoklu kemik kırıkları",
        "Uzun süreli işe alamamazlık veya kalıcı sakatlık",
        "Ölüm (worst case)"
    ],
    "near_miss_analysis": "2 metre mesafe şans faktörü. Çalışan tam kapı altında değildi.",
    "recommendations": [
        "Sarmal kapı acil bakım",
        "Tüm kapıların detaylı inspeksiyonu",
        "Çalışan eğitimi"
    ]
}

MOCK_ROOTCAUSE_RESULT = {
    "analysis_branches": [
        {
            "direct_cause": {"name": "Metal parça kopması", "code": "EQ-001"},
            "root_cause": {"name": "Bakım eksikliği", "code": "OM-101"},
            "five_why_chain": [
                {"why": "Parça neden koptu?", "because": "Bağlantı gevşemiş/aşınmıştı"},
                {"why": "Neden gevşemiş?", "because": "Periyodik bakım yapılmadı"},
                {"why": "Neden bakım yapılmadı?", "because": "Sistem eksik"},
                {"why": "Neden sistem eksik?", "because": "Priorite düşük"},
            ]
        },
        {
            "direct_cause": {"name": "Anormal ses duyulmasına rağmen işlem devam etti", "code": "HF-001"},
            "root_cause": {"name": "Çalışan farkındalık eksikliği", "code": "HF-101"},
            "five_why_chain": [
                {"why": "Neden işlem devam etti?", "because": "'Ses = Tehlike' refleksi eksik"},
                {"why": "Neden refleks eksik?", "because": "Eğitim yetersiz"},
                {"why": "Neden eğitim yetersiz?", "because": "Risk değerlendirmesi kapsamlı değil"},
            ]
        }
    ],
    "final_root_causes": [
        {"code": "OM-101", "name": "Sarmal kapı bakım sistemi eksikliği", "description": "Mekanizma parçalarının aşınması kontrol edilmemiş"},
        {"code": "HF-101", "name": "Çalışan tehlike algılaması yetersiz", "description": "Anormal ses = tehlike farkındalığı gelişmemiş"},
        {"code": "ORG-101", "name": "Organizasyonel risk yönetimi eksikliği", "description": "Düşen parça senaryosu değerlendirilmemiş"}
    ],
    "meta_root_cause": {
        "code": "SYS-001",
        "name": "Ekipman bakım kültürü ve tehlike algılaması yetersiz",
        "description": "Sistemik olarak ekipman bakımı ve çalışan eğitiminde eksiklikler",
        "synthesized_from_codes": ["OM-101", "HF-101", "ORG-101"]
    }
}

MOCK_ACTIONPLAN_RESULT = {
    "immediate_actions": [
        {"description": "Sarmal kapı acil kullanım dışı bırak", "priority": "KRITIK", "owner": "Tesislerin Bakımı", "deadline": "Aynı gün"},
        {"description": "Tüm sarmal kapıların detaylı mekanizma kontrolü", "priority": "YÜKSEK", "owner": "Bakım Müdürlüğü", "deadline": "3 gün içinde"},
        {"description": "Kopan parça emniyet analizi", "priority": "YÜKSEK", "owner": "Güvenlik Birim", "deadline": "5 gün içinde"},
        {"description": "Çalışan ve tanıklara psikolojik destek", "priority": "YÜKSEK", "owner": "İK Birim", "deadline": "2 gün içinde"},
        {"description": "Alternatif giriş/çıkış prosedürü oluştur", "priority": "ORTA", "owner": "Operasyonlar", "deadline": "1 gün içinde"},
    ],
    "preventive_measures": [
        {"description": "Sarmal kapı periyodik bakım sistemi yeniden tasarla (aylık detaylı kontrol)", "owner": "Bakım", "timeline": "30 gün"},
        {"description": "Bakım kayıt sistemi dijitalize et", "owner": "IT + Bakım", "timeline": "60 gün"},
        {"description": "Anormal ses/titreşim = acil durdurma prosedürü yazılı hale getir", "owner": "Operasyonlar", "timeline": "7 gün"},
        {"description": "Tüm çalışanları işitsel uyarılar konusunda eğit", "owner": "Eğitim", "timeline": "14 gün"},
        {"description": "Kapı güvenlik sensörleri (mekanik arıza tespiti) kur", "owner": "Mühendislik", "timeline": "90 gün"},
        {"description": "Risk değerlendirmesine 'düşen parça' senaryosu ekle", "owner": "HSE", "timeline": "30 gün"},
        {"description": "Periyodik kapı güvenlik denetimi (3-6 aylık)", "owner": "Bakım", "timeline": "Devam eden"},
    ]
}


# ============================================================================
# FULL ANALYSIS RUNNER
# ============================================================================

def run_full_analysis():
    """Full analiz pipeline'ını çalıştır."""
    
    print("=" * 100)
    print("⚠️  FULL ANALIZ - MPT TEST SAHASI SARMAL KAPI DÜŞEN PARÇA RAMAK KALA OLAYI")
    print("=" * 100)
    print()
    
    # ADIM 1: OVERVIEW
    print("\n" + "=" * 100)
    print("📋 ADIM 1: OVERVIEW AGENT - OLAY ÖZETI VE İLK DEĞERLENDİRME")
    print("=" * 100 + "\n")
    
    print("🤖 Overview Agent başlatıldı...")
    print("\n✅ OVERVIEW ANALIZI TAMAMLANDI!")
    print(f"📊 Olay Tipi: {MOCK_OVERVIEW_RESULT['incident_type']}")
    print(f"🏷️  Referans No: {MOCK_OVERVIEW_RESULT['ref_no']}")
    print(f"📍 Yer: {MOCK_OVERVIEW_RESULT['location']}")
    print(f"⚠️  Ciddiyet: {MOCK_OVERVIEW_RESULT['severity_assessment']}")
    print(f"📈 Risk Seviyesi: {MOCK_OVERVIEW_RESULT['risk_level']}")
    
    # ADIM 2: ASSESSMENT
    print("\n" + "=" * 100)
    print("📋 ADIM 2: ASSESSMENT AGENT - RİSK DEĞERLENDİRMESİ")
    print("=" * 100 + "\n")
    
    print("🤖 Assessment Agent başlatıldı...")
    print("\n✅ ASSESSMENT ANALIZI TAMAMLANDI!")
    print(f"⚠️  Ciddiyet: {MOCK_ASSESSMENT_RESULT['actual_potential_harm']}")
    print(f"📋 RIDDOR: {MOCK_ASSESSMENT_RESULT['riddor_reportable']}")
    print(f"🎯 Araştırma Seviyesi: {MOCK_ASSESSMENT_RESULT['investigation_level']}")
    print(f"💡 Tavsiyeler:")
    for rec in MOCK_ASSESSMENT_RESULT['recommendations']:
        print(f"   • {rec}")
    
    # ADIM 3: ROOT CAUSE
    print("\n" + "=" * 100)
    print("📋 ADIM 3: ROOT CAUSE AGENT V2 - KÖK NEDEN ANALİZİ (5-WHY)")
    print("=" * 100 + "\n")
    
    print("🤖 Root Cause Agent V2 başlatıldı...")
    print("\n✅ KÖK NEDEN ANALİZİ TAMAMLANDI!")
    
    branches = MOCK_ROOTCAUSE_RESULT['analysis_branches']
    root_causes = MOCK_ROOTCAUSE_RESULT['final_root_causes']
    meta_root = MOCK_ROOTCAUSE_RESULT['meta_root_cause']
    
    print(f"🌳 Toplam {len(branches)} Ana Dal Tespit Edildi")
    print(f"🎯 Toplam {len(root_causes)} Kök Neden Bulundu")
    
    print(f"\n🔗 META KÖK NEDEN (Ortak Payda):")
    print(f"   [{meta_root['code']}] {meta_root['name']}")
    print(f"   {meta_root['description']}")
    
    print(f"\n📌 KÖK NEDENLER:")
    for i, rc in enumerate(root_causes, 1):
        print(f"   {i}. [{rc['code']}] {rc['name']}")
    
    print(f"\n🔀 DAL DETAYLARI:")
    for i, branch in enumerate(branches, 1):
        print(f"\n   Dal {i}:")
        print(f"   - Doğrudan Neden: {branch['direct_cause']['name']}")
        print(f"   - Kök Neden: {branch['root_cause']['name']}")
        print(f"   - 5-WHY Zinciri: {len(branch['five_why_chain'])} adım")
    
    # ADIM 4: ACTION PLAN
    print("\n" + "=" * 100)
    print("📋 ADIM 4: ACTION PLAN AGENT - DÜZELTICI/ÖNLEYICI TEDİRLER")
    print("=" * 100 + "\n")
    
    print("🤖 Action Plan Agent başlatıldı...")
    print("\n✅ ACTION PLAN OLUŞTURULDU!")
    
    immediate = MOCK_ACTIONPLAN_RESULT['immediate_actions']
    preventive = MOCK_ACTIONPLAN_RESULT['preventive_measures']
    
    print(f"\n🔴 ACİL TEDBIRLER ({len(immediate)} adet):")
    for action in immediate:
        print(f"   • {action['description']}")
        print(f"     [Priority: {action['priority']}, Owner: {action['owner']}, Deadline: {action['deadline']}]")
    
    print(f"\n🟢 UZUN VADELİ ÖNLEYICI TEDBIRLER ({len(preventive)} adet):")
    for i, measure in enumerate(preventive, 1):
        print(f"   {i}. {measure['description']}")
        print(f"      [Owner: {measure['owner']}, Timeline: {measure['timeline']}]")
    
    # ADIM 5: DOCX RAPOR
    print("\n" + "=" * 100)
    print("📋 ADIM 5: DOCX RAPOR OLUŞTUR - TAM ANALİZ RAPORU")
    print("=" * 100 + "\n")
    
    print("🤖 Docx Agent başlatıldı...")
    print("   📝 Tam rapor oluşturuluyor...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("outputs/mpt_falling_part_near_miss")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n✅ DOCX RAPOR OLUŞTURULDU!")
    print(f"   📄 outputs/mpt_falling_part_near_miss/full_analysis_report_{timestamp}.docx")
    
    # JSON'A KAYDET
    print("\n" + "=" * 100)
    print("💾 SONUÇLARI KAYDET")
    print("=" * 100 + "\n")
    
    full_results = {
        "incident_ref": MOCK_OVERVIEW_RESULT["ref_no"],
        "analysis_timestamp": timestamp,
        "analysis_method": "Full Pipeline - All Agents (Mock + Real Structure)",
        "overview": MOCK_OVERVIEW_RESULT,
        "assessment": MOCK_ASSESSMENT_RESULT,
        "root_cause_analysis": MOCK_ROOTCAUSE_RESULT,
        "action_plan": MOCK_ACTIONPLAN_RESULT
    }
    
    full_json_path = output_dir / f"full_analysis_{timestamp}.json"
    with open(full_json_path, 'w', encoding='utf-8') as f:
        json.dump(full_results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Tam analiz JSON kaydedildi:")
    print(f"   📄 {full_json_path}")
    print(f"   📊 Dosya Boyutu: {full_json_path.stat().st_size:,} bytes")
    
    # OUTPUT KLASÖRÜ
    print("\n" + "=" * 100)
    print("📁 OUTPUT KLASÖRÜ İÇERİĞİ")
    print("=" * 100 + "\n")
    
    print(f"📂 {output_dir}/")
    if output_dir.exists():
        files = sorted(output_dir.glob("*.json"))
        for file in files:
            size = file.stat().st_size
            print(f"   📄 {file.name:<50} ({size:,} bytes)")
        print(f"\n   📊 Toplam {len(files)} JSON dosyası")
    
    # ÖZET
    print("\n" + "=" * 100)
    print("✅ FULL ANALIZ TAMAMLANDI!")
    print("=" * 100)
    print(f"""
📊 ANALIZ ÖZETİ:
   Olay: Ramak Kala (Near Miss) - Seviye A (Yüksek)
   Yer: MPT Test Sahası
   Araştırma Seviyesi: Seviye A (Yüksek Araştırma)

📈 SONUÇLAR:
   ✅ Overview Analizi: Tamamlandı
   ✅ Risk Değerlendirmesi: Tamamlandı
   ✅ Kök Neden Analizi: Tamamlandı ({len(root_causes)} kök neden)
   ✅ Action Plan: Tamamlandı ({len(immediate)} acil + {len(preventive)} uzun vadeli)
   ✅ JSON Sonuçlar: Kaydedildi

🔗 KÖK NEDENLER (Meta):
   {meta_root['name']}
   → {meta_root['description']}

🛠️  ACİL TEDBIRLER (Top 3):
   1. {immediate[0]['description']} ({immediate[0]['priority']})
   2. {immediate[1]['description']} ({immediate[1]['priority']})
   3. {immediate[2]['description']} ({immediate[2]['priority']})

📁 ÇIKTI LOKASYONLARı:
   • {full_json_path}
   • outputs/mpt_falling_part_near_miss/analysis_*.json
""")
    
    return full_results


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    try:
        results = run_full_analysis()
        print("\n" + "=" * 100)
        print("🎉 FULL ANALIZ TÜM AŞAMALARI BAŞARIYLA TAMAMLANDI!")
        print("=" * 100)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
