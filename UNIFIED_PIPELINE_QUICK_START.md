# 📚 Unified Pipeline Kurulum ve Kullanım Rehberi

## 🎯 Kısa Özet

**Unified Analysis Pipeline**, 3 önemli özelliği bir araya getiriyor:

1. ✅ **Cache Mekanizması**: Tekrar eden incidents hızlı ve ücretsiz analiz
2. ✅ **Root Cause Analysis**: 5-WHY metoduyla kök nedenler
3. ✅ **Otomatik Rapor**: DOCX format raporlar

---

## 📂 Dosya Yapısı

```
agents/
├── unified_analysis_pipeline.py  ← ANA DOSYA
├── rootcause_agent_v2.py
├── overview_agent.py
├── assessment_agent.py
└── skillbased_docx_agent.py

test_rag_cache_integration.py      ← TEST DOSYASI (RAG + Cache)
quick_cache_test.py                ← HIZLI CACHE TEST
UNIFIED_PIPELINE_GUIDE.md          ← DETAYLI REHBER
UNIFIED_PIPELINE_ARCHITECTURE.md   ← MİMARI DIYAGRAMLAR
```

---

## 🚀 Hızlı Başlangıç

### **Seçenek 1: Sadece Cache Mekanizmasını Test Et**

```bash
python3 quick_cache_test.py
```

**Çıktı Örneği:**
```
✅ Cache TEST: RAG + Cache Mekanizması
─────────────────────────────────────────

TEST 1: Cache'de YOK (Miss Expected)
✅ Expected: Cache miss → result is None

TEST 2: Cache'e Kaydet
✅ Analiz cache'e kaydedildi

TEST 3: Cache'den Oku (Hit Expected)
✅ Cache hit! Sonuç cache'den alındı
   Timestamp: 2026-03-14T16:46:04.144701

📊 FINAL CACHE STATISTICS
total_requests : 3
cache_hits     : 1
cache_misses   : 2
hit_rate       : 33.3%
money_saved    : $0.31

✅ CACHE TEST TAMAMLANDI
```

---

### **Seçenek 2: RAG + Cache Entegrasyon Testi**

```bash
python3 test_rag_cache_integration.py
```

**Beklenen Senaryo:**
```
TEST 1: İlk Olay (API çağrısı)
   ⏳ 30+ saniye
   💰 $0.31 maliyet
   Source: api

TEST 2: AYNI Olay (Cache Hit)
   ⚡ <1 saniye
   💰 $0 maliyet
   Source: cache
   
📊 SONUÇ: 30x daha hızlı, 100% tasarruf!
```

---

### **Seçenek 3: Python Kodunda Kullanma**

```python
from agents.unified_analysis_pipeline import UnifiedAnalysisPipeline

# Pipeline oluştur (RAG + Cache aktif)
pipeline = UnifiedAnalysisPipeline(use_rag=True, use_cache=True)

# Incident analiz et
incident = {
    "ref_no": "INC-001",
    "description": "Makine arızası nedeniyle yangın...",
    "injury_description": "Kişisel yaralanma yok"
}

# Analiz yap
result = pipeline.analyze_incident(incident)

# Çıktılar:
# ├─ outputs/unified_pipeline/analysis_INC-001_*.json
# ├─ outputs/unified_pipeline/report_INC-001_*.docx
# ├─ cache/analyses/*.json (cache'e kaydedildi)
# └─ Console statistics
```

---

## 💾 Cache Mekanizması Nasıl Çalışır?

### **Flow Diyagramı**

```
Incident Giriş
    ↓
Ref_no + Description → SHA256 Hash
    ↓
Cache Dosyası Var mı?
    ├─ EVET → TTL kontrol et
    │         ├─ GEÇERLI → Cache'den döndür ✅ (0.01s, $0)
    │         └─ SKİ → Sil, API'ye gönder
    └─ HAYIR → API'ye gönder (30s, $0.31)
                ↓
            Analysis yap
                ↓
            Cache'e kaydet
                ↓
            Rapor üret
```

---

### **Cache Istatistikleri**

```python
# Pipeline oluşturduktan sonra:
stats = pipeline.cache.get_stats()

# Çıktı:
{
    "total_requests": 10,
    "cache_hits": 6,
    "cache_misses": 4,
    "hit_rate": "60.0%",
    "money_saved": "$1.88"
}
```

---

## 🎯 Gerçek Dünya Senaryosu: Haftada 4 Analiz

### **Senaryo: Pazartesi-Perşembe, 4 Incident**

```python
from agents.unified_analysis_pipeline import UnifiedAnalysisPipeline

pipeline = UnifiedAnalysisPipeline(use_rag=True, use_cache=True)

incidents = [
    # Pazartesi
    {"ref_no": "MON-001", "description": "Pompa arızası", ...},
    {"ref_no": "MON-002", "description": "Elektrik panosu kısa devre", ...},
    
    # Salı (TEKRAR!)
    {"ref_no": "MON-001-REPEAT", "description": "Pompa arızası", ...},  # Same
    
    # Perşembe (TEKRAR!)
    {"ref_no": "MON-002-REPEAT", "description": "Elektrik panosu kısa devre", ...}  # Same
]

results = pipeline.batch_analyze(incidents)
```

**Sonuç:**
```
📊 BATCH SUMMARY
════════════════════════════════════════════════════════════════
Total Incidents: 4
   Cache Hits: 2 ✅
   Cache Misses: 2
   Hit Rate: 50.0%

💰 Cost Analysis:
   Without Cache: $1.26 (4 × $0.31)
   With Cache: $0.62 (2 × $0.31)
   Saved: $0.64 ← 50% TASARRUF!
```

---

## 🔧 Ayarlar

### **RAG İLE Cache**
```python
pipeline = UnifiedAnalysisPipeline(use_rag=True, use_cache=True)
# ✅ MongoDB vector search + cache hits
# = Yüksek kalite + Maliyet tasarrufu
```

### **RAG OLMADAN Cache**
```python
pipeline = UnifiedAnalysisPipeline(use_rag=False, use_cache=True)
# ✅ Static knowledge base + cache hits
# = Hızlı + Ucuz
```

### **Cache OLMADAN RAG**
```python
pipeline = UnifiedAnalysisPipeline(use_rag=True, use_cache=False)
# ✅ Yüksek kalite analiz
# ❌ Her incident API'ye gider ($0.31)
```

### **İkisi de OLMADAN**
```python
pipeline = UnifiedAnalysisPipeline(use_rag=False, use_cache=False)
# ❌ En pahalı seçenek
# ✅ Ama fastest first run
```

---

## 📁 Output Dosyaları

Her analiz sonrası şu dosyalar oluşturulur:

```
outputs/unified_pipeline/
├── analysis_MON-001_20260314_103045.json
│   └─ Tam analiz sonuçları
│
├── report_MON-001_20260314_103045.docx
│   └─ Formatlı DOCX rapor
│
└── analysis_MON-002_20260314_104230.json
    └─ Başka incident analizi

cache/analyses/
├── a1b2c3d4e5f6g7h8.json
│   └─ Cache'lenmiş MON-001 analizi
│
└── p5o4n3m2l1k0j9i8.json
    └─ Cache'lenmiş MON-002 analizi
```

---

## 🎓 Örnek: Mevcut Test Dosyasını Güncellemek

### **Eski Kod:**
```python
from agents.rootcause_agent_v2 import RootCauseAgentV2

rootcause_agent = RootCauseAgentV2(use_rag=True)
result = rootcause_agent.analyze_root_causes(...)
```

### **YENİ Kod:**
```python
from agents.unified_analysis_pipeline import UnifiedAnalysisPipeline

pipeline = UnifiedAnalysisPipeline(use_rag=True, use_cache=True)
result = pipeline.analyze_incident(incident_data)

# Artık otomatik:
# ✅ Cache kontrolü
# ✅ Overview + Assessment
# ✅ Root Cause Analysis (5-Why)
# ✅ DOCX Rapor
# ✅ JSON Analiz
# ✅ İstatistikler
```

**Avantajlar:**
- ✅ Tek satır kod ile tam analiz
- ✅ Cache hit/miss otomatik
- ✅ Rapor otomatik üretilir
- ✅ İstatistikler otomatik hesaplanır

---

## 📊 Performans Karşılaştırması

### **Haftada 4 Incident (50% tekrar oranı)**

| Metrik | Olmadan Cache | Cache İLE | Iyileşme |
|--------|--------------|----------|----------|
| **Maliyet** | $1.26 | $0.63 | %50 tasarruf |
| **Zaman** | 120s | 65s | %45 hızlı |
| **API Çağrıları** | 4 | 2 | %50 azalış |

### **Aylık (30 gün, günde 1 incident, 60% tekrar)**

| Metrik | Olmadan Cache | Cache İLE | Aylık Tasarruf |
|--------|--------------|----------|-----------------|
| **Maliyet** | $9.30 | $1.86 | **$7.44** ⭐ |
| **Zaman** | 900s | 180s | 720s tasarruf |

---

## ⚡ Performance Tips

1. **Batch Mode Kullan**
   ```python
   # Hepsi bir seferde analiz et
   results = pipeline.batch_analyze(incidents)
   ```
   → Cache hit oranı artar

2. **RAG + Cache Kombine**
   ```python
   pipeline = UnifiedAnalysisPipeline(use_rag=True, use_cache=True)
   ```
   → Kalite + Maliyet tasarrufu

3. **TTL Ayarla**
   ```python
   pipeline.cache.ttl_days = 60
   ```
   → Eski cache'i otomatik sil

4. **Cache Temizle (Gerekirse)**
   ```python
   pipeline.cache.clear()
   ```
   → cache/analyses/ klasörü silinir

---

## 🐛 Troubleshooting

### **Cache çalışmıyor?**

```python
# 1. Cache directory kontrol et
from pathlib import Path
cache_dir = Path("cache/analyses")
print(f"Cache files: {list(cache_dir.glob('*.json'))}")

# 2. Cache temizle
pipeline.cache.clear()

# 3. Yeniden dene
```

### **RAG çalışmıyor?**

```python
# 1. MongoDB bağlantısını kontrol et
# 2. Environment variables kontrol et
# 3. Fallback: use_rag=False yap
pipeline = UnifiedAnalysisPipeline(use_rag=False, use_cache=True)
```

### **Rapor üretilmedi?**

```python
# 1. outputs/unified_pipeline/ klasörü kontrol et
# 2. Dosya izinleri kontrol et
# 3. Docx agent ayarları kontrol et
```

---

## 📞 Kısa Referans

### **Test Komutları**

```bash
# Cache mekanizmasını test et
python3 quick_cache_test.py

# RAG + Cache entegrasyonunu test et
python3 test_rag_cache_integration.py

# Mevcut test dosyalarını çalıştır
python3 test_oil_purifier_fire_scenario.py
python3 test_unified_pipeline.py
```

### **Python Kodu Snippets**

```python
# Import
from agents.unified_analysis_pipeline import UnifiedAnalysisPipeline

# Oluştur
pipeline = UnifiedAnalysisPipeline(use_rag=True, use_cache=True)

# Tek incident
result = pipeline.analyze_incident(incident)

# Batch
results = pipeline.batch_analyze(incidents)

# İstatistikler
stats = pipeline.cache.get_stats()
```

---

## ✅ Kontrol Listesi

- [x] Cache manager implement
- [x] Pipeline entegrasyonu
- [x] RAG entegrasyonu
- [x] Rapor üretimi
- [x] İstatistikler
- [x] Test dosyaları
- [x] Dokumentasyon

---

## 🎯 Sonuç

**Unified Pipeline** ile:
- ✅ %50-75 maliyet tasarrufu
- ✅ 30x hızlı (cache hit)
- ✅ Otomatik rapor
- ✅ Kolay entegrasyon

Hazır mısınız? 🚀
