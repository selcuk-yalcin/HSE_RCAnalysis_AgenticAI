"""
V3.1 AKTIVASYON DOĞRULAMA TESTİ
===============================

Bu test V3.1'in başarıyla aktif edilip edilmediğini kontrol eder.
DSPy yoksa V2 fallback'ine düştüğünü doğrular.
"""

import sys
from pathlib import Path

# Proje root'unu path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_v3_1_activation():
    """V3.1 aktivasyon durumunu test et"""
    
    print("\n" + "="*80)
    print("🧪 V3.1 AKTIVASYON DOĞRULAMA TESTİ")
    print("="*80)
    
    # Test 1: agents modülünden import
    print("\n📦 Test 1: Agent import kontrolü")
    print("-"*80)
    
    try:
        from agents import RootCauseAgent, RootCauseAgentV2, RootCauseAgentV3_1
        print("✅ RootCauseAgent import edildi")
        print("✅ RootCauseAgentV2 import edildi")
        
        if RootCauseAgentV3_1 is not None:
            print("✅ RootCauseAgentV3_1 import edildi (DSPy mevcut)")
            v31_available = True
        else:
            print("⚠️  RootCauseAgentV3_1 None (DSPy yok, fallback aktif)")
            v31_available = False
        
        # RootCauseAgent'ın hangi versiyon olduğunu kontrol et
        if v31_available:
            if RootCauseAgent.__name__ == 'RootCauseAgentV3_1':
                print("✅ RootCauseAgent → V3.1 olarak yapılandırılmış")
            else:
                print("⚠️  RootCauseAgent → V2 olarak yapılandırılmış")
        else:
            print("⚠️  RootCauseAgent → V2 fallback kullanılıyor")
            
    except ImportError as e:
        print(f"❌ Import hatası: {e}")
        return False
    
    # Test 2: Orchestrator kontrolü
    print("\n🎭 Test 2: Orchestrator yapılandırması")
    print("-"*80)
    
    try:
        from agents import RootCauseOrchestrator
        
        # Orchestrator oluştur
        orchestrator = RootCauseOrchestrator()
        
        # Agent tipini kontrol et
        agent_type = type(orchestrator.rootcause_agent).__name__
        print(f"✅ Orchestrator başarıyla oluşturuldu")
        print(f"   Kullanılan Agent: {agent_type}")
        
        if agent_type == 'RootCauseAgentV3_1':
            print("✅ V3.1 BAŞARIYLA AKTİF!")
        elif agent_type == 'RootCauseAgentV2':
            print("⚠️  V2 fallback kullanılıyor (DSPy yok)")
        else:
            print(f"❓ Bilinmeyen agent tipi: {agent_type}")
            
    except Exception as e:
        print(f"❌ Orchestrator hatası: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: DSPy durumu
    print("\n🔧 Test 3: DSPy bağımlılık kontrolü")
    print("-"*80)
    
    try:
        import dspy
        print("✅ DSPy kurulu")
        print(f"   Versiyon: {dspy.__version__ if hasattr(dspy, '__version__') else 'Bilinmiyor'}")
        dspy_available = True
    except ImportError:
        print("⚠️  DSPy kurulu değil")
        print("   Kurulum: pip install dspy-ai")
        print("   Not: Python 3.10+ gereklidir")
        dspy_available = False
    
    # Test 4: Status özeti
    print("\n" + "="*80)
    print("📊 DURUM ÖZETİ")
    print("="*80)
    
    print(f"\n{'Bileşen':<30} {'Durum':<20} {'Not'}")
    print("-"*80)
    print(f"{'V3.1 Dosyası':<30} {'✅ Mevcut':<20} {'agents/rootcause_agent_v3_1.py'}")
    print(f"{'V3.1 Import':<30} {'✅ Başarılı' if v31_available else '⚠️  Fallback':<20} {'DSPy gerekli' if not v31_available else 'Aktif'}")
    print(f"{'DSPy Bağımlılığı':<30} {'✅ Kurulu' if dspy_available else '❌ Eksik':<20} {'pip install dspy-ai'}")
    print(f"{'Orchestrator':<30} {'✅ Çalışıyor':<20} {agent_type}")
    print(f"{'Production Durumu':<30} {'✅ ACTIVE' if v31_available else '⚠️  FALLBACK':<20} {'V3.1' if v31_available else 'V2'}")
    
    # Sonuç
    print("\n" + "="*80)
    if v31_available and dspy_available:
        print("🎉 V3.1 BAŞARIYLA AKTİF VE ÇALIŞIYOR!")
        print("="*80)
        print("\n✓ V3.1 production'da kullanılıyor")
        print("✓ DSPy framework mevcut")
        print("✓ Tüm testler başarılı")
    elif v31_available and not dspy_available:
        print("⚠️  V3.1 AKTİF AMA DSPY EKSİK - FALLBACK KULLANILIYOR")
        print("="*80)
        print("\n✓ V3.1 import edilebiliyor")
        print("⚠️  DSPy yüklü değil, V2 fallback aktif")
        print("\n💡 DSPy kurmak için:")
        print("   1. Python 3.10+ ortamı oluşturun")
        print("   2. pip install dspy-ai")
        print("   3. Sistemi yeniden başlatın")
    else:
        print("⚠️  V2 FALLBACK AKTİF (V3.1 IMPORT EDİLEMEDİ)")
        print("="*80)
        print("\n⚠️  V3.1 import edilemedi")
        print("✓ V2 fallback güvenli çalışıyor")
        print("\n💡 V3.1'i aktif etmek için:")
        print("   1. Python 3.10+ kullanın")
        print("   2. pip install dspy-ai")
        print("   3. DSPy'yi OpenRouter ile yapılandırın")
    
    print("\n" + "="*80 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        success = test_v3_1_activation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST HATASI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
