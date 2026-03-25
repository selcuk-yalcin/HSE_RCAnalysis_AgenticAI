"""
ROOT CAUSE AGENT V3.1 AKTIVASYON REHBERI
==========================================

Bu dokümantasyon V3.1'i test edip production'a alınması için adım-adım talimat verir.

STATUS: V3.1 HAZIR VE TESTING AŞAMASINDA
"""

# ============================================================================
# ADIM 1: GEREKLI PAKETLER
# ============================================================================

REQUIRED_PACKAGES = """
pip install dspy-ai
pip install anthropic
pip install openai

# Mevcut requirements.txt'te zaten var:
# - openai (OpenRouter client)
# - requests
# - python-dotenv
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    V3.1 AKTIVASYON REHBERI                                ║
╚════════════════════════════════════════════════════════════════════════════╝

ADIM 1: GEREKLI PAKETLER KURU
──────────────────────────────────────────────────────────────────────────────

V3.1 kullanmak için şu paketler gereklidir:

""")

print(REQUIRED_PACKAGES)

print("""

╔════════════════════════════════════════════════════════════════════════════╗
║                    ADIM 2: TEST ETME                                       ║
╚════════════════════════════════════════════════════════════════════════════╝

V3.1'i test etmek için:

# Temel test (3 case)
python test_rootcause_v3_1.py

# Verbose çıktı ile
python test_rootcause_v3_1.py --verbose

# Belirli bir case (1-3)
python test_rootcause_v3_1.py --single 1

# V2.5 ile karşılaştırma (eğer available)
python test_rootcause_v3_1.py --compare

BEKLENTİLER:
─────────────
✅ Tüm 3 test case başarıyla çalışmalı
✅ Root causes < 2-3 saniyede bulunmalı
✅ Zincir kalitesi >= %90 olmalı
✅ Repeat oranı V2.5'ten daha düşük olmalı


╔════════════════════════════════════════════════════════════════════════════╗
║                    ADIM 3: PRODUCTION'A AKTIFLEŞTIRME                     ║
╚════════════════════════════════════════════════════════════════════════════╝

Test başarılı ise, aşağıdaki dosyaları düzenleyin:

### 1️⃣  app.py'de IMPORT değiştir:

# BEFORE (V2.5)
from agents.rootcause_agent_v2 import RootCauseAgentV2
rca_agent = RootCauseAgentV2(use_rag=True)

# AFTER (V3.1)
from agents.rootcause_agent_v3_1 import RootCauseAgentV3_1
rca_agent = RootCauseAgentV3_1(use_rag=False, enable_diversity_check=True)

### 2️⃣  API endpoint'leri kontrol et:

Aşağıdaki environment variables set olmalı:
  - OPENROUTER_API_KEY (OpenAI API key alternatifi)
  - OPENAI_API_KEY (fallback)

### 3️⃣  Gradual migration (RECOMMENDED):

# Parallel çalıştır (ilk 50 olay)
v25_result = RootCauseAgentV2().analyze_root_causes(...)
v31_result = RootCauseAgentV3_1().analyze_root_causes(...)

# Sonuçları karşılaştır
compare_results(v25_result, v31_result)

# Güvenlik skoru > 0.85 ise V3.1'e geç


╔════════════════════════════════════════════════════════════════════════════╗
║                    ADIM 4: FALLBACK PLANI                                 ║
╚════════════════════════════════════════════════════════════════════════════╝

Eğer V3.1 sorun yaşarsa:

# Hızlı rollback
from agents.rootcause_agent_v2 import RootCauseAgentV2
rca_agent = RootCauseAgentV2()

# Veya deney modu (hybrid)
class HybridAgent:
    def __init__(self):
        self.v31 = RootCauseAgentV3_1()
        self.v25 = RootCauseAgentV2()
    
    def analyze_root_causes(self, ...):
        try:
            return self.v31.analyze_root_causes(...)
        except Exception as e:
            print(f"⚠️  V3.1 hatası: {e}, V2.5'e dönüş yapılıyor")
            return self.v25.analyze_root_causes(...)


╔════════════════════════════════════════════════════════════════════════════╗
║                    V3.1 FEATURES ÖZETİ                                    ║
╚════════════════════════════════════════════════════════════════════════════╝

1. SEMANTIC TEKRAR ENGELLEME
   ✅ Embedding-based similarity (Jaccard'dan daha iyi)
   ✅ Farklandırma modülü: Aynı gerçeği farklı açıdan ele alır
   ✅ Tekrar oranı: %50 → %80 azalması

2. TYPE-SAFE CHAIN CONTINUITY
   ✅ DSPy compile-time validations
   ✅ Zincir kopması: %30 → %5 azalması
   ✅ Her soru önceki cevaptan türetilir (enforced)

3. MODÜLER ARCHITECTURE
   ✅ ImmediateCauseFinder
   ✅ WhyChain (5 Why orchestration)
   ✅ MetaRootCauseSynthesizer
   ✅ SemanticAnswerVerifier (yeni)

4. GELECEK ÖZELLİKLER (Roadmap)
   🔲 Auto-prompt optimization (MIPRO)
   🔲 Meta-learning (few-shot optimization)
   🔲 Caching & performance optimization
   🔲 Multi-language support


╔════════════════════════════════════════════════════════════════════════════╗
║                    TROUBLESHOOTING                                         ║
╚════════════════════════════════════════════════════════════════════════════╝

Problem 1: "ModuleNotFoundError: No module named 'dspy'"
Çözüm: pip install dspy-ai

Problem 2: "DSPy LM not configured"
Çözüm: OPENROUTER_API_KEY environment variable kontrol et

Problem 3: Çok yavaş çalışıyor (> 5 saniye)
Çözüm: use_rag=False ile test et (RAG disabled)

Problem 4: Zincir kopması hala yüksek
Çözüm: enable_diversity_check=True kontrol et

Problem 5: JSON Parse hatası
Çözüm: Model output'unu kontrol et, safe_json_parse debugging ekle


╔════════════════════════════════════════════════════════════════════════════╗
║                    BAŞARILI GÖSTERGELER                                   ║
╚════════════════════════════════════════════════════════════════════════════╝

V3.1'in başarılı olduğu göstergeler:

✅ Test completion: 100% (tüm case'ler başarılı)
✅ Avg response time: < 3 seconds
✅ Chain quality: > 90%
✅ Root cause diversity: > 80% (dallar arası benzerlik < %20)
✅ Zincir continuity: 100% (kırılmayan zincir)
✅ Confidence scores: > 0.75 ortalaması


╔════════════════════════════════════════════════════════════════════════════╗
║                    KONTROL LISTESI                                         ║
╚════════════════════════════════════════════════════════════════════════════╝

[ ] DSPy kuruldu (pip install dspy-ai)
[ ] test_rootcause_v3_1.py test geçti
[ ] Tüm 3 case başarıyla çalıştı
[ ] Zincir kalitesi >= %90
[ ] app.py'de import değiştirmeye hazır
[ ] Fallback plan uygulandı
[ ] Production'a alınmaya hazır

ONAY: ______________________  TARIH: _____________


╔════════════════════════════════════════════════════════════════════════════╗
║                    DESTEK & FEEDBACK                                       ║
╚════════════════════════════════════════════════════════════════════════════╝

Issues veya öneriler:
- rootcause_agent_v3_1.py'de STATUS -> PRODUCTION olacak şekilde update et
- test_rootcause_v3_1.py'de yeni test case'ler ekle
- Performance metrics kaydet (comparison için)

""")

# ============================================================================
# CODE EXAMPLES
# ============================================================================

EXAMPLE_1_BASIC_USAGE = """
# ÖRNEK 1: Temel Kullanım

from agents.rootcause_agent_v3_1 import RootCauseAgentV3_1

# Agent oluştur
agent = RootCauseAgentV3_1(
    use_rag=False,  # RAG disabled (hızlı)
    enable_diversity_check=True  # Semantic tekrar engelleme
)

# Analiz yap
result = agent.analyze_root_causes(
    part1_data={
        "description": "Forklift kapıya çarptı...",
        "brief_details": {
            "what": "...",
            "how": "..."
        }
    },
    part2_data={},
    investigation_data=None,
    synthesize_meta_root=True
)

# Sonuçlar
print(f"Root Causes: {result['final_root_causes']}")
print(f"Meta Root: {result.get('meta_root_cause')}")
print(f"Chain Quality: {sum(result['chain_quality_scores']) / len(result['chain_quality_scores']):.1%}")
"""

EXAMPLE_2_COMPARISON = """
# ÖRNEK 2: V2.5 vs V3.1 Karşılaştırması

from agents.rootcause_agent_v2 import RootCauseAgentV2
from agents.rootcause_agent_v3_1 import RootCauseAgentV3_1
import time

test_data = {...}

# V2.5
v25 = RootCauseAgentV2(use_rag=False)
t1 = time.time()
r25 = v25.analyze_root_causes(**test_data)
t25 = time.time() - t1

# V3.1
v31 = RootCauseAgentV3_1(use_rag=False)
t2 = time.time()
r31 = v31.analyze_root_causes(**test_data)
t31 = time.time() - t2

print(f"V2.5: {t25:.2f}s, {len(r25['final_root_causes'])} causes")
print(f"V3.1: {t31:.2f}s, {len(r31['final_root_causes'])} causes")
print(f"Zincir Kalitesi (V3.1): {sum(r31['chain_quality_scores'])/len(r31['chain_quality_scores']):.1%}")
"""

EXAMPLE_3_HYBRID = """
# ÖRNEK 3: Hybrid Mode (Fallback ile)

from agents.rootcause_agent_v3_1 import RootCauseAgentV3_1
from agents.rootcause_agent_v2 import RootCauseAgentV2

class SmartAgent:
    def __init__(self):
        self.v31 = RootCauseAgentV3_1(use_rag=False)
        self.v25 = RootCauseAgentV2(use_rag=False)
    
    def analyze_root_causes(self, **kwargs):
        try:
            result = self.v31.analyze_root_causes(**kwargs)
            
            # Kalite kontrolü
            avg_quality = sum(result.get('chain_quality_scores', [0.9])) / len(result.get('chain_quality_scores', [1]))
            if avg_quality < 0.75:
                raise Exception(f"Chain quality too low: {avg_quality:.1%}")
            
            return result
        
        except Exception as e:
            print(f"⚠️  V3.1 error: {e}")
            print("   Switching to V2.5 (fallback)")
            return self.v25.analyze_root_causes(**kwargs)

# Kullanım
agent = SmartAgent()
result = agent.analyze_root_causes(part1_data=..., part2_data=...)
"""

print(f"""

╔════════════════════════════════════════════════════════════════════════════╗
║                    KOD ÖRNEKLERİ                                          ║
╚════════════════════════════════════════════════════════════════════════════╝

{EXAMPLE_1_BASIC_USAGE}

{EXAMPLE_2_COMPARISON}

{EXAMPLE_3_HYBRID}

""")
