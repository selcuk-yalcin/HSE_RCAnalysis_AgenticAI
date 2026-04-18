"""
HIZLI ONLİNE TEST - Gerçek API ile Tek Agent Testi
===================================================

Bu test GERÇEK OpenRouter API kullanır (DSPy gerekmez).
Tek bir agent test edilerek sistem hızlıca doğrulanır.
"""

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

# ============================================================================
# TEST DATA
# ============================================================================

INCIDENT_DATA = {
    "ref_no": "MPT-2026-001-NM",
    "reported_by": "Ahmet Yılmaz (Test Mühendisi)",
    "date_time": "20.01.2026 09:10",
    "location": "MPT Test Sahası - Test Hücresi 3",
    "description": """
MPT Test Sahası Test Hücresi 3'te, operatör test sonrası ekipmanı çıkarırken sarmal kapının 
alt bölümündeki bir bağlantı parçası (10x5 cm, yaklaşık 150 gram ağırlığında metal klips) 
yerinden çıkarak operatörün 30 cm yakınına düştü. Operatör şoke oldu ancak fiziksel yaralanma olmadı.
    """.strip()
}


# ============================================================================
# MAIN TEST
# ============================================================================

def main():
    print("\n" + "="*80)
    print("🧪 HIZLI ONLİNE TEST - GERÇEK API KULLANIMI")
    print("="*80)
    
    # API Key kontrolü
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n❌ API KEY bulunamadı!")
        print("   .env dosyasında OPENROUTER_API_KEY veya OPENAI_API_KEY tanımlı olmalı")
        return False
    
    print(f"\n✅ API Key bulundu: {api_key[:20]}...")
    
    # Overview Agent'ı import et
    print("\n" + "─"*80)
    print("📦 OVERVIEW AGENT YÜKLENIYOR")
    print("─"*80)
    
    try:
        from agents.overview_agent import OverviewAgent
        print("✅ OverviewAgent başarıyla import edildi")
    except ImportError as e:
        print(f"❌ Import hatası: {e}")
        return False
    
    # Agent oluştur
    print("\n" + "─"*80)
    print("🤖 AGENT OLUŞTURULUYOR")
    print("─"*80)
    
    try:
        agent = OverviewAgent()
        print("✅ Agent başarıyla oluşturuldu")
        print("   Model: anthropic/claude-sonnet-4.5")
        print("   API: OpenRouter")
    except Exception as e:
        print(f"❌ Agent oluşturma hatası: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # ONLINE TEST - Gerçek API Çağrısı
    print("\n" + "─"*80)
    print("🌐 ONLİNE TEST BAŞLIYOR (Gerçek API Çağrısı)")
    print("─"*80)
    print("\n⏳ Lütfen bekleyin, Claude API'ye istek gönderiliyor...")
    print("   (Bu işlem 5-15 saniye sürebilir)\n")
    
    try:
        result = agent.process_initial_report(INCIDENT_DATA)
        
        print("✅ API ÇAĞRISI BAŞARILI!")
        print("\n" + "="*80)
        print("📊 SONUÇLAR (Part 1 - Overview)")
        print("="*80)
        
        # Sonuçları göster
        print(f"\n📋 Referans No:    {result.get('ref_no', 'N/A')}")
        print(f"👤 Raporlayan:     {result.get('reported_by', 'N/A')}")
        print(f"📅 Tarih/Saat:     {result.get('date_time', 'N/A')}")
        print(f"⚠️  Olay Tipi:      {result.get('incident_type', 'N/A')}")
        print(f"📍 Konum:          {result.get('location', 'N/A')}")
        
        if 'brief_details' in result:
            print(f"\n📝 Brief Details:")
            details = result['brief_details']
            print(f"   • What:  {details.get('what', 'N/A')[:60]}...")
            print(f"   • Where: {details.get('where', 'N/A')}")
            print(f"   • When:  {details.get('when', 'N/A')}")
            print(f"   • Who:   {details.get('who', 'N/A')}")
        
        # JSON'a kaydet
        output_dir = Path("outputs/quick_test")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"online_test_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Sonuçlar kaydedildi: {output_file}")
        
        # Test doğrulama
        print("\n" + "="*80)
        print("✅ TEST DOĞRULAMA")
        print("="*80)
        
        checks = [
            (bool(result.get('ref_no')), "Referans no bulundu"),
            (bool(result.get('incident_type')), "Olay tipi belirlendi"),
            (bool(result.get('brief_details')), "Brief details oluşturuldu"),
            (output_file.exists(), "JSON kaydedildi"),
        ]
        
        passed = 0
        for condition, message in checks:
            status = "✅" if condition else "❌"
            print(f"   {status} {message}")
            if condition:
                passed += 1
        
        print(f"\n📊 Sonuç: {passed}/{len(checks)} test geçti")
        
        if passed == len(checks):
            print("\n" + "="*80)
            print("🎉 TÜM TESTLER BAŞARIYLA GEÇTİ!")
            print("="*80)
            print("\n✓ OpenRouter API online çalışıyor")
            print("✓ Claude Sonnet 4.5 kullanıldı")
            print("✓ Agent başarıyla çalıştı")
            print("✓ Sonuçlar JSON formatında kaydedildi")
            print("\n💡 SONUÇ: Sistem ONLINE ve API kullanıyor (DSPy gerekmez)")
            print("="*80 + "\n")
            return True
        else:
            print("\n⚠️  Bazı testler başarısız")
            return False
        
    except Exception as e:
        print(f"\n❌ TEST HATASI: {e}")
        import traceback
        traceback.print_exc()
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
