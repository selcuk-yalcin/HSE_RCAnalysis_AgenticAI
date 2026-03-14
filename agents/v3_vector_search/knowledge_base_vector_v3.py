"""
MongoDB Atlas Vector Search için HSG245 Knowledge Base - V3
============================================================
Hibrit yaklaşım: Basit dictionary (hızlı) + Vector embeddings (semantik)

NOT: Bu dosya V3 test ortamı içindir. Orijinal knowledge_base.py değiştirilmemiştir.
"""

import os
from typing import List, Dict, Optional
from pymongo import MongoClient
from openai import OpenAI
import re

# ─────────────────────────────────────────────────────────────
# BAĞLANTI YÖNETİMİ
# ─────────────────────────────────────────────────────────────

class HSG245VectorDB:
    """MongoDB Atlas Vector Search entegrasyonu"""
    
    def __init__(self):
        # MongoDB Atlas bağlantısı
        mongo_uri = os.getenv("MONGODB_URI")
        if not mongo_uri:
            raise ValueError("MONGODB_URI gerekli (.env dosyasına ekleyin)")
        
        self.client = MongoClient(mongo_uri)
        self.db = self.client["hsg245_kb"]
        self.collection = self.db["codes"]
        
        # OpenRouter embedding için
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_key:
            raise ValueError("OPENROUTER_API_KEY gerekli (.env dosyasına ekleyin)")
        
        self.embedder = OpenAI(
            api_key=openrouter_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        print("✅ MongoDB Vector DB hazır")
    
    # ───────────────────────────────────────────────────────
    # VECTOR EMBEDDING
    # ───────────────────────────────────────────────────────
    
    def _get_embedding(self, text: str) -> List[float]:
        """
        OpenRouter üzerinden text embedding al
        Model: text-embedding-3-small (hızlı + uygun maliyetli)
        """
        try:
            response = self.embedder.embeddings.create(
                model="openai/text-embedding-3-small",  # 1536 boyut
                input=text[:8000]  # Token limit
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"⚠️  Embedding hatası: {e}")
            return []
    
    # ───────────────────────────────────────────────────────
    # POPULATE DATABASE (İLK KURULUM)
    # ───────────────────────────────────────────────────────
    
    def populate_from_markdown(self, md_file: str = "agents/knowledge_base.md"):
        """
        knowledge_base.md'yi parse edip MongoDB'ye yükle
        Her kod bloğu için:
        - Metadata (kod, kategori, başlık)
        - Full text (seçim kriterleri, örnekler, NOT THIS IF)
        - Vector embedding (semantik arama için)
        """
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chunks = []
        
        # Regex: #### A1.1 Individual Rule Violation
        code_pattern = re.compile(r'####\s+([A-D]\d+\.\d+)\s+(.+?)(?=####|\Z)', re.DOTALL)
        
        for match in code_pattern.finditer(content):
            code = match.group(1)
            block = match.group(2).strip()
            
            # Başlık ayıkla
            title_match = re.match(r'^(.+?)(?:\n|$)', block)
            title = title_match.group(1).strip() if title_match else ""
            
            # Tam metin (embeddings için)
            full_text = f"{code} {title}\n{block}"
            
            # Kategori
            category = code[0]  # A, B, C, D
            
            # Tipik örnekler
            typical = re.findall(r'→ Typical:\s*(.+?)(?=✗|→|####|$)', block, re.DOTALL)
            typical_clean = [t.strip() for t in typical if t.strip()]
            
            # NOT THIS IF redirections
            not_this_if = re.findall(r'✗ Not this if:\s*(.+?)\s*→\s*([A-D]\d+\.\d+)', block)
            
            # Embedding oluştur
            embedding = self._get_embedding(full_text)
            
            if not embedding:
                print(f"  ⚠️  {code}: Embedding oluşturulamadı, atlanıyor")
                continue
            
            chunk = {
                "code": code,
                "category": category,
                "title": title,
                "full_text": full_text,
                "typical_examples": typical_clean,
                "not_this_if": [
                    {"condition": cond.strip(), "redirect_to": redir.strip()}
                    for cond, redir in not_this_if
                ],
                "embedding": embedding,  # 1536-boyut vector
                "metadata": {
                    "block_length": len(block),
                    "num_examples": len(typical_clean),
                    "num_redirects": len(not_this_if)
                }
            }
            
            chunks.append(chunk)
            
            if len(chunks) % 10 == 0:
                print(f"  📦 {len(chunks)} kod işlendi...")
        
        # MongoDB'ye toplu insert
        if chunks:
            self.collection.delete_many({})  # Önceki verileri temizle
            self.collection.insert_many(chunks)
            print(f"\n✅ {len(chunks)} kod MongoDB'ye yüklendi")
            
            # Vector search index oluştur (manuel talimat)
            self._create_vector_index()
        
        return len(chunks)
    
    # ───────────────────────────────────────────────────────
    # VECTOR SEARCH INDEX
    # ───────────────────────────────────────────────────────
    
    def _create_vector_index(self):
        """
        MongoDB Atlas'ta vector search index oluştur
        MANUEL: Atlas UI'dan yapılmalı (programatik API yok)
        """
        print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  ⚠️  MANUEL ADIM: MongoDB Atlas UI'dan Vector Search Index Oluşturun          ║
╚═══════════════════════════════════════════════════════════════════════════════╝

1. Atlas → Database → Search → Create Search Index
2. Index Type: Vector Search
3. Configuration (JSON Editor):

{
  "mappings": {
    "dynamic": true,
    "fields": {
      "embedding": {
        "type": "knnVector",
        "dimensions": 1536,
        "similarity": "cosine"
      },
      "code": {
        "type": "string"
      },
      "category": {
        "type": "string"
      }
    }
  }
}

4. Index Name: vector_index
5. Database: hsg245_kb
6. Collection: codes

⏳ Index oluşturma süresi: ~2-5 dakika
        """)
    
    # ───────────────────────────────────────────────────────
    # SEMANTİK ARAMA
    # ───────────────────────────────────────────────────────
    
    def semantic_search(
        self,
        query: str,
        top_k: int = 5,
        category_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Semantik benzerlik ile kod ara
        
        Args:
            query: "Worker bypassed LOTO procedure"
            top_k: En benzer 5 sonuç
            category_filter: "C" veya "D" (root causes için)
        
        Returns:
            [
                {
                    "code": "D4.5",
                    "title": "Energy Isolation (LOTO) Ineffective",
                    "score": 0.92,
                    "full_text": "...",
                    "typical_examples": [...]
                },
                ...
            ]
        """
        
        # Query embedding
        query_vector = self._get_embedding(query)
        
        if not query_vector:
            print("⚠️  Query embedding oluşturulamadı, boş liste dönüyor")
            return []
        
        try:
            # Vector search aggregation pipeline
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_index",
                        "path": "embedding",
                        "queryVector": query_vector,
                        "numCandidates": 100,
                        "limit": top_k
                    }
                },
                {
                    "$project": {
                        "code": 1,
                        "title": 1,
                        "category": 1,
                        "full_text": 1,
                        "typical_examples": 1,
                        "not_this_if": 1,
                        "score": {"$meta": "vectorSearchScore"}
                    }
                }
            ]
            
            # Kategori filtresi
            if category_filter:
                pipeline.insert(1, {
                    "$match": {"category": category_filter}
                })
            
            results = list(self.collection.aggregate(pipeline))
            return results
        
        except Exception as e:
            print(f"⚠️  Vector search hatası: {e}")
            print(f"   Muhtemelen Atlas'ta 'vector_index' henüz oluşturulmadı.")
            return []
    
    # ───────────────────────────────────────────────────────
    # HIZLI KEYWORD ARAMA (Fallback)
    # ───────────────────────────────────────────────────────
    
    def keyword_search(
        self,
        keywords: List[str],
        category_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Hızlı text arama (vector arama başarısızsa)
        
        Args:
            keywords: ["LOTO", "isolation", "procedure"]
            category_filter: "D"
        """
        
        # Text search query
        regex_pattern = "|".join(keywords)
        query = {
            "full_text": {"$regex": regex_pattern, "$options": "i"}
        }
        
        if category_filter:
            query["category"] = category_filter
        
        results = list(self.collection.find(
            query,
            {"embedding": 0}  # Embedding'i döndürme (büyük)
        ).limit(10))
        
        return results


# ─────────────────────────────────────────────────────────────
# HİBRİT HELPER (RootCauseAgentV3 için)
# ─────────────────────────────────────────────────────────────

class HybridKnowledgeBase:
    """
    Hibrit yaklaşım:
    1. İlk önce basit dictionary (mevcut knowledge_base.py) - çok hızlı
    2. Belirsizlik varsa MongoDB vector search - daha akıllı
    """
    
    def __init__(self):
        # Basit dictionary (mevcut sistem)
        try:
            # Orijinal knowledge_base.py'yi import et
            import sys
            import os
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            from knowledge_base import HSG245_TAXONOMY, get_category_text
            self.local_kb = HSG245_TAXONOMY
            self.get_category = get_category_text
            print("✅ Dictionary knowledge base yüklendi")
        except ImportError as e:
            print(f"⚠️  Dictionary KB import hatası: {e}")
            self.local_kb = None
            self.get_category = None
        
        # MongoDB vector DB (opsiyonel)
        self.use_vector = os.getenv("USE_VECTOR_SEARCH", "false").lower() == "true"
        
        if self.use_vector:
            try:
                self.vector_db = HSG245VectorDB()
                print("✅ Hibrit mod: Dictionary + Vector Search")
            except Exception as e:
                print(f"⚠️  Vector DB başarısız, sadece dictionary: {e}")
                self.use_vector = False
                self.vector_db = None
        else:
            self.vector_db = None
            print("✅ Sadece dictionary mod (hızlı)")
    
    def get_relevant_codes(
        self,
        incident_summary: str,
        category: str = "D",  # C veya D (root causes)
        top_k: int = 5
    ) -> str:
        """
        Olay özetine en uygun kodları getir
        
        STRATEJI:
        1. Basit dictionary'den kategori metnini al (hızlı)
        2. Vector search aktifse, semantik benzerlik ekle (akıllı)
        """
        
        # 1. Basit dictionary (her zaman)
        if self.get_category:
            category_text = self.get_category(category)
        else:
            category_text = f"Kategori {category} (Dictionary yüklenemedi)"
        
        # 2. Vector search (opsiyonel, daha akıllı)
        if self.use_vector and self.vector_db:
            try:
                semantic_results = self.vector_db.semantic_search(
                    query=incident_summary,
                    top_k=top_k,
                    category_filter=category
                )
                
                if semantic_results:
                    # En benzer kodları vurgula
                    highlights = "\n\n" + "=" * 80 + "\n"
                    highlights += f"🎯 SEMANTİK OLARAK EN YAKIN KODLAR (Bu Olay İçin):\n"
                    highlights += "=" * 80 + "\n\n"
                    
                    for r in semantic_results:
                        score = r.get('score', 0)
                        code = r.get('code', '???')
                        title = r.get('title', '')
                        examples = r.get('typical_examples', [])
                        
                        highlights += f"{code} (Benzerlik: {score:.3f}): {title}\n"
                        if examples:
                            highlights += f"  Örnekler: {examples[0][:100]}...\n"
                        highlights += "\n"
                    
                    highlights += "=" * 80 + "\n"
                    highlights += "NOT: Yukarıdaki kodlar bu olay için öncelikli olarak değerlendirilmelidir.\n"
                    highlights += "     Ancak aşağıdaki tam listedeki diğer kodlar da uygun olabilir.\n"
                    highlights += "=" * 80 + "\n\n"
                    
                    return highlights + category_text
            
            except Exception as e:
                print(f"⚠️  Vector search hatası: {e}")
                return category_text
        
        return category_text


# ─────────────────────────────────────────────────────────────
# KULLANIM ÖRNEĞİ
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "populate":
        # İlk kurulum: knowledge_base.md → MongoDB
        print("\n🚀 Knowledge Base → MongoDB yükleniyor...\n")
        db = HSG245VectorDB()
        
        # Dosya yolu
        kb_path = "agents/knowledge_base.md"
        if not os.path.exists(kb_path):
            kb_path = "../knowledge_base.md"
        
        count = db.populate_from_markdown(kb_path)
        print(f"\n🎉 {count} kod MongoDB'ye yüklendi")
        print("\n⚠️  Atlas UI'dan vector index oluşturun (yukarıdaki talimatları izleyin)")
    
    elif len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test: Semantik arama
        print("\n🧪 Vector Search Test\n")
        db = HSG245VectorDB()
        
        test_queries = [
            ("Worker bypassed LOTO procedure to save time", "D"),
            ("Maintenance was delayed for 6 months", "D"),
            ("Supervisor didn't notice the unsafe condition", "D"),
            ("Worker was fatigued from long shifts", "C")
        ]
        
        for query, cat in test_queries:
            print(f"\n{'=' * 80}")
            print(f"🔍 Query: {query}")
            print(f"📁 Category Filter: {cat}")
            print(f"{'=' * 80}\n")
            
            results = db.semantic_search(query, top_k=3, category_filter=cat)
            
            if results:
                for i, r in enumerate(results, 1):
                    print(f"{i}. {r['code']} (Score: {r['score']:.3f}): {r['title']}")
                    if r.get('typical_examples'):
                        print(f"   Örnek: {r['typical_examples'][0][:100]}...")
                    print()
            else:
                print("   ⚠️  Sonuç bulunamadı (vector index oluşturulmamış olabilir)\n")
    
    else:
        print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  V3 Vector Search - Kullanım Kılavuzu                                         ║
╚═══════════════════════════════════════════════════════════════════════════════╝

KURULUM:

1. Bağımlılıkları yükle:
   pip install -r agents/v3_vector_search/requirements_v3.txt

2. .env dosyasına ekle:
   USE_VECTOR_SEARCH=true
   MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net
   OPENROUTER_API_KEY=sk-or-v1-...

3. Knowledge base'i yükle (İLK KURULUM - TEK SEFER):
   python agents/v3_vector_search/knowledge_base_vector_v3.py populate

4. Atlas UI'dan vector index oluştur (MANUEL):
   - Atlas → Database → Search → Create Search Index
   - JSON config'i yukarıdaki talimatlarda

5. Test et:
   python agents/v3_vector_search/knowledge_base_vector_v3.py test

KULLANIM:

# RootCauseAgentV3 içinde:
from knowledge_base_vector_v3 import HybridKnowledgeBase

kb = HybridKnowledgeBase()
context = kb.get_relevant_codes(
    incident_summary="Worker fell from height...",
    category="D",
    top_k=5
)
        """)
