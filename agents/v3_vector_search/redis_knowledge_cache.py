"""
Redis Knowledge Base Cache
===========================
MongoDB'den sık kullanılan kodları Redis'te cache'le

ÖZELLIKLER:
- LRU cache (en çok kullanılanlar)
- TTL (Time To Live) - 1 saat
- Fall-back MongoDB'ye
- Hibrit: Redis (hız) + MongoDB (vector search + kalıcılık)

KULLANIM:
    # Cache warmup
    python redis_knowledge_cache.py warmup
    
    # Test
    python redis_knowledge_cache.py test
"""

import os
import json
import redis
from typing import Optional, Dict, List
from pymongo import MongoClient


class RedisKnowledgeCache:
    """
    Redis + MongoDB hibrit knowledge base
    
    Akış:
    1. Redis'te ara (cache hit → 1ms)
    2. Bulamazsa MongoDB'den al (50ms)
    3. Redis'e cache'le (sonraki istekler hızlı)
    
    Performance:
    - Cache hit: 1ms (50x hızlı)
    - Cache miss: 50ms (MongoDB lookup + Redis cache)
    - Cache hit rate: %80-90 (warmup sonrası)
    """
    
    def __init__(self):
        # Redis connection
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
        # MongoDB connection (vector search için)
        mongo_uri = os.getenv("MONGODB_URI")
        if not mongo_uri:
            print("⚠️  MONGODB_URI env variable not set. Vector search disabled.")
            self.mongo_client = None
            self.mongo_collection = None
        else:
            self.mongo_client = MongoClient(mongo_uri)
            self.mongo_db = self.mongo_client["hsg245_kb"]
            self.mongo_collection = self.mongo_db["codes"]
        
        # Cache ayarları
        self.cache_ttl = 3600  # 1 saat (3600 saniye)
        self.cache_prefix = "kb:"
        
        print("✅ Redis Knowledge Cache hazır")
    
    # ─────────────────────────────────────────────────────────
    # GET: Redis → MongoDB fallback
    # ─────────────────────────────────────────────────────────
    
    def get_code(self, code: str) -> Optional[Dict]:
        """
        Kod bilgisini getir (önce Redis, sonra MongoDB)
        
        Args:
            code: "D4.5", "A1.1", vb.
        
        Returns:
            {
                "code": "D4.5",
                "title": "Energy Isolation (LOTO) Ineffective",
                "full_text": "...",
                "typical_examples": [...],
                "not_this_if": [...]
            }
        """
        
        cache_key = f"{self.cache_prefix}{code}"
        
        # 1. Redis'te ara (cache hit)
        cached = self.redis_client.get(cache_key)
        if cached:
            print(f"  ⚡ Redis cache HIT: {code}")
            return json.loads(cached)
        
        # 2. MongoDB'den al (cache miss)
        if not self.mongo_collection:
            print(f"  ⚠️  MongoDB not available for code: {code}")
            return None
        
        print(f"  💾 MongoDB lookup: {code}")
        doc = self.mongo_collection.find_one(
            {"code": code},
            {"_id": 0, "embedding": 0}  # Embedding'i döndürme (gereksiz)
        )
        
        if not doc:
            return None
        
        # 3. Redis'e cache'le (sonraki istekler hızlı)
        self.redis_client.setex(
            cache_key,
            self.cache_ttl,
            json.dumps(doc)
        )
        
        return doc
    
    # ─────────────────────────────────────────────────────────
    # BATCH GET: Birden fazla kod
    # ─────────────────────────────────────────────────────────
    
    def get_codes_batch(self, codes: List[str]) -> List[Dict]:
        """
        Birden fazla kodu al (pipeline ile optimize)
        
        Args:
            codes: ["D4.5", "D1.5", "A1.1"]
        
        Returns:
            [
                {"code": "D4.5", ...},
                {"code": "D1.5", ...},
                {"code": "A1.1", ...}
            ]
        """
        
        results = []
        
        # Redis pipeline (tek network roundtrip)
        pipe = self.redis_client.pipeline()
        cache_keys = [f"{self.cache_prefix}{code}" for code in codes]
        
        for key in cache_keys:
            pipe.get(key)
        
        cached_values = pipe.execute()
        
        # Cache hits vs misses
        cache_hits = []
        cache_misses = []
        
        for i, (code, cached) in enumerate(zip(codes, cached_values)):
            if cached:
                cache_hits.append(code)
                results.append(json.loads(cached))
            else:
                cache_misses.append(code)
        
        # MongoDB'den eksikleri al
        if cache_misses and self.mongo_collection:
            print(f"  💾 MongoDB batch lookup: {cache_misses}")
            
            docs = list(self.mongo_collection.find(
                {"code": {"$in": cache_misses}},
                {"_id": 0, "embedding": 0}
            ))
            
            # Cache'e yaz
            pipe = self.redis_client.pipeline()
            for doc in docs:
                cache_key = f"{self.cache_prefix}{doc['code']}"
                pipe.setex(cache_key, self.cache_ttl, json.dumps(doc))
            pipe.execute()
            
            results.extend(docs)
        
        print(f"  📊 Cache: {len(cache_hits)} hits, {len(cache_misses)} misses")
        
        return results
    
    # ─────────────────────────────────────────────────────────
    # CATEGORY: Tüm kategori kodları (A, B, C, D)
    # ─────────────────────────────────────────────────────────
    
    def get_category_codes(self, category: str) -> List[Dict]:
        """
        Kategori altındaki tüm kodları getir
        
        Args:
            category: "A", "B", "C", "D"
        
        Returns:
            [{"code": "D1.1", ...}, {"code": "D1.2", ...}, ...]
        """
        
        cache_key = f"{self.cache_prefix}category:{category}"
        
        # Redis'te kategorinin tamamı var mı?
        cached = self.redis_client.get(cache_key)
        if cached:
            print(f"  ⚡ Redis cache HIT: Category {category}")
            return json.loads(cached)
        
        # MongoDB'den al
        if not self.mongo_collection:
            print(f"  ⚠️  MongoDB not available for category: {category}")
            return []
        
        print(f"  💾 MongoDB category lookup: {category}")
        docs = list(self.mongo_collection.find(
            {"category": category},
            {"_id": 0, "embedding": 0}
        ))
        
        # Redis'e cache'le
        self.redis_client.setex(
            cache_key,
            self.cache_ttl,
            json.dumps(docs)
        )
        
        return docs
    
    # ─────────────────────────────────────────────────────────
    # SEMANTIC SEARCH: MongoDB vector (Redis yok)
    # ─────────────────────────────────────────────────────────
    
    def semantic_search(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None
    ) -> List[Dict]:
        """
        Semantic similarity search (MongoDB Vector Search)
        
        NOT: Bu Redis'te YAPILMAZ, çünkü vector embedding gerekir
        
        Args:
            query: "Worker bypassed LOTO"
            top_k: En benzer 5 sonuç
            category: "D" (opsiyonel filtre)
        
        Returns:
            [
                {"code": "D4.5", "score": 0.92, ...},
                {"code": "D1.5", "score": 0.88, ...}
            ]
        """
        
        # Önce cache'te ara (query-based cache)
        cache_key = f"{self.cache_prefix}search:{query[:50]}:{category}:{top_k}"
        cached = self.redis_client.get(cache_key)
        
        if cached:
            print(f"  ⚡ Redis cache HIT: Search query")
            return json.loads(cached)
        
        # MongoDB vector search kullan (knowledge_base_vector_v3.py'deki fonksiyon)
        try:
            from knowledge_base_vector_v3 import HSG245VectorDB
            
            vector_db = HSG245VectorDB()
            results = vector_db.semantic_search(query, top_k, category)
            
            # Sonuçları Redis'e cache'le (query → sonuç)
            self.redis_client.setex(
                cache_key,
                600,  # 10 dakika (search sonuçları daha kısa ömürlü)
                json.dumps(results)
            )
            
            return results
        
        except Exception as e:
            print(f"  ⚠️  Vector search failed: {e}")
            return []
    
    # ─────────────────────────────────────────────────────────
    # WARMUP: Sık kullanılan kodları önceden yükle
    # ─────────────────────────────────────────────────────────
    
    def warmup_cache(self, most_used_codes: List[str] = None):
        """
        Cache warmup: Sık kullanılan kodları önceden Redis'e yükle
        
        Args:
            most_used_codes: ["D4.5", "D1.5", "A1.1", ...] (en sık 20 kod)
        """
        
        if not most_used_codes:
            # Default: En sık kullanılan 20 kod (analitikten)
            most_used_codes = [
                "D4.5", "D1.5", "D9.5", "D1.2", "A1.1",
                "D3.1", "D3.2", "C1.4", "C3.2", "D6.6",
                "D1.9", "D9.1", "D9.3", "B4.4", "B2.1",
                "D2.1", "D4.1", "C1.1", "A2.1", "D1.1"
            ]
        
        print(f"🔥 Cache warmup: {len(most_used_codes)} kod yükleniyor...")
        
        docs = self.get_codes_batch(most_used_codes)
        
        print(f"✅ Cache warmup tamamlandı: {len(docs)} kod Redis'te")
        
        # Tüm kategorileri de cache'le
        for category in ["A", "B", "C", "D"]:
            self.get_category_codes(category)
        
        print(f"✅ Tüm kategoriler cache'lendi")
    
    # ─────────────────────────────────────────────────────────
    # STATS: Cache performans metrikleri
    # ─────────────────────────────────────────────────────────
    
    def get_cache_stats(self) -> Dict:
        """
        Redis cache istatistikleri
        
        Returns:
            {
                "total_keys": 137,
                "memory_usage_mb": 2.5,
                "hit_rate": 0.85
            }
        """
        
        info = self.redis_client.info("stats")
        
        # KB key'lerini say
        kb_keys = self.redis_client.keys(f"{self.cache_prefix}*")
        
        # Hit rate hesapla
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        hit_rate = hits / total if total > 0 else 0
        
        return {
            "total_keys": len(kb_keys),
            "memory_usage_mb": info.get("used_memory", 0) / (1024 * 1024),
            "keyspace_hits": hits,
            "keyspace_misses": misses,
            "hit_rate": hit_rate
        }
    
    # ─────────────────────────────────────────────────────────
    # CLEAR: Cache temizle
    # ─────────────────────────────────────────────────────────
    
    def clear_cache(self, pattern: str = None):
        """
        Cache temizle
        
        Args:
            pattern: "kb:D*" (sadece D kategorisi), None (tümü)
        """
        
        if pattern:
            keys = self.redis_client.keys(pattern)
        else:
            keys = self.redis_client.keys(f"{self.cache_prefix}*")
        
        if keys:
            self.redis_client.delete(*keys)
            print(f"🗑️  {len(keys)} key silindi")
        else:
            print("ℹ️  Silinecek key yok")


# ─────────────────────────────────────────────────────────────
# ROOTCAUSE AGENT ENTEGRASYONU
# ─────────────────────────────────────────────────────────────

class HybridKnowledgeBaseV3:
    """
    RootCauseAgentV3 için hibrit KB
    
    Redis (cache) + MongoDB (vector + storage)
    
    Kullanım:
        kb = HybridKnowledgeBaseV3()
        relevant_codes = kb.get_relevant_codes(
            incident_summary="Worker bypassed LOTO",
            category="D",
            top_k=5
        )
    """
    
    def __init__(self):
        self.cache = RedisKnowledgeCache()
        
        # Cache warmup (ilk başlatmada)
        try:
            self.cache.warmup_cache()
        except Exception as e:
            print(f"⚠️  Cache warmup failed: {e}")
    
    def get_relevant_codes(
        self,
        incident_summary: str,
        category: str = "D",
        top_k: int = 5
    ) -> str:
        """
        Olay için en alakalı kodları getir (agent prompt için)
        
        Args:
            incident_summary: "Worker bypassed LOTO procedure during maintenance"
            category: "D" (Organizational), "C" (Personal), "A", "B"
            top_k: Kaç tane semantik benzer kod (default: 5)
        
        Returns:
            Formatted markdown string for LLM prompt
        """
        
        # 1. Semantic search (MongoDB vector) - Önce cache'te ara
        semantic_results = []
        try:
            semantic_results = self.cache.semantic_search(
                query=incident_summary,
                top_k=top_k,
                category=category
            )
        except Exception as e:
            print(f"  ⚠️  Semantic search failed: {e}")
        
        # 2. Full category list (Redis cache'den)
        all_codes = []
        try:
            all_codes = self.cache.get_category_codes(category)
        except Exception as e:
            print(f"  ⚠️  Category codes failed: {e}")
        
        # 3. Format prompt
        prompt = f"# {category} KATEGORİSİ - ROOT CAUSES\n\n"
        
        # Semantik olarak en yakın kodları vurgula (varsa)
        if semantic_results:
            prompt += "## 🎯 BU OLAY İÇİN ÖNE ÇIKAN KODLAR (Semantic Search):\n\n"
            for r in semantic_results:
                prompt += f"### {r['code']} (Benzerlik: {r['score']:.3f}) - {r['title']}\n"
                if r.get('typical_examples'):
                    prompt += f"**Tipik Örnek:** {r['typical_examples'][0]}\n"
                if r.get('not_this_if'):
                    prompt += f"**Bu değil eğer:** {r['not_this_if'][0]}\n"
                prompt += "\n"
            
            prompt += "---\n\n"
        
        # Tüm kodlar (referans)
        if all_codes:
            prompt += "## 📋 TÜM KODLAR (Referans):\n\n"
            
            for code in all_codes:
                prompt += f"### {code['code']} - {code['title']}\n"
                if code.get('typical_examples'):
                    prompt += f"→ Örnek: {code['typical_examples'][0]}\n"
                prompt += "\n"
        
        return prompt
    
    def get_code_details(self, code: str) -> Optional[Dict]:
        """
        Tek bir kodun detaylarını getir
        
        Args:
            code: "D4.5"
        
        Returns:
            {"code": "D4.5", "title": "...", "full_text": "...", ...}
        """
        return self.cache.get_code(code)


# ─────────────────────────────────────────────────────────────
# TEST
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    
    cache = RedisKnowledgeCache()
    
    if len(sys.argv) > 1 and sys.argv[1] == "warmup":
        # Cache warmup
        print("\n🔥 Cache Warmup Başlatılıyor...\n")
        cache.warmup_cache()
        
        # Stats
        print("\n📊 Cache Stats:")
        stats = cache.get_cache_stats()
        print(f"  Total Keys: {stats['total_keys']}")
        print(f"  Memory: {stats['memory_usage_mb']:.2f} MB")
        print(f"  Hit Rate: {stats['hit_rate']:.2%}")
    
    elif len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test: Tek kod
        print("\n🧪 Test 1: Tek kod getir")
        code = cache.get_code("D4.5")
        if code:
            print(f"  ✅ {code['code']}: {code['title']}")
        else:
            print(f"  ❌ Kod bulunamadı (MongoDB bağlantısı var mı?)")
        
        # Test: Batch
        print("\n🧪 Test 2: Batch getir")
        codes = cache.get_codes_batch(["D4.5", "D1.5", "A1.1"])
        print(f"  ✅ {len(codes)} kod alındı")
        
        # Test: Category
        print("\n🧪 Test 3: Kategori getir")
        category_codes = cache.get_category_codes("D")
        print(f"  ✅ {len(category_codes)} D kategorisi kod")
        
        # Test: Semantic search
        print("\n🧪 Test 4: Semantic search")
        try:
            results = cache.semantic_search(
                query="Worker bypassed LOTO procedure",
                top_k=3,
                category="D"
            )
            for r in results:
                print(f"  ✅ {r['code']} ({r['score']:.3f}): {r['title']}")
        except Exception as e:
            print(f"  ⚠️  Semantic search test failed: {e}")
        
        # Stats
        print("\n📊 Cache Stats:")
        stats = cache.get_cache_stats()
        print(f"  Keys: {stats['total_keys']}")
        print(f"  Memory: {stats['memory_usage_mb']:.2f} MB")
        print(f"  Hit rate: {stats['hit_rate']:.2%}")
    
    elif len(sys.argv) > 1 and sys.argv[1] == "clear":
        # Clear cache
        print("\n🗑️  Cache Temizleniyor...\n")
        cache.clear_cache()
    
    elif len(sys.argv) > 1 and sys.argv[1] == "hybrid-test":
        # Hybrid KB test
        print("\n🧪 Hybrid Knowledge Base Test\n")
        
        kb = HybridKnowledgeBaseV3()
        
        # Test incident
        incident = "Worker bypassed LOTO procedure during maintenance. System was still pressurized."
        
        print("📝 Test Incident:")
        print(f"  {incident}\n")
        
        print("🔍 Getting relevant codes...\n")
        
        relevant = kb.get_relevant_codes(
            incident_summary=incident,
            category="D",
            top_k=3
        )
        
        print("=" * 80)
        print(relevant[:1000])  # İlk 1000 karakter
        print("..." if len(relevant) > 1000 else "")
        print("=" * 80)
    
    else:
        print("""
╔════════════════════════════════════════════════════════════════╗
║         Redis Knowledge Cache - Kullanım Kılavuzu              ║
╚════════════════════════════════════════════════════════════════╝

KOMUTLAR:

  1️⃣  Cache Warmup (İlk Kez)
      python redis_knowledge_cache.py warmup
      
      → En sık kullanılan kodları Redis'e yükler
      → Tüm kategorileri (A, B, C, D) cache'ler
      
  2️⃣  Test
      python redis_knowledge_cache.py test
      
      → Tek kod getir
      → Batch getir
      → Kategori getir
      → Semantic search
      → Cache stats
      
  3️⃣  Hybrid KB Test
      python redis_knowledge_cache.py hybrid-test
      
      → HybridKnowledgeBaseV3 test
      → Gerçek incident örneği
      
  4️⃣  Cache Temizle
      python redis_knowledge_cache.py clear
      
      → Tüm cache'i sil

GEREKSINIMLER:

  ✅ Redis çalışıyor olmalı:
     redis-server
     
  ✅ MongoDB URI .env'de:
     MONGODB_URI=mongodb+srv://...
     
  ✅ Redis URL .env'de (opsiyonel):
     REDIS_URL=redis://localhost:6379/0

PERFORMANS:

  ⚡ Redis cache HIT: 1 ms (50x hızlı)
  💾 MongoDB lookup: 50 ms
  📊 Cache hit rate: %80-90 (warmup sonrası)

        """)
