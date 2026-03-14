"""
RAG Integration Guide & Example
==============================

Bu dosya, RAG systemi'ni rootcause_agent_v2.py içine entegre etmek için 
adımları ve kod örneklerini sağlar.

Entegrasyon Adımları:
  1. RAGAnalyzer'ı import et
  2. Prompt hazırlama sırasında augment_prompt() kullan
  3. LLM'e augmented prompt'u gönder

Örnek Kullanım:
"""

import sys
from pathlib import Path

# Proje kök dizinini Python path'e ekle
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from rag_pipeline.retrieval import RAGAnalyzer

# Basit Örnek
def analyze_incident_with_rag(incident_description: str) -> dict:
    """
    Incident'ı RAG context'i ile analiz et.
    
    Args:
        incident_description: Incident açıklaması
    
    Returns:
        Analysis sonucu
    """
    
    # RAG Analyzer'ı başlat
    analyzer = RAGAnalyzer()
    
    # Orijinal sistem prompt'u
    system_prompt = """
    Siz bir HSE Kök Neden Analizi ajanısınız.
    Verilen incident'ı detaylı şekilde analiz ederek:
    1. Kök nedenleri (root causes) belirleyin
    2. Immediate sebepleri (immediate causes) tanıyın
    3. İyileştirme önerileri sunun
    """
    
    # Prompt'u RAG context'i ile zenginleştir
    augmented_prompt = analyzer.augment_prompt(
        original_prompt=system_prompt,
        query=incident_description,
        k=5,
        language="tr"
    )
    
    print("=" * 70)
    print("📊 AUGMENTED PROMPT")
    print("=" * 70)
    print(augmented_prompt[:1000])
    print("\n... [kesintili, toplam uzunluk:", len(augmented_prompt), "char]")
    
    # Buradan sonra, augmented_prompt'u LLM'e gönderebilirsiniz
    # response = call_llm(augmented_prompt, incident_description)
    
    analyzer.close()
    
    return {
        "status": "augmented",
        "prompt_length": len(augmented_prompt),
        "message": "Augmented prompt hazır. LLM'e gönder."
    }


# İleri Örnek: Rootcause Agent ile Entegrasyon
def integrate_into_rootcause_agent_v2():
    """
    rootcause_agent_v2.py içine RAG entegrasyonunun nasıl yapılacağını gösterir.
    
    rootcause_agent_v2.py dosyasında şunu yapmalısınız:
    
    1. Import ekleyin:
       ```python
       from rag_pipeline.retrieval import RAGAnalyzer
       ```
    
    2. Ajan class'ının __init__ içinde:
       ```python
       self.rag_analyzer = RAGAnalyzer()
       ```
    
    3. Prompt hazırlama fonksiyonunda:
       ```python
       def prepare_prompt(self, incident_data):
           # Orijinal prompt
           base_prompt = "Incident'ı analiz et..."
           
           # RAG ile augment et
           augmented = self.rag_analyzer.augment_prompt(
               original_prompt=base_prompt,
               query=incident_data.get('description'),
               k=5,
               language="tr"
           )
           
           return augmented
       ```
    
    4. Kapatma sırasında:
       ```python
       def cleanup(self):
           if hasattr(self, 'rag_analyzer'):
               self.rag_analyzer.close()
       ```
    """
    
    print("""
    ╔════════════════════════════════════════════════════════════════════╗
    ║       RAG ENTEGRASYONu rootcause_agent_v2.py İÇİNE                 ║
    ╚════════════════════════════════════════════════════════════════════╝
    
    ADIM 1: Import ekleyin (dosya başında)
    ─────────────────────────────────────────
    from rag_pipeline.retrieval import RAGAnalyzer
    
    
    ADIM 2: Ajan class'ında initialize et
    ─────────────────────────────────────────
    class RootCauseAnalysisAgent:
        def __init__(self):
            # ... diğer initializations ...
            self.rag_analyzer = RAGAnalyzer()
    
    
    ADIM 3: Prompt hazırlama fonksiyonunu güncelle
    ─────────────────────────────────────────
    def analyze(self, incident_data):
        # Temel prompt
        base_system_prompt = '''
        Siz HSE kök neden analizi ajanısınız...
        '''
        
        # RAG ile augment et
        augmented_prompt = self.rag_analyzer.augment_prompt(
            original_prompt=base_system_prompt,
            query=incident_data['description'],
            k=5,
            language="tr"
        )
        
        # LLM'e augmented prompt gönder
        response = self.llm_client.call(
            system_prompt=augmented_prompt,
            user_message=incident_data['description']
        )
        
        return response
    
    
    ADIM 4: Cleanup
    ─────────────────────────────────────────
    def __del__(self):
        self.rag_analyzer.close()
    
    
    SONUÇ:
    ──────
    Artık LLM'ınız, incident'a en uygun taxonomy causes'larını bilecek
    ve daha akurat ve konsistent analiz yapacaktır.
    
    Faydalar:
    • Tutarlı termin ve kategori kullanımı
    • Daha akurat kök neden tanımlaması
    • Exclsion koşullarının göz önünde bulundurulması
    • Multilingual support (TR + EN)
    """)


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 RAG Integration Example")
    print("=" * 70)
    
    # Örnek 1: Basit kullanım
    print("\n📝 Örnek 1: Basit RAG Augmentation")
    print("─" * 70)
    
    result = analyze_incident_with_rag(
        "İnşaat alanında çalışan yüksekten düşerek yaralandı"
    )
    
    print(f"\n✓ Sonuç: {result}")
    
    # Örnek 2: Entegrasyon Rehberi
    print("\n" + "=" * 70)
    print("📚 Örnek 2: rootcause_agent_v2.py Entegrasyon Rehberi")
    print("=" * 70)
    
    integrate_into_rootcause_agent_v2()
