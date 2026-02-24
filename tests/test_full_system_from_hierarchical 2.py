"""
Full System Test - test_hierarchical_output.json üzerinden
===========================================================

Bu test, test_hierarchical_output.json içindeki gerçek RCA verisini kullanarak
tüm sistemi uçtan uca test eder:

  ADIM 1  ─ Ortam & Bağımlılıklar (env vars, paketler)
  ADIM 2  ─ JSON şema doğrulaması (hierarchical output yapısı)
  ADIM 3  ─ OverviewAgent   (Part 1)
  ADIM 4  ─ AssessmentAgent (Part 2)
  ADIM 5  ─ RootCauseAgentV2 (Part 3 — AI analizi)
  ADIM 6  ─ SkillBasedDocxAgent (DOCX rapor üretimi)
  ADIM 7  ─ Orchestrator (tam pipeline — uçtan uca)
  ADIM 8  ─ Çıktı Doğrulaması (JSON + DOCX dosya kontrolleri)
  ADIM 9  ─ Özet Rapor

Çalıştırma:
    python test_full_system_from_hierarchical.py
"""

import sys
import os
import json
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# ── Proje kök dizinini Python path'e ekle ─────────────────────────────────────
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

# ── Ortam değişkenlerini yükle ─────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()

# ── Renk ve biçimlendirme sabitleri ───────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

HIERARCHICAL_JSON_PATH = ROOT / "test_hierarchical_output.json"
OUTPUTS_DIR = ROOT / "outputs"

# ─────────────────────────────────────────────────────────────────────────────
# Yardımcı fonksiyonlar
# ─────────────────────────────────────────────────────────────────────────────

def section(title: str):
    print(f"\n{BOLD}{CYAN}{'='*80}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'='*80}{RESET}")


def subsection(title: str):
    print(f"\n{BOLD}  ── {title}{RESET}")


def ok(msg: str):
    print(f"  {GREEN}✅ {msg}{RESET}")


def fail(msg: str):
    print(f"  {RED}❌ {msg}{RESET}")


def warn(msg: str):
    print(f"  {YELLOW}⚠️  {msg}{RESET}")


def info(msg: str):
    print(f"     {msg}")


# ─────────────────────────────────────────────────────────────────────────────
# TEST SONUÇ TAKİPÇİSİ
# ─────────────────────────────────────────────────────────────────────────────

class TestResults:
    def __init__(self):
        self.results: Dict[str, Dict] = {}

    def record(self, name: str, passed: bool, detail: str = ""):
        self.results[name] = {"passed": passed, "detail": detail}

    def summary(self) -> Tuple[int, int]:
        total  = len(self.results)
        passed = sum(1 for r in self.results.values() if r["passed"])
        return passed, total

    def print_summary(self):
        passed, total = self.summary()
        section("TEST ÖZET RAPORU")
        print(f"\n  {'ADIM':<45} SONUÇ")
        print(f"  {'-'*45} {'------'}")
        for name, r in self.results.items():
            status = f"{GREEN}GEÇTI{RESET}" if r["passed"] else f"{RED}BAŞARISIZ{RESET}"
            detail = f"  → {r['detail']}" if r["detail"] else ""
            print(f"  {name:<45} {status}{detail}")

        print(f"\n  Toplam: {passed}/{total} adım geçti")
        print(f"\n{'='*80}")
        if passed == total:
            print(f"{GREEN}{BOLD}  🎉 TÜM TESTLER GEÇTI! Sistem tam çalışıyor.{RESET}")
        elif passed >= total * 0.7:
            print(f"{YELLOW}{BOLD}  ⚠️  KISMI BAŞARI — Bazı adımlar başarısız.{RESET}")
        else:
            print(f"{RED}{BOLD}  ❌ ÇOKLU HATA — Sistem dikkat gerektiriyor.{RESET}")
        print(f"{'='*80}")


tracker = TestResults()

# ─────────────────────────────────────────────────────────────────────────────
# ADIM 1 — ORTAM & BAĞIMLILIK KONTROLÜ
# ─────────────────────────────────────────────────────────────────────────────

def test_environment() -> bool:
    section("ADIM 1: Ortam & Bağımlılık Kontrolü")
    all_ok = True

    # Gerekli paketler
    required = ["openai", "dotenv", "docx", "requests"]
    subsection("Paket kontrolleri")
    for pkg in required:
        try:
            __import__(pkg)
            ok(f"  {pkg} — yüklü")
        except ImportError:
            fail(f"  {pkg} — EKSİK (pip install {pkg})")
            all_ok = False

    # API anahtarları
    subsection("API Anahtarları")
    openrouter_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if openrouter_key:
        masked = openrouter_key[:8] + "..." + openrouter_key[-4:]
        ok(f"OPENROUTER_API_KEY: {masked}")
    else:
        fail("OPENROUTER_API_KEY bulunamadı! .env dosyasını kontrol edin.")
        all_ok = False

    # Hierarchical JSON dosyası
    subsection("Test Dosyası")
    if HIERARCHICAL_JSON_PATH.exists():
        size = HIERARCHICAL_JSON_PATH.stat().st_size
        ok(f"test_hierarchical_output.json mevcut ({size:,} bytes)")
    else:
        fail(f"test_hierarchical_output.json bulunamadı: {HIERARCHICAL_JSON_PATH}")
        all_ok = False

    # Outputs dizini
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    ok(f"outputs/ dizini hazır: {OUTPUTS_DIR}")

    tracker.record("ADIM 1 — Ortam & Bağımlılık", all_ok)
    return all_ok


# ─────────────────────────────────────────────────────────────────────────────
# ADIM 2 — JSON ŞEMA DOĞRULAMASI
# ─────────────────────────────────────────────────────────────────────────────

def test_json_schema() -> Optional[Dict]:
    section("ADIM 2: test_hierarchical_output.json Şema Doğrulaması")

    try:
        with open(HIERARCHICAL_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        ok("JSON dosyası başarıyla yüklendi")
    except Exception as e:
        fail(f"JSON yükleme hatası: {e}")
        tracker.record("ADIM 2 — JSON Şema Doğrulama", False, str(e))
        return None

    errors = []

    # Zorunlu üst düzey alanlar
    required_top = ["incident_summary", "analysis_branches", "final_root_causes",
                    "analysis_method", "final_report_tr"]
    subsection("Üst düzey alanlar")
    for field in required_top:
        if field in data:
            ok(f"  '{field}' mevcut")
        else:
            fail(f"  '{field}' EKSİK!")
            errors.append(field)

    # analysis_branches yapısı
    subsection("analysis_branches yapısı")
    branches = data.get("analysis_branches", [])
    info(f"Dal sayısı: {len(branches)}")
    if len(branches) == 0:
        fail("Hiç analiz dalı yok!")
        errors.append("analysis_branches boş")
    else:
        for i, branch in enumerate(branches):
            branch_errors = []
            for key in ["branch_number", "immediate_cause", "why_chain", "root_cause"]:
                if key not in branch:
                    branch_errors.append(key)
            if branch_errors:
                fail(f"  Dal {i+1}: eksik alanlar → {branch_errors}")
                errors.extend(branch_errors)
            else:
                ok(f"  Dal {i+1} (no={branch.get('branch_number')}): tüm alanlar mevcut")

            # why_chain seviye kontrolü
            why_chain = branch.get("why_chain", [])
            if len(why_chain) >= 5:
                ok(f"    why_chain: {len(why_chain)} seviye (≥5 ✓)")
            else:
                warn(f"    why_chain: sadece {len(why_chain)} seviye (beklenen ≥5)")

            # immediate_cause alanları
            ic = branch.get("immediate_cause", {})
            for ic_key in ["code", "standard_title_tr", "category_type", "cause_tr", "evidence_tr"]:
                if ic_key not in ic:
                    warn(f"    immediate_cause['{ic_key}'] eksik")

            # root_cause alanları
            rc = branch.get("root_cause", {})
            for rc_key in ["code", "standard_title_tr", "category_type", "cause_tr", "explanation_tr"]:
                if rc_key not in rc:
                    warn(f"    root_cause['{rc_key}'] eksik")

    # final_root_causes
    subsection("final_root_causes")
    final_rcs = data.get("final_root_causes", [])
    info(f"Kök neden sayısı: {len(final_rcs)}")
    if final_rcs:
        ok(f"  {len(final_rcs)} kök neden bulundu")
        for i, rc in enumerate(final_rcs):
            code = rc.get("code", "?")
            title = rc.get("standard_title_tr", "?")
            category = rc.get("category_type", "?")
            info(f"    [{i+1}] [{code}] {title} ({category})")
    else:
        fail("final_root_causes boş!")
        errors.append("final_root_causes boş")

    # final_report_tr uzunluk kontrolü
    subsection("Metin rapor")
    report_text = data.get("final_report_tr", "")
    info(f"final_report_tr uzunluğu: {len(report_text):,} karakter")
    if len(report_text) > 500:
        ok("  final_report_tr yeterince uzun")
    else:
        warn("  final_report_tr çok kısa")

    passed = len(errors) == 0
    tracker.record("ADIM 2 — JSON Şema Doğrulama", passed,
                   "" if passed else f"{len(errors)} hata")
    return data if passed else None


# ─────────────────────────────────────────────────────────────────────────────
# ADIM 3 — OVERVIEW AGENT (Part 1)
# ─────────────────────────────────────────────────────────────────────────────

def test_overview_agent(hierarchical_data: Dict) -> Optional[Dict]:
    section("ADIM 3: OverviewAgent (Part 1)")

    try:
        from agents.overview_agent import OverviewAgent
        agent = OverviewAgent()
        ok("OverviewAgent başlatıldı")
    except Exception as e:
        fail(f"OverviewAgent import/init hatası: {e}")
        traceback.print_exc()
        tracker.record("ADIM 3 — OverviewAgent", False, str(e))
        return None

    # hierarchical output'tan olay verisini çıkar
    incident_summary = hierarchical_data.get("incident_summary", "")
    incident_data = {
        "reported_by": "Vardiya Güvenlik Sorumlusu",
        "description": incident_summary,
        "injury_description": "Operatörün eli pres makinesinde sıkışarak ezildi - mekanik yaralanma",
        "forwarded_to": "HSE Direktörü ve Üretim Müdürü",
        "date_time": datetime.now().strftime("%d.%m.%Y %H:%M"),
    }

    subsection("Olay raporu işleniyor...")
    t0 = time.time()
    try:
        part1 = agent.process_initial_report(incident_data)
        elapsed = time.time() - t0
        ok(f"Part 1 tamamlandı ({elapsed:.1f}s)")
    except Exception as e:
        fail(f"process_initial_report hatası: {e}")
        traceback.print_exc()
        tracker.record("ADIM 3 — OverviewAgent", False, str(e))
        return None

    # Zorunlu alanları kontrol et
    errors = []
    for key in ["ref_no", "incident_type", "brief_details"]:
        if key in part1:
            ok(f"  '{key}' mevcut: {str(part1[key])[:60]}...")
        else:
            fail(f"  '{key}' eksik!")
            errors.append(key)

    passed = len(errors) == 0
    tracker.record("ADIM 3 — OverviewAgent", passed,
                   f"ref_no={part1.get('ref_no', 'N/A')}" if passed else f"Eksik: {errors}")
    return part1 if passed else None


# ─────────────────────────────────────────────────────────────────────────────
# ADIM 4 — ASSESSMENT AGENT (Part 2)
# ─────────────────────────────────────────────────────────────────────────────

def test_assessment_agent(part1_data: Dict, hierarchical_data: Dict) -> Optional[Dict]:
    section("ADIM 4: AssessmentAgent (Part 2)")

    try:
        from agents.assessment_agent import AssessmentAgent
        agent = AssessmentAgent()
        ok("AssessmentAgent başlatıldı")
    except Exception as e:
        fail(f"AssessmentAgent import/init hatası: {e}")
        traceback.print_exc()
        tracker.record("ADIM 4 — AssessmentAgent", False, str(e))
        return None

    # hierarchical output'tan ek bağlam
    branches = hierarchical_data.get("analysis_branches", [])
    extra_context = {
        "investigation_notes": f"{len(branches)} analiz dalı tespit edildi. "
                               f"Yöntem: {hierarchical_data.get('analysis_method', 'HSG245')}",
    }

    subsection("İlk değerlendirme yapılıyor...")
    t0 = time.time()
    try:
        part2 = agent.assess_incident(part1_data, extra_context)
        elapsed = time.time() - t0
        ok(f"Part 2 tamamlandı ({elapsed:.1f}s)")
    except Exception as e:
        fail(f"assess_incident hatası: {e}")
        traceback.print_exc()
        tracker.record("ADIM 4 — AssessmentAgent", False, str(e))
        return None

    # Zorunlu alanları kontrol et
    errors = []
    for key in ["type_of_event", "actual_potential_harm", "investigation_level"]:
        if key in part2:
            ok(f"  '{key}': {part2[key]}")
        else:
            fail(f"  '{key}' eksik!")
            errors.append(key)

    info(f"  RIDDOR Reportable: {part2.get('riddor_reportable', 'N/A')}")
    info(f"  Priority: {part2.get('priority', 'N/A')}")

    passed = len(errors) == 0
    tracker.record("ADIM 4 — AssessmentAgent", passed,
                   f"level={part2.get('investigation_level', 'N/A')}" if passed else f"Eksik: {errors}")
    return part2 if passed else None


# ─────────────────────────────────────────────────────────────────────────────
# ADIM 5 — ROOT CAUSE AGENT V2 (Part 3 — AI analizi)
# ─────────────────────────────────────────────────────────────────────────────

def test_rootcause_agent(part1_data: Dict, part2_data: Dict, hierarchical_data: Dict) -> Optional[Dict]:
    section("ADIM 5: RootCauseAgentV2 (Part 3 — AI Analizi)")

    try:
        from agents.rootcause_agent_v2 import RootCauseAgentV2
        agent = RootCauseAgentV2()
        ok("RootCauseAgentV2 başlatıldı")
    except Exception as e:
        fail(f"RootCauseAgentV2 import/init hatası: {e}")
        traceback.print_exc()
        tracker.record("ADIM 5 — RootCauseAgentV2", False, str(e))
        return None

    # Olay araştırma detayları hierarchical JSON'dan al
    incident_summary = hierarchical_data.get("incident_summary", "")
    investigation_data = {
        "how_happened": incident_summary,
    }

    subsection("Kök neden analizi yapılıyor (5-Why / HSG245)...")
    t0 = time.time()
    try:
        part3 = agent.analyze_root_causes(
            part1_data=part1_data,
            part2_data=part2_data,
            investigation_data=investigation_data,
        )
        elapsed = time.time() - t0
        ok(f"Part 3 tamamlandı ({elapsed:.1f}s)")
    except Exception as e:
        fail(f"analyze_root_causes hatası: {e}")
        traceback.print_exc()
        tracker.record("ADIM 5 — RootCauseAgentV2", False, str(e))
        return None

    # Yapısal kontroller
    errors = []
    for key in ["analysis_branches", "final_root_causes", "analysis_method"]:
        if key in part3:
            ok(f"  '{key}' mevcut")
        else:
            fail(f"  '{key}' eksik!")
            errors.append(key)

    branches   = part3.get("analysis_branches", [])
    root_causes = part3.get("final_root_causes", [])
    info(f"  Analiz Dalı Sayısı:   {len(branches)}")
    info(f"  Kök Neden Sayısı:     {len(root_causes)}")
    info(f"  Yöntem:               {part3.get('analysis_method', 'N/A')}")

    # Hierarchical JSON ile karşılaştır
    subsection("Hierarchical JSON ile karşılaştırma")
    expected_branches   = len(hierarchical_data.get("analysis_branches", []))
    expected_root_causes = len(hierarchical_data.get("final_root_causes", []))
    info(f"  Beklenen dal:        {expected_branches}   Üretilen: {len(branches)}")
    info(f"  Beklenen kök neden:  {expected_root_causes}  Üretilen: {len(root_causes)}")

    if len(branches) > 0:
        ok("  En az 1 analiz dalı üretildi ✓")
    else:
        fail("  Hiç analiz dalı üretilmedi!")
        errors.append("analysis_branches boş")

    if len(root_causes) > 0:
        ok("  En az 1 kök neden üretildi ✓")
        for i, rc in enumerate(root_causes):
            code    = rc.get("code", rc.get("standard_title_tr", "?"))[:20]
            category = rc.get("category_type", "?")
            info(f"    [{i+1}] [{code}] ({category})")
    else:
        fail("  Hiç kök neden üretilmedi!")
        errors.append("final_root_causes boş")

    # Sonuçları kaydet
    output_file = OUTPUTS_DIR / f"rca_full_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(part3, f, ensure_ascii=False, indent=2)
        ok(f"  RCA sonuçları kaydedildi: {output_file.name}")
    except Exception as e:
        warn(f"  Kaydetme hatası: {e}")

    passed = len(errors) == 0
    tracker.record("ADIM 5 — RootCauseAgentV2", passed,
                   f"{len(branches)} dal, {len(root_causes)} kök neden" if passed else f"Hatalar: {errors}")
    return part3 if passed else None


# ─────────────────────────────────────────────────────────────────────────────
# ADIM 6 — SKILLBASED DOCX AGENT (DOCX rapor üretimi)
# ─────────────────────────────────────────────────────────────────────────────

def test_docx_agent(part1_data: Dict, part2_data: Dict, part3_data: Dict,
                    hierarchical_data: Dict) -> Optional[str]:
    section("ADIM 6: SkillBasedDocxAgent (DOCX Rapor Üretimi)")

    try:
        from agents.skillbased_docx_agent import SkillBasedDocxAgent
        agent = SkillBasedDocxAgent()
        ok("SkillBasedDocxAgent başlatıldı")
    except ValueError as e:
        fail(f"SkillBasedDocxAgent başlatılamadı (API key eksik?): {e}")
        tracker.record("ADIM 6 — SkillBasedDocxAgent", False, str(e))
        return None
    except Exception as e:
        fail(f"SkillBasedDocxAgent hatası: {e}")
        traceback.print_exc()
        tracker.record("ADIM 6 — SkillBasedDocxAgent", False, str(e))
        return None

    # investigation_data'yı oluştur — orchestrator ile aynı yapı
    investigation_data = {
        "part1":      part1_data,
        "part2":      part2_data,
        "part3_rca":  part3_data,
        "status":     "test_complete",
    }

    ref_no      = part1_data.get("ref_no", "full_test")
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = str(OUTPUTS_DIR / f"{ref_no}_full_test_{timestamp}.docx")

    subsection(f"DOCX raporu üretiliyor → {Path(output_path).name}")
    t0 = time.time()
    try:
        result_path = agent.generate_report(
            investigation_data=investigation_data,
            output_path=output_path,
        )
        elapsed = time.time() - t0
        ok(f"Rapor üretildi ({elapsed:.1f}s)")
    except Exception as e:
        fail(f"generate_report hatası: {e}")
        traceback.print_exc()
        tracker.record("ADIM 6 — SkillBasedDocxAgent", False, str(e))
        return None

    # Dosya var mı?
    docx_path = Path(result_path) if result_path else Path(output_path)
    if docx_path.exists():
        size_kb = docx_path.stat().st_size / 1024
        ok(f"  DOCX dosyası oluşturuldu: {docx_path.name}")
        info(f"  Boyut: {size_kb:.1f} KB")
        info(f"  Tam yol: {docx_path}")
        tracker.record("ADIM 6 — SkillBasedDocxAgent", True, f"{docx_path.name} ({size_kb:.1f} KB)")
        return str(docx_path)
    else:
        fail(f"  DOCX dosyası bulunamadı: {docx_path}")
        tracker.record("ADIM 6 — SkillBasedDocxAgent", False, "Dosya oluşturulamadı")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# ADIM 7 — ORCHESTRATOR (tam pipeline)
# ─────────────────────────────────────────────────────────────────────────────

def test_orchestrator(hierarchical_data: Dict) -> Optional[Dict]:
    section("ADIM 7: RootCauseOrchestrator — Tam Pipeline Testi")

    try:
        from agents.orchestrator import RootCauseOrchestrator
        orchestrator = RootCauseOrchestrator()
        ok("RootCauseOrchestrator başlatıldı")
    except Exception as e:
        fail(f"Orchestrator init hatası: {e}")
        traceback.print_exc()
        tracker.record("ADIM 7 — Orchestrator", False, str(e))
        return None

    # Hierarchical JSON'dan gerçek olay verisini al
    incident_summary = hierarchical_data.get("incident_summary", "")
    branches         = hierarchical_data.get("analysis_branches", [])

    incident_data = {
        "reported_by": "Vardiya Amiri - Gece Vardiyası",
        "description": incident_summary,
        "injury_description": "El ezilmesi — pres makinesinde interlock baypas sonrası mekanik yaralanma",
        "forwarded_to": "HSE Direktörü",
        "date_time": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "investigation_details": {
            "how_happened": incident_summary,
            "analysis_method": hierarchical_data.get("analysis_method", "HSG245"),
            "branch_count": len(branches),
        },
    }

    subsection("Tam soruşturma başlatılıyor (4 adım: Overview → Assessment → RCA → DOCX)...")
    t0 = time.time()
    try:
        result = orchestrator.run_investigation(incident_data)
        elapsed = time.time() - t0
        ok(f"Orchestrator tamamlandı ({elapsed:.1f}s)")
    except Exception as e:
        fail(f"run_investigation hatası: {e}")
        traceback.print_exc()
        tracker.record("ADIM 7 — Orchestrator", False, str(e))
        return None

    # Sonuçları doğrula
    errors = []
    for key in ["part1", "part2", "part3_rca", "status"]:
        if key in result:
            ok(f"  '{key}' mevcut")
        else:
            fail(f"  '{key}' eksik!")
            errors.append(key)

    info(f"\n  Referans No:        {result.get('part1', {}).get('ref_no', 'N/A')}")
    info(f"  Olay Tipi:          {result.get('part1', {}).get('incident_type', 'N/A')}")
    info(f"  Değerlendirme:      {result.get('part2', {}).get('investigation_level', 'N/A')}")
    info(f"  Analiz Dalı:        {len(result.get('part3_rca', {}).get('analysis_branches', []))}")
    info(f"  Kök Neden:          {len(result.get('part3_rca', {}).get('final_root_causes', []))}")
    info(f"  DOCX Rapor:         {result.get('docx_report', 'Üretilmedi (API key eksik?)')}")
    info(f"  Durum:              {result.get('status', 'N/A')}")

    # Orchestrator çıktısını JSON olarak kaydet
    output_file = OUTPUTS_DIR / f"orchestrator_full_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        orchestrator.export_to_json(str(output_file))
        ok(f"  Orchestrator çıktısı kaydedildi: {output_file.name}")
    except Exception as e:
        warn(f"  Kaydetme hatası: {e}")

    passed = len(errors) == 0
    tracker.record("ADIM 7 — Orchestrator", passed,
                   f"status={result.get('status', 'N/A')}" if passed else f"Eksik: {errors}")
    return result if passed else None


# ─────────────────────────────────────────────────────────────────────────────
# ADIM 8 — ÇIKTI DOĞRULAMASI
# ─────────────────────────────────────────────────────────────────────────────

def test_output_validation():
    section("ADIM 8: Çıktı Dosyaları Doğrulaması")

    issues = []

    # outputs/ dizinindeki dosyaları listele
    output_files = list(OUTPUTS_DIR.glob("*.json")) + list(OUTPUTS_DIR.glob("*.docx"))
    info(f"outputs/ altındaki dosya sayısı: {len(output_files)}")

    subsection("Bu test tarafından üretilen dosyalar")
    test_files = (
        list(OUTPUTS_DIR.glob("*full_test*.json"))
        + list(OUTPUTS_DIR.glob("*full_test*.docx"))
        + list(OUTPUTS_DIR.glob("orchestrator_full_test*.json"))
        + list(OUTPUTS_DIR.glob("rca_full_test*.json"))
    )

    if test_files:
        for f in sorted(test_files, key=lambda x: x.stat().st_mtime, reverse=True):
            size_kb = f.stat().st_size / 1024
            ok(f"  {f.name} ({size_kb:.1f} KB)")
    else:
        warn("  Bu test tarafından üretilen dosya bulunamadı.")
        issues.append("test çıktı dosyası yok")

    # JSON dosyalarını oku ve doğrula
    subsection("JSON çıktı içerik doğrulaması")
    json_files = sorted(
        OUTPUTS_DIR.glob("rca_full_test*.json"),
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    )
    if json_files:
        latest = json_files[0]
        try:
            with open(latest, "r", encoding="utf-8") as f:
                rca_data = json.load(f)
            ok(f"  En son RCA JSON okundu: {latest.name}")
            info(f"    Dallar:     {len(rca_data.get('analysis_branches', []))}")
            info(f"    Kök neden:  {len(rca_data.get('final_root_causes', []))}")
            info(f"    Yöntem:     {rca_data.get('analysis_method', 'N/A')}")
        except Exception as e:
            fail(f"  JSON okuma hatası ({latest.name}): {e}")
            issues.append(str(e))
    else:
        warn("  Doğrulanacak RCA JSON dosyası yok (ADIM 5 atlandı mı?)")

    passed = len(issues) == 0
    tracker.record("ADIM 8 — Çıktı Doğrulama", passed,
                   "" if passed else f"{len(issues)} sorun")
    return passed


# ─────────────────────────────────────────────────────────────────────────────
# ADIM 9 — HIERARCHICAL DATA MUKAYESESİ
# ─────────────────────────────────────────────────────────────────────────────

def test_hierarchical_comparison(hierarchical_data: Dict, part3_data: Optional[Dict]):
    section("ADIM 9: Hierarchical JSON ↔ Üretilen RCA Karşılaştırması")

    if part3_data is None:
        warn("Part 3 verisi yok — karşılaştırma atlanıyor.")
        tracker.record("ADIM 9 — Karşılaştırma", False, "Part 3 mevcut değil")
        return False

    subsection("Dal sayısı karşılaştırması")
    expected = len(hierarchical_data.get("analysis_branches", []))
    actual   = len(part3_data.get("analysis_branches", []))
    info(f"  Beklenen dal sayısı (JSON): {expected}")
    info(f"  Üretilen dal sayısı (AI):   {actual}")
    if actual >= 1:
        ok(f"  En az 1 dal üretildi ✓")
    else:
        fail("  Hiç dal üretilmedi!")

    subsection("Kök neden kodu örtüşmesi")
    expected_codes = {rc.get("code") for rc in hierarchical_data.get("final_root_causes", [])}
    actual_codes   = {rc.get("code") for rc in part3_data.get("final_root_causes", [])}
    common         = expected_codes & actual_codes
    info(f"  JSON kodları:       {sorted(expected_codes)}")
    info(f"  AI üretilen kodlar: {sorted(actual_codes)}")
    info(f"  Ortak kodlar:       {sorted(common)}")

    if common:
        ok(f"  {len(common)} ortak kök neden kodu bulundu: {sorted(common)}")
    else:
        warn("  Ortak kök neden kodu yok (AI farklı sonuç vermiş olabilir — normal)")

    subsection("Kategori tipi karşılaştırması")
    expected_cats = {rc.get("category_type") for rc in hierarchical_data.get("final_root_causes", [])}
    actual_cats   = {rc.get("category_type") for rc in part3_data.get("final_root_causes", [])}
    info(f"  JSON kategorileri: {expected_cats}")
    info(f"  AI kategorileri:   {actual_cats}")
    if expected_cats & actual_cats:
        ok(f"  Kategori örtüşmesi var: {expected_cats & actual_cats}")
    else:
        warn("  Kategori örtüşmesi yok")

    tracker.record("ADIM 9 — Karşılaştırma", actual >= 1,
                   f"{actual} dal, {len(common)} ortak kod")
    return actual >= 1


# ─────────────────────────────────────────────────────────────────────────────
# ANA ÇALIŞTIRICISI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{BOLD}{CYAN}{'='*80}")
    print("  HSE RCA SİSTEMİ — TAM UÇTAN UCA TEST")
    print(f"  test_hierarchical_output.json bazlı kapsamlı sistem testi")
    print(f"  Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}{RESET}\n")

    # ── ADIM 1: Ortam kontrolü ─────────────────────────────────────────────
    env_ok = test_environment()
    if not env_ok:
        fail("Ortam hazır değil — test durduruluyor.")
        tracker.print_summary()
        return False

    # ── ADIM 2: JSON şema doğrulaması ─────────────────────────────────────
    hierarchical_data = test_json_schema()
    if hierarchical_data is None:
        fail("JSON geçersiz — test durduruluyor.")
        tracker.print_summary()
        return False

    # ── ADIM 3: Overview Agent ────────────────────────────────────────────
    part1 = test_overview_agent(hierarchical_data)

    # ── ADIM 4: Assessment Agent ──────────────────────────────────────────
    part2 = None
    if part1:
        part2 = test_assessment_agent(part1, hierarchical_data)

    # ── ADIM 5: Root Cause Agent V2 ───────────────────────────────────────
    part3 = None
    if part1 and part2:
        part3 = test_rootcause_agent(part1, part2, hierarchical_data)
    else:
        warn("ADIM 5 atlandı (Part 1 veya Part 2 başarısız)")
        tracker.record("ADIM 5 — RootCauseAgentV2", False, "Önceki adım başarısız")

    # ── ADIM 6: SkillBased DOCX Agent ─────────────────────────────────────
    docx_path = None
    if part1 and part2 and part3:
        docx_path = test_docx_agent(part1, part2, part3, hierarchical_data)
    else:
        warn("ADIM 6 atlandı (Part 1/2/3 tamamlanmadı)")
        tracker.record("ADIM 6 — SkillBasedDocxAgent", False, "Önceki adım başarısız")

    # ── ADIM 7: Orchestrator ──────────────────────────────────────────────
    orchestrator_result = test_orchestrator(hierarchical_data)

    # ── ADIM 8: Çıktı doğrulaması ─────────────────────────────────────────
    test_output_validation()

    # ── ADIM 9: Karşılaştırma ────────────────────────────────────────────
    test_hierarchical_comparison(hierarchical_data, part3)

    # ── ÖZET RAPOR ────────────────────────────────────────────────────────
    tracker.print_summary()

    passed, total = tracker.summary()

    # Sonraki adımlar
    if passed >= total * 0.7:
        print(f"\n{BOLD}📝 Üretilen Dosyalar:{RESET}")
        for f in sorted(OUTPUTS_DIR.glob("*full_test*"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
            info(f"  {f}")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
