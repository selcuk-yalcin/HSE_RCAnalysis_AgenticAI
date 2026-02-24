"""
=============================================================================
TAM SİSTEM TESTİ — test_hierarchical_output.json Tabanlı
=============================================================================
Bu test dosyası aşağıdaki adımları sırayla çalıştırır ve her adımı doğrular:

  TEST 1  — Ortam & API Anahtarları
  TEST 2  — test_hierarchical_output.json okunması & doğrulanması
  TEST 3  — SkillBasedDocxAgent: JSON → DOCX rapor üretimi
  TEST 4  — Orchestrator: tam pipeline (Part1 → Part2 → Part3 → DOCX)
  TEST 5  — Çıktı dosyaları doğrulaması (outputs/ klasörü)
  TEST 6  — JSON yapı bütünlüğü (schema kontrolleri)
  TEST 7  — Performans & zamanlama

Çalıştır:
    python test_full_system.py
=============================================================================
"""

import sys
import os
import json
import time
import traceback
from datetime import datetime
from pathlib import Path

# ── Proje kökünü Python path'ine ekle ─────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# RENK KODLARI (terminal çıktısı için)
# ─────────────────────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

# ─────────────────────────────────────────────────────────────────────────────
# SAYAÇLAR
# ─────────────────────────────────────────────────────────────────────────────
PASS = 0
FAIL = 0
WARN = 0
results = []   # (test_adı, durum, mesaj, süre_ms)


# ─────────────────────────────────────────────────────────────────────────────
# YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────────────────────────────────────────

def header(title: str):
    print(f"\n{BOLD}{BLUE}{'='*78}{RESET}")
    print(f"{BOLD}{BLUE}  {title}{RESET}")
    print(f"{BOLD}{BLUE}{'='*78}{RESET}")


def subheader(title: str):
    print(f"\n{CYAN}{'─'*78}{RESET}")
    print(f"{CYAN}  {title}{RESET}")
    print(f"{CYAN}{'─'*78}{RESET}")


def ok(msg: str, detail: str = ""):
    global PASS
    PASS += 1
    detail_str = f"  {YELLOW}» {detail}{RESET}" if detail else ""
    print(f"  {GREEN}✅ PASS{RESET}  {msg}{detail_str}")


def fail(msg: str, detail: str = ""):
    global FAIL
    FAIL += 1
    detail_str = f"\n         {RED}» {detail}{RESET}" if detail else ""
    print(f"  {RED}❌ FAIL{RESET}  {msg}{detail_str}")


def warn(msg: str, detail: str = ""):
    global WARN
    WARN += 1
    detail_str = f"  {YELLOW}» {detail}{RESET}" if detail else ""
    print(f"  {YELLOW}⚠️  WARN{RESET}  {msg}{detail_str}")


def info(msg: str):
    print(f"  {CYAN}ℹ️  {msg}{RESET}")


def assert_true(condition: bool, pass_msg: str, fail_msg: str, detail: str = ""):
    if condition:
        ok(pass_msg, detail)
        return True
    else:
        fail(fail_msg, detail)
        return False


def assert_key(d: dict, key: str, name: str = "") -> bool:
    label = name or key
    return assert_true(key in d and d[key] is not None,
                       f"Alan mevcut: '{label}'",
                       f"Alan eksik veya None: '{label}'")


def assert_list_min(d: dict, key: str, min_len: int, name: str = "") -> bool:
    label = name or key
    lst = d.get(key, [])
    return assert_true(isinstance(lst, list) and len(lst) >= min_len,
                       f"'{label}' listesi ≥{min_len} eleman içeriyor ({len(lst)})",
                       f"'{label}' listesi yetersiz — beklenen ≥{min_len}, bulunan {len(lst)}")


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1 — ORTAM & API ANAHTARLARI
# ─────────────────────────────────────────────────────────────────────────────

def test_01_environment():
    header("TEST 1 — Ortam & API Anahtarları")
    t0 = time.time()

    # OPENROUTER_API_KEY
    openrouter = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if openrouter:
        masked = openrouter[:12] + "..." + openrouter[-4:]
        ok("OPENROUTER_API_KEY", masked)
    else:
        fail("OPENROUTER_API_KEY bulunamadı",
             "OPENROUTER_API_KEY veya OPENAI_API_KEY .env dosyasında olmalı")

    # ANTHROPIC / OPENROUTER ikincil key
    anthropic = os.getenv("ANTHROPIC_API_KEY")
    if anthropic:
        ok("ANTHROPIC_API_KEY", anthropic[:12] + "...")
    else:
        warn("ANTHROPIC_API_KEY ayarlanmamış",
             "SkillBasedDocxAgent OPENROUTER_API_KEY'i kullanacak")

    # Python versiyonu
    v = sys.version_info
    assert_true(v >= (3, 8),
                f"Python versiyonu uygun: {v.major}.{v.minor}.{v.micro}",
                f"Python ≥3.8 gerekli, bulunan: {v.major}.{v.minor}")

    # Gerekli paketler
    packages = ["openai", "anthropic", "dotenv", "docx", "requests", "pathlib"]
    for pkg in packages:
        try:
            __import__(pkg if pkg != "docx" else "docx")
            ok(f"Paket kurulu: {pkg}")
        except ImportError:
            warn(f"Paket eksik: {pkg}",
                 f"pip install {pkg if pkg != 'docx' else 'python-docx'}")

    # Outputs klasörü
    out_dir = ROOT / "outputs"
    if not out_dir.exists():
        out_dir.mkdir(parents=True)
        info("outputs/ klasörü oluşturuldu")
    ok("outputs/ klasörü mevcut", str(out_dir))

    elapsed = (time.time() - t0) * 1000
    results.append(("TEST 1 — Ortam", "done", "", elapsed))
    return openrouter is not None


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2 — test_hierarchical_output.json OKUMA & DOĞRULAMA
# ─────────────────────────────────────────────────────────────────────────────

def test_02_load_hierarchical_json() -> dict | None:
    header("TEST 2 — test_hierarchical_output.json Okuma & Doğrulama")
    t0 = time.time()

    json_path = ROOT / "test_hierarchical_output.json"

    # Dosya mevcut mu?
    if not assert_true(json_path.exists(),
                       f"Dosya bulundu: {json_path.name}",
                       f"Dosya bulunamadı: {json_path}"):
        return None

    # JSON parse
    try:
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
        ok("JSON parse başarılı")
    except json.JSONDecodeError as e:
        fail("JSON parse hatası", str(e))
        return None

    # ── Üst seviye alanlar ───────────────────────────────────────────────────
    subheader("2.1 — Üst Seviye Alan Kontrolleri")
    assert_key(data, "incident_summary", "incident_summary")
    assert_key(data, "analysis_branches", "analysis_branches")
    assert_key(data, "final_root_causes", "final_root_causes")
    assert_key(data, "analysis_method",   "analysis_method")
    assert_key(data, "final_report_tr",   "final_report_tr")

    # ── analysis_branches ────────────────────────────────────────────────────
    subheader("2.2 — Analiz Dalları Kontrolleri")
    branches = data.get("analysis_branches", [])
    assert_true(len(branches) >= 1,
                f"analysis_branches: {len(branches)} dal bulundu",
                "analysis_branches boş!")

    for i, branch in enumerate(branches, 1):
        prefix = f"Dal {i}"
        assert_key(branch, "branch_number", f"{prefix}.branch_number")
        assert_key(branch, "immediate_cause", f"{prefix}.immediate_cause")
        assert_key(branch, "why_chain", f"{prefix}.why_chain")
        assert_key(branch, "root_cause", f"{prefix}.root_cause")

        # immediate_cause alt alanları
        ic = branch.get("immediate_cause", {})
        for field in ["code", "standard_title_tr", "category_type", "cause_tr"]:
            assert_key(ic, field, f"{prefix}.immediate_cause.{field}")

        # why_chain uzunluğu
        chain = branch.get("why_chain", [])
        assert_true(len(chain) == 5,
                    f"{prefix}: why_chain 5 adımlı ✓",
                    f"{prefix}: why_chain beklenen 5 adım, bulunan {len(chain)}")

        # root_cause alt alanları
        rc = branch.get("root_cause", {})
        for field in ["code", "standard_title_tr", "category_type", "cause_tr"]:
            assert_key(rc, field, f"{prefix}.root_cause.{field}")

    # ── final_root_causes ────────────────────────────────────────────────────
    subheader("2.3 — Nihai Kök Nedenler Kontrolleri")
    frcs = data.get("final_root_causes", [])
    assert_true(len(frcs) >= 1,
                f"final_root_causes: {len(frcs)} kök neden bulundu",
                "final_root_causes boş!")

    for i, frc in enumerate(frcs, 1):
        for field in ["code", "standard_title_tr", "category_type", "cause_tr"]:
            assert_key(frc, field, f"FinalRC {i}.{field}")

    # ── Özet bilgi ───────────────────────────────────────────────────────────
    info(f"incident_summary uzunluğu: {len(data.get('incident_summary',''))} karakter")
    info(f"Toplam dal sayısı: {len(branches)}")
    info(f"Toplam final kök neden: {len(frcs)}")
    info(f"analysis_method: {data.get('analysis_method','N/A')}")

    elapsed = (time.time() - t0) * 1000
    results.append(("TEST 2 — JSON Yükleme", "done", "", elapsed))
    info(f"⏱  Tamamlandı: {elapsed:.0f}ms")
    return data


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3 — SkillBasedDocxAgent: HIERARCHICAL JSON → DOCX
# ─────────────────────────────────────────────────────────────────────────────

def test_03_docx_from_hierarchical(hierarchical_data: dict) -> str | None:
    header("TEST 3 — SkillBasedDocxAgent: Hierarchical JSON → DOCX Raporu")
    t0 = time.time()

    # ── Ajan import ──────────────────────────────────────────────────────────
    try:
        from agents.skillbased_docx_agent import SkillBasedDocxAgent
        ok("SkillBasedDocxAgent import başarılı")
    except ImportError as e:
        fail("SkillBasedDocxAgent import hatası", str(e))
        return None

    # ── Ajan başlatma ────────────────────────────────────────────────────────
    try:
        agent = SkillBasedDocxAgent()
        ok("SkillBasedDocxAgent başlatıldı")
    except Exception as e:
        fail("SkillBasedDocxAgent başlatılamadı", str(e))
        return None

    # ── investigation_data oluştur ───────────────────────────────────────────
    # Hierarchical JSON'ı orchestrator çıktısı formatına wrap ediyoruz
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    ref_no = f"TEST-{ts}"

    investigation_data = {
        "part1": {
            "ref_no": ref_no,
            "incident_type": "Serious injury",
            "date_time": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "brief_details": {
                "what": "Operatörün eli pres makinesinde sıkıştı ve ezildi",
                "where": "Üretim hattı, pres istasyonu",
                "when": "Gece vardiyası",
                "who": "Pres operatörü",
                "emergency_measures": "İlk yardım uygulandı, acil servise sevk edildi"
            }
        },
        "part2": {
            "type_of_event": "Accident",
            "actual_potential_harm": "Serious",
            "riddor_reportable": "Y",
            "investigation_level": "High level",
            "priority": "High"
        },
        "part3_rca": hierarchical_data,
        "status": "investigation_complete"
    }

    # ── DOCX üretimi ─────────────────────────────────────────────────────────
    output_path = str(ROOT / "outputs" / f"test_full_system_{ts}.docx")
    info(f"Çıktı dosyası: {output_path}")

    subheader("3.1 — API çağrısı & DOCX üretimi (lütfen bekleyin...)")
    try:
        report_path = agent.generate_report(
            investigation_data=investigation_data,
            output_path=output_path
        )
        elapsed = (time.time() - t0) * 1000

        if report_path and Path(report_path).exists():
            size_kb = Path(report_path).stat().st_size / 1024
            ok(f"DOCX raporu başarıyla üretildi",
               f"{Path(report_path).name}  ({size_kb:.1f} KB)")
            assert_true(size_kb > 5,
                        f"Dosya boyutu yeterli ({size_kb:.1f} KB > 5 KB)",
                        f"Dosya çok küçük ({size_kb:.1f} KB) — içerik eksik olabilir")
            info(f"⏱  Toplam süre: {elapsed:.0f}ms  ({elapsed/1000:.1f}s)")
            results.append(("TEST 3 — DOCX Üretimi", "pass", report_path, elapsed))
            return report_path
        else:
            fail("DOCX dosyası oluşturulamadı", f"Dönen yol: {report_path}")
            results.append(("TEST 3 — DOCX Üretimi", "fail", "", elapsed))
            return None

    except Exception as e:
        elapsed = (time.time() - t0) * 1000
        fail("DOCX üretimi sırasında hata oluştu", str(e))
        traceback.print_exc()
        results.append(("TEST 3 — DOCX Üretimi", "fail", str(e), elapsed))
        return None


# ─────────────────────────────────────────────────────────────────────────────
# TEST 4 — ORCHESTRATOR TAM PİPELİNE
# ─────────────────────────────────────────────────────────────────────────────

def test_04_orchestrator_full_pipeline() -> dict | None:
    header("TEST 4 — Orchestrator Tam Pipeline (Part1 → Part2 → Part3 → DOCX)")
    t0 = time.time()

    # ── Orchestrator import ──────────────────────────────────────────────────
    try:
        from agents.orchestrator import RootCauseOrchestrator
        ok("RootCauseOrchestrator import başarılı")
    except ImportError as e:
        fail("RootCauseOrchestrator import hatası", str(e))
        return None

    # ── Orchestrator başlatma ────────────────────────────────────────────────
    try:
        orchestrator = RootCauseOrchestrator()
        ok("Orchestrator başlatıldı")
        info(f"DOCX agent etkin: {orchestrator._docx_enabled}")
    except Exception as e:
        fail("Orchestrator başlatılamadı", str(e))
        traceback.print_exc()
        return None

    # ── Pres kazası olay verisi ──────────────────────────────────────────────
    incident_data = {
        "ref_no": f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "reported_by": "Vardiya Amiri",
        "description": (
            "Operatörün eli pres makinesinde sıkıştı ve ezildi. "
            "Konum: Üretim hattı, pres istasyonu. "
            "Olay Tipi: Mekanik yaralanma - el ezilmesi. "
            "Operatör gece vardiyasında pres makinesinde çalışıyordu. "
            "Güvenlik switch'i (interlock) arızalı olduğu için üretim durmasın diye "
            "kısa devre yapılmıştı. "
            "Operatör makineye yetkisi olmadığı halde müdahale etti ve eli "
            "koruyucu kapak açıkken sıkıştı. "
            "Bakımcı gece vardiyasında yoktu ve yedek parça stokta bulunmuyordu."
        ),
        "investigation_details": {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "location": "Üretim Hattı - Pres İstasyonu",
            "department": "Üretim",
            "shift": "Gece Vardiyası",
            "injured_person": "Pres Operatörü",
            "injury_type": "El ezilmesi - mekanik yaralanma",
            "equipment_involved": "Hidrolik pres makinesi",
            "witnesses": ["Vardiya Amiri", "Üretim Operatörü B"],
            "assessed_by": "HSE Uzmanı"
        }
    }

    # ── Pipeline çalıştırma ──────────────────────────────────────────────────
    subheader("4.1 — Soruşturma pipeline'ı çalıştırılıyor (lütfen bekleyin...)")
    try:
        result = orchestrator.run_investigation(incident_data)
        elapsed = (time.time() - t0) * 1000

        ok(f"Pipeline tamamlandı", f"Durum: {result.get('status','?')}")
        info(f"⏱  Toplam süre: {elapsed:.0f}ms  ({elapsed/1000:.1f}s)")

        # ── Part 1 doğrulama ─────────────────────────────────────────────────
        subheader("4.2 — Part 1 (Overview) Doğrulama")
        p1 = result.get("part1", {})
        assert_key(p1, "ref_no",         "part1.ref_no")
        assert_key(p1, "incident_type",  "part1.incident_type")
        assert_key(p1, "brief_details",  "part1.brief_details")
        info(f"Ref No: {p1.get('ref_no','N/A')}")
        info(f"Incident Type: {p1.get('incident_type','N/A')}")

        # ── Part 2 doğrulama ─────────────────────────────────────────────────
        subheader("4.3 — Part 2 (Assessment) Doğrulama")
        p2 = result.get("part2", {})
        assert_key(p2, "type_of_event",        "part2.type_of_event")
        assert_key(p2, "actual_potential_harm", "part2.actual_potential_harm")
        assert_key(p2, "riddor_reportable",     "part2.riddor_reportable")
        assert_key(p2, "investigation_level",   "part2.investigation_level")
        info(f"Şiddet: {p2.get('actual_potential_harm','N/A')}")
        info(f"RIDDOR: {p2.get('riddor_reportable','N/A')}")
        info(f"Soruşturma Seviyesi: {p2.get('investigation_level','N/A')}")

        # ── Part 3 doğrulama ─────────────────────────────────────────────────
        subheader("4.4 — Part 3 (RCA) Doğrulama")
        p3 = result.get("part3_rca", {})
        assert_key(p3, "analysis_branches", "part3.analysis_branches")
        assert_key(p3, "final_root_causes", "part3.final_root_causes")

        branches = p3.get("analysis_branches", [])
        final_rc = p3.get("final_root_causes", [])
        assert_true(len(branches) >= 1,
                    f"Analiz dalları üretildi: {len(branches)} dal",
                    "Analiz dalları boş!")
        assert_true(len(final_rc) >= 1,
                    f"Nihai kök nedenler üretildi: {len(final_rc)} kök neden",
                    "Nihai kök nedenler boş!")

        for i, branch in enumerate(branches, 1):
            info(f"Dal {i}: {branch.get('immediate_cause',{}).get('code','N/A')} → "
                 f"{branch.get('root_cause',{}).get('code','N/A')}")

        # ── DOCX doğrulama ───────────────────────────────────────────────────
        subheader("4.5 — DOCX Raporu Doğrulama")
        docx_path = result.get("docx_report")
        if docx_path:
            if Path(docx_path).exists():
                size_kb = Path(docx_path).stat().st_size / 1024
                ok(f"Orchestrator DOCX raporu oluşturuldu",
                   f"{Path(docx_path).name} ({size_kb:.1f} KB)")
            else:
                fail("DOCX yolu döndü ama dosya bulunamadı", docx_path)
        else:
            warn("Orchestrator DOCX raporu üretmedi",
                 "ANTHROPIC_API_KEY veya OPENROUTER_API_KEY eksik olabilir")

        # ── JSON dışa aktarma ────────────────────────────────────────────────
        subheader("4.6 — JSON Dışa Aktarma")
        ts2 = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_out = str(ROOT / "outputs" / f"test_full_pipeline_{ts2}.json")
        try:
            orchestrator.export_to_json(json_out)
            if Path(json_out).exists():
                ok("Soruşturma JSON olarak dışa aktarıldı", json_out)
            else:
                warn("JSON dosyası oluşturulamadı")
        except Exception as e:
            warn("JSON dışa aktarma hatası", str(e))

        results.append(("TEST 4 — Orchestrator Pipeline", "pass", "", elapsed))
        return result

    except Exception as e:
        elapsed = (time.time() - t0) * 1000
        fail("Orchestrator pipeline hatası", str(e))
        traceback.print_exc()
        results.append(("TEST 4 — Orchestrator Pipeline", "fail", str(e), elapsed))
        return None


# ─────────────────────────────────────────────────────────────────────────────
# TEST 5 — ÇIKTI DOSYALARI DOĞRULAMASI
# ─────────────────────────────────────────────────────────────────────────────

def test_05_output_files():
    header("TEST 5 — Çıktı Dosyaları Doğrulaması")
    t0 = time.time()

    out_dir = ROOT / "outputs"

    # ── Klasör ──────────────────────────────────────────────────────────────
    assert_true(out_dir.exists(),
                f"outputs/ klasörü mevcut",
                "outputs/ klasörü bulunamadı")

    # ── DOCX dosyaları ───────────────────────────────────────────────────────
    docx_files = list(out_dir.glob("*.docx"))
    assert_true(len(docx_files) >= 1,
                f"{len(docx_files)} adet .docx dosyası bulundu",
                "Hiç .docx dosyası bulunamadı")

    for f in sorted(docx_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
        size_kb = f.stat().st_size / 1024
        mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%H:%M:%S")
        info(f"  📄 {f.name}  ({size_kb:.1f} KB)  {mtime}")

    # ── JSON dosyaları ───────────────────────────────────────────────────────
    json_files = list(out_dir.glob("*.json"))
    if json_files:
        ok(f"{len(json_files)} adet .json çıktı dosyası bulundu")
        for f in sorted(json_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
            size_kb = f.stat().st_size / 1024
            info(f"  📋 {f.name}  ({size_kb:.1f} KB)")
    else:
        warn("Henüz JSON çıktı dosyası yok")

    # ── Son oluşturulan test DOCX boyut kontrolü ─────────────────────────────
    if docx_files:
        newest = max(docx_files, key=lambda x: x.stat().st_mtime)
        size_kb = newest.stat().st_size / 1024
        assert_true(size_kb > 5,
                    f"En son DOCX boyutu yeterli: {size_kb:.1f} KB",
                    f"En son DOCX çok küçük: {size_kb:.1f} KB")

    elapsed = (time.time() - t0) * 1000
    results.append(("TEST 5 — Çıktı Dosyaları", "done", "", elapsed))


# ─────────────────────────────────────────────────────────────────────────────
# TEST 6 — JSON ŞEMA BÜTÜNLÜĞÜ
# ─────────────────────────────────────────────────────────────────────────────

def test_06_schema_integrity(hierarchical_data: dict, pipeline_result: dict | None):
    header("TEST 6 — JSON Şema Bütünlüğü Kontrolleri")
    t0 = time.time()

    # ── hierarchical_data derinlemesine şema ─────────────────────────────────
    subheader("6.1 — Hierarchical JSON Derinlemesine Kontrol")

    branches = hierarchical_data.get("analysis_branches", [])
    for bi, branch in enumerate(branches, 1):
        chain = branch.get("why_chain", [])
        for wi, why in enumerate(chain, 1):
            assert_key(why, "level",       f"Dal{bi}.Why{wi}.level")
            assert_key(why, "question_tr", f"Dal{bi}.Why{wi}.question_tr")
            assert_key(why, "answer_tr",   f"Dal{bi}.Why{wi}.answer_tr")

            # İçerik boş değil mi?
            assert_true(len(why.get("question_tr","")) > 10,
                        f"Dal{bi}.Why{wi} sorusu yeterince uzun",
                        f"Dal{bi}.Why{wi} sorusu çok kısa/boş")
            assert_true(len(why.get("answer_tr","")) > 10,
                        f"Dal{bi}.Why{wi} cevabı yeterince uzun",
                        f"Dal{bi}.Why{wi} cevabı çok kısa/boş")

    # ── incident_summary uzunluğu ────────────────────────────────────────────
    summary = hierarchical_data.get("incident_summary", "")
    assert_true(len(summary) > 50,
                f"incident_summary yeterince uzun ({len(summary)} karakter)",
                "incident_summary çok kısa!")

    # ── final_report_tr metin içeriği ────────────────────────────────────────
    report_text = hierarchical_data.get("final_report_tr", "")
    assert_true(len(report_text) > 500,
                f"final_report_tr metin içeriği yeterli ({len(report_text)} karakter)",
                f"final_report_tr çok kısa: {len(report_text)} karakter")

    # Anahtar ifadeler raporun içinde mi?
    for keyword in ["DAL", "KÖK NEDEN", "Neden"]:
        assert_true(keyword in report_text,
                    f"final_report_tr '{keyword}' içeriyor",
                    f"final_report_tr '{keyword}' içermiyor")

    # ── Pipeline sonucu şema kontrolü ────────────────────────────────────────
    if pipeline_result:
        subheader("6.2 — Pipeline Sonucu Şema Kontrolü")
        for key in ["part1", "part2", "part3_rca", "status"]:
            assert_key(pipeline_result, key)

        status = pipeline_result.get("status", "")
        assert_true("complete" in status,
                    f"Pipeline durumu geçerli: '{status}'",
                    f"Pipeline durumu beklenmedik: '{status}'")

    elapsed = (time.time() - t0) * 1000
    results.append(("TEST 6 — Şema Bütünlüğü", "done", "", elapsed))


# ─────────────────────────────────────────────────────────────────────────────
# TEST 7 — AJAN IMPORT & BAŞLATMA TESTLERİ
# ─────────────────────────────────────────────────────────────────────────────

def test_07_agent_imports():
    header("TEST 7 — Ajan Import & Başlatma Testleri")
    t0 = time.time()

    agents = [
        ("agents.overview_agent",      "OverviewAgent"),
        ("agents.assessment_agent",    "AssessmentAgent"),
        ("agents.rootcause_agent_v2",  "RootCauseAgentV2"),
        ("agents.skillbased_docx_agent","SkillBasedDocxAgent"),
        ("agents.orchestrator",        "RootCauseOrchestrator"),
        ("agents.json_parser",         "extract_json_from_response"),
        ("agents.knowledge_base",      "HSG245_TAXONOMY"),
    ]

    for module_path, class_name in agents:
        try:
            mod = __import__(module_path, fromlist=[class_name])
            cls = getattr(mod, class_name, None)
            if cls is not None:
                ok(f"Import: {module_path}.{class_name}")
            else:
                warn(f"Modül import edildi ama '{class_name}' bulunamadı", module_path)
        except ImportError as e:
            fail(f"Import başarısız: {module_path}", str(e))
        except Exception as e:
            warn(f"Import sırasında uyarı: {module_path}", str(e))

    # ── shared config ────────────────────────────────────────────────────────
    try:
        from shared.config import Config
        ok("shared.config.Config import başarılı")
        info(f"Proje kökü: {Config.PROJECT_ROOT}")
    except Exception as e:
        warn("shared.config import hatası", str(e))

    elapsed = (time.time() - t0) * 1000
    results.append(("TEST 7 — Ajan Importları", "done", "", elapsed))


# ─────────────────────────────────────────────────────────────────────────────
# TEST 8 — JSON PARSER BAĞIMSIZ TEST
# ─────────────────────────────────────────────────────────────────────────────

def test_08_json_parser():
    header("TEST 8 — JSON Parser Bağımsız Test")
    t0 = time.time()

    try:
        from agents.json_parser import extract_json_from_response, safe_json_parse
        ok("json_parser import başarılı")
    except ImportError as e:
        fail("json_parser import hatası", str(e))
        return

    # ── Geçerli JSON ──────────────────────────────────────────────────────────
    valid_cases = [
        ('{"key":"val"}',                  "düz JSON"),
        ('```json\n{"key":"val"}\n```',     "markdown code block"),
        ('Some text {"key":"val"} more',    "metin içinde gömülü JSON"),
        ('{"a":1, "b": [1,2,3]}',          "dizili JSON"),
    ]
    for raw, desc in valid_cases:
        try:
            parsed = extract_json_from_response(raw)
            assert_true(isinstance(parsed, dict),
                        f"extract_json_from_response({desc}) → dict",
                        f"extract_json_from_response({desc}) → dict değil: {type(parsed)}")
        except Exception as e:
            fail(f"extract_json_from_response({desc}) hata", str(e))

    # ── safe_json_parse ──────────────────────────────────────────────────────
    try:
        result = safe_json_parse('{"test": 123}')
        assert_true(result.get("test") == 123,
                    "safe_json_parse doğru değer döndürdü",
                    f"safe_json_parse hatalı değer: {result}")
    except Exception as e:
        fail("safe_json_parse hatası", str(e))

    elapsed = (time.time() - t0) * 1000
    results.append(("TEST 8 — JSON Parser", "done", "", elapsed))


# ─────────────────────────────────────────────────────────────────────────────
# SONUÇ ÖZETİ
# ─────────────────────────────────────────────────────────────────────────────

def print_summary():
    global PASS, FAIL, WARN
    total_time = sum(r[3] for r in results)

    print(f"\n{BOLD}{'='*78}{RESET}")
    print(f"{BOLD}  📊 TEST SONUÇLARI ÖZETİ{RESET}")
    print(f"{BOLD}{'='*78}{RESET}")

    for name, status, detail, ms in results:
        stat_str = f"{GREEN}DONE{RESET}" if status == "done" \
                   else f"{GREEN}PASS{RESET}" if status == "pass" \
                   else f"{RED}FAIL{RESET}"
        detail_str = f"  → {detail[:60]}" if detail else ""
        print(f"  {stat_str}  {name:<40} {ms:>8.0f}ms{detail_str}")

    print(f"\n{BOLD}{'─'*78}{RESET}")
    print(f"  {GREEN}✅ PASS: {PASS}{RESET}   "
          f"{RED}❌ FAIL: {FAIL}{RESET}   "
          f"{YELLOW}⚠️  WARN: {WARN}{RESET}   "
          f"⏱  Toplam: {total_time/1000:.1f}s")
    print(f"{BOLD}{'='*78}{RESET}")

    if FAIL == 0:
        print(f"\n  {GREEN}{BOLD}🎉 TÜM TESTLER BAŞARILI!{RESET}\n")
    else:
        print(f"\n  {RED}{BOLD}💥 {FAIL} TEST BAŞARISIZ — yukarıdaki hataları inceleyin.{RESET}\n")


# ─────────────────────────────────────────────────────────────────────────────
# ANA GİRİŞ
# ─────────────────────────────────────────────────────────────────────────────

def main():
    global_start = time.time()

    print(f"\n{BOLD}{CYAN}")
    print("╔══════════════════════════════════════════════════════════════════════════╗")
    print("║       HSE RCA SİSTEMİ — TAM ENTEGRASYON TESTİ                          ║")
    print("║       test_hierarchical_output.json → DOCX + Pipeline                  ║")
    print(f"║       {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}                                          ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝")
    print(RESET)

    # ── TEST 1: Ortam ─────────────────────────────────────────────────────────
    env_ok = test_01_environment()

    # ── TEST 7: Ajan importları ───────────────────────────────────────────────
    test_07_agent_imports()

    # ── TEST 8: JSON Parser ───────────────────────────────────────────────────
    test_08_json_parser()

    # ── TEST 2: JSON yükleme ─────────────────────────────────────────────────
    hierarchical_data = test_02_load_hierarchical_json()

    if hierarchical_data is None:
        fail("test_hierarchical_output.json yüklenemedi — devam edilemiyor")
        print_summary()
        return

    # ── TEST 6: Şema bütünlüğü (pipeline öncesi) ─────────────────────────────
    test_06_schema_integrity(hierarchical_data, None)

    # ── TEST 3: SkillBasedDocxAgent → DOCX ───────────────────────────────────
    if env_ok:
        docx_path = test_03_docx_from_hierarchical(hierarchical_data)
    else:
        warn("TEST 3 atlandı", "API anahtarı eksik")
        docx_path = None

    # ── TEST 5: Çıktı dosyaları ───────────────────────────────────────────────
    test_05_output_files()

    # ── TEST 4: Orchestrator tam pipeline ────────────────────────────────────
    header("TEST 4 — ORCHESTRATOR TAM PİPELİNE")
    print(f"  {YELLOW}⚠️  Bu test AI API'ye çok sayıda istek gönderir ve ~2-5 dakika sürebilir.{RESET}")
    confirm = input(f"\n  {BOLD}Orchestrator pipeline testini çalıştırmak istiyor musunuz? [e/H]: {RESET}").strip().lower()

    if confirm in ("e", "evet", "y", "yes"):
        pipeline_result = test_04_orchestrator_full_pipeline()
        test_06_schema_integrity(hierarchical_data, pipeline_result)
        test_05_output_files()
    else:
        warn("TEST 4 atlandı (kullanıcı tarafından)")
        results.append(("TEST 4 — Orchestrator Pipeline", "done", "atlandı", 0))
        pipeline_result = None

    # ── ÖZET ──────────────────────────────────────────────────────────────────
    global_elapsed = (time.time() - global_start)
    info(f"Toplam test süresi: {global_elapsed:.1f}s")
    print_summary()


if __name__ == "__main__":
    main()
