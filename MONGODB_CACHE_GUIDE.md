# 🗄️ MongoDB Cache Implementation Guide

## 📍 Nereye Kaydediliyor?

```
rca_database (MongoDB)
└── analysis_cache (Collection)
    ├── Document 1: {cache_key, incident_ref, analysis_result, created_at, expires_at}
    ├── Document 2: {cache_key, incident_ref, analysis_result, created_at, expires_at}
    └── Document 3: ...
```

**Key Points:**
- ✅ **Persistent**: Container restart'ta cache kalır (Railway production için ideal)
- ✅ **Shared**: Multi-container'da tüm instance'lar paylaşabilir
- ✅ **TTL**: 30 gün sonra otomatik silinir (MongoDB TTL index)
- ✅ **Fast**: ~10-50ms query time
- ✅ **Scalable**: Unlimited storage

---

## 🚀 Kullanım - 3 Seçenek

### Seçenek 1: Auto-Detection (Önerilen)

```python
from agents.unified_analysis_pipeline import UnifiedAnalysisPipeline

# Otomatik olarak ortama göre seçer:
# - Railway production: MongoDB cache
# - Local development: Disk cache
pipeline = UnifiedAnalysisPipeline(
    use_rag=True,
    use_cache=True
    # use_mongodb_cache=None (auto-detect - default)
)

result = pipeline.analyze_incident(incident_data)
```

### Seçenek 2: Force MongoDB Cache

```python
pipeline = UnifiedAnalysisPipeline(
    use_rag=True,
    use_cache=True,
    use_mongodb_cache=True  # ← Force MongoDB
)
```

### Seçenek 3: Force Disk Cache

```python
pipeline = UnifiedAnalysisPipeline(
    use_rag=True,
    use_cache=True,
    use_mongodb_cache=False  # ← Force Disk
)
```

### Seçenek 4: Cache Devre Dışı

```python
pipeline = UnifiedAnalysisPipeline(
    use_rag=True,
    use_cache=False  # ← Cache kapalı
)
```

---

## 📋 Environment Variables

### Local Development (.env)

```env
# API Keys
OPENROUTER_API_KEY=sk-or-...
MONGODB_URI=mongodb://localhost:27017/

# Optional
RAILWAY_ENVIRONMENT=
```

### Railway Production (Project Settings)

```env
# Added automatically by Railway PostgreSQL
DATABASE_URL=postgresql://...

# Added automatically by Railway MongoDB
MONGODB_URI=mongodb+srv://...

# API Keys (manual setup)
OPENROUTER_API_KEY=sk-or-...

# Set to production
RAILWAY_ENVIRONMENT=production
```

---

## 🔍 MongoDB Cache Koleksyon Şeması

```json
{
  "_id": ObjectId,
  "cache_key": "a1b2c3d4e5f6g7h8...",  // MD5 hash of ref_no:description
  "incident_ref": "OIL-PURIFIER-001",
  "analysis_result": {
    "source": "api",
    "overview": { ... },
    "assessment": { ... },
    "root_cause_analysis": { ... }
  },
  "created_at": ISODate("2026-03-14T16:46:04.144Z"),
  "expires_at": ISODate("2026-04-13T16:46:04.144Z")  // TTL sütunu
}
```

---

## ⚙️ MongoDB Kurulum Adımları

### 1️⃣ Local Development (MongoDB Community)

```bash
# macOS
brew install mongodb-community
brew services start mongodb-community

# Windows (Docker)
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Linux
sudo systemctl start mongod
```

### 2️⃣ Railway Production

1. **Railway Dashboard'da**:
   - Project → Add → MongoDB
   - Otomatik olarak `MONGODB_URI` environment variable oluşturur

2. **Verify connection**:
```bash
# Test local connection
mongosh "mongodb://localhost:27017/"

# Test Railway connection
mongosh "$MONGODB_URI"
```

### 3️⃣ TTL Index Setup

Otomatik olarak `MongoDBCache.__init__()` oluşturur:

```python
# Manually if needed:
db.analysis_cache.createIndex(
    {"expires_at": 1},
    {expireAfterSeconds: 0}
)
```

---

## 📊 Cache Statistikleri

```python
from agents.unified_analysis_pipeline import UnifiedAnalysisPipeline

pipeline = UnifiedAnalysisPipeline(use_cache=True, use_mongodb_cache=True)

# Analiz yap
for incident in incidents:
    result = pipeline.analyze_incident(incident)

# İstatistikleri görmek
stats = pipeline.cache.get_stats()
print(f"Hit Rate: {stats['hit_rate']}")
print(f"Money Saved: {stats['money_saved']}")
print(f"Total Requests: {stats['total_requests']}")
```

**Output Örneği:**
```
{
  "total_requests": 10,
  "cache_hits": 5,
  "cache_misses": 5,
  "hit_rate": "50.0%",
  "money_saved": "$1.57"
}
```

---

## 🧹 Cache Yönetimi

### Cache'i Temizle

```python
# Disk cache temizle
from agents.unified_analysis_pipeline import AnalysisCache
cache = AnalysisCache()
cache.clear()

# MongoDB cache temizle
from agents.unified_analysis_pipeline import MongoDBCache
cache = MongoDBCache()
cache.clear()

# Pipeline aracılığıyla
pipeline.cache.clear()
```

### MongoDB'den Doğrudan Query

```bash
# MongoDB shell
mongosh

# Database seç
use rca_database

# Tüm cache'leri görmek
db.analysis_cache.find({})

# Spesifik cache görmek
db.analysis_cache.findOne({cache_key: "a1b2c3d4e5f6..."})

# Cache sayısını kontrol et
db.analysis_cache.countDocuments({})

# Süresi geçmiş cache'leri görmek
db.analysis_cache.find({expires_at: {$lt: new Date()}})

# Tüm cache'i silmek
db.analysis_cache.deleteMany({})
```

---

## 🔄 Migration Path: Disk → MongoDB

Mevcut disk cache'den MongoDB'ye migrate etmek:

```python
from pathlib import Path
import json
from agents.unified_analysis_pipeline import AnalysisCache, MongoDBCache

# Disk cache'den oku
disk_cache = AnalysisCache(cache_dir="cache/analyses")

# MongoDB cache'e yaz
mongo_cache = MongoDBCache()

# Tüm disk cache'leri migrate et
cache_dir = Path("cache/analyses")
for cache_file in cache_dir.glob("*.json"):
    with open(cache_file, 'r') as f:
        cached_data = json.load(f)
    
    # MongoDB'ye yaz
    mongo_cache.collection.insert_one({
        "cache_key": cache_file.stem,
        "incident_ref": cached_data.get("incident_ref"),
        "analysis_result": cached_data.get("analysis_result"),
        "created_at": cached_data.get("timestamp"),
        "expires_at": datetime.now() + timedelta(days=30)
    })

print("✅ Migration completed!")
```

---

## 📈 Performance Metrics

### Cache Hit Performance

| Metrik | Disk Cache | MongoDB Cache | API Call |
|--------|-----------|--------------|----------|
| **Latency** | <10ms | 10-50ms | 25-35s |
| **Cost** | $0.00 | $0.00 | $0.31 |
| **Persistence** | Session | ✅ Persistent | N/A |
| **Multi-container** | ❌ No | ✅ Yes | N/A |

### ROI Calculation

**Scenario:** 4 incidents/week, 60% repeat rate

```
Run 1 (New incident):     $0.31 (API)
Run 2-6 (Repeats):        $0.00 × 5 = $0 (Cache)
─────────────────────
Average per week:         $0.31 ÷ 1.2 = $0.155/incident
Weekly cost:              $0.155 × 4 = $0.62
Monthly savings:          $0.31 × 2 = $0.62/month
Annual savings:           $0.62 × 12 = $7.44/year
```

---

## 🚨 Troubleshooting

### MongoDB bağlantısı başarısız

```python
# Error: "MONGODB_URI environment variable not set!"
# Çözüm: .env dosyasına ekle
MONGODB_URI=mongodb://localhost:27017/

# Veya Railway'de Project Settings'ten ekle
```

### Cache'den okuma başarısız

```python
# Error: "MongoDB okuma hatası"
# Çözüm 1: MongoDB servisinin çalıştığını kontrol et
mongosh "mongodb://localhost:27017/"

# Çözüm 2: TTL index'in oluşturulduğunu kontrol et
db.analysis_cache.getIndexes()

# Çözüm 3: Log'ları kontrol et
# MongoDB daemon log: /var/log/mongodb/mongod.log
```

### Railway'de Production hatası

```
Error: "MONGODB_URI environment variable not set!"

Çözüm:
1. Railway Dashboard → Project → Variables
2. MongoDB service add edilmiş mi kontrol et
3. auto-inject görmek için redeploy yap
```

---

## ✅ Verification Checklist

- [ ] `MONGODB_URI` environment variable set edildi
- [ ] MongoDB service running (local dev)
- [ ] `pymongo` paketi installed: `pip install pymongo`
- [ ] Pipeline'da `use_mongodb_cache=True` veya auto-detect çalışıyor
- [ ] İlk analiz başarılı (API call)
- [ ] İkinci analiz MongoDB cache'den hızlı (cache hit)
- [ ] `pipeline.cache.get_stats()` hit rate > 0%
- [ ] Railway production'da MONGODB_URI injected edildi
- [ ] Container restart'ta cache kalıyor

---

## 💡 Best Practices

1. **Local dev'de disk cache kullan**
   ```python
   pipeline = UnifiedAnalysisPipeline(use_cache=True, use_mongodb_cache=False)
   ```

2. **Production'da MongoDB cache kullan**
   - `use_mongodb_cache=True` yap veya auto-detect'e bırak

3. **Regular backups**
   ```bash
   # MongoDB backup
   mongodump --uri="$MONGODB_URI" --out=./backup/
   ```

4. **Monitor cache hit rate**
   ```python
   stats = pipeline.cache.get_stats()
   if float(stats['hit_rate'].rstrip('%')) < 30:
       print("⚠️ Low cache hit rate - check repeat incident frequency")
   ```

5. **Clean up old cache**
   ```python
   # TTL otomatik temizler, ama manuel de yapabilirsin:
   pipeline.cache.collection.delete_many({
       "expires_at": {"$lt": datetime.now()}
   })
   ```

---

## 📞 Test

```bash
# MongoDB cache demo çalıştır
python3 test_mongodb_cache.py

# Expected output:
# RUN 1: ~30 seconds, $0.31 (API)
# RUN 2: <1 second, $0.00 (MongoDB Cache) 🎉
```

---

**🎯 Result:** Cache'ler artık MongoDB'de, Railway'de persistent ve scalable! 🚀
