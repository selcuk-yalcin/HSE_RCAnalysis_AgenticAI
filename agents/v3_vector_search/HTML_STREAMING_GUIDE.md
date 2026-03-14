# HTML Streaming - Kullanıcının Canlı Rapor İzlemesi

## 🎯 Özellik

Kullanıcı, raporun oluşturulmasını **canlı olarak** izleyebilir. HTML içeriği yazıldıkça ekranda belirir.

---

## 📺 Kullanım Akışı

### 1. Analiz Başlat

```bash
# POST isteği gönder
curl -X POST http://localhost:8000/api/v3/analyze \
  -H "Content-Type: application/json" \
  -d @test_incident.json

# Response:
# {
#   "job_id": "abc-123-def",
#   "status": "Job başlatıldı",
#   "estimated_time": "5-10 dakika"
# }
```

### 2. Canlı İzleme Sayfasını Aç

```
http://localhost:8000/streaming_html_viewer.html?job_id=abc-123-def
```

**Ekranda görecekler:**
- ✅ **Sol panel:** Progress bar + Timeline (hangi adımda)
- ✅ **Sağ panel:** HTML raporu canlı olarak yazılıyor
- ✅ **Bağlantı durumu:** Canlı / Kesildi (üst sağ köşe)

---

## 🔍 Nasıl Çalışır?

### Mimari

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser (Frontend)                        │
│  ┌───────────────────────────────────────────────────┐     │
│  │   streaming_html_viewer.html                       │     │
│  │                                                     │     │
│  │   [Progress Panel]    [HTML Preview Panel]        │     │
│  │    - Progress Bar      - Real-time HTML content   │     │
│  │    - Timeline          - Download/Copy buttons    │     │
│  └───────────────────────────────────────────────────┘     │
│             ↕ WebSocket (ws://)                             │
└─────────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────────┐
│                FastAPI Backend (async_orchestrator_v3.py)    │
│  ┌───────────────────────────────────────────────────┐     │
│  │   WebSocket Endpoint: /ws/progress/{job_id}       │     │
│  │                                                     │     │
│  │   Every 1 second:                                  │     │
│  │   1. MongoDB'den job status al                     │     │
│  │   2. Progress + HTML content gönder                │     │
│  └───────────────────────────────────────────────────┘     │
│             ↕                                               │
│  ┌───────────────────────────────────────────────────┐     │
│  │   MongoDB Collection: rca_jobs                     │     │
│  │                                                     │     │
│  │   {                                                │     │
│  │     job_id: "abc-123",                             │     │
│  │     progress: 85,                                  │     │
│  │     current_step: "HTML oluşturuluyor",            │     │
│  │     html_content: "<html>...</html>"  ← 🆕         │     │
│  │   }                                                │     │
│  └───────────────────────────────────────────────────┘     │
│             ↕                                               │
│  ┌───────────────────────────────────────────────────┐     │
│  │   Celery Worker (Background Task)                 │     │
│  │                                                     │     │
│  │   analyze_incident_task():                         │     │
│  │   1. Immediate causes → Progress 40%               │     │
│  │   2. Root causes → Progress 70%                    │     │
│  │   3. HTML header → Progress 82% (+ HTML chunk 1)   │     │
│  │   4. HTML table → Progress 90% (+ HTML chunk 2)    │     │
│  │   5. Final HTML → Progress 100% (+ Full HTML)      │     │
│  └───────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 Kod Akışı

### 1. Backend: HTML İçeriği Streaming

**`async_orchestrator_v3.py` - Celery Task:**

```python
@celery_app.task(bind=True)
def analyze_incident_task(self, job_id, tenant_id, incident_data):
    tracker = JobTracker()
    
    # ... analiz yapılıyor ...
    
    # 🆕 HTML oluşturma (incremental)
    
    # Step 1: HTML header (Progress 82%)
    html_header = """
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <title>RCA Report</title>
        <style>...</style>
    </head>
    <body>
    """
    
    tracker.update_progress(
        job_id=job_id,
        progress=82,
        step="HTML başlığı oluşturuldu",
        html_content=html_header  # 🆕 İlk chunk
    )
    
    # Step 2: Başlık ve olay bilgileri (Progress 85%)
    html_content = html_header
    html_content += "<h1>HSG245 Root Cause Analysis</h1>"
    html_content += f"<p>Job ID: {job_id}</p>"
    
    tracker.update_progress(
        job_id=job_id,
        progress=85,
        step="Olay bilgileri eklendi",
        html_content=html_content  # 🆕 Güncel HTML
    )
    
    # Step 3: Root causes tablosu (Progress 90%)
    html_content += "<h2>Root Causes</h2>"
    html_content += "<table>..."
    
    tracker.update_progress(
        job_id=job_id,
        progress=90,
        step="Root causes tablosu eklendi",
        html_content=html_content  # 🆕 Daha fazla içerik
    )
    
    # Step 4: Final HTML (Progress 100%)
    html_content += "</body></html>"
    
    tracker.update_progress(
        job_id=job_id,
        progress=100,
        step="Tamamlandı",
        html_content=html_content  # 🆕 Tam rapor
    )
```

### 2. MongoDB: HTML Content Storage

**JobTracker.update_progress():**

```python
def update_progress(
    self,
    job_id: str,
    progress: int,
    step: str,
    html_content: str = None  # 🆕 Opsiyonel HTML
):
    update = {
        "progress": progress,
        "current_step": step,
        "updated_at": datetime.utcnow()
    }
    
    # HTML varsa ekle
    if html_content:
        update["html_content"] = html_content
        update["html_updated_at"] = datetime.utcnow()
    
    self.collection.update_one(
        {"job_id": job_id},
        {"$set": update}
    )
```

### 3. WebSocket: Frontend'e Gönderme

**`/ws/progress/{job_id}` endpoint:**

```python
@app.websocket("/ws/progress/{job_id}")
async def websocket_progress(websocket: WebSocket, job_id: str):
    await websocket.accept()
    
    while True:
        # MongoDB'den job al
        job = tracker.get_job_status(job_id)
        
        # Progress mesajı
        message = {
            "progress": job["progress"],
            "step": job["current_step"],
            "status": job["status"]
        }
        
        # 🆕 HTML content varsa ekle
        if job.get("html_content"):
            message["html_content"] = job["html_content"]
        
        await websocket.send_json(message)
        
        # Tamamlandıysa dur
        if job["status"] == "completed":
            break
        
        await asyncio.sleep(1)  # Her saniye güncelle
```

### 4. Frontend: HTML Rendering

**`streaming_html_viewer.html` - JavaScript:**

```javascript
// WebSocket connection
const ws = new WebSocket(`ws://localhost:8000/ws/progress/${jobId}`);

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    // Progress bar güncelle
    document.getElementById('progressBar').style.width = data.progress + '%';
    
    // 🆕 HTML content varsa render et
    if (data.html_content) {
        updateHTMLPreview(data.html_content);
    }
};

function updateHTMLPreview(htmlContent) {
    const previewEl = document.getElementById('previewContent');
    
    // HTML wrapper
    const wrapper = document.createElement('div');
    wrapper.className = 'html-content typing';  // Fade-in animasyon
    wrapper.innerHTML = htmlContent;  // 🆕 Canlı HTML
    
    // Replace content
    previewEl.innerHTML = '';
    previewEl.appendChild(wrapper);
}
```

---

## 🎬 Demo Akışı (Kullanıcı Perspektifi)

### T=0s: Analiz Başlat
```bash
POST /api/v3/analyze
```

**Ekran:**
```
📊 HSG245 Root Cause Analysis - Live Report

[Left Panel]
Progress: 0%
Status: PENDING
Timeline: All steps gray

[Right Panel]
🔄 Rapor Oluşturuluyor...
(Loading spinner)
```

---

### T=5s: Immediate Causes (Progress 40%)

**Backend:**
```python
tracker.update_progress(job_id, 40, "Immediate causes belirlendi")
```

**Ekran:**
```
Progress: 40%
Status: RUNNING
Timeline: Step 1 ✓ (green), Step 2 active (animated)

[Right Panel]
(Still loading - no HTML yet)
```

---

### T=15s: HTML Header (Progress 82%)

**Backend:**
```python
html_header = "<!DOCTYPE html><html>..."
tracker.update_progress(job_id, 82, "HTML başlığı", html_content=html_header)
```

**Ekran:**
```
Progress: 82%

[Right Panel] 🆕
┌────────────────────────────────────┐
│ (Blank white page - HTML skeleton)│
│                                    │
│                                    │
└────────────────────────────────────┘
```

---

### T=18s: Title Added (Progress 85%)

**Backend:**
```python
html_content = html_header + "<h1>HSG245 RCA Report</h1>"
tracker.update_progress(job_id, 85, "Başlık eklendi", html_content=html_content)
```

**Ekran:**
```
[Right Panel] 🆕
┌────────────────────────────────────┐
│ HSG245 Root Cause Analysis Report │ ← Fade-in animasyon
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                    │
│ Job ID: abc-123-def                │
│                                    │
└────────────────────────────────────┘
```

---

### T=20s: Root Causes Table (Progress 90%)

**Backend:**
```python
html_content += """
<h2>Root Causes</h2>
<table>
  <tr><th>Code</th><th>Description</th></tr>
  <tr><td>D4.5</td><td>LOTO Ineffective</td></tr>
</table>
"""
tracker.update_progress(job_id, 90, "Tablo eklendi", html_content=html_content)
```

**Ekran:**
```
[Right Panel] 🆕
┌────────────────────────────────────┐
│ HSG245 Root Cause Analysis Report │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                    │
│ Job ID: abc-123-def                │
│                                    │
│ ## Root Causes                     │ ← Yeni eklendi
│                                    │
│ ┌─────┬───────────────────────┐   │
│ │Code │Description            │   │
│ ├─────┼───────────────────────┤   │
│ │D4.5 │LOTO Ineffective       │   │
│ └─────┴───────────────────────┘   │
└────────────────────────────────────┘
```

---

### T=22s: Complete (Progress 100%)

**Backend:**
```python
html_content += "</body></html>"
tracker.complete_job(job_id, final_result)
```

**Ekran:**
```
Progress: 100%
Status: COMPLETED ✅

[Right Panel]
(Full HTML report with all sections)

[Buttons Active]
⬇️ İndir    📋 Kopyala    ⛶ Tam Ekran
```

---

## 🛠️ Kurulum ve Test

### 1. Backend Başlat

```bash
cd agents/v3_vector_search

# Redis
redis-server

# Celery Worker
celery -A async_orchestrator_v3.celery_app worker --loglevel=info &

# FastAPI
uvicorn async_orchestrator_v3:app --reload
```

### 2. Test İsteği Gönder

```bash
# Test incident analizi başlat
curl -X POST http://localhost:8000/api/v3/analyze \
  -H "Content-Type: application/json" \
  -d @test_incident.json

# Response:
# {
#   "job_id": "e4c2a1b3-...",
#   "status": "Job başlatıldı"
# }
```

### 3. Canlı İzleme Sayfasını Aç

```
http://localhost:8000/streaming_html_viewer.html?job_id=e4c2a1b3-...
```

**Beklenen Görüntü:**
- Sol panel: Progress bar artıyor
- Sağ panel: HTML içeriği canlı olarak yazılıyor
- Bağlantı durumu: "Canlı Bağlantı" (yeşil)

---

## 🎨 Frontend Özellikleri

### Split View Layout

```
┌──────────────────┬──────────────────────────────────┐
│  Progress Panel  │    HTML Preview Panel            │
│                  │                                  │
│  📊 85%          │  ┌─────────────────────────┐    │
│  ████████░░      │  │ HSG245 RCA Report       │    │
│                  │  │ ─────────────────────   │    │
│  Status: RUNNING │  │ Job ID: abc-123        │    │
│                  │  │                         │    │
│  Timeline:       │  │ ## Root Causes          │    │
│  ✓ Step 1        │  │ ...                     │    │
│  ⚡ Step 2       │  │                         │    │
│  ○ Step 3        │  └─────────────────────────┘    │
│                  │                                  │
│                  │  [Download] [Copy] [Fullscreen] │
└──────────────────┴──────────────────────────────────┘
```

### Real-time Features

1. **Progress Bar**
   - Animasyonlu shimmer efekti (processing göstergesi)
   - Smooth transition (0.5s ease)
   - Percentage gösterimi

2. **Timeline**
   - 5 adım (Immediate → 5-Why → Merge → HTML → Done)
   - Icon durumları: Pending (○), Active (⚡), Completed (✓)
   - Her adımın timestamp'i

3. **HTML Preview**
   - Fade-in animasyon (her güncelleme)
   - Scrollable content
   - Professional styling (Georgia font, table borders)

4. **Connection Status**
   - Üst sağ köşe badge
   - Bağlı: Yeşil (blinking dot)
   - Kesildi: Kırmızı + Otomatik reconnect

5. **Action Buttons**
   - **İndir:** HTML dosyası olarak kaydet
   - **Kopyala:** Clipboard'a kopyala
   - **Tam Ekran:** Raporu fullscreen göster

---

## 📊 Performance

### WebSocket vs Polling

| Yöntem | Latency | Server Load | Kullanım |
|--------|---------|-------------|----------|
| **WebSocket** | **~100ms** | Düşük (persistent connection) | Primary ✅ |
| **Polling** | ~2000ms | Yüksek (her 2s HTTP request) | Fallback ⚠️ |

**Hibrit Yaklaşım:**
- WebSocket çalışıyorsa → real-time (100ms)
- WebSocket başarısızsa → otomatik polling'e geç (2s)

### HTML Content Size

```python
# Typical report size:
# ─────────────────────────────────────
HTML header: ~500 bytes
Olay bilgileri: ~1 KB
Root causes table: ~2 KB (10 kod)
Detaylı analiz: ~5 KB
Total: ~8-10 KB

# MongoDB document limit: 16 MB
# 10 KB << 16 MB ✅ Rahatça sığar
```

---

## 🚀 Production Deployment

### Railway Configuration

**Environment Variables:**
```bash
# Backend URL (production)
WS_URL=wss://your-app.railway.app/ws/progress/${jobId}
API_URL=https://your-app.railway.app/api/v3/status/${jobId}
```

**Frontend Update:**
```javascript
// streaming_html_viewer.html
const WS_URL = window.location.protocol === 'https:' 
    ? `wss://${window.location.host}/ws/progress/${jobId}`
    : `ws://${window.location.host}/ws/progress/${jobId}`;
```

---

## ✅ Checklist

- [ ] `streaming_html_viewer.html` oluşturuldu
- [ ] `async_orchestrator_v3.py` HTML streaming ekle geldi
- [ ] `JobTracker.update_progress()` html_content parametresi eklendi
- [ ] WebSocket endpoint HTML content gönderiyor
- [ ] Celery task incremental HTML oluşturuyor
- [ ] Local test edildi
- [ ] Railway'e deploy edildi
- [ ] Production URL'leri güncellendi

---

## 🎯 Sonuç

**Kullanıcı deneyimi:**
- ✅ Rapor oluşurken **canlı izleme**
- ✅ **Adım adım progress** (timeline)
- ✅ **HTML içeriği anında görüntülenme**
- ✅ İndirme/kopyalama butonları
- ✅ Mobil uyumlu (responsive)

**Teknik avantajlar:**
- ✅ WebSocket (real-time) + Polling (fallback)
- ✅ Incremental HTML streaming (memory efficient)
- ✅ MongoDB'de HTML cache (re-view için)
- ✅ Clean UI/UX

**Kullanıcı artık 800 saniye beklerken ne olduğunu görür!** 🎉
