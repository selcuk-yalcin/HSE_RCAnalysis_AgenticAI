"""
Asenkron RCA Orchestrator V3
=============================
Railway timeout problemini çözmek için background job sistemi

ÖZELLIKLER:
- Celery + Redis (background jobs)
- WebSocket (real-time progress)
- MongoDB (job status tracking)
- 200 eşzamanlı kullanıcı desteği
- 10 paralel rapor işleme

KULLANIM:
1. Redis başlat: redis-server
2. Worker başlat: celery -A async_orchestrator_v3.celery_app worker --loglevel=info --concurrency=10
3. API başlat: uvicorn async_orchestrator_v3:app --host 0.0.0.0 --port 8000
"""

import os
import uuid
from datetime import datetime
from typing import Dict, Optional, List
from celery import Celery
from celery.result import AsyncResult
from pymongo import MongoClient
import json

# ─────────────────────────────────────────────────────────────
# CELERY YAPISI (Railway + Redis)
# ─────────────────────────────────────────────────────────────

# Redis connection (Railway'de provision edilmeli)
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "rca_tasks",
    broker=redis_url,
    backend=redis_url
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 dakika max
    task_soft_time_limit=1500,  # 25 dakika uyarı
    
    # Worker ayarları
    worker_concurrency=10,  # 10 paralel task
    worker_prefetch_multiplier=1,  # Her worker 1 task alır (adil dağılım)
    worker_max_tasks_per_child=50,  # 50 task sonrası worker restart
    
    # Retry politikası
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Result backend
    result_expires=3600,  # Sonuçları 1 saat sakla
)


# ─────────────────────────────────────────────────────────────
# MONGODB JOB TRACKER
# ─────────────────────────────────────────────────────────────

class JobTracker:
    """Job durumunu MongoDB'de takip et"""
    
    def __init__(self):
        mongo_uri = os.getenv("MONGODB_URI")
        if not mongo_uri:
            raise ValueError("MONGODB_URI environment variable gerekli")
        
        self.client = MongoClient(mongo_uri)
        self.db = self.client["hsg245_jobs"]
        self.collection = self.db["rca_jobs"]
    
    def create_job(self, tenant_id: str, incident_id: str) -> str:
        """Yeni job oluştur"""
        job_id = str(uuid.uuid4())
        
        self.collection.insert_one({
            "job_id": job_id,
            "tenant_id": tenant_id,
            "incident_id": incident_id,
            "status": "pending",
            "progress": 0,
            "current_step": "Başlatılıyor...",
            "created_at": datetime.utcnow(),
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None
        })
        
        return job_id
    
    def update_progress(
        self,
        job_id: str,
        progress: int,
        step: str,
        status: str = "running",
        html_content: str = None  # 🆕 HTML streaming için
    ):
        """İlerleme güncelle (HTML content streaming ile)"""
        update = {
            "status": status,
            "progress": progress,
            "current_step": step,
            "updated_at": datetime.utcnow()
        }
        
        # HTML content varsa ekle
        if html_content:
            update["html_content"] = html_content
            update["html_updated_at"] = datetime.utcnow()
        
        job = self.collection.find_one({"job_id": job_id})
        if job and status == "running" and not job.get("started_at"):
            update["started_at"] = datetime.utcnow()
        
        self.collection.update_one(
            {"job_id": job_id},
            {"$set": update}
        )
    
    def complete_job(self, job_id: str, result: Dict):
        """Job'ı tamamla"""
        self.collection.update_one(
            {"job_id": job_id},
            {"$set": {
                "status": "completed",
                "progress": 100,
                "current_step": "Tamamlandı",
                "completed_at": datetime.utcnow(),
                "result": result
            }}
        )
    
    def fail_job(self, job_id: str, error: str):
        """Job'ı başarısız işaretle"""
        self.collection.update_one(
            {"job_id": job_id},
            {"$set": {
                "status": "failed",
                "current_step": "Hata",
                "completed_at": datetime.utcnow(),
                "error": error
            }}
        )
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Job durumunu getir"""
        job = self.collection.find_one({"job_id": job_id}, {"_id": 0})
        
        if job:
            # Datetime'ları ISO format'a çevir
            for field in ["created_at", "started_at", "completed_at", "updated_at"]:
                if field in job and job[field]:
                    job[field] = job[field].isoformat()
        
        return job


# ─────────────────────────────────────────────────────────────
# CELERY TASK (Background Worker)
# ─────────────────────────────────────────────────────────────

@celery_app.task(bind=True, name="rca_tasks.analyze_incident")
def analyze_incident_task(
    self,
    job_id: str,
    tenant_id: str,
    incident_data: Dict
) -> Dict:
    """
    Background'da RCA analizi yap
    
    Args:
        job_id: Unique job ID
        tenant_id: Müşteri ID
        incident_data: {
            "part1_data": {...},
            "part2_data": {...},
            "investigation_data": {...}
        }
    
    Returns:
        {
            "job_id": "...",
            "final_root_causes": [...],
            "final_report_tr": "..."
        }
    """
    
    tracker = JobTracker()
    
    try:
        # İlk durum güncelle
        tracker.update_progress(job_id, 5, "RootCauseAgentV3 başlatılıyor...")
        
        # Agent'ı import et
        import sys
        import os
        v3_dir = os.path.dirname(os.path.abspath(__file__))
        if v3_dir not in sys.path:
            sys.path.insert(0, v3_dir)
        
        from rootcause_agent_v3 import RootCauseAgentV3
        agent = RootCauseAgentV3()
        
        # Celery progress callback
        def progress_callback(progress: int, step: str):
            """Her adımda MongoDB'yi güncelle"""
            tracker.update_progress(job_id, progress, step)
            self.update_state(
                state="PROGRESS",
                meta={"progress": progress, "step": step}
            )
        
        # Tam analiz
        tracker.update_progress(job_id, 10, "Analiz başlıyor...")
        
        result = agent.analyze_root_causes(
            part1_data=incident_data.get("part1_data", {}),
            part2_data=incident_data.get("part2_data", {}),
            investigation_data=incident_data.get("investigation_data", {})
        )
        
        # İlerleme simülasyonu (RootCauseAgentV3 içinde callback yoksa)
        tracker.update_progress(job_id, 40, "Immediate causes belirlendi")
        tracker.update_progress(job_id, 70, "Root causes analizi tamamlandı")
        
        # 🆕 HTML raporu oluşturma (incremental streaming)
        tracker.update_progress(job_id, 80, "HTML raporu oluşturuluyor...")
        
        # HTML header oluştur
        html_header = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>HSG245 Root Cause Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 40px auto; padding: 20px; }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th { background: #3498db; color: white; padding: 12px; text-align: left; }
        td { padding: 10px; border-bottom: 1px solid #ddd; }
        .root-cause { background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 10px 0; }
    </style>
</head>
<body>
"""
        
        # İlk HTML içeriği gönder
        tracker.update_progress(job_id, 82, "HTML başlığı oluşturuldu", html_content=html_header)
        
        # Ana içerik oluştur
        html_content = html_header
        html_content += f"<h1>HSG245 Root Cause Analysis Report</h1>\n"
        html_content += f"<p><strong>Job ID:</strong> {job_id}</p>\n"
        html_content += f"<p><strong>Tarih:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>\n"
        
        tracker.update_progress(job_id, 85, "Olay bilgileri ekleniyor", html_content=html_content)
        
        # Root causes tablosu
        html_content += "<h2>🎯 Identified Root Causes</h2>\n"
        html_content += "<table>\n<thead><tr><th>Category</th><th>Code</th><th>Description</th></tr></thead>\n<tbody>\n"
        
        for rc in result.get("final_root_causes", []):
            html_content += f"<tr><td>{rc.get('category', 'N/A')}</td><td>{rc.get('code', 'N/A')}</td><td>{rc.get('title', 'N/A')}</td></tr>\n"
        
        html_content += "</tbody>\n</table>\n"
        
        tracker.update_progress(job_id, 90, "Root causes tablosu eklendi", html_content=html_content)
        
        # Final report text
        if result.get("final_report_tr"):
            html_content += "<h2>📋 Detaylı Analiz</h2>\n"
            html_content += f"<div style='white-space: pre-wrap;'>{result['final_report_tr']}</div>\n"
        
        # Close HTML
        html_content += "</body>\n</html>"
        
        tracker.update_progress(job_id, 95, "HTML raporu tamamlandı", html_content=html_content)
        
        # Sonuç
        final_result = {
            "job_id": job_id,
            "tenant_id": tenant_id,
            "analysis_branches": result.get("analysis_branches", []),
            "final_root_causes": result.get("final_root_causes", []),
            "final_report_tr": result.get("final_report_tr", ""),
            "analysis_method": result.get("analysis_method", "HSG245 V3")
        }
        
        # MongoDB'ye kaydet
        tracker.complete_job(job_id, final_result)
        
        tracker.update_progress(job_id, 100, "✅ Analiz tamamlandı")
        
        return final_result
    
    except Exception as e:
        # Hata durumu
        import traceback
        error_msg = f"Analiz hatası: {str(e)}\n{traceback.format_exc()}"
        tracker.fail_job(job_id, error_msg)
        
        raise


# ─────────────────────────────────────────────────────────────
# FASTAPI ENDPOINT (Railway'de çalışacak)
# ─────────────────────────────────────────────────────────────

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio

app = FastAPI(
    title="HSG245 RCA Async API",
    description="Asenkron Root Cause Analysis API - Railway Optimized",
    version="3.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da kısıtla
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tracker = JobTracker()


class AnalysisRequest(BaseModel):
    """Analiz request modeli"""
    tenant_id: str
    incident_id: str
    part1_data: Dict
    part2_data: Dict
    investigation_data: Dict


@app.get("/")
async def root():
    """Ana sayfa"""
    return {
        "service": "HSG245 RCA Async API V3",
        "status": "running",
        "endpoints": {
            "analyze": "POST /api/v3/analyze",
            "status": "GET /api/v3/status/{job_id}",
            "websocket": "WS /ws/progress/{job_id}",
            "streaming_ui": "GET /streaming",
            "health": "GET /health"
        }
    }


@app.post("/api/v3/analyze")
async def start_analysis(request: AnalysisRequest):
    """
    Asenkron analiz başlat (5s içinde döner)
    
    Response:
        {
            "job_id": "uuid",
            "status": "pending",
            "message": "Analiz başlatıldı",
            "websocket_url": "ws://.../ws/progress/uuid"
        }
    """
    
    # Job oluştur
    job_id = tracker.create_job(
        tenant_id=request.tenant_id,
        incident_id=request.incident_id
    )
    
    # Background task başlat
    incident_data = {
        "part1_data": request.part1_data,
        "part2_data": request.part2_data,
        "investigation_data": request.investigation_data
    }
    
    analyze_incident_task.delay(
        job_id=job_id,
        tenant_id=request.tenant_id,
        incident_data=incident_data
    )
    
    return JSONResponse({
        "job_id": job_id,
        "status": "pending",
        "message": "Analiz başlatıldı. /api/v3/status/{job_id} ile durumu kontrol edin.",
        "websocket_url": f"ws://localhost:8000/ws/progress/{job_id}",
        "streaming_ui_url": f"/streaming?job_id={job_id}"
    })


@app.get("/api/v3/status/{job_id}")
async def get_job_status(job_id: str):
    """
    Job durumunu sorgula
    
    Response:
        {
            "job_id": "...",
            "status": "running" | "completed" | "failed",
            "progress": 45,
            "current_step": "5-Why Chain 2/3",
            "result": {...} (sadece completed ise)
        }
    """
    
    job = tracker.get_job_status(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job bulunamadı")
    
    return job


@app.websocket("/ws/progress/{job_id}")
async def websocket_progress(websocket: WebSocket, job_id: str):
    """
    Real-time progress updates (WebSocket)
    
    Client'a her saniye güncel durum gönderilir
    """
    
    await websocket.accept()
    
    try:
        while True:
            job = tracker.get_job_status(job_id)
            
            if not job:
                await websocket.send_json({"error": "Job not found"})
                break
            
            # 🆕 HTML content ekle
            message = {
                "progress": job["progress"],
                "step": job["current_step"],
                "status": job["status"]
            }
            
            # HTML content varsa ekle
            if job.get("html_content"):
                message["html_content"] = job["html_content"]
            
            await websocket.send_json(message)
            
            # Tamamlandı veya hata
            if job["status"] in ["completed", "failed"]:
                if job["status"] == "completed":
                    await websocket.send_json({
                        "progress": 100,
                        "step": "Tamamlandı",
                        "status": "completed",
                        "result": job.get("result"),
                        "html_content": job.get("html_content")  # 🆕 Final HTML
                    })
                break
            
            await asyncio.sleep(1)  # Her saniye güncelle
    
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for job {job_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()


@app.get("/streaming", response_class=HTMLResponse)
async def streaming_ui(job_id: str = None):
    """Streaming HTML UI"""
    
    # HTML içeriğini oku
    import os
    html_path = os.path.join(os.path.dirname(__file__), "streaming_client.html")
    
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Job ID'yi inject et
        if job_id:
            html_content = html_content.replace(
                "const JOB_ID = new URLSearchParams(window.location.search).get('job_id');",
                f"const JOB_ID = '{job_id}';"
            )
        
        return HTMLResponse(content=html_content)
    else:
        return HTMLResponse(
            content="<h1>Streaming UI bulunamadı</h1><p>streaming_client.html dosyası yok</p>",
            status_code=404
        )


@app.get("/health")
async def health_check():
    """Railway health check"""
    return {
        "status": "healthy",
        "service": "rca-async-v3",
        "timestamp": datetime.utcnow().isoformat()
    }


# ─────────────────────────────────────────────────────────────
# BATCH PROCESSING
# ─────────────────────────────────────────────────────────────

from celery import group

class BatchAnalysisRequest(BaseModel):
    """Batch analiz request"""
    tenant_id: str
    incidents: List[Dict]
    priority: int = 5  # 1-10


@app.post("/api/v3/batch-analyze")
async def start_batch_analysis(request: BatchAnalysisRequest):
    """
    Toplu analiz başlat (10 rapor paralel)
    
    Response:
        {
            "batch_id": "batch-abc",
            "job_ids": ["job1", "job2", ...],
            "total": 10
        }
    """
    
    job_ids = []
    tasks = []
    
    for incident in request.incidents:
        # Her incident için job oluştur
        job_id = tracker.create_job(
            tenant_id=request.tenant_id,
            incident_id=incident.get("incident_id", "unknown")
        )
        
        job_ids.append(job_id)
        
        # Celery task
        task = analyze_incident_task.s(
            job_id=job_id,
            tenant_id=request.tenant_id,
            incident_data={
                "part1_data": incident.get("part1_data", {}),
                "part2_data": incident.get("part2_data", {}),
                "investigation_data": incident.get("investigation_data", {})
            }
        ).set(priority=request.priority)
        
        tasks.append(task)
    
    # Paralel çalıştır
    job_group = group(tasks)
    result = job_group.apply_async()
    
    batch_id = f"batch-{request.tenant_id}-{len(job_ids)}"
    
    return {
        "batch_id": batch_id,
        "job_ids": job_ids,
        "total": len(job_ids),
        "message": f"{len(job_ids)} analiz batch olarak başlatıldı"
    }


@app.get("/api/v3/batch-status")
async def get_batch_status(job_ids: str):
    """
    Batch durumu
    
    Query params:
        job_ids: comma-separated (job1,job2,job3)
    """
    
    job_ids_list = job_ids.split(',')
    
    statuses = {
        "total": len(job_ids_list),
        "completed": 0,
        "running": 0,
        "failed": 0,
        "pending": 0
    }
    
    for job_id in job_ids_list:
        job = tracker.get_job_status(job_id)
        if job:
            status = job["status"]
            statuses[status] = statuses.get(status, 0) + 1
    
    return statuses


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    
    print("""
╔═══════════════════════════════════════════════════════════════╗
║         HSG245 RCA Async Orchestrator V3                      ║
╚═══════════════════════════════════════════════════════════════╝

BAŞLATMA TALİMATLARI:

1. Redis başlat:
   redis-server

2. Celery worker başlat (başka terminal):
   celery -A async_orchestrator_v3.celery_app worker \\
     --loglevel=info \\
     --concurrency=10

3. Bu API çalışıyor...

ENDPOINTS:
- POST /api/v3/analyze           → Analiz başlat
- GET  /api/v3/status/{job_id}   → Durum sorgula
- WS   /ws/progress/{job_id}     → Real-time progress
- GET  /streaming?job_id=xxx     → Streaming UI
- POST /api/v3/batch-analyze     → Batch analiz

════════════════════════════════════════════════════════════════
    """)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )
