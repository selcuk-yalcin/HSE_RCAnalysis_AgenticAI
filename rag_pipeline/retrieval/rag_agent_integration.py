"""
RAG Agent Integration - Retrieval-Augmented Analysis
====================================================

Bu modül, retrieval sistemini ana ajan ile bağlayarak, sorguların
uygun taxonomy causes'ları bulup analiz için kullanmasını sağlar.

Kullanım:
    from rag_pipeline.retrieval.rag_agent_integration import RAGAnalyzer
    
    analyzer = RAGAnalyzer()
    context = analyzer.get_context_for_query(query="çalışan düşü")
    # context, sorguya uygun causes ve açıklamalarını içerir
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import os
from dotenv import load_dotenv
import json

# Proje kök dizinini Python path'e ekle
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from rag_pipeline.retrieval.query_mongodb_vector_store import MongoVectorRetriever

# Ortam değişkenlerini yükle
load_dotenv()


class RAGAnalyzer:
    """
    Retrieval-Augmented Generation ile analiz yapan ajan.
    MongoDB'den alınan context ile LLM prompt'ını zenginleştirir.
    """
    
    def __init__(self, retriever: Optional[MongoVectorRetriever] = None):
        """
        RAG Analyzer'ı başlatır.
        
        Args:
            retriever: Özel bir MongoVectorRetriever örneği (test için)
        """
        if retriever:
            self.retriever = retriever
        else:
            try:
                self.retriever = MongoVectorRetriever()
                print("✓ RAG Analyzer başlatıldı.")
            except Exception as e:
                print(f"❌ Retriever başlatılamadı: {e}")
                print("   MongoDB veritabanınız erişilebilir olduğundan emin olun.")
                self.retriever = None
    
    def get_context_for_query(
        self,
        query: str,
        k: int = 5,
        language: Optional[str] = None,
        cause_type_filter: Optional[str] = None,
        include_exclusions: bool = True
    ) -> Dict:
        """
        Verilen sorgu için RAG context'i oluşturur.
        
        Args:
            query: Analiz sorgusu
            k: Döndürülecek cause sayısı
            language: Filtre dili ("tr" veya "en")
            cause_type_filter: Cause tür filtresi
            include_exclusions: Exclusion koşullarını dahil et mi?
        
        Returns:
            Sorgu için zenginleştirilmiş context
        """
        if not self.retriever or not self.retriever.connected:
            return {
                "status": "error",
                "message": "Retriever not available",
                "retrieved_causes": []
            }
        
        try:
            # Vector similarity search ile ilgili causes'ı bul
            results = self.retriever.retrieve(
                query=query,
                k=k,
                language=language,
                cause_type_filter=cause_type_filter,
                min_score=0.3
            )
            
            # Context'i format et
            context = {
                "status": "success",
                "query": query,
                "retrieved_causes": [],
                "knowledge_base_excerpt": ""
            }
            
            # Causes'ları format et
            formatted_causes = []
            for result in results:
                cause_info = {
                    "code": result.get("code"),
                    "type": result.get("cause_type"),
                    "similarity_score": result.get("similarityScore", 0),
                    "content": result.get("content", {}),
                    "exclusions": result.get("exclusion_conditions", []) if include_exclusions else []
                }
                formatted_causes.append(cause_info)
                context["retrieved_causes"].append(cause_info)
            
            # Prompt için metin versiyonunu oluştur
            context["knowledge_base_excerpt"] = self._format_causes_for_prompt(
                formatted_causes,
                language=language
            )
            
            return context
        
        except Exception as e:
            print(f"❌ Context oluşturma hatası: {e}")
            return {
                "status": "error",
                "message": str(e),
                "retrieved_causes": []
            }
    
    def _format_causes_for_prompt(
        self,
        causes: List[Dict],
        language: Optional[str] = None
    ) -> str:
        """
        Causes'ları LLM prompt'u için formatlar.
        
        Args:
            causes: Formatted cause listesi
            language: Filtre dili
        
        Returns:
            LLM prompt'u için metin versiyonu
        """
        if not causes:
            return "Uygun sebepler bulunamadı."
        
        lines = ["=== İLGİLİ TAKSONOMI SEBEPLERİ ===\n"]
        
        for i, cause in enumerate(causes, 1):
            code = cause.get("code", "?")
            cause_type = cause.get("type", "?")
            score = cause.get("similarity_score", 0)
            
            lines.append(f"\n{i}. [{code}] Tür: {cause_type} (Benzerlik: {score:.2%})")
            
            # Çok dilli içeriği format et
            content = cause.get("content", {})
            
            # Dil seçimi
            display_langs = []
            if language and language in content:
                display_langs = [language]
            else:
                display_langs = list(content.keys())
            
            for lang in display_langs:
                lang_content = content.get(lang, {})
                lang_flag = "🇹🇷" if lang == "tr" else "🇬🇧" if lang == "en" else f"[{lang}]"
                
                lines.append(f"\n   {lang_flag} Başlık: {lang_content.get('title', 'N/A')}")
                
                definition = lang_content.get('definition', '')
                if definition:
                    # Tanımı satır satır göster (uzunsa kesintisiz)
                    lines.append(f"      Tanım: {definition}")
                
                examples = lang_content.get('typical_examples', [])
                if examples:
                    lines.append(f"      Örnekler:")
                    for example in examples[:2]:  # İlk 2 örneği göster
                        lines.append(f"        • {example}")
                    if len(examples) > 2:
                        lines.append(f"        • ... ve {len(examples) - 2} daha")
            
            # Exclusion koşulları
            exclusions = cause.get("exclusions", [])
            if exclusions:
                lines.append(f"\n   ⛔ Dışlama Koşulları:")
                for exc in exclusions[:2]:  # İlk 2'sini göster
                    exc_text = exc.get("condition", "N/A") if isinstance(exc, dict) else str(exc)
                    lines.append(f"      • {exc_text}")
                if len(exclusions) > 2:
                    lines.append(f"      • ... ve {len(exclusions) - 2} daha")
        
        lines.append("\n\n=== SONUÇ ===")
        return "\n".join(lines)
    
    def augment_prompt(
        self,
        original_prompt: str,
        query: str,
        k: int = 5,
        language: Optional[str] = None
    ) -> str:
        """
        Orijinal prompt'u RAG context'i ile zenginleştirir.
        
        Args:
            original_prompt: Orijinal sistem/kullanıcı prompt'u
            query: Analiz sorgusu
            k: Döndürülecek cause sayısı
            language: Filtre dili
        
        Returns:
            Context ile zenginleştirilmiş prompt
        """
        context_data = self.get_context_for_query(
            query=query,
            k=k,
            language=language
        )
        
        if context_data.get("status") != "success" or not context_data.get("retrieved_causes"):
            # Retrieval başarısız oldu
            return original_prompt
        
        knowledge_excerpt = context_data.get("knowledge_base_excerpt", "")
        
        # Prompt'u zenginleştir
        augmented = f"""{original_prompt}

{knowledge_excerpt}

Yukarıda verilen taksonomi bilgisini referans alarak analiz yapınız.
Sonuç, bu sebepler arasından en uygun olanları içermelidir."""
        
        return augmented
    
    def close(self):
        """Retriever'ı kapat."""
        if self.retriever:
            self.retriever.close()
    
    def __enter__(self):
        """Context manager desteği."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager desteği."""
        self.close()


def demo_rag_analyzer():
    """RAG Analyzer'ı test eden demo."""
    print("=" * 70)
    print("🧪 RAG Analyzer Demo")
    print("=" * 70)
    
    try:
        with RAGAnalyzer() as analyzer:
            test_query = "işçi inşaat alanında yüksekten düştü"
            
            print(f"\n📝 Test Sorgusu: '{test_query}'")
            print("─" * 70)
            
            # Context al
            context = analyzer.get_context_for_query(
                query=test_query,
                k=3,
                language="tr"
            )
            
            # Sonuç göster
            if context.get("status") == "success":
                print(f"\n✓ {len(context.get('retrieved_causes', []))} cause bulundu.")
                print(context.get("knowledge_base_excerpt", ""))
            else:
                print(f"\n❌ Hata: {context.get('message')}")
            
            # Augmented prompt örneği
            print("\n" + "=" * 70)
            print("📌 Prompt Augmentation Örneği:")
            print("=" * 70)
            
            original_prompt = "Verilen incident'ı analiz et."
            augmented = analyzer.augment_prompt(
                original_prompt=original_prompt,
                query=test_query,
                k=3,
                language="tr"
            )
            
            print("\n🔄 Augmented Prompt (ilk 500 char):")
            print(augmented[:500] + "...")
        
        print(f"\n{'=' * 70}")
        print("✅ Demo tamamlandı!")
        print(f"{'=' * 70}")
    
    except Exception as e:
        print(f"\n❌ Demo hatası: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demo_rag_analyzer()
