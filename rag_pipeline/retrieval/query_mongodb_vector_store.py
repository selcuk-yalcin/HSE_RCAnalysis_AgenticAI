"""
MongoDB Vector Retrieval - Benzerlik Araması
=============================================

Bu modül, MongoDB'ye stored embedding'ler ile benzerlik araması yapar.
Kullanıcı sorgularını vectorize ederek, en benzer taxonomy causes'ları bulur.

Kullanım:
    from rag_pipeline.retrieval.query_mongodb_vector_store import MongoVectorRetriever
    
    retriever = MongoVectorRetriever()
    results = retriever.retrieve(query="çalışan düşü", k=5, language="tr")
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import json

# sentence_transformers → torch ağır; sadece MongoVectorRetriever() anında yüklenir

# Proje kök dizinini Python path'e ekle
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from rag_pipeline.schemas.cause_models import Cause

# Ortam değişkenlerini yükle
load_dotenv()


class MongoVectorRetriever:
    """
    MongoDB'deki vektör embedding'lerini kullanarak benzerlik araması yapar.
    """
    
    def __init__(self, model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2'):
        """
        Retriever'ı başlatır.
        
        Args:
            model_name: SentenceTransformer modeli adı (multilingual desteği için)
        """
        self.model = None
        self.client = None
        self.db = None
        self.collection = None
        self.connected = False
        try:
            from sentence_transformers import SentenceTransformer  # noqa: WPS433

            print(f"🤖 Sentence Transformer modeli yükleniyor: {model_name}")
            self.model = SentenceTransformer(model_name)
        except Exception as e:  # noqa: BLE001
            print(
                f"⚠️  SentenceTransformer yüklenemedi; vektör RAG bu process için kapalı. "
                f"Torch/sentence-transformers kurulumunu kontrol edin. Detay: {e}"
            )
            return
        # MongoDB'ye bağlan
        self._connect_to_db()
    
    def _connect_to_db(self):
        """MongoDB'ye bağlanır."""
        mongo_uri = os.getenv("MONGODB_URI")
        if not mongo_uri:
            raise ValueError("MONGODB_URI ortam değişkeni bulunamadı.")
        
        try:
            self.client = MongoClient(mongo_uri, server_api=ServerApi('1'))
            self.client.admin.command('ping')
            self.db = self.client.rca
            self.collection = self.db.taxonomy
            self.connected = True
            print("✓ MongoDB bağlantısı başarılı!")
        except Exception as e:
            print(f"❌ MongoDB bağlantısı başarısız: {e}")
            self.connected = False
            raise
    
    def retrieve(
        self,
        query: str,
        k: int = 5,
        language: Optional[str] = None,
        cause_type_filter: Optional[str] = None,
        min_score: float = 0.3
    ) -> List[Dict]:
        """
        Verilen sorguya en benzer causes'ları döndürür.
        Basit KNN (K-Nearest Neighbors) kullanan client-side similarity hesaplama.
        
        Args:
            query: Arama sorgusu (türkçe veya ingilizce)
            k: Döndürülecek sonuç sayısı
            language: Filtre dili ("tr" veya "en", isteğe bağlı)
            cause_type_filter: Cause tipi filtresi ("A", "B", "C" vb., isteğe bağlı)
            min_score: Minimum benzerlik skoru (0.0-1.0)
        
        Returns:
            En benzer causes'ların listesi (embedding skoru ile birlikte)
        """
        if not self.connected:
            raise RuntimeError("MongoDB'ye bağlı değiliz. Tekrar denemeyi başarısız oldu.")
        
        print(f"\n🔍 Sorgu: '{query}'")
        print(f"   Parametre k={k}, language={language}, cause_type={cause_type_filter}")
        
        # Sorguyu vectorize et
        query_embedding = self.model.encode(query, convert_to_tensor=False)
        query_embedding_list = query_embedding.tolist()
        
        try:
            # Filtreler
            filter_dict = {}
            if cause_type_filter:
                filter_dict["cause_type"] = cause_type_filter
            
            # Tüm dokümanları çek ve client-side KNN yap
            all_docs = list(self.collection.find(filter_dict))
            
            if not all_docs:
                print(f"⚠️ Sorguya uygun doküman bulunamadı.")
                return []
            
            # Similarity hesapla (cosine)
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
            
            scored_results = []
            for doc in all_docs:
                doc_embedding = doc.get("embedding", [])
                if doc_embedding:
                    # Cosine similarity hesapla
                    similarity = cosine_similarity(
                        [query_embedding],
                        [doc_embedding]
                    )[0][0]
                    
                    if similarity >= min_score:
                        scored_results.append((doc, float(similarity)))
            
            # Benzerliğe göre sırala
            scored_results.sort(key=lambda x: x[1], reverse=True)
            
            # Top-k seç
            results = []
            for doc, score in scored_results[:k]:
                result_doc = {
                    "_id": doc.get("_id"),
                    "code": doc.get("code"),
                    "cause_type": doc.get("cause_type"),
                    "content": doc.get("content"),
                    "exclusion_conditions": doc.get("exclusion_conditions"),
                    "similarityScore": score
                }
                results.append(result_doc)
            
            if not results:
                print(f"⚠️ Minimum threshold'ü aşan sonuç bulunamadı.")
                return self._fallback_search(query, k, cause_type_filter)
            
            print(f"✓ {len(results)} sonuç bulundu.")
            return results
        
        except Exception as e:
            print(f"❌ Sorgu hatası: {e}")
            print("💡 Client-side similarity search başarısız oldu. Fallback text aramasıyla devam ediliyor...")
            return self._fallback_search(query, k, cause_type_filter)
    
    def _fallback_search(
        self,
        query: str,
        k: int = 5,
        cause_type_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Vector search başarısız olduğunda yedek arama yöntemi.
        Basit text matching kullanır.
        """
        filters = {}
        if cause_type_filter:
            filters["cause_type"] = cause_type_filter
        
        # Tüm dokümanları çek
        results = list(self.collection.find(filters).limit(k))
        
        # Basit text matching ile sırala
        query_lower = query.lower()
        scored_results = []
        
        for doc in results:
            score = 0
            # Code'da eşleşme
            if query_lower in doc.get("code", "").lower():
                score += 2
            
            # Content'te eşleşme
            content = doc.get("content", {})
            for lang, lang_content in content.items():
                text_fields = [
                    lang_content.get("title", ""),
                    lang_content.get("definition", ""),
                    " ".join(lang_content.get("typical_examples", []))
                ]
                for field in text_fields:
                    if query_lower in field.lower():
                        score += 1
            
            if score > 0:
                scored_results.append((doc, score))
        
        # Skora göre sırala
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        # Format
        return [
            {
                **doc,
                "similarityScore": min(score / 2, 1.0)  # 0-1 aralığına normalize et
            }
            for doc, score in scored_results[:k]
        ]
    
    def retrieve_by_code(self, code: str) -> Optional[Dict]:
        """
        Kod tarafından belirli bir cause'ı döndürür.
        
        Args:
            code: Cause kodu (örn. "A1.1")
        
        Returns:
            Cause dokümanı veya None
        """
        if not self.connected:
            raise RuntimeError("MongoDB'ye bağlı değiliz.")
        
        print(f"\n🔎 Kod ile arama: '{code}'")
        result = self.collection.find_one({"code": code})
        
        if result:
            print(f"✓ '{code}' bulundu.")
        else:
            print(f"⚠️ '{code}' bulunamadı.")
        
        return result
    
    def close(self):
        """MongoDB bağlantısını kapatır."""
        if self.client:
            self.client.close()
            self.connected = False
            print("\n🔌 MongoDB bağlantısı kapatıldı.")
    
    def __enter__(self):
        """Context manager desteği."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager desteği."""
        self.close()


def demo_retrieval():
    """Retrieval'ı test eden demo fonksiyonu."""
    print("=" * 70)
    print("🧪 MongoDB Vector Retrieval Demo")
    print("=" * 70)
    
    try:
        # Retriever oluştur
        with MongoVectorRetriever() as retriever:
            # Test sorguları
            test_queries = [
                ("çalışan düşü", "tr", None),
                ("worker fall", "en", None),
                ("electrical hazard", "en", "A"),
            ]
            
            for query, lang, cause_type in test_queries:
                print(f"\n{'─' * 70}")
                results = retriever.retrieve(
                    query=query,
                    k=3,
                    language=lang,
                    cause_type_filter=cause_type
                )
                
                if results:
                    print(f"\n📊 İlk 3 sonuç:")
                    for i, result in enumerate(results, 1):
                        score = result.get("similarityScore", 0)
                        code = result.get("code", "?")
                        cause_type = result.get("cause_type", "?")
                        print(f"\n  {i}. [{code}] Tür: {cause_type}")
                        print(f"     Benzerlik Skoru: {score:.4f}")
                        
                        # Content'i göster
                        content = result.get("content", {})
                        if lang in content:
                            lang_content = content[lang]
                            print(f"     Başlık: {lang_content.get('title', 'N/A')}")
                            definition = lang_content.get('definition', '')
                            if len(definition) > 100:
                                print(f"     Tanım: {definition[:100]}...")
                            else:
                                print(f"     Tanım: {definition}")
        
        print(f"\n{'=' * 70}")
        print("✅ Demo tamamlandı!")
        print(f"{'=' * 70}")
    
    except Exception as e:
        print(f"\n❌ Demo hatası: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demo_retrieval()
