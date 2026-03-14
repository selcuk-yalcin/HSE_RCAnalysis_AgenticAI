# Railway Deployment Guide - Async V3

## 🏗️ Railway Services Architecture

### Gerekli Servisler

```
Railway Project: HSG245-RCA-V3
├── Web Service (FastAPI)
├── Worker Service (Celery)
├── Redis (Message Broker)
└── MongoDB Atlas (External - Vector + Jobs)
```

---

## 1️⃣ Redis Service Kurulumu

### Railway Dashboard
1. **New** → **Database** → **Add Redis**
2. **Name:** `hsg245-redis`
3. Deploy ettikten sonra **REDIS_URL** kopyala

**Output:**
```
REDIS_URL=redis://default:password@redis.railway.internal:6379
```

---

## 2️⃣ Web Service (FastAPI)

### Dosya: `railway.toml`
```toml
[build]
builder = "NIXPACKS"
buildCommand = "pip install -r agents/v3_vector_search/requirements_async.txt"

[deploy]
startCommand = "cd agents/v3_vector_search && uvicorn async_orchestrator_v3:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3

[env]
PORT = { default = "8000" }
```

### Environment Variables
```bash
# Railway Dashboard → Web Service → Variables

# Ports
PORT=8000

# MongoDB (Atlas)
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/hsg245_kb

# Redis (Railway internal)
REDIS_URL=${{Redis.REDIS_URL}}

# API Keys
OPENROUTER_API_KEY=sk-or-v1-...
ANTHROPIC_API_KEY=sk-ant-...

# Vector Search
USE_VECTOR_SEARCH=true
```

**Deploy Command:**
```bash
railway up --service web
```

---

## 3️⃣ Worker Service (Celery)

### Dosya: `railway-worker.toml`
```toml
[build]
builder = "NIXPACKS"
buildCommand = "pip install -r agents/v3_vector_search/requirements_async.txt"

[deploy]
startCommand = "cd agents/v3_vector_search && celery -A async_orchestrator_v3.celery_app worker --loglevel=info --concurrency=10 --max-tasks-per-child=50"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[env]
WORKER_CONCURRENCY = { default = "10" }
```

### Environment Variables
```bash
# Railway Dashboard → Worker Service → Variables
# (Web ile aynı variables'ları kopyala)

MONGODB_URI=${{Web.MONGODB_URI}}
REDIS_URL=${{Redis.REDIS_URL}}
OPENROUTER_API_KEY=${{Web.OPENROUTER_API_KEY}}
ANTHROPIC_API_KEY=${{Web.ANTHROPIC_API_KEY}}
USE_VECTOR_SEARCH=true

# Worker-specific
WORKER_CONCURRENCY=10
```

**Deploy Command:**
```bash
railway up --service worker --config railway-worker.toml
```

---

## 4️⃣ Auto-Scaling Configuration

### Web Service Scaling
```yaml
# Railway Dashboard → Web Service → Settings → Scaling

# Vertical Scaling
Memory: 512 MB (min) → 2 GB (max)
CPU: 0.5 vCPU (min) → 2 vCPU (max)

# Horizontal Scaling
Replicas: 1 (min) → 3 (max)
Target CPU: 70%
Target Memory: 80%
```

### Worker Service Scaling
```yaml
# Railway Dashboard → Worker Service → Settings → Scaling

# Vertical Scaling
Memory: 1 GB (min) → 4 GB (max)
CPU: 1 vCPU (min) → 2 vCPU (max)

# Horizontal Scaling
Replicas: 2 (normal) → 10 (peak)
Custom Metric: Queue Length
  - Queue < 10: 2 workers
  - Queue 10-50: 5 workers
  - Queue > 50: 10 workers
```

---

## 5️⃣ Health Checks & Monitoring

### Web Service Health Check
```python
# async_orchestrator_v3.py'de mevcut
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "rca-async-v3",
        "timestamp": datetime.utcnow().isoformat()
    }
```

**Railway Health Check Config:**
- Path: `/health`
- Interval: 30s
- Timeout: 10s
- Success Threshold: 2
- Failure Threshold: 3

### Worker Health Monitoring
```bash
# Celery events monitoring
celery -A async_orchestrator_v3.celery_app events

# Worker status
celery -A async_orchestrator_v3.celery_app inspect active
celery -A async_orchestrator_v3.celery_app inspect stats
```

---

## 6️⃣ Custom Domains & NGINX

### Railway Public URL
```
Default: https://hsg245-rca-v3.up.railway.app
Custom: https://rca.yourcompany.com
```

### NGINX Reverse Proxy (Opsiyonel)
```nginx
# Railway → New Service → NGINX

upstream fastapi_backend {
    server web.railway.internal:8000;
}

server {
    listen 80;
    server_name rca.yourcompany.com;

    location / {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws/ {
        proxy_pass http://fastapi_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
```

---

## 7️⃣ Deployment Commands Özeti

```bash
# İlk kurulum
railway login
railway init
railway link

# Redis ekle
railway add -d redis

# Web service deploy
railway up --service web

# Worker service deploy
railway up --service worker --config railway-worker.toml

# Environment variables ayarla
railway variables set MONGODB_URI=...
railway variables set OPENROUTER_API_KEY=...

# Logs
railway logs --service web
railway logs --service worker

# Domain ekle
railway domain

# Redeploy (update sonrası)
railway up
```

---

## 8️⃣ Maliyet Tahmini

| Service | Tier | RAM | CPU | Maliyet/Ay |
|---------|------|-----|-----|------------|
| **Web** | Starter | 512 MB | 0.5 vCPU | $5 |
| **Web** | Pro | 2 GB | 1 vCPU | $20 |
| **Worker (2x)** | Pro | 1 GB × 2 | 1 vCPU × 2 | $20 |
| **Worker (10x)** | Pro | 1 GB × 10 | 1 vCPU × 10 | $100 |
| **Redis** | - | 256 MB | - | $5 |
| **NGINX** | - | 128 MB | - | $5 (opsiyonel) |

### Senaryo Maliyetleri
```
Minimal (Test):         $10/ay  (Web + Worker + Redis)
Standart (50 user):     $30/ay  (Web + 2 Worker + Redis)
Pro (200 user):         $70/ay  (Web + 5 Worker + Redis)
Enterprise (1000 user): $250/ay (Web×2 + 20 Worker + Redis)
```

**MongoDB Atlas:** Ücretsiz M0 veya $9/ay (M2)

---

## 9️⃣ Monitoring & Alerting

### Sentry Integration (Hata İzleme)
```python
# async_orchestrator_v3.py başına ekle
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=1.0,
    environment="production"
)
```

**Railway Variables:**
```bash
SENTRY_DSN=https://...@sentry.io/...
```

### Datadog (Opsiyonel)
```bash
# Railway → Add Integration → Datadog
# Otomatik metrics, logs, traces
```

---

## 🔟 Production Checklist

### Deployment Öncesi
- [ ] MongoDB Atlas'ta vector index oluşturuldu
- [ ] Redis Railway'de provision edildi
- [ ] Environment variables tamamlandı
- [ ] Health check endpoints test edildi
- [ ] WebSocket connections test edildi

### Deployment
- [ ] Web service deploy edildi
- [ ] Worker service deploy edildi
- [ ] Custom domain ayarlandı (opsiyonel)
- [ ] SSL certificate aktif
- [ ] CORS settings production için güncellendi

### Deployment Sonrası
- [ ] /health endpoint erişilebilir
- [ ] Test analizi başarıyla tamamlandı
- [ ] WebSocket real-time progress çalışıyor
- [ ] Batch processing test edildi
- [ ] Monitoring aktif (Sentry/Datadog)
- [ ] Backup stratejisi oluşturuldu

---

## 🆘 Troubleshooting

### Problem: Worker bağlanamıyor
```bash
# Redis URL'i kontrol et
railway logs --service worker | grep "REDIS"

# Çözüm: Environment variable güncelle
railway variables set REDIS_URL=${{Redis.REDIS_URL}}
```

### Problem: WebSocket timeout
```bash
# Railway proxy timeout artır
# railway.toml'a ekle:
[deploy]
websocketTimeout = 3600  # 1 saat
```

### Problem: Memory leak
```bash
# Worker restart policy
celery -A async_orchestrator_v3.celery_app worker \
  --max-tasks-per-child=50 \
  --max-memory-per-child=800000  # 800 MB
```

### Problem: Slow performance
```bash
# Worker concurrency artır
railway variables set WORKER_CONCURRENCY=20

# Redeploy
railway up --service worker
```

---

## 📞 Support & Resources

- **Railway Docs:** https://docs.railway.app
- **Celery Docs:** https://docs.celeryq.dev
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **MongoDB Atlas:** https://www.mongodb.com/docs/atlas

---

## ✅ Quick Start

```bash
# 1. Redis ekle
railway add -d redis

# 2. Variables ayarla
railway variables set MONGODB_URI=mongodb+srv://...
railway variables set OPENROUTER_API_KEY=sk-or-v1-...
railway variables set REDIS_URL=${{Redis.REDIS_URL}}

# 3. Deploy
railway up

# 4. Test
curl https://your-app.up.railway.app/health
```

**Railway production'da çalışıyor!** 🚀
