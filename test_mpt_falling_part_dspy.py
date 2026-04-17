"""
TEST: MPT DÜŞEN PARÇA RAMAK KALA - DSPY İLE YAPSAL ANALIZ
==========================================================

Senaryoyu DSpy framework'ü kullanarak yapılandırılmış çıktılar üzerinden analiz eden test.
DSpy signatures ve modules ile incident analizi yapılır ve optimizasyon yapılabilir.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

import dspy
from dspy.signatures.signature import Signature
from dspy.functional.functional import TypedChainOfThought


# ============================================================================
# 1. DSPY SİGNATURES - YAPSAL GİRDİ/ÇIKTI TANIMLARI
# ============================================================================

class IncidentOverviewSignature(Signature):
    """Ramak kala olayının genel özeti ve ilk değerlendirmesini yap."""
    
    incident_description: str = dspy.InputField(desc="Olay açıklaması ve detayları")
    incident_date: str = dspy.InputField(desc="Olay tarihi ve saati")
    location: str = dspy.InputField(desc="Olay yeri")
    
    incident_type: str = dspy.OutputField(desc="Olay türü (Ramak Kala, LTI, vb.)")
    severity_level: str = dspy.OutputField(desc="Ciddiyet seviyesi (Çok Yüksek, Yüksek, vb.)")
    potential_harm: str = dspy.OutputField(desc="Potansiyel zarar türleri")
    summary: str = dspy.OutputField(desc="Olay özeti (2-3 cümle)")


class IncidentAssessmentSignature(Signature):
    """Ramak kala olayının risk değerlendirmesi."""
    
    overview: str = dspy.InputField(desc="Olay özeti")
    injury_description: str = dspy.InputField(desc="Yaralanma tanımı (gerçek ve potansiyel)")
    
    assessment_result: str = dspy.OutputField(desc="Risk değerlendirmesi")
    potential_consequences: str = dspy.OutputField(desc="Potansiyel sonuçlar listesi")
    near_miss_analysis: str = dspy.OutputField(desc="Ramak kala analizi - neden ciddi değil ama riski yüksek")


class RootCauseAnalysisSignature(Signature):
    """Ramak kala olayının kök nedenleri - 5-WHY metodolojisi."""
    
    incident_summary: str = dspy.InputField(desc="Olay özeti")
    technical_failure: str = dspy.InputField(desc="Teknik başarısızlık (kopan parça, mekanizma, vb.)")
    human_factor: str = dspy.InputField(desc="İnsan faktörü (anormal ses duyuldu ama işlem devam etti)")
    
    root_cause_1: str = dspy.OutputField(desc="Birinci kök neden")
    root_cause_2: str = dspy.OutputField(desc="İkinci kök neden")
    root_cause_3: str = dspy.OutputField(desc="Üçüncü kök neden")
    meta_root_cause: str = dspy.OutputField(desc="Tüm kök nedenlerin ortak paydası (meta root cause)")
    five_why_chain: str = dspy.OutputField(desc="5-WHY zinciri açıklaması")


class CorrectiveActionSignature(Signature):
    """Ramak kala olayı için düzeltici/önleyici tedbirler."""
    
    root_causes: str = dspy.InputField(desc="Tespit edilen kök nedenler")
    potential_harm: str = dspy.InputField(desc="Potansiyel zarar")
    
    immediate_actions: str = dspy.OutputField(desc="Acil alınacak tedbirler")
    preventive_measures: str = dspy.OutputField(desc="Uzun vadeli önleyici tedbirler")
    success_criteria: str = dspy.OutputField(desc="Tamamlanma kriterleri")


# ============================================================================
# 2. DSPY MODULES - AJANLAR
# ============================================================================

class IncidentOverviewModule(dspy.Module):
    """Olay özeti modülü."""
    
    def __init__(self):
        super().__init__()
        self.overview_chain = TypedChainOfThought(IncidentOverviewSignature)
    
    def forward(self, incident_data):
        return self.overview_chain(
            incident_description=incident_data.get("description", ""),
            incident_date=f"{incident_data.get('incident_date')} {incident_data.get('incident_time')}",
            location=incident_data.get("location", "")
        )


class IncidentAssessmentModule(dspy.Module):
    """Risk değerlendirmesi modülü."""
    
    def __init__(self):
        super().__init__()
        self.assessment_chain = TypedChainOfThought(IncidentAssessmentSignature)
    
    def forward(self, overview_result, incident_data):
        return self.assessment_chain(
            overview=overview_result.summary,
            injury_description=incident_data.get("injury_description", "")
        )


class RootCauseAnalysisModule(dspy.Module):
    """Kök neden analizi modülü."""
    
    def __init__(self):
        super().__init__()
        self.rootcause_chain = TypedChainOfThought(RootCauseAnalysisSignature)
    
    def forward(self, overview_result, incident_data):
        return self.rootcause_chain(
            incident_summary=overview_result.summary,
            technical_failure="Sarmal kapı üst mekanizmasından metal parça koparak düştü",
            human_factor="Anormal ses fark edildi ama işlem durdurulmadı (tehlike algısı eksik)"
        )


class CorrectiveActionModule(dspy.Module):
    """Düzeltici tedbirler modülü."""
    
    def __init__(self):
        super().__init__()
        self.corrective_chain = TypedChainOfThought(CorrectiveActionSignature)
    
    def forward(self, root_causes, incident_data):
        return self.corrective_chain(
            root_causes=root_causes,
            potential_harm=incident_data.get("potential_severity", "")
        )


class MPTIncidentPipeline(dspy.Module):
    """Tam incident analiz pipeline'ı."""
    
    def __init__(self):
        super().__init__()
        self.overview = IncidentOverviewModule()
        self.assessment = IncidentAssessmentModule()
        self.rootcause = RootCauseAnalysisModule()
        self.corrective = CorrectiveActionModule()
    
    def forward(self, incident_data):
        # Adım 1: Overview
        print("📋 Adım 1: Olay Özeti Oluşturuluyor...")
        overview_result = self.overview.forward(incident_data)
        print(f"   ✅ Olay Tipi: {overview_result.incident_type}")
        print(f"   ✅ Ciddiyet: {overview_result.severity_level}")
        
        # Adım 2: Assessment
        print("\n📋 Adım 2: Risk Değerlendirmesi Yapılıyor...")
        assessment_result = self.assessment.forward(overview_result, incident_data)
        print(f"   ✅ Değerlendirme: {assessment_result.assessment_result[:80]}...")
        
        # Adım 3: Root Cause
        print("\n📋 Adım 3: Kök Neden Analizi Yapılıyor (5-WHY)...")
        rootcause_result = self.rootcause.forward(overview_result, incident_data)
        print(f"   ✅ Birinci Kök Neden: {rootcause_result.root_cause_1[:60]}...")
        print(f"   ✅ İkinci Kök Neden: {rootcause_result.root_cause_2[:60]}...")
        print(f"   ✅ Meta Kök Neden: {rootcause_result.meta_root_cause[:60]}...")
        
        # Adım 4: Corrective Actions
        print("\n📋 Adım 4: Düzeltici Tedbirler Belirleniyor...")
        corrective_result = self.corrective.forward(
            f"{rootcause_result.root_cause_1}\n{rootcause_result.root_cause_2}\n{rootcause_result.root_cause_3}",
            incident_data
        )
        print(f"   ✅ Acil Tedbirler: {corrective_result.immediate_actions[:60]}...")
        
        return {
            "overview": overview_result,
            "assessment": assessment_result,
            "rootcause": rootcause_result,
            "corrective": corrective_result
        }


# ============================================================================
# 3. TEST VERİLERİ
# ============================================================================

INCIDENT_DATA = {
    "ref_no": "02-26",
    "report_date": "21.01.2026",
    "incident_date": "20.01.2026",
    "incident_time": "09:10",
    "incident_type": "Ramak Kala (Near Miss)",
    "location": "MPT Test Sahası",
    "activity": "Test - Sarmal Kapı Kapatma İşlemi",
    "reported_by": "Hakan Sevil",
    "description": """
MPT Test Sahasında bulunan sarmal kapının kapatılması işlemi sırasında, kapının üst 
mekanizmasından anormal sesler gelmiştir. Seslerin hemen ardından, kapının üst bölümünde 
yer alan bir parçanın yerinden koparak düştüğü tespit edilmiştir.

Kopan parça, olay esnasında test sahasında bulunan çalışanın yaklaşık 2 metre yakınına 
düşmüştür. Olay sırasında herhangi bir yaralanma meydana gelmemiştir. Ancak olay, 
potansiyel yaralanma riski (near miss) oluşturmuştur.

Potansiyel Zarar:
- Parça ağırlığı: Orta-ağır metal parça (mekanizma parçası)
- Düşme yüksekliği: ~3-4 metre
- Potansiyel vuruş bölgesi: Baş, omuz, sırt
- Sonuç olabilirdi: Kafatası kırığı, omurga hasarı, ölüm
""",
    "injury_description": """
Gerçek Zarar: Kişisel yaralanma yok (şans faktörü - 2 metre mesafe).

Potansiyel Zarar:
- Ölüm: Parça baş bölgesine düşseydi kafatası kırığı/iç kanama/ölüm
- Kalıcı Sakatlık: Omurga hasarı/felç
- Ağır Yaralanma: Kırıklar, iç kanama, uzun süreli iş göremezlik
- Psikolojik: Travma

Ramak Kala Değerlendirmesi: Çok Yüksek Riskli
""",
    "potential_severity": "ÇOK YÜKSEK (baş/omur bölgesine düşme = ölüm/kalıcı sakatlık riski)",
    "witnesses": [
        "Vardiya arkadaşı 1 (anormal ses duydu)",
        "Vardiya arkadaşı 2 (düşme anını gördü)"
    ],
    "photos_available": True,
    "investigation_level": "Seviye A (Yüksek)"
}


# ============================================================================
# 4. TEST FONKSİYONU
# ============================================================================

def test_mpt_near_miss_with_dspy():
    """MPT Ramak Kala Olayını DSpy ile test et."""
    
    print("=" * 100)
    print("⚠️  MPT TEST SAHASI SARMAL KAPI DÜŞEN PARÇA RAMAK KALA OLAYI - DSPY TESTİ")
    print("=" * 100)
    print()
    
    # DSpy LM setup (OpenAI API kullanıyoruz)
    try:
        lm = dspy.OpenAI(
            model="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7,
            max_tokens=1000
        )
        dspy.settings.configure(lm=lm)
        print("✅ DSpy LM başlatıldı (GPT-4o)")
    except Exception as e:
        print(f"⚠️  OpenAI API hatası, Claude kullanılıyor: {e}")
        try:
            lm = dspy.Anthropic(
                model="claude-opus-4-7",
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                temperature=0.7,
                max_tokens=1000
            )
            dspy.settings.configure(lm=lm)
            print("✅ DSpy LM başlatıldı (Claude Opus 4.7)")
        except Exception as e2:
            print(f"❌ LM başlatma hatası: {e2}")
            raise
    
    # Pipeline oluştur ve çalıştır
    print("\n" + "=" * 100)
    print("🤖 DSpy Pipeline Başlatılıyor...")
    print("=" * 100 + "\n")
    
    pipeline = MPTIncidentPipeline()
    results = pipeline.forward(INCIDENT_DATA)
    
    # Sonuçları göster
    print("\n" + "=" * 100)
    print("📊 DSPY ANALIZ SONUÇLARI")
    print("=" * 100)
    
    print("\n" + "─" * 100)
    print("1️⃣  OVERVIEW (Olay Özeti)")
    print("─" * 100)
    overview = results["overview"]
    print(f"   Olay Tipi: {overview.incident_type}")
    print(f"   Ciddiyet: {overview.severity_level}")
    print(f"   Potansiyel Zarar: {overview.potential_harm}")
    print(f"   Özet: {overview.summary}")
    
    print("\n" + "─" * 100)
    print("2️⃣  ASSESSMENT (Risk Değerlendirmesi)")
    print("─" * 100)
    assessment = results["assessment"]
    print(f"   Değerlendirme: {assessment.assessment_result}")
    print(f"   Potansiyel Sonuçlar:")
    for line in assessment.potential_consequences.split('\n'):
        if line.strip():
            print(f"      • {line.strip()}")
    print(f"\n   Ramak Kala Analizi:")
    for line in assessment.near_miss_analysis.split('\n'):
        if line.strip():
            print(f"      • {line.strip()}")
    
    print("\n" + "─" * 100)
    print("3️⃣  ROOT CAUSE ANALYSIS (Kök Neden Analizi - 5-WHY)")
    print("─" * 100)
    rootcause = results["rootcause"]
    print(f"   Kök Neden 1: {rootcause.root_cause_1}")
    print(f"   Kök Neden 2: {rootcause.root_cause_2}")
    print(f"   Kök Neden 3: {rootcause.root_cause_3}")
    print(f"\n   Meta Kök Neden (Ortak Payda):")
    print(f"      {rootcause.meta_root_cause}")
    print(f"\n   5-WHY Zinciri:")
    for line in rootcause.five_why_chain.split('\n'):
        if line.strip():
            print(f"      {line.strip()}")
    
    print("\n" + "─" * 100)
    print("4️⃣  CORRECTIVE ACTIONS (Düzeltici Tedbirler)")
    print("─" * 100)
    corrective = results["corrective"]
    print(f"   Acil Tedbirler:")
    for line in corrective.immediate_actions.split('\n'):
        if line.strip():
            print(f"      • {line.strip()}")
    print(f"\n   Uzun Vadeli Önleyici Tedbirler:")
    for line in corrective.preventive_measures.split('\n'):
        if line.strip():
            print(f"      • {line.strip()}")
    print(f"\n   Başarı Kriterleri:")
    for line in corrective.success_criteria.split('\n'):
        if line.strip():
            print(f"      • {line.strip()}")
    
    # Sonuçları JSON'a kaydet
    print("\n" + "=" * 100)
    print("💾 SONUÇLAR KAYDEDILIYOR")
    print("=" * 100 + "\n")
    
    output_dir = Path("outputs/mpt_falling_part_near_miss")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    output_data = {
        "incident_ref": INCIDENT_DATA["ref_no"],
        "test_timestamp": timestamp,
        "analysis_method": "DSpy Chain-of-Thought",
        "overview": {
            "incident_type": overview.incident_type,
            "severity_level": overview.severity_level,
            "potential_harm": overview.potential_harm,
            "summary": overview.summary
        },
        "assessment": {
            "assessment_result": assessment.assessment_result,
            "potential_consequences": assessment.potential_consequences,
            "near_miss_analysis": assessment.near_miss_analysis
        },
        "rootcause": {
            "root_cause_1": rootcause.root_cause_1,
            "root_cause_2": rootcause.root_cause_2,
            "root_cause_3": rootcause.root_cause_3,
            "meta_root_cause": rootcause.meta_root_cause,
            "five_why_chain": rootcause.five_why_chain
        },
        "corrective": {
            "immediate_actions": corrective.immediate_actions,
            "preventive_measures": corrective.preventive_measures,
            "success_criteria": corrective.success_criteria
        }
    }
    
    with open(output_dir / f"dspy_analysis_{timestamp}.json", 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ DSpy analiz sonuçları kaydedildi: {output_dir}/dspy_analysis_{timestamp}.json")
    
    # Test doğrulama
    print("\n" + "=" * 100)
    print("✅ TEST DOĞRULAMA")
    print("=" * 100 + "\n")
    
    assertions = [
        (overview.incident_type.lower().__contains__("ramak") or overview.incident_type.lower().__contains__("near"), 
         "✅ Olay tipi 'Ramak Kala' olarak tanımlandı"),
        (assessment.near_miss_analysis != "", 
         "✅ Ramak kala analizi yapıldı"),
        (rootcause.meta_root_cause != "", 
         "✅ Meta kök neden bulundu"),
        (len(corrective.immediate_actions) > 10, 
         "✅ Düzeltici tedbirler belirlendi"),
    ]
    
    passed = 0
    for condition, message in assertions:
        if condition:
            print(f"   {message}")
            passed += 1
        else:
            print(f"   ❌ {message.replace('✅', '❌')}")
    
    print(f"\n📊 Test Sonucu: {passed}/{len(assertions)} başarılı\n")
    
    return results, output_data


# ============================================================================
# 5. MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        results, output_data = test_mpt_near_miss_with_dspy()
        
        print("\n" + "=" * 100)
        print("🎉 MPT RAMAK KALA - DSPY ANALIZ TESTİ TAMAMLANDI!")
        print("=" * 100 + "\n")
        
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ TEST HATASI: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
