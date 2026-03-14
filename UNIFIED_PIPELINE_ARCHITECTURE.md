# 🏗️ Unified Pipeline Architecture

## **Sistem Mimarisi**

```
┌─────────────────────────────────────────────────────────────────────┐
│                     UNIFIED ANALYSIS PIPELINE                       │
│                   (agents/unified_analysis_pipeline.py)             │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
        ┌──────────────────┐  ┌──────────────┐  ┌─────────────────┐
        │ AnalysisCache    │  │  Overview    │  │  Assessment     │
        │  (Hash-based)    │  │   Agent      │  │    Agent        │
        │                  │  │              │  │                 │
        │ • get()          │  │ • Title      │  │ • Severity      │
        │ • set()          │  │ • Category   │  │ • Contributing  │
        │ • get_stats()    │  │ • Summary    │  │ • Risk          │
        │ • clear()        │  │              │  │                 │
        └──────────────────┘  └──────────────┘  └─────────────────┘
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      │
                                      ▼
                    ┌──────────────────────────────┐
                    │ Root Cause Analysis Agent    │
                    │  (RootCauseAgentV2)          │
                    │                              │
                    │ • 5-Why Chain                │
                    │ • RAG (optional)             │
                    │ • Root Causes                │
                    └──────────────────────────────┘
                                      │
                                      ▼
                    ┌──────────────────────────────┐
                    │   Report Generation          │
                    │ (SkillBasedDocxAgent)        │
                    │                              │
                    │ • DOCX Format                │
                    │ • Investigation Details      │
                    │ • Root Cause Summary         │
                    └──────────────────────────────┘
                                      │
                ┌─────────────────────┼──────────────────────┐
                │                     │                      │
                ▼                     ▼                      ▼
        ┌──────────────┐      ┌──────────────┐     ┌──────────────┐
        │   JSON File  │      │  DOCX Report │     │ Statistics   │
        │              │      │              │     │              │
        │ Analysis     │      │ • Title      │     │ • Hit Rate   │
        │ Details      │      │ • Overview   │     │ • Cost Saved │
        │ Cache Info   │      │ • Assessment │     │ • Hit/Miss   │
        └──────────────┘      │ • Root Causes│     │ • Hit Rate   │
                              └──────────────┘     └──────────────┘
```

---

## **Cache Flow Diyagramı**

```
INCIDENT GİRİŞİ
    │
    ▼
┌────────────────────────────────────────┐
│ Create Hash from:                      │
│ - ref_no                               │
│ - description                          │
└────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────┐
│ Check Cache Directory:                 │
│ cache/analyses/{hash}.json             │
└────────────────────────────────────────┘
    │
    ├─────────────────────┬──────────────────────┐
    │                     │                      │
    ▼                     ▼                      ▼
  EXISTS?          CHECK TTL?             FILE READ?
    │               (30 days?)                  │
    │                 │                        ▼
  NO/EXPIRED        EXPIRED              ✅ SUCCESS
    │                 │                      │
    │             DELETE                     │
    │                 │                      ▼
    │             CONTINUE              RETURN CACHED
    │                 │                 (0.01 sec, $0)
    │                 │                      │
    └─────────────────┴──────────────────────┘
              │
              ▼
    ┌──────────────────────────┐
    │ PERFORM NEW ANALYSIS     │
    │ (API Call to Claude)     │
    │ (30 sec, $0.31)          │
    └──────────────────────────┘
              │
              ▼
    ┌──────────────────────────┐
    │ SAVE TO CACHE            │
    │ cache/analyses/{hash}.json│
    └──────────────────────────┘
              │
              ▼
    ┌──────────────────────────┐
    │ GENERATE REPORT          │
    │ outputs/report_*.docx    │
    └──────────────────────────┘
              │
              ▼
        RETURN RESULT
```

---

## **Data Flow: Tek Incident**

```
incident_data = {
  "ref_no": "OIL-001",
  "description": "Yağ yangını...",
  "injury": "Kişisel yaralanma yok"
}
    │
    ▼
UnifiedAnalysisPipeline.analyze_incident()
    │
    ├─► AnalysisCache.get()
    │     │
    │     ├─► Cache'de VAR? 
    │     │     └─► return cached_result
    │     │
    │     └─► Cache'de YOK?
    │           └─► continue to analysis
    │
    ├─► OverviewAgent.process_initial_report()
    │     └─► {incident_type, title, category, ...}
    │
    ├─► AssessmentAgent.assess_incident()
    │     └─► {severity, contributing_factors, risk_level, ...}
    │
    ├─► RootCauseAgentV2.analyze_root_causes()
    │     └─► {branches, root_causes, 5_why_chain, ...}
    │
    ├─► Save JSON
    │     └─► outputs/analysis_OIL-001_timestamp.json
    │
    ├─► SkillBasedDocxAgent.generate_report()
    │     └─► outputs/report_OIL-001_timestamp.docx
    │
    ├─► AnalysisCache.set()
    │     └─► cache/analyses/{hash}.json
    │
    └─► Return Result
          {source, cached, timestamp, analysis, ...}
```

---

## **Batch Processing Flow**

```
incidents = [OIL-001, ELEC-002, OIL-001]
    │
    ▼
UnifiedAnalysisPipeline.batch_analyze()
    │
    ├─► For i=1: OIL-001
    │     ├─ Cache miss → API call ($0.31)
    │     └─ Save to cache
    │
    ├─► For i=2: ELEC-002
    │     ├─ Cache miss → API call ($0.31)
    │     └─ Save to cache
    │
    ├─► For i=3: OIL-001 (REPEAT)
    │     ├─ Cache HIT! ($0.00) ✅
    │     └─ Return cached result
    │
    └─► Summary
          {
            total: 3,
            hits: 1,
            misses: 2,
            hit_rate: 33.3%,
            cost_saved: $0.31,
            total_cost: $0.63
          }
```

---

## **Cost Analysis: Weekly (Haftada 4 Analiz)**

```
Senaryo 1: Hepsi YENI (Cache İşe yaramıyor)
┌───────┬───────┬───────┬───────┐
│ MON-1 │ MON-2 │ TUE-1 │ THU-1 │
├───────┼───────┼───────┼───────┤
│ API   │ API   │ API   │ API   │
│ $0.31 │ $0.31 │ $0.31 │ $0.31 │
└───────┴───────┴───────┴───────┘
TOTAL: $1.24 (0% tasarruf)

Senaryo 2: 2 TEKRAR (Cache işe yarıyor!)
┌───────┬───────┬───────┬───────┐
│ MON-1 │ MON-2 │ MON-1 │ MON-2 │
├───────┼───────┼───────┼───────┤
│ API   │ API   │ CACHE │ CACHE │
│ $0.31 │ $0.31 │ $0.00 │ $0.00 │
└───────┴───────┴───────┴───────┘
TOTAL: $0.62 (50% tasarruf = $0.62 tasarruf!)

Senaryo 3: 3 TEKRAR (Maksimum tasarruf)
┌───────┬───────┬───────┬───────┐
│ MON-1 │ MON-2 │ MON-1 │ MON-1 │
├───────┼───────┼───────┼───────┤
│ API   │ API   │ CACHE │ CACHE │
│ $0.31 │ $0.31 │ $0.00 │ $0.00 │
└───────┴───────┴───────┴───────┘
TOTAL: $0.62 (50% tasarruf)
```

---

## **Database Schema: Cache Storage**

```
cache/analyses/
│
├─ a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6.json
│  {
│    "timestamp": "2026-03-14T10:30:45.123456",
│    "incident_ref": "OIL-PURIFIER-001",
│    "analysis_result": {
│      "overview": {
│        "incident_type": "Equipment Damage",
│        "title": "Oil Purifier Fire",
│        ...
│      },
│      "assessment": {
│        "severity": "High",
│        "contributing_factors": [...],
│        ...
│      },
│      "root_cause_analysis": {
│        "branches": [
│          {
│            "direct_cause": "...",
│            "five_why_chain": [...],
│            "root_cause": "..."
│          }
│        ]
│      }
│    }
│  }
│
├─ p5o4n3m2l1k0j9i8h7g6f5e4d3c2b1a0.json
│  ...
│
└─ ...
```

---

## **Files Generated: Output Structure**

```
outputs/unified_pipeline/
│
├─ analysis_OIL-PURIFIER-001_20260314_103045.json
│  └─ Contains: Complete analysis results
│
├─ report_OIL-PURIFIER-001_20260314_103045.docx
│  └─ Contains: Formatted investigation report
│
├─ analysis_ELECTRICAL-PANEL-002_20260314_104230.json
│  └─ Contains: Complete analysis results
│
├─ report_ELECTRICAL-PANEL-002_20260314_104230.docx
│  └─ Contains: Formatted investigation report
│
└─ ...
```

---

## **Integration Points**

```
Mevcut Sistem                  Unified Pipeline
─────────────────────────────────────────────────
test_oil_purifier_fire_scenario.py
    │
    └─► OverviewAgent ────┐
    │   AssessmentAgent ──┼──► UnifiedAnalysisPipeline
    │   RootCauseAgentV2 ─┤
    └─► SkillBasedDocxAgent

Kazanç:
  ✅ Cache management (otomatik)
  ✅ Tek entry point (easy to use)
  ✅ Rapor + JSON (aynı anda)
  ✅ Statistics (built-in)
```

---

## **Performance Comparison**

```
WITHOUT CACHE:
Time: 30s × 4 = 120s (2 dakika)
Cost: $0.31 × 4 = $1.24
Memory: Tüm agents load

WITH CACHE (50% hit rate):
Time: 30s × 2 + 0.01s × 2 = 60s (1 dakika)
Cost: $0.31 × 2 + $0 × 2 = $0.62
Memory: Tüm agents load (ilk), sadece cache (sonra)

IMPROVEMENT:
⚡ 50% daha hızlı
💰 50% daha ucuz
📊 Consistent results
```

---

## **Decision Tree: Cache Hit/Miss**

```
Incident Geldi mi?
    │
    ├─ FIRST TIME?
    │  └─ NO CACHE → Go to API
    │
    ├─ SEEN BEFORE?
    │  └─ YES CACHE!
    │     ├─ EXPIRED (30+ days)?
    │     │  └─ DELETE → Go to API
    │     └─ VALID?
    │        └─ RETURN CACHED ✅
    │
    └─ SIMILAR BUT NOT IDENTICAL?
       └─ NEW HASH → Go to API
```

---

**Bu mimaride:**
- ✅ Cache işlemleri otomatik yönetiliyor
- ✅ Rapor ve JSON aynı anda üretiliyor
- ✅ İstatistikler real-time hesaplanıyor
- ✅ Maliyet %50-75 düşüyor
- ✅ Hız 30x artıyor (cache hit durumunda)

Hazır mısınız? 🚀
