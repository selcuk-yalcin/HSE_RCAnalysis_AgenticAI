"""
TEST: MPT DÜŞEN PARÇA RAMAK KALA - GERÇEK DSPY İLE ONLİNE ÇALIŞMA
===================================================================

Bu test dosyası GERÇEK DSPy framework ve OpenRouter API kullanır.
Mock/simülasyon değil, tam online çalışma.

GEREKSINIMLER:
- dspy paketi kurulu olmalı (pip install dspy)
- .env dosyasında OPENROUTER_API_KEY tanımlı olmalı
"""

import dspy
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Proje root'unu path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# .env dosyasını yükle
load_dotenv()

from agents.model_constants import resolve_openrouter_dspy_model

# ============================================================================
# DSPY YAPINDIRMA - OpenRouter (varsayılan: Gemini Flash)
# ============================================================================

def configure_dspy():
    """DSPy'yi OpenRouter ile yapılandır"""
    print("\n" + "="*80)
    print("🔧 DSPY YAPINDIRILIYOR (OpenRouter)")
    print("="*80)
    
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_key:
        raise ValueError("OPENROUTER_API_KEY bulunamadı! .env dosyasını kontrol edin.")
    
    print(f"✅ API Key bulundu: {openrouter_key[:20]}...")
    
    model_id = resolve_openrouter_dspy_model()
    # DSPy OpenAI wrapper ile OpenRouter
    try:
        lm = dspy.OpenAI(
            model=model_id,
            api_key=openrouter_key,
            api_base="https://openrouter.ai/api/v1",
            model_type="chat",
            max_tokens=4000,
            temperature=0.3
        )
        dspy.settings.configure(lm=lm)
        print("✅ DSPy başarıyla yapılandırıldı")
        print(f"   Model: {model_id}")
        print(f"   API Base: https://openrouter.ai/api/v1")
        return True
    except Exception as e:
        print(f"❌ DSPy yapılandırma hatası: {e}")
        return False


# ============================================================================
# TEST DATA - MPT SARMAL KAPI OLAYI
# ============================================================================

INCIDENT_DATA = {
    "ref_no": "MPT-2026-001-NM",
    "reported_by": "Ahmet Yılmaz (Test Mühendisi)",
    "date": "20.01.2026",
    "time": "09:10",
    "location": "MPT Test Sahası - Test Hücresi 3",
    "incident_type": "Near-miss (Ramak Kala)",
    "description": """
MPT Test Sahası Test Hücresi 3'te, operatör test sonrası ekipmanı çıkarırken sarmal kapının (rolling shutter door) alt bölümündeki bir bağlantı parçası (10x5 cm, yaklaşık 150 gram ağırlığında metal klips) yerinden çıkarak operatörün 30 cm yakınına düştü. 

Operatör o anda eğilmiş durumda ekipman kablosunu toplamakta idi. Parça düştüğünde operatör anormal ses duyarak son anda geri çekildi. Parça betonzemine çarparak sert ses çıkardı. Operatör şoke oldu ancak fiziksel yaralanma olmadı.

Kapı son 3 aydır periyodik bakım kaydı görmemiş, ancak günlük kullanımda herhangi bir anormallik raporlanmamıştı. Olay sonrası yapılan incelemede kapının 4 farklı bağlantı noktasında gevşeme ve yıpranma izleri tespit edildi.

Test hücresinde 2 operatör bulunmaktaydı. İkinci operatör kontrol panelinde olayı görmemiş ancak ses üzerine fark etmiştir. Acil durdurma yapılarak tüm hücre ekipmanları güvenli konuma getirilmiş ve olay güvenlik ekibine bildirilmiştir.
    """.strip(),
    "emergency_response": "Kapı kapatılıp kilitlendi, test hücresi karantinaya alındı, bakım ekibi çağrıldı, olay formu dolduruldu.",
    "witnesses": ["Mehmet Kaya (Operatör 2)", "Ayşe Demir (Vardiya Amiri)"],
    "environment": "İç mekan, aydınlatma yeterli, zemin kuru, sıcaklık 22°C",
    "equipment_involved": ["Sarmal kapı (10 yıllık)", "Metal bağlantı klipsi", "Test ekipmanı"]
}


# ============================================================================
# MAIN TEST
# ============================================================================

def main():
    print("\n" + "="*100)
    print("🧪 MPT TEST SAHASI - GERÇEK DSPY İLE ROOT CAUSE ANALYSIS")
    print("="*100)
    print("\n⚠️  NOT: Bu test ONLINE çalışır - OpenRouter API kullanır")
    print("   Mock/simülasyon değil, gerçek AI analizi yapılacak\n")
    
    # DSPy yapılandır
    if not configure_dspy():
        print("\n❌ DSPy yapılandırılamadı, test sonlandırıldı.")
        return False
    
    # RootCauseAgentV3_1'i import et
    print("\n" + "="*80)
    print("📦 ROOT CAUSE AGENT V3.1 YÜKLENIYOR")
    print("="*80)
    
    try:
        from agents.rootcause_agent_v3_1 import RootCauseAgentV3_1
        print("✅ RootCauseAgentV3_1 başarıyla import edildi")
    except ImportError as e:
        print(f"❌ Import hatası: {e}")
        print("   rootcause_agent_v3_1.py dosyası mevcut mu?")
        return False
    
    # Agent oluştur
    print("\n" + "="*80)
    print("🤖 AGENT OLUŞTURULUYOR")
    print("="*80)
    
    try:
        agent = RootCauseAgentV3_1(
            use_rag=False,  # Hızlı test için RAG kapalı
            enable_diversity_check=True  # Semantic tekrar engelleme aktif
        )
        print("✅ Agent başarıyla oluşturuldu")
        print("   • RAG: Kapalı (hızlı test)")
        print("   • Diversity Check: Aktif")
    except Exception as e:
        print(f"❌ Agent oluşturma hatası: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Part 1 verisi hazırla
    part1_data = {
        "ref_no": INCIDENT_DATA["ref_no"],
        "reported_by": INCIDENT_DATA["reported_by"],
        "date_time": f"{INCIDENT_DATA['date']} {INCIDENT_DATA['time']}",
        "incident_type": INCIDENT_DATA["incident_type"],
        "location": INCIDENT_DATA["location"],
        "description": INCIDENT_DATA["description"],
        "brief_details": {
            "what": "Sarmal kapı metal klipsi düştü",
            "where": INCIDENT_DATA["location"],
            "when": INCIDENT_DATA["date"],
            "who": "Test operatörü",
            "emergency_measures": INCIDENT_DATA["emergency_response"]
        }
    }
    
    part2_data = {
        "event_type": "Near-miss",
        "potential_harm": "Major injury (kafa travması)",
        "investigation_level": "YÜKSEK",
        "priority": "YÜKSEK"
    }
    
    # ANALIZ BAŞLAT
    print("\n" + "="*80)
    print("🔬 ROOT CAUSE ANALYSIS BAŞLIYOR (DSPY + CLAUDE)")
    print("="*80)
    print("\n⏳ Lütfen bekleyin, bu işlem 30-60 saniye sürebilir...")
    print("   (DSPy modülleri Claude API ile analiz yapıyor)\n")
    
    try:
        result = agent.analyze_root_causes(
            part1_data=part1_data,
            part2_data=part2_data,
            investigation_data=None,
            synthesize_meta_root=True
        )
        
        print("\n" + "="*80)
        print("✅ ANALİZ TAMAMLANDI!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Analiz hatası: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # SONUÇLARI GÖSTER
    print("\n" + "="*100)
    print("📊 SONUÇLAR")
    print("="*100)
    
    # Root Causes
    print("\n" + "─"*100)
    print("🎯 ROOT CAUSES (Kök Nedenler)")
    print("─"*100)
    
    if "final_root_causes" in result and result["final_root_causes"]:
        for i, cause in enumerate(result["final_root_causes"], 1):
            code = cause.get("code", "N/A")
            name = cause.get("name", "N/A")
            category = cause.get("category", "N/A")
            desc = cause.get("description", "")
            
            print(f"\n{i}. [{code}] {name}")
            print(f"   Kategori: {category}")
            if desc:
                print(f"   Açıklama: {desc[:100]}...")
    else:
        print("⚠️  Root causes bulunamadı")
    
    # Meta Root Cause
    if "meta_root_cause" in result and result["meta_root_cause"]:
        print("\n" + "─"*100)
        print("🌟 META ROOT CAUSE (Üst Seviye Kök Neden)")
        print("─"*100)
        
        meta = result["meta_root_cause"]
        print(f"\n[{meta.get('code', 'N/A')}] {meta.get('name', 'N/A')}")
        print(f"Kategori: {meta.get('category', 'N/A')}")
        if meta.get('description'):
            print(f"Açıklama: {meta['description']}")
    
    # Analysis Branches
    if "analysis_branches" in result and result["analysis_branches"]:
        print("\n" + "─"*100)
        print("🌳 ANALYSIS BRANCHES (5-Why Zincirleri)")
        print("─"*100)
        
        for branch in result["analysis_branches"]:
            branch_id = branch.get("branch_id", "?")
            direct_cause = branch.get("direct_cause", {})
            root_cause = branch.get("root_cause", {})
            
            print(f"\n▸ Dal {branch_id}:")
            print(f"  Doğrudan Neden: [{direct_cause.get('code', 'N/A')}] {direct_cause.get('name', 'N/A')}")
            print(f"  Kök Neden: [{root_cause.get('code', 'N/A')}] {root_cause.get('name', 'N/A')}")
            
            if "five_why_chain" in branch:
                print(f"  5-Why Zinciri:")
                for why in branch["five_why_chain"]:
                    level = why.get("level", "?")
                    question = why.get("why", "")
                    answer = why.get("because", "")
                    print(f"    Why-{level}: {question}")
                    print(f"    → {answer[:80]}...")
    
    # Kalite Metrikleri
    if "chain_quality_scores" in result and result["chain_quality_scores"]:
        print("\n" + "─"*100)
        print("📈 KALİTE METRİKLERİ")
        print("─"*100)
        
        scores = result["chain_quality_scores"]
        avg_quality = sum(scores) / len(scores) if scores else 0
        
        print(f"\n✓ Zincir Kalitesi: {avg_quality:.1%}")
        print(f"✓ Analiz Dalı Sayısı: {len(result.get('analysis_branches', []))}")
        print(f"✓ Root Cause Sayısı: {len(result.get('final_root_causes', []))}")
        
        if avg_quality >= 0.90:
            print("\n🎉 MÜKEMMEL! Zincir kalitesi çok yüksek (≥90%)")
        elif avg_quality >= 0.75:
            print("\n✅ İYİ! Zincir kalitesi kabul edilebilir (≥75%)")
        else:
            print("\n⚠️  DİKKAT! Zincir kalitesi düşük (<75%)")
    
    # JSON'a kaydet
    print("\n" + "="*100)
    print("💾 SONUÇLAR KAYDEDILIYOR")
    print("="*100)
    
    output_dir = Path("outputs/mpt_falling_part_near_miss")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"dspy_analysis_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Sonuçlar kaydedildi: {output_file}")
    print(f"   📊 Dosya boyutu: {output_file.stat().st_size:,} bytes")
    
    # Test doğrulama
    print("\n" + "="*100)
    print("✅ TEST DOĞRULAMA")
    print("="*100)
    
    checks = [
        (bool(result.get("final_root_causes")), "Root causes bulundu"),
        (bool(result.get("meta_root_cause")), "Meta root cause bulundu"),
        (bool(result.get("analysis_branches")), "Analysis branches oluşturuldu"),
        (len(result.get("analysis_branches", [])) >= 2, "En az 2 analiz dalı var"),
        (output_file.exists(), "JSON sonuçları kaydedildi"),
    ]
    
    passed = 0
    for condition, message in checks:
        status = "✅" if condition else "❌"
        print(f"   {status} {message}")
        if condition:
            passed += 1
    
    print(f"\n📊 Test Sonucu: {passed}/{len(checks)} başarılı")
    
    if passed == len(checks):
        print("\n" + "="*100)
        print("🎉 TÜM TESTLER BAŞARIYLA GEÇTİ!")
        print("="*100)
        print("\n✓ DSPy framework online olarak çalıştı")
        print("✓ OpenRouter API ile Claude kullanıldı")
        print("✓ Root cause analysis tamamlandı")
        print("✓ Sonuçlar JSON formatında kaydedildi")
        print("\n" + "="*100)
        return True
    else:
        print("\n⚠️  Bazı testler başarısız oldu, sonuçları kontrol edin.")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test kullanıcı tarafından durduruldu")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ BEKLENMEYEN HATA: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
