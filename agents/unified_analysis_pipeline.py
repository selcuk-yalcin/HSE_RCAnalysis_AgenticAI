"""
UNIFIED ANALYSIS PIPELINE with CACHING
========================================
Tek dosyada:
  1. Cache yönetimi (incident analiz sonuçları)
  2. Kök neden analizi (5-WHY)
  3. Rapor üretimi (DOCX)
  4. İstatistikler ve özet
  
Kullanım:
  from agents.unified_analysis_pipeline import UnifiedAnalysisPipeline
  
  pipeline = UnifiedAnalysisPipeline(use_rag=False, use_cache=True)
  result = pipeline.analyze_incident(incident_data)
"""

import json
import hashlib
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .overview_agent import OverviewAgent
from .assessment_agent import AssessmentAgent
from .rootcause_agent_v2 import RootCauseAgentV2
from .skillbased_docx_agent import SkillBasedDocxAgent

# MongoDB for cache storage
try:
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False


# ============================================================================
# CACHE MANAGER
# ============================================================================

class AnalysisCache:
    """
    Incident analiz sonuçlarını cache'e kaydet.
    Aynı incident tekrar gelirse, cache'den hızlı getir.
    """
    
    def __init__(self, cache_dir: str = "cache/analyses", ttl_days: int = 30):
        """
        cache_dir: Cache dosyaları nereye kaydedilsin?
        ttl_days: Time To Live - Kaç gün sonra cache silinsin?
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_days = ttl_days
        
        self.stats = {
            "hits": 0,      # Cache'den getirilen
            "misses": 0,    # API'ye gidenleri
            "saved_cost": 0.0,  # Tasarruf edilen para
            "total_cost": 0.0   # Toplam harcama
        }
    
    def get_cache_key(self, incident_data: dict) -> str:
        """
        Incident'ın unique hash'ini oluştur.
        Aynı description = Aynı hash = Aynı sonuç
        """
        # Description'ı al
        description = incident_data.get("description", "")
        ref_no = incident_data.get("ref_no", "")
        
        # Boşlukları temizle (normalizasyon)
        normalized = f"{ref_no}:{description}".strip().lower()
        normalized = " ".join(normalized.split())
        
        # MD5 hash oluştur (kısa ve hızlı)
        hash_obj = hashlib.md5(normalized.encode())
        return hash_obj.hexdigest()
    
    def get(self, incident_data: dict) -> Optional[dict]:
        """
        Cache'den sonuç getir.
        Varsa → Döndür
        Yoksa → None döndür
        """
        key = self.get_cache_key(incident_data)
        cache_file = self.cache_dir / f"{key}.json"
        
        # Dosya var mı?
        if not cache_file.exists():
            self.stats["misses"] += 1
            return None
        
        # TTL kontrol et (expiration)
        file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
        if file_age > timedelta(days=self.ttl_days):
            cache_file.unlink()  # Eski dosyayı sil
            self.stats["misses"] += 1
            return None
        
        # Dosyayı oku
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                result = json.load(f)
            
            self.stats["hits"] += 1
            self.stats["saved_cost"] += 0.3144  # Yaklaşık olarak bir analiz maliyeti
            
            print(f"   ✅ CACHE HIT! Cache'den alındı")
            print(f"      💰 Tasarruf: $0.31")
            return result
        
        except Exception as e:
            print(f"   ⚠️ Cache okuma hatası: {e}")
            self.stats["misses"] += 1
            return None
    
    def set(self, incident_data: dict, result: dict) -> bool:
        """
        Analiz sonucunu cache'e kaydet.
        """
        key = self.get_cache_key(incident_data)
        cache_file = self.cache_dir / f"{key}.json"
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "incident_ref": incident_data.get("ref_no", "UNKNOWN"),
                    "analysis_result": result
                }, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"   ⚠️ Cache yazma hatası: {e}")
            return False
    
    def get_stats(self) -> dict:
        """
        Cache istatistiklerini döndür.
        """
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0
        
        return {
            "total_requests": total,
            "cache_hits": self.stats["hits"],
            "cache_misses": self.stats["misses"],
            "hit_rate": f"{hit_rate:.1f}%",
            "money_saved": f"${self.stats['saved_cost']:.2f}"
        }
    
    def clear(self):
        """
        Tüm cache'i sil.
        """
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            print("🗑️ Cache temizlendi")


# ============================================================================
# MONGODB CACHE MANAGER (Railway Production'a uygun)
# ============================================================================

class MongoDBCache:
    """
    Incident analiz sonuçlarını MongoDB'de cache'le.
    Production'da (Railway) container restart'ta cache kalır.
    """
    
    def __init__(self, db_name: str = "rca_database", collection_name: str = "analysis_cache", ttl_days: int = 30):
        """
        db_name: MongoDB database adı
        collection_name: Cache collection adı
        ttl_days: Kaç gün sonra cache silinsin?
        """
        if not MONGODB_AVAILABLE:
            raise ImportError("pymongo paketi yüklü değil. Kurulum: pip install pymongo")
        
        # MongoDB URI'ı .env'den al
        mongo_uri = os.getenv("MONGODB_URI")
        if not mongo_uri:
            raise ValueError("MONGODB_URI environment variable not set!")
        
        try:
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            # Bağlantı testı
            self.client.admin.command('ping')
            print("✅ MongoDB bağlantısı başarılı (Cache)")
        except Exception as e:
            raise ConnectionError(f"MongoDB bağlantı hatası: {e}")
        
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.ttl_days = ttl_days
        
        # İstatistikler
        self.stats = {
            "hits": 0,
            "misses": 0,
            "saved_cost": 0.0
        }
        
        # TTL index oluştur (otomatik silme)
        try:
            self.collection.create_index(
                "expires_at",
                expireAfterSeconds=0
            )
            print("✅ MongoDB TTL index oluşturuldu")
        except Exception as e:
            print(f"⚠️  TTL index hatası: {e}")
    
    def get_cache_key(self, incident_data: dict) -> str:
        """
        Incident'ın unique hash'ini oluştur.
        Aynı description = Aynı hash = Aynı sonuç
        """
        description = incident_data.get("description", "")
        ref_no = incident_data.get("ref_no", "")
        
        # Normalizasyon
        normalized = f"{ref_no}:{description}".strip().lower()
        normalized = " ".join(normalized.split())
        
        # MD5 hash
        hash_obj = hashlib.md5(normalized.encode())
        return hash_obj.hexdigest()
    
    def get(self, incident_data: dict) -> Optional[dict]:
        """
        MongoDB'den cache getir.
        Varsa → Döndür
        Yoksa → None döndür
        """
        key = self.get_cache_key(incident_data)
        
        try:
            # Cache ara
            cached = self.collection.find_one({
                "cache_key": key,
                "expires_at": {"$gt": datetime.now()}
            })
            
            if cached:
                self.stats["hits"] += 1
                self.stats["saved_cost"] += 0.3144
                
                print(f"   ✅ MONGODB CACHE HIT!")
                print(f"      💰 Tasarruf: $0.31")
                print(f"      ⏰ Cached: {cached.get('created_at', 'N/A')}")
                
                return {
                    "timestamp": cached.get("created_at", "").isoformat() if hasattr(cached.get("created_at"), 'isoformat') else str(cached.get("created_at")),
                    "analysis_result": cached.get("analysis_result")
                }
            else:
                self.stats["misses"] += 1
                return None
        
        except Exception as e:
            print(f"   ⚠️ MongoDB okuma hatası: {e}")
            self.stats["misses"] += 1
            return None
    
    def set(self, incident_data: dict, result: dict) -> bool:
        """
        Analiz sonucunu MongoDB'ye kaydet.
        """
        key = self.get_cache_key(incident_data)
        expires_at = datetime.now() + timedelta(days=self.ttl_days)
        
        try:
            self.collection.update_one(
                {"cache_key": key},
                {
                    "$set": {
                        "cache_key": key,
                        "incident_ref": incident_data.get("ref_no", "UNKNOWN"),
                        "analysis_result": result,
                        "created_at": datetime.now(),
                        "expires_at": expires_at
                    }
                },
                upsert=True  # Varsa güncelle, yoksa ekle
            )
            
            return True
        
        except Exception as e:
            print(f"   ⚠️ MongoDB yazma hatası: {e}")
            return False
    
    def get_stats(self) -> dict:
        """
        Cache istatistiklerini döndür.
        """
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0
        
        return {
            "total_requests": total,
            "cache_hits": self.stats["hits"],
            "cache_misses": self.stats["misses"],
            "hit_rate": f"{hit_rate:.1f}%",
            "money_saved": f"${self.stats['saved_cost']:.2f}"
        }
    
    def clear(self):
        """
        Tüm cache'i sil.
        """
        try:
            self.collection.delete_many({})
            print("🗑️ MongoDB cache temizlendi")
        except Exception as e:
            print(f"❌ Cache temizleme hatası: {e}")


# ============================================================================
# UNIFIED ANALYSIS PIPELINE
# ============================================================================

class UnifiedAnalysisPipeline:
    """
    Tüm analiz adımlarını bir pipeline'da yönet.
    Cache, RCA, Rapor - hepsi burada!
    """
    
    def __init__(self, use_rag: bool = True, use_cache: bool = True, use_mongodb_cache: bool = None):
        """
        use_rag: MongoDB vector search kullan mı?
        use_cache: Cache mekanizması kullan mı?
        use_mongodb_cache: 
            - None/False: Disk cache (local development)
            - True: MongoDB cache (Railway production)
        """
        print("🚀 Pipeline başlatılıyor...")
        
        self.overview_agent = OverviewAgent()
        self.assessment_agent = AssessmentAgent()
        self.rootcause_agent = RootCauseAgentV2(use_rag=use_rag)
        self.docx_agent = SkillBasedDocxAgent()
        
        self.use_cache = use_cache
        
        # Auto-detect: Railway production'da MongoDB cache, local'da disk cache
        if use_mongodb_cache is None:
            use_mongodb_cache = os.getenv("RAILWAY_ENVIRONMENT") == "production"
        
        if use_cache:
            if use_mongodb_cache and MONGODB_AVAILABLE:
                print("📦 Using MongoDB Cache (Railway compatible)")
                try:
                    self.cache = MongoDBCache()
                except Exception as e:
                    print(f"⚠️ MongoDB cache initialization failed: {e}")
                    print("   Falling back to disk cache...")
                    self.cache = AnalysisCache()
            else:
                print("💾 Using Disk Cache (Local development)")
                self.cache = AnalysisCache()
        else:
            self.cache = None
        
        self.output_dir = Path("outputs/unified_pipeline")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        mode = "AKTIF (RAG açık)" if use_rag else "PASIF (RAG kapalı)"
        cache_mode = "AKTIF" if use_cache else "PASIF"
        
        print(f"✅ Pipeline hazır:")
        print(f"   RAG: {mode}")
        print(f"   Cache: {cache_mode}")
        print()
    
    def analyze_incident(self, incident_data: Dict) -> Dict:
        """
        Tam analiz pipeline'ı çalıştır:
        1. Cache kontrolü
        2. Overview
        3. Assessment
        4. Root Cause Analysis
        5. Rapor üretimi
        6. Cache'e kayıt
        """
        
        ref_no = incident_data.get("ref_no", "UNKNOWN")
        
        # ============================================================
        # ADIM 1: CACHE KONTROLÜ
        # ============================================================
        if self.use_cache:
            print(f"🔍 Cache kontrol ediliyor ({ref_no})...")
            cached_analysis = self.cache.get(incident_data)
            
            if cached_analysis:
                print(f"   Cached timestamp: {cached_analysis.get('timestamp')}")
                return {
                    "source": "cache",
                    "cached": True,
                    "analysis": cached_analysis.get("analysis_result", {}),
                    "timestamp": cached_analysis.get("timestamp"),
                    "incident_ref": ref_no
                }
        
        print(f"🆕 Yeni analiz başlıyor ({ref_no})...")
        
        # ============================================================
        # ADIM 2: OVERVIEW
        # ============================================================
        print(f"\n   📋 STEP 1: Overview Analysis...")
        try:
            overview_result = self.overview_agent.process_initial_report(incident_data)
            incident_type = overview_result.get('incident_type', 'Unknown')
            print(f"      ✅ Incident Type: {incident_type}")
        except Exception as e:
            print(f"      ❌ Error: {e}")
            return {"error": str(e), "step": "overview"}
        
        # ============================================================
        # ADIM 3: ASSESSMENT
        # ============================================================
        print(f"\n   📋 STEP 2: Assessment Analysis...")
        try:
            assessment_result = self.assessment_agent.assess_incident(
                overview_result, 
                incident_data
            )
            severity = assessment_result.get('actual_potential_harm', 'Unknown')
            print(f"      ✅ Severity: {severity}")
        except Exception as e:
            print(f"      ❌ Error: {e}")
            return {"error": str(e), "step": "assessment"}
        
        # ============================================================
        # ADIM 4: ROOT CAUSE ANALYSIS
        # ============================================================
        print(f"\n   📋 STEP 3: Root Cause Analysis (5-WHY)...")
        try:
            root_cause_result = self.rootcause_agent.analyze_root_causes(
                overview_result,
                assessment_result,
                incident_data
            )
            
            root_causes = root_cause_result.get('final_root_causes', [])
            print(f"      ✅ Found {len(root_causes)} Root Causes:")
            for i, rc in enumerate(root_causes, 1):
                code = rc.get('code', '?')
                name = rc.get('name', 'Unknown')
                print(f"         {i}. [{code}] {name}")
        
        except Exception as e:
            print(f"      ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e), "step": "root_cause"}
        
        # ============================================================
        # ADIM 5: JSON SONUÇLAR KAYDET
        # ============================================================
        print(f"\n   📁 Saving JSON results...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        analysis_result = {
            "source": "api",
            "cached": False,
            "timestamp": datetime.now().isoformat(),
            "incident_ref": incident_data.get("ref_no"),
            "overview": overview_result,
            "assessment": assessment_result,
            "root_cause_analysis": root_cause_result
        }
        
        json_path = self.output_dir / f"analysis_{ref_no}_{timestamp}.json"
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=2)
            print(f"      ✅ Saved: {json_path.name}")
        except Exception as e:
            print(f"      ⚠️ JSON save error: {e}")
        
        # ============================================================
        # ADIM 6: CACHE'E KAYDET (eğer yeni analiz ise)
        # ============================================================
        if self.use_cache:
            print(f"\n   💾 Saving to cache...")
            self.cache.set(incident_data, analysis_result)
            print(f"      ✅ Cached")
        
        # ============================================================
        # ADIM 7: RAPOR ÜRET
        # ============================================================
        print(f"\n   📄 Generating DOCX Report...")
        try:
            investigation_data = {
                "part1": overview_result,
                "part2": assessment_result,
                "part3_rca": root_cause_result
            }
            
            report_filename = f"report_{ref_no}_{timestamp}.docx"
            report_path = self.output_dir / report_filename
            
            docx_path = self.docx_agent.generate_report(
                investigation_data, 
                str(report_path)
            )
            
            print(f"      ✅ Report: {Path(docx_path).name}")
            analysis_result["report_path"] = str(docx_path)
        
        except Exception as e:
            print(f"      ⚠️ Report generation error: {e}")
            analysis_result["report_error"] = str(e)
        
        # ============================================================
        # ADIM 8: İSTATİSTİKLER
        # ============================================================
        if self.use_cache:
            print(f"\n   📊 Cache Statistics:")
            stats = self.cache.get_stats()
            print(f"      Hit Rate: {stats['hit_rate']}")
            print(f"      Money Saved: {stats['money_saved']}")
        
        return {
            "source": "api",
            "cached": False,
            "analysis": analysis_result,
            "timestamp": datetime.now().isoformat(),
            "incident_ref": ref_no
        }
    
    def batch_analyze(self, incidents: List[Dict]) -> List[Dict]:
        """
        Birden çok olay analiz et (Cache hit/miss test için ideal)
        """
        print(f"\n{'='*100}")
        print(f"🔄 Analyzing {len(incidents)} incidents...")
        print(f"{'='*100}\n")
        
        results = []
        for i, incident in enumerate(incidents, 1):
            ref_no = incident.get("ref_no", f"INCIDENT-{i}")
            
            print(f"\n{'─'*100}")
            print(f"INCIDENT {i}/{len(incidents)}: {ref_no}")
            print(f"{'─'*100}")
            
            result = self.analyze_incident(incident)
            results.append(result)
        
        # ============================================================
        # BATCH ÖZETI
        # ============================================================
        print(f"\n\n{'='*100}")
        print(f"📊 BATCH SUMMARY")
        print(f"{'='*100}")
        
        cache_hits = sum(1 for r in results if r.get('cached', False))
        cache_misses = len(results) - cache_hits
        
        print(f"\n Total Incidents: {len(results)}")
        print(f"   Cache Hits: {cache_hits}")
        print(f"   Cache Misses: {cache_misses}")
        
        if len(results) > 0:
            hit_rate = cache_hits / len(results) * 100
            print(f"   Hit Rate: {hit_rate:.1f}%")
        
        if self.use_cache and self.cache:
            stats = self.cache.get_stats()
            print(f"\n Cache Statistics:")
            for key, value in stats.items():
                print(f"   {key}: {value}")
        
        # Maliyet hesabı
        cost_without_cache = len(results) * 0.3144
        cost_with_cache = cache_misses * 0.3144
        saved = cost_without_cache - cost_with_cache
        
        print(f"\n💰 Cost Analysis:")
        print(f"   Without Cache: ${cost_without_cache:.2f}")
        print(f"   With Cache: ${cost_with_cache:.2f}")
        print(f"   Saved: ${saved:.2f}")
        
        if len(results) > 0:
            savings_pct = saved / cost_without_cache * 100
            print(f"   Savings: {savings_pct:.1f}%")
        
        print(f"\n{'='*100}\n")
        
        return results


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_sample_incident_1() -> Dict:
    """Örnek Olay 1: Yağ tasfiye cihazı yangını"""
    return {
        "ref_no": "OIL-PURIFIER-001",
        "reported_by": "Vardiya Amiri",
        "date_time": "15:20",
        "description": """
KAZA RAPORU - YAĞ TASFİYE CİHAZI YANMASI - YANLIŞ DEVREYE ALMA SIRASI
======================================================================

1. OLAY ÖZETİ
Saat 15:20'de görevli yağcı, yağ tasfiye cihazını "ON" konumuna alarak sistemi devreye
sokmuştur. Ancak normal çalışma sırasına göre cihaz devreye alınmadan önce hat vanasının
açılması gerekmekteyken, ilgili çalışan tarafından vana açılmadan cihaz çalıştırılmıştır.

Bu durum, cihazın yağ akışı olmadan ısıtılmasına ve sonuç olarak cihaz gövdesinin aşırı
ısınarak yangın oluşmasına neden olmuştur.

2. KATEGORİZASYON

2.1 Personel:
✅ Deneyim: 4 yıllık kıdemli personel
✅ Vardiya başında değil
❌ Yazılı çalışma talimatı: VERİLMEMİŞ
❌ Uyarıcı levha: YOK

2.2 Ekipman/Sistem Özellikleri:
❌ Emniyet sensörü (Flow sensor): YOK (bu cihazda)
❌ İnterlock sistemi: YOK (bu cihazda)
✅ Tesisteki diğer iki benzer cihaz: Sensör VAR

2.3 Yönetim Sistemi:
❌ Yazılı iş talimatı: YOK
❌ Uyarıcı levha: YOK
✅ Teknik Risk Analizleri (HAZOP/LOPA): YAPILDI
❌ Ancak bu spesifik cihaz için yağ akışsız çalıştırma senaryosu: KAPSAM DIŞI

3. HASAR/SONUÇ
- Kişisel yaralanma: YOK
- Ekipman hasarı: Cihaz gövdesinde yanma hasarı
- Operasyon durması: 2 gün
""",
        "injury_description": "Kişisel yaralanma yok. Ekipman hasarı.",
        "equipment": "Yağ Tasfiye Cihazı Model XYZ"
    }


def get_sample_incident_2() -> Dict:
    """Örnek Olay 2: Elektrik panosu yangını"""
    return {
        "ref_no": "ELECTRICAL-PANEL-002",
        "reported_by": "Elektrik Müdürü",
        "date_time": "09:45",
        "description": """
KAZA RAPORU - ELEKTRİK PANOSU KISA DEVRESİ
===========================================

1. OLAY ÖZETİ
Sabah 09:45'te elektrik panosu alanından duman ve ışık flaşı görülmüştür. 
Uzmanlar tarafından kontrol edildiğinde, panel içerisinde kısa devre oluştuğu ve 
bazı bileşenlerin yanmaya başladığı tespit edilmiştir.

2. KATEGORİZASYON

2.1 Personel:
✅ Deneyim: 10 yıllık elektrikçi
✅ Rutin bakım yapıyordu

2.2 Ekipman/Sistem Özellikleri:
❌ Termal kameralar: YOK
❌ Otomatik kesici sistem: ESKİ
✅ Manuel kesici: VAR

2.3 Yönetim Sistemi:
❌ Preventif bakım programı: YOK
✅ Arızalı cihaz raporlama: VAR

3. HASAR/SONUÇ
- Kişisel yaralanma: YOK
- Ekipman hasarı: Panel bileşenleri yanmış
""",
        "injury_description": "Kişisel yaralanma yok",
        "equipment": "Elektrik Dağıtım Paneli"
    }
