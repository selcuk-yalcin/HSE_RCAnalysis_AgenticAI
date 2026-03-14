# V3 Vector Search Test Environment

Bu klasör, MongoDB Atlas Vector Search entegrasyonunu test etmek için oluşturulmuştur.
Orijinal agent'lar (`rootcause_agent_v2.py`, `orchestrator.py`) değiştirilmemiştir.

## 📁 Yapı

```
v3_vector_search/
├── README.md                           # Bu dosya
├── requirements_v3.txt                 # Ek bağımlılıklar (pymongo, openai)
├── .env.v3.example                     # Örnek environment variables
│
├── knowledge_base_vector_v3.py         # MongoDB vector search implementasyonu
│                                       # - HSG245VectorDB: Veritabanı yönetimi
│                                       # - HybridKnowledgeBase: Dictionary + Vector
│
├── rootcause_agent_v3.py               # V2'den kopyalanmış + vector entegrasyonu
│                                       # - Immediate causes: Dictionary (aynı)
│                                       # - Root causes: Hibrit (vector öncelikli)
│
├── orchestrator_v3.py                  # Orchestrator'ın vector versiyonu
│                                       # - RootCauseAgentV3 kullanıyor
│                                       # - Tüm diğer agent'lar aynı
│
└── test_vector_search.py               # Test scripti
                                        # - Vector search testi
                                        # - Hibrit KB testi
                                        # - Tam analiz testi
```

## 🚀 Kurulum

### 1. MongoDB Atlas Hesabı Oluştur
```bash
# https://www.mongodb.com/cloud/atlas/register
# M0 (Free tier) yeterli
```

### 2. Bağımlılıkları Yükle
```bash
pip install -r v3_vector_search/requirements_v3.txt
```

### 3. Environment Variables Ayarla
```bash
# .env dosyasına ekle (veya .env.v3 oluştur)
USE_VECTOR_SEARCH=true
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/hsg245_kb
OPENROUTER_API_KEY=sk-or-v1-...
```

### 4. Knowledge Base'i Yükle
```bash
# knowledge_base.md → MongoDB'ye yükle
python agents/v3_vector_search/knowledge_base_vector_v3.py populate
```

### 5. MongoDB Atlas Vector Index Oluştur (MANUEL)
Atlas UI → Database → Search → Create Search Index:
```json
{
  "mappings": {
    "dynamic": true,
    "fields": {
      "embedding": {
        "type": "knnVector",
        "dimensions": 1536,
        "similarity": "cosine"
      }
    }
  }
}
```

### 6. Test Et
```bash
# Semantik arama testi
python agents/v3_vector_search/test_vector_search.py

# Tam analiz testi (V3 orchestrator)
python agents/v3_vector_search/orchestrator_v3.py
```

## 🔄 Orijinal vs V3 Farkları

### `rootcause_agent_v2.py` → `rootcause_agent_v3.py`
- ✅ V2'nin tüm özellikleri korundu
- ➕ Hibrit knowledge base eklendi (dictionary + vector)
- ➕ Semantik benzerlik bazlı kod önceliklendirme

### `orchestrator.py` → `orchestrator_v3.py`
- ✅ Tüm agent'lar aynı şekilde çalışıyor
- ➕ RootCauseAgentV3 kullanıyor
- ➕ Vector search aktif/pasif toggle

## 📊 Performans Karşılaştırması

Test için aynı vakayı hem V2 hem V3 ile analiz edin:

```bash
# V2 (Orijinal)
python test_reca_maog_detailed.py

# V3 (Vector Search)
python agents/v3_vector_search/test_vector_search.py
```

## 🎯 Avantajlar

| Özellik | V2 | V3 |
|---------|----|----|
| **Hız** | ⚡⚡⚡ | ⚡⚡⚡ (aynı) |
| **Doğruluk** | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Kod Önceliklendirme** | ❌ | ✅ |
| **Semantik Arama** | ❌ | ✅ |
| **Maliyet** | $0 | +$0.10/100 analiz |

## ⚠️ Notlar

- Orijinal `rootcause_agent_v2.py` **değiştirilmedi**
- V3 tamamen ayrı klasörde çalışıyor
- `.env` dosyasında `USE_VECTOR_SEARCH=false` ise V3 bile dictionary kullanır (fallback)
- Production'a geçmeden önce yeterince test edin

## 🔙 Geri Dönüş

V3'ü beğenmediyseniz:
```bash
# Sadece bu klasörü silin
rm -rf agents/v3_vector_search

# Orijinal kodlar aynen çalışmaya devam eder
```
