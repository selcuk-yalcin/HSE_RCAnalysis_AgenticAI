# Async V3 - Hızlı Başlangıç Kılavuzu

## 🎯 Problem ve Çözüm

### ❌ Problem
- **800 saniye** analiz süresi → Railway timeout (300s)
- Kullanıcı 13 dakika bekliyor → Kötü UX
- Eşzamanlı kullanıcı desteği yok

### ✅ Çözüm: Async Orchestrator
- **5 saniye** response → Job ID döner
- Analiz background'da çalışır (800s sorun değil)
- Real-time progress (WebSocket)
- 200 eşzamanlı kullanıcı desteği

---

## 🚀 Local Test (5 Dakika)

### 1. Redis Başlat
```bash
# macOS
brew install redis
redis-server

# veya Docker
docker run -d -p 6379:6379 redis
```

### 2. Celery Worker Başlat (Yeni Terminal)
```bash
cd agents/v3_vector_search

# Dependencies yükle (ilk kez)
pip install -r requirements_async.txt

# Worker başlat (10 paralel task)
celery -A async_orchestrator_v3.celery_app worker \
  --loglevel=info \
  --concurrency=10
```

**Output:**
```
[2024-03-08 10:00:00,000: INFO/MainProcess] Connected to redis://localhost:6379/0
[2024-03-08 10:00:00,100: INFO/MainProcess] celery@hostname ready.
```

### 3. FastAPI Başlat (Yeni Terminal)
```bash
cd agents/v3_vector_search

# API başlat
uvicorn async_orchestrator_v3:app --reload --port 8000
```

**Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 4. Test Request Gönder
```bash
# Test incident data
curl -X POST http://localhost:8000/api/v3/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "company_test",
    "incident_id": "INC-001",
    "part1_data": {"description": "Test incident"},
    "part2_data": {},
    "investigation_data": {
      "description": "Worker bypassed LOTO procedure. System was still pressurized. Chemical spray incident. Worker had done this 5 times before without issue."
    }
  }'
```

**Response (5s içinde):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Analiz başlatıldı. /api/v3/status/{job_id} ile durumu kontrol edin.",
  "websocket_url": "ws://localhost:8000/ws/progress/550e8400-...",
  "streaming_ui_url": "/streaming?job_id=550e8400-..."
}
```

### 5. Streaming UI'ı Aç
```bash
# Browser'da aç
open http://localhost:8000/streaming?job_id=550e8400-e29b-41d4-a716-446655440000
```

**Göreceksiniz:**
- ✅ Real-time progress bar
- ✅ Adım adım güncelleme (Immediate Causes → Root Causes → Rapor)
- ✅ Tamamlandığında sonuç gösterimi

---

## 📊 Alternatif: Polling (WebSocket yerine)

```bash
# Status sorgula (her 5 saniyede)
while true; do
  curl http://localhost:8000/api/v3/status/550e8400-e29b-41d4-a716-446655440000
  sleep 5
done
```

**Output (running):**
```json
{
  "job_id": "550e8400-...",
  "status": "running",
  "progress": 45,
  "current_step": "Root Causes analizi yapılıyor...",
  "created_at": "2024-03-08T10:00:00",
  "started_at": "2024-03-08T10:00:05"
}
```

**Output (completed):**
```json
{
  "job_id": "550e8400-...",
  "status": "completed",
  "progress": 100,
  "current_step": "Tamamlandı",
  "result": {
    "final_root_causes": [
      {
        "code": "D4.5",
        "standard_title_tr": "Energy Isolation (LOTO) Ineffective",
        "cause_tr": "LOTO prosedürü mevcut ancak doğrulama yapılmıyor"
      },
      {
        "code": "D1.5",
        "standard_title_tr": "Normalization of Deviance",
        "cause_tr": "Tekrarlanan ihlaller normal kabul edildi"
      }
    ],
    "final_report_tr": "<html>...</html>"
  }
}
```

---

## 🔥 Batch Processing (10 Rapor Paralel)

### Test Data Hazırla
```bash
# test_batch.json
cat > test_batch.json << 'EOF'
{
  "tenant_id": "company_test",
  "incidents": [
    {
      "incident_id": "INC-001",
      "part1_data": {},
      "part2_data": {},
      "investigation_data": {"description": "LOTO bypass incident 1"}
    },
    {
      "incident_id": "INC-002",
      "part1_data": {},
      "part2_data": {},
      "investigation_data": {"description": "LOTO bypass incident 2"}
    },
    {
      "incident_id": "INC-003",
      "part1_data": {},
      "part2_data": {},
      "investigation_data": {"description": "Fall from height incident"}
    }
  ],
  "priority": 3
}
EOF
```

### Batch Request Gönder
```bash
curl -X POST http://localhost:8000/api/v3/batch-analyze \
  -H "Content-Type: application/json" \
  -d @test_batch.json
```

**Response:**
```json
{
  "batch_id": "batch-company_test-3",
  "job_ids": [
    "job-1-uuid",
    "job-2-uuid",
    "job-3-uuid"
  ],
  "total": 3,
  "message": "3 analiz batch olarak başlatıldı"
}
```

### Batch Status
```bash
curl "http://localhost:8000/api/v3/batch-status?job_ids=job-1-uuid,job-2-uuid,job-3-uuid"
```

**Response:**
```json
{
  "total": 3,
  "completed": 1,
  "running": 2,
  "failed": 0,
  "pending": 0
}
```

---

## 🌐 Frontend Entegrasyonu

### JavaScript Example
```javascript
// 1. Analiz başlat
const response = await fetch('http://localhost:8000/api/v3/analyze', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    tenant_id: 'company_a',
    incident_id: 'INC-001',
    part1_data: {},
    part2_data: {},
    investigation_data: {description: 'Incident description...'}
  })
});

const {job_id} = await response.json();

// 2. WebSocket bağlan (Real-time progress)
const ws = new WebSocket(`ws://localhost:8000/ws/progress/${job_id}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Progress: ${data.progress}% - ${data.step}`);
  
  // UI güncelle
  document.getElementById('progressBar').style.width = `${data.progress}%`;
  document.getElementById('stepText').textContent = data.step;
  
  if (data.status === 'completed') {
    // Sonucu göster
    displayResult(data.result);
  }
};

// 3. Alternatif: Polling (WebSocket yerine)
function pollJobStatus() {
  setInterval(async () => {
    const res = await fetch(`http://localhost:8000/api/v3/status/${job_id}`);
    const job = await res.json();
    
    updateUI(job.progress, job.current_step);
    
    if (job.status === 'completed') {
      displayResult(job.result);
      clearInterval(polling);
    }
  }, 2000);
}
```

---

## 📈 Performans Metrikleri

### Senkron (Mevcut) vs Asenkron (V3)

| Metrik | Senkron | Asenkron | İyileşme |
|--------|---------|----------|----------|
| **İlk Response** | 800s (timeout) | **5s** | **160x hızlı** |
| **UX** | Kullanıcı bekler | Real-time progress | ✅ |
| **Eşzamanlılık** | 1 | **200+** | **200x** |
| **Railway Uyumlu** | ❌ | ✅ | - |
| **Hata Recovery** | ❌ | ✅ Retry | - |

### Kapasite Hesaplama
```python
# 10 Worker, 800s/analiz
Throughput: 10 × (3600/800) = 45 rapor/saat

# 200 kullanıcı senaryosu
Bekleme: 200 / 45 = 4.4 saat

# ÇÖZ ÜM: Auto-scaling
Peak time: 10 worker → 20 worker
Throughput: 90 rapor/saat
Bekleme: 200 / 90 = 2.2 saat ✅
```

---

## 🐛 Debugging

### Celery Worker Logs
```bash
# Worker logs
celery -A async_orchestrator_v3.celery_app worker --loglevel=debug

# Active tasks
celery -A async_orchestrator_v3.celery_app inspect active

# Worker stats
celery -A async_orchestrator_v3.celery_app inspect stats
```

### MongoDB Job Collection
```javascript
// MongoDB shell'de
use hsg245_jobs
db.rca_jobs.find({status: "running"})
db.rca_jobs.find({job_id: "550e8400-..."})
```

### Redis Queue
```bash
# Redis CLI
redis-cli

# Keys kontrol
KEYS celery*

# Queue uzunluğu
LLEN celery

# Pending tasks
LRANGE celery 0 -1
```

---

## ✅ Production'a Geçiş

### 1. Environment Variables
```bash
# .env
USE_VECTOR_SEARCH=true
MONGODB_URI=mongodb+srv://prod-user:pass@cluster.mongodb.net/hsg245_kb
REDIS_URL=redis://prod-redis:6379/0
OPENROUTER_API_KEY=sk-or-v1-...
ANTHROPIC_API_KEY=sk-ant-...
```

### 2. Railway Deploy
```bash
# Railway'e deploy et
railway up --service web
railway up --service worker --config railway-worker.toml

# Variables ayarla
railway variables set MONGODB_URI=...
railway variables set REDIS_URL=${{Redis.REDIS_URL}}
```

### 3. Test Production
```bash
# Production test
curl -X POST https://your-app.up.railway.app/api/v3/analyze \
  -H "Content-Type: application/json" \
  -d @test_incident.json

# Streaming UI
open https://your-app.up.railway.app/streaming?job_id=...
```

---

## 📞 Troubleshooting

### Problem: Redis connection hatası
```bash
# Kontrol
redis-cli ping
# PONG

# Çözüm: Redis başlat
redis-server
```

### Problem: Worker başlamıyor
```bash
# Logs kontrol
celery -A async_orchestrator_v3.celery_app worker --loglevel=debug

# MongoDB connection kontrol
echo $MONGODB_URI
```

### Problem: WebSocket bağlanamıyor
```bash
# Firewall kontrol
# uvicorn WebSocket support var mı
pip install "uvicorn[standard]"

# Browser console logs
# Connection refused → API çalışıyor mu kontrol et
```

---

## 🎉 Başarı Kriterleri

✅ Redis çalışıyor (redis-cli ping → PONG)
✅ Worker aktif (celery inspect stats)
✅ API sağlıklı (curl /health → 200)
✅ Test analizi başladı (job_id alındı)
✅ WebSocket bağlandı (progress updates geliyor)
✅ Analiz tamamlandı (result alındı)
✅ Streaming UI açıldı ve progress görünüyor

**Sistem hazır!** 🚀
