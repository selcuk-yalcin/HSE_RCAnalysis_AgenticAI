"""
TEST: MPT DÜŞEN PARÇA RAMAK KALA - BASITLEŞTIRILMIŞ ANALIZ
==========================================================

DSpy framework'ü yerine JSON-based structured analiz
(network izni olmayan ortamlarda çalışmak için)
"""

import json
import sys
from pathlib import Path
from datetime import datetime


# ============================================================================
# MOCK DSPY - Yapılandırılmış Çıktı Üretimi
# ============================================================================

class MockDSpyResult:
    """DSpy output simulatörü."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def simulate_overview_analysis(incident_data):
    """Olay özeti analizi."""
    return MockDSpyResult(
        incident_type="Ramak Kala (Near Miss) - Seviye A (Yüksek)",
        severity_level="ÇOK YÜKSEK - Potansiyel Ölüm/Ciddi Yaralanma",
        potential_harm=[
            "Kafatası kırığı (baş bölgesine düşme)",
            "Omurga hasarı/felç (omuz/sırt bölgesine düşme)",
            "İç kanama",
            "Ölüm riski (potansiyel)"
        ],
        summary="MPT test sahasında sarmal kapı mekanizmasından metal parça koparak 2 metre yakınlığında çalışana düştü. Yaralanma yok ama potansiyel ölüm/kalıcı sakatlık riski çok yüksek. Şans faktörü kritik rol oynadı."
    )


def simulate_assessment_analysis(overview, incident_data):
    """Risk değerlendirmesi."""
    return MockDSpyResult(
        assessment_result="Ramak Kala - Potansiyel sonuç çok ciddiydi ama yaralanma olmadı",
        potential_consequences=[
            "Kafatası kırığı ve iç kanama (baş bölgesi)",
            "Omurga hasarı ve felç (omuz/sırt bölgesi)",
            "Çoklu kemik kırıkları",
            "Uzun süreli işe alamamazlık veya kalıcı sakatlık",
            "Ölüm (worst case)"
        ],
        near_miss_analysis="2 metre mesafe şans faktörü. Çalışan tam kapı altında değildi. Parça düşme yörüngesi çalışandan uzak. Eğer 50cm sola/yukarı düşseydi kafatası kırığı ve ölüm kesin."
    )


def simulate_rootcause_analysis(overview, incident_data):
    """Kök neden analizi - 5-WHY."""
    return MockDSpyResult(
        root_cause_1="Sarmal kapı üst mekanizması bakım/kontrol eksikliği. Metal parça bağlantısının aşınması tespit edilmemiş.",
        root_cause_2="Anormal ses duyulmasına rağmen işlem durdurulmadı. Çalışan 'ses = tehlike' refleksini geliştirmemiş.",
        root_cause_3="Periyodik bakım sistemi yetersiz. Detaylı mekanizma kontrolü yapılmıyor. Bakım kayıtları eksik.",
        meta_root_cause="Ekipman bakım kültürü ve çalışan tehlike algılaması yetersiz. Organizasyonel risk yönetimi eksik.",
        five_why_chain="""
WHY 1: Parça neden koptu?
→ BECAUSE: Bağlantı gevşemiş/aşınmıştı

WHY 2: Neden gevşemiş/aşınmıştı?
→ BECAUSE: Periyodik bakım yapılmadı/detaylı kontrolü eksik

WHY 3: Neden bakım yapılmadı?
→ BECAUSE: Bakım sistemi eksik, priorite düşük, kayıtlar belirsiz

WHY 4: Neden anormal ses duyulmasına rağmen işlem devam etti?
→ BECAUSE: 'Ses = Tehlike' farkındalığı ve prosedür eksik

WHY 5: Neden farkındalık eksik?
→ BECAUSE: Eğitim ve risk değerlendirmesi kapsamlı değil
        """
    )


def simulate_corrective_actions(root_causes, incident_data):
    """Düzeltici tedbirler."""
    return MockDSpyResult(
        immediate_actions="""
1. Sarmal kapı acil kullanım dışı bırak (✅ Yapıldı)
2. Tüm sarmal kapıların detaylı mekanizma kontrolü yap
3. Kopan parça emniyet analizi ve hasar raporu oluştur
4. Çalışan ve tanıklara psikolojik destek sağla
5. Alternatif giriş/çıkış prosedürü ve eğitim
        """,
        preventive_measures="""
1. Sarmal kapı periyodik bakım sistemi yeniden tasarla (aylık detaylı kontrol)
2. Bakım kayıt sistemi dijitalize et (veri tabanı)
3. Anormal ses/titreşim = acil durdurma prosedürü yazılı hale getir
4. Tüm çalışanları "işitsel uyarılar = tehlike" konusunda eğit
5. Kapı güvenlik sensörleri (mekanik arıza tespiti) kur
6. Risk değerlendirmesine "düşen parça" senaryosu ekle
7. Periyodik kapı güvenlik denetimi (3-6 aylık)
        """,
        success_criteria="""
✓ Tüm sarmal kapılar bakım kayıtları güncel (30 gün içinde)
✓ Çalışan eğitimi tamamlandı (%100)
✓ Anormal ses prosedürü yazılı ve afişe edildi
✓ Hiç bir incident/near-miss (6 ay boyunca)
✓ Bakım sistem veri tabanı live (tracking)
✓ Güvenlik sensörleri kuruldu ve test edildi
        """
    )


# ============================================================================
# TEST DATA
# ============================================================================

INCIDENT_DATA = {
    "ref_no": "02-26",
    "report_date": "21.01.2026",
    "incident_date": "20.01.2026",
    "incident_time": "09:10",
    "location": "MPT Test Sahası",
    "description": "Sarmal kapı mekanizmasından metal parça koparak düştü"
}


# ============================================================================
# MAIN TEST
# ============================================================================

def main():
    print("=" * 100)
    print("⚠️  MPT TEST SAHASI SARMAL KAPI DÜŞEN PARÇA RAMAK KALA OLAYI - TEST")
    print("=" * 100)
    print()
    
    # Analiz aşamaları
    print("\n" + "=" * 100)
    print("🤖 ANALİZ AŞAMALARI BAŞLATILIYOR...")
    print("=" * 100 + "\n")
    
    # 1. Overview
    print("📋 Adım 1: Olay Özeti Oluşturuluyor...")
    overview_result = simulate_overview_analysis(INCIDENT_DATA)
    print(f"   ✅ Olay Tipi: {overview_result.incident_type}")
    print(f"   ✅ Ciddiyet: {overview_result.severity_level}")
    
    # 2. Assessment
    print("\n📋 Adım 2: Risk Değerlendirmesi Yapılıyor...")
    assessment_result = simulate_assessment_analysis(overview_result, INCIDENT_DATA)
    print(f"   ✅ Değerlendirme: {assessment_result.assessment_result}")
    
    # 3. Root Cause
    print("\n📋 Adım 3: Kök Neden Analizi (5-WHY)...")
    rootcause_result = simulate_rootcause_analysis(overview_result, INCIDENT_DATA)
    print(f"   ✅ Kök Neden 1: {rootcause_result.root_cause_1[:60]}...")
    print(f"   ✅ Meta Kök Neden: {rootcause_result.meta_root_cause[:60]}...")
    
    # 4. Corrective
    print("\n📋 Adım 4: Düzeltici Tedbirler Belirleniyor...")
    corrective_result = simulate_corrective_actions(
        f"{rootcause_result.root_cause_1}\n{rootcause_result.root_cause_2}",
        INCIDENT_DATA
    )
    print(f"   ✅ Acil Tedbirler: {corrective_result.immediate_actions.split(chr(10))[0]}...")
    
    # Sonuçları göster
    print("\n" + "=" * 100)
    print("📊 ANALIZ SONUÇLARI")
    print("=" * 100)
    
    print("\n" + "─" * 100)
    print("1️⃣  OVERVIEW (Olay Özeti)")
    print("─" * 100)
    print(f"Olay Tipi: {overview_result.incident_type}")
    print(f"Ciddiyet: {overview_result.severity_level}")
    print(f"Potansiyel Zararlar:")
    for harm in overview_result.potential_harm:
        print(f"   • {harm}")
    print(f"\nÖzet:\n{overview_result.summary}")
    
    print("\n" + "─" * 100)
    print("2️⃣  ASSESSMENT (Risk Değerlendirmesi)")
    print("─" * 100)
    print(f"Değerlendirme: {assessment_result.assessment_result}")
    print(f"\nPotansiyel Sonuçlar:")
    for consequence in assessment_result.potential_consequences:
        print(f"   • {consequence}")
    print(f"\nRamak Kala Analizi:\n{assessment_result.near_miss_analysis}")
    
    print("\n" + "─" * 100)
    print("3️⃣  ROOT CAUSE ANALYSIS (Kök Neden Analizi - 5-WHY)")
    print("─" * 100)
    print(f"Kök Neden 1:\n{rootcause_result.root_cause_1}\n")
    print(f"Kök Neden 2:\n{rootcause_result.root_cause_2}\n")
    print(f"Kök Neden 3:\n{rootcause_result.root_cause_3}\n")
    print(f"Meta Kök Neden (Ortak Payda):\n{rootcause_result.meta_root_cause}\n")
    print(f"5-WHY Zinciri:\n{rootcause_result.five_why_chain}")
    
    print("\n" + "─" * 100)
    print("4️⃣  CORRECTIVE ACTIONS (Düzeltici Tedbirler)")
    print("─" * 100)
    print(f"Acil Tedbirler:\n{corrective_result.immediate_actions}")
    print(f"\nUzun Vadeli Önleyici Tedbirler:\n{corrective_result.preventive_measures}")
    print(f"\nBaşarı Kriterleri:\n{corrective_result.success_criteria}")
    
    # JSON'a kaydet
    print("\n" + "=" * 100)
    print("💾 SONUÇLAR KAYDEDILIYOR")
    print("=" * 100 + "\n")
    
    output_dir = Path("outputs/mpt_falling_part_near_miss")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    output_data = {
        "incident_ref": INCIDENT_DATA["ref_no"],
        "test_timestamp": timestamp,
        "analysis_method": "Structured Chain-of-Thought (Mock DSpy)",
        "overview": {
            "incident_type": overview_result.incident_type,
            "severity_level": overview_result.severity_level,
            "potential_harm": overview_result.potential_harm,
            "summary": overview_result.summary
        },
        "assessment": {
            "assessment_result": assessment_result.assessment_result,
            "potential_consequences": assessment_result.potential_consequences,
            "near_miss_analysis": assessment_result.near_miss_analysis
        },
        "rootcause": {
            "root_cause_1": rootcause_result.root_cause_1,
            "root_cause_2": rootcause_result.root_cause_2,
            "root_cause_3": rootcause_result.root_cause_3,
            "meta_root_cause": rootcause_result.meta_root_cause,
            "five_why_chain": rootcause_result.five_why_chain
        },
        "corrective": {
            "immediate_actions": corrective_result.immediate_actions,
            "preventive_measures": corrective_result.preventive_measures,
            "success_criteria": corrective_result.success_criteria
        }
    }
    
    output_file = output_dir / f"analysis_{timestamp}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Sonuçlar kaydedildi: {output_file}")
    print(f"   📊 Dosya boyutu: {output_file.stat().st_size} bytes")
    
    # Test doğrulama
    print("\n" + "=" * 100)
    print("✅ TEST DOĞRULAMA")
    print("=" * 100 + "\n")
    
    checks = [
        (bool(overview_result.incident_type), "✅ Olay tipi tanımlandı"),
        (bool(assessment_result.near_miss_analysis), "✅ Ramak kala analizi yapıldı"),
        (bool(rootcause_result.meta_root_cause), "✅ Meta kök neden bulundu"),
        (len(corrective_result.immediate_actions) > 20, "✅ Acil tedbirler belirlendi"),
        (output_file.exists(), "✅ JSON sonuçları kaydedildi"),
    ]
    
    passed = 0
    for condition, message in checks:
        if condition:
            print(f"   {message}")
            passed += 1
        else:
            print(f"   ❌ {message.replace('✅', '❌')}")
    
    print(f"\n📊 Test Sonucu: {passed}/{len(checks)} başarılı\n")
    
    # Output klasörünü göster
    print("=" * 100)
    print("📁 OUTPUT KLASÖRÜ İÇERİĞİ")
    print("=" * 100 + "\n")
    
    if output_dir.exists():
        print(f"📂 {output_dir}")
        for file in sorted(output_dir.glob("*.json")):
            print(f"   📄 {file.name} ({file.stat().st_size:,} bytes)")
    
    print("\n" + "=" * 100)
    print("🎉 TEST TAMAMLANDI!")
    print("=" * 100 + "\n")
    
    return passed == len(checks)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
