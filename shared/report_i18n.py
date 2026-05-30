"""
P0.13 — Report shell labels (cover, TOC, sections, tables, toolbar).
Fallback: requested lang -> en -> [missing:key]
"""

from __future__ import annotations

from contextvars import ContextVar
from typing import Dict

_REPORT_LANG: ContextVar[str] = ContextVar("report_lang", default="tr")

SUPPORTED_LANGS = ("tr", "en", "de", "fr", "es", "ar")

# Shared label keys — values per language
_LABELS: Dict[str, Dict[str, str]] = {
    "tr": {
        "cover_title": "KÖK NEDEN ANALİZİ RAPORU",
        "cover_subtitle": "Profesyonel Araştırma ve Analiz Raporu",
        "cover_confidentiality": "GİZLİ - SADECE YETKİLİ PERSONELİN ERİŞİMİNE AÇIKTIR",
        "ref_no": "Referans No",
        "date": "Tarih",
        "location": "Lokasyon",
        "incident_type": "Olay Tipi",
        "incident_summary": "OLAY ÖZETİ",
        "nav_toc": "İçindekiler",
        "nav_toc_title": "İÇİNDEKİLER",
        "nav_cover": "Kapak Sayfası",
        "nav_executive_summary": "Yönetici Özeti",
        "nav_incident_details": "Olay Bilgileri",
        "nav_analysis_method": "Analiz Yöntemi",
        "nav_branches": "5-Why Dalları",
        "nav_contributing": "Katkıda Bulunan Faktörler",
        "nav_corrective": "Düzeltici Faaliyetler",
        "nav_lessons": "Çıkarılan Dersler",
        "nav_conclusion": "Sonuç",
        "nav_signatures": "İmzalar",
        "nav_photos": "Olay Fotoğrafları",
        "toolbar_edit_off": "Düzenleme Modu: KAPALI",
        "toolbar_edit_on": "Düzenleme Modu: AÇIK",
        "toolbar_save": "Kaydet",
        "toolbar_word": "Word İndir",
        "toolbar_html": "HTML İndir",
        "toolbar_reset": "Sıfırla",
        "section_executive_summary": "YÖNETİCİ ÖZETİ",
        "subsection_incident_summary": "Olay Özeti",
        "subsection_key_findings": "Temel Bulgular",
        "subsection_immediate_actions": "Acil Eylemler",
        "th_immediate_action": "Acil Eylem",
        "th_responsible": "Sorumlu",
        "th_status": "Durum",
        "section_incident_details": "OLAY BİLGİLERİ",
        "subsection_info_table": "Detaylı Bilgi Tablosu",
        "subsection_event_details": "Olay Detayları",
        "subsection_timeline": "Kronolojik Olay Akışı",
        "subsection_severity": "Aciliyet Seviyeleri",
        "event_summary_label": "Olay Özeti",
        "th_time": "Zaman",
        "th_event": "Olay",
        "severity_actual": "Gerçek Zarar",
        "severity_potential": "Potansiyel Zarar",
        "severity_investigation": "Soruşturma Seviyesi",
        "section_analysis_method": "ANALİZ YÖNTEMİ - 5 WHY",
        "subsection_five_why": "5-Why Tekniği",
        "subsection_code_system": "Kod Sistemi",
        "subsection_analysis_team": "Analiz Ekibi",
        "th_category": "Kategori",
        "th_description": "Açıklama",
        "th_name": "İsim",
        "th_role": "Rol",
        "subsection_branch_start": "Başlangıç Durumu ve Doğrudan Neden",
        "subsection_why_chain": "5-Why Analiz Zinciri",
        "subsection_why_table": "5-Why Analiz Tablosu",
        "subsection_root_cause": "Kök Neden",
        "subsection_org_factors": "Organizasyonel Faktörler",
        "subsection_factor_categories": "Faktör Kategorileri",
        "branch_critical_factor": "KRİTİK FAKTÖR",
        "section_final_root_causes": "NİHAİ KÖK NEDENLER",
        "section_meta_root_cause": "META KÖK NEDEN ANALİZİ",
        "subsection_systemic_weakness": "Sistemik Zayıflık",
        "section_systemic_factors": "DİĞER OLASI SİSTEMSEL FAKTÖRLER",
        "section_corrective_actions": "DÜZELTİCİ VE ÖNLEYİCİ FAALİYETLER",
        "section_lessons_learned": "ÇIKARILAN DERSLER",
        "section_conclusion": "SONUÇ VE ÖNERİLER",
        "subsection_general_assessment": "Genel Değerlendirme",
        "subsection_recommendations": "Öneriler",
        "section_signatures": "ONAY VE İMZA SAYFASI",
        "th_title": "Ünvan",
        "root_causes_title": "Kök Nedenler",
        "th_question": "Soru",
        "th_answer": "Cevap",
        "th_level": "Seviye",
        "th_priority": "Öncelik",
        "th_action": "Eylem",
        "th_deadline": "Termin",
        "th_lesson": "Ders",
        "th_application": "Uygulama",
        "default_incident_title": "Kaza Analizi",
        "th_date": "Tarih",
        "th_code": "Kod",
        "th_factor_type": "Faktör Türü",
        "th_impact_level": "Etki Seviyesi",
        "th_no": "No",
        "th_activity": "Faaliyet",
        "th_duration": "Süre",
        "th_kpi": "KPI",
        "lesson_what_to_do": "NE YAPILMALI",
        "lesson_long_term": "UZUN VADELİ ÇÖZÜMLER",
        "lesson_communication": "İLETİŞİM VE PAYLAŞIM",
        "lesson_training": "EĞİTİM VE FARKINDALIK",
        "subsection_short_term": "Kısa Vadeli Önlemler (1-2 Ay)",
        "subsection_long_term": "Uzun Vadeli İyileştirmeler (3-12 Ay)",
        "subsection_comparison": "Mevcut vs Hedef Karşılaştırması",
        "th_criterion": "Kriter",
        "th_current": "Mevcut Durum",
        "th_target": "Hedeflenen",
        "th_signature": "İmza / Tarih",
        "sig_role_prepared": "HAZIRLAYAN",
        "sig_role_reviewed": "İNCELEYEN",
        "sig_role_approved": "ONAYLAYAN",
        "ai_disclaimer": "Bu rapor yapay zeka ile hazırlanmıştır.\nBir uzman tarafından kontrol edilmesi önerilir.",
        "why_prefix": "NEDEN",
        "answer_prefix": "YANIT",
        "root_cause_prefix": "KÖK NEDEN",
        "why_number_col": "Neden #",
        "why_qa_col": "Soru ve Yanıt",
        "th_related_units": "İlgili Birimler",
        "impacts_from_cause": "Bu Nedenden Kaynaklanan Etkiler:",
        "html_edit_note": "Bu HTML raporu tamamen düzenlenebilir. Herhangi bir alana tıklayarak içeriği değiştirebilirsiniz. Değişiklikleriniz tarayıcınızın yerel belleğine otomatik olarak kaydedilir.",
        "notify_edit_on": "Düzenleme modu AÇIK - İstediğiniz alanı düzenleyebilirsiniz",
        "notify_edit_off": "Düzenleme modu KAPALI",
        "notify_saved": "Rapor başarıyla kaydedildi!",
        "notify_word_prep": "Word dosyası hazırlanıyor...",
        "notify_word_dl": "Word dosyası indiriliyor...",
        "notify_html_dl": "HTML dosyası indiriliyor...",
        "section_contributing_short": "SİSTEMSEL FAKTÖRLER",
    },
    "en": {
        "cover_title": "ROOT CAUSE ANALYSIS REPORT",
        "cover_subtitle": "Professional Investigation and Analysis Report",
        "cover_confidentiality": "CONFIDENTIAL - ACCESS LIMITED TO AUTHORIZED PERSONNEL ONLY",
        "ref_no": "Reference No",
        "date": "Date",
        "location": "Location",
        "incident_type": "Incident Type",
        "incident_summary": "INCIDENT SUMMARY",
        "nav_toc": "Contents",
        "nav_toc_title": "TABLE OF CONTENTS",
        "nav_cover": "Cover Page",
        "nav_executive_summary": "Executive Summary",
        "nav_incident_details": "Incident Details",
        "nav_analysis_method": "Analysis Method",
        "nav_branches": "5-Why Branches",
        "nav_contributing": "Contributing Factors",
        "nav_corrective": "Corrective Actions",
        "nav_lessons": "Lessons Learned",
        "nav_conclusion": "Conclusion",
        "nav_signatures": "Signatures",
        "nav_photos": "Incident Photos",
        "toolbar_edit_off": "Edit Mode: OFF",
        "toolbar_edit_on": "Edit Mode: ON",
        "toolbar_save": "Save",
        "toolbar_word": "Download Word",
        "toolbar_html": "Download HTML",
        "toolbar_reset": "Reset",
        "section_executive_summary": "EXECUTIVE SUMMARY",
        "subsection_incident_summary": "Incident Summary",
        "subsection_key_findings": "Key Findings",
        "subsection_immediate_actions": "Immediate Actions",
        "th_immediate_action": "Immediate Action",
        "th_responsible": "Responsible",
        "th_status": "Status",
        "section_incident_details": "INCIDENT DETAILS",
        "subsection_info_table": "Detailed Information Table",
        "subsection_event_details": "Incident Details",
        "subsection_timeline": "Chronological Incident Timeline",
        "subsection_severity": "Severity Levels",
        "event_summary_label": "Incident Summary",
        "th_time": "Time",
        "th_event": "Event",
        "severity_actual": "Actual Harm",
        "severity_potential": "Potential Harm",
        "severity_investigation": "Investigation Level",
        "section_analysis_method": "ANALYSIS METHOD - 5 WHY",
        "subsection_five_why": "5-Why Technique",
        "subsection_code_system": "Code System",
        "subsection_analysis_team": "Analysis Team",
        "th_category": "Category",
        "th_description": "Description",
        "th_name": "Name",
        "th_role": "Role",
        "subsection_branch_start": "Initial Condition and Direct Cause",
        "subsection_why_chain": "5-Why Analysis Chain",
        "subsection_why_table": "5-Why Analysis Table",
        "subsection_root_cause": "Root Cause",
        "subsection_org_factors": "Organizational Factors",
        "subsection_factor_categories": "Factor Categories",
        "branch_critical_factor": "CRITICAL FACTOR",
        "section_final_root_causes": "FINAL ROOT CAUSES",
        "section_meta_root_cause": "META ROOT CAUSE ANALYSIS",
        "subsection_systemic_weakness": "Systemic Weakness",
        "section_systemic_factors": "OTHER POSSIBLE SYSTEMIC FACTORS",
        "section_corrective_actions": "CORRECTIVE AND PREVENTIVE ACTIONS",
        "section_lessons_learned": "LESSONS LEARNED",
        "section_conclusion": "CONCLUSION AND RECOMMENDATIONS",
        "subsection_general_assessment": "General Assessment",
        "subsection_recommendations": "Recommendations",
        "section_signatures": "APPROVAL AND SIGNATURE PAGE",
        "th_title": "Title",
        "root_causes_title": "Root Causes",
        "th_question": "Question",
        "th_answer": "Answer",
        "th_level": "Level",
        "th_priority": "Priority",
        "th_action": "Action",
        "th_deadline": "Deadline",
        "th_lesson": "Lesson",
        "th_application": "Application",
        "default_incident_title": "Incident Analysis",
        "th_date": "Date",
        "th_code": "Code",
        "th_factor_type": "Factor Type",
        "th_impact_level": "Impact Level",
        "th_no": "No",
        "th_activity": "Activity",
        "th_duration": "Duration",
        "th_kpi": "KPI",
        "lesson_what_to_do": "WHAT TO DO",
        "lesson_long_term": "LONG-TERM SOLUTIONS",
        "lesson_communication": "COMMUNICATION AND SHARING",
        "lesson_training": "TRAINING AND AWARENESS",
        "subsection_short_term": "Short-Term Measures (1-2 Months)",
        "subsection_long_term": "Long-Term Improvements (3-12 Months)",
        "subsection_comparison": "Current vs Target Comparison",
        "th_criterion": "Criterion",
        "th_current": "Current State",
        "th_target": "Target",
        "th_signature": "Signature / Date",
        "sig_role_prepared": "PREPARED BY",
        "sig_role_reviewed": "REVIEWED BY",
        "sig_role_approved": "APPROVED BY",
        "ai_disclaimer": "This report was prepared with artificial intelligence.\nReview by a qualified expert is recommended.",
        "why_prefix": "WHY",
        "answer_prefix": "ANSWER",
        "root_cause_prefix": "ROOT CAUSE",
        "why_number_col": "Why #",
        "why_qa_col": "Question and Answer",
        "th_related_units": "Related Units",
        "impacts_from_cause": "Impacts Resulting from This Cause:",
        "html_edit_note": "This HTML report is fully editable. Click any field to change content. Changes are saved automatically in your browser's local storage.",
        "notify_edit_on": "Edit mode ON - You can edit any field",
        "notify_edit_off": "Edit mode OFF",
        "notify_saved": "Report saved successfully!",
        "notify_word_prep": "Preparing Word file...",
        "notify_word_dl": "Downloading Word file...",
        "notify_html_dl": "Downloading HTML file...",
        "section_contributing_short": "SYSTEMIC FACTORS",
    },
}


def set_report_lang(lang_code: str) -> None:
    code = (lang_code or "tr").strip().lower()
    if code not in SUPPORTED_LANGS:
        code = "en" if code != "tr" else "tr"
    _REPORT_LANG.set(code)


def get_report_lang() -> str:
    return _REPORT_LANG.get()


def report_label(lang_code: str, key: str) -> str:
    code = (lang_code or get_report_lang() or "tr").strip().lower()
    if code not in _LABELS:
        code = "en"
    bucket = _LABELS.get(code) or _LABELS["en"]
    if key in bucket:
        return bucket[key]
    en = _LABELS.get("en", {})
    if key in en:
        return en[key]
    return f"[missing:{key}]"


def shell_fallback_replacements(target_lang: str) -> Dict[str, str]:
    """Map Turkish shell strings to target language (for legacy HTML post-process)."""
    target = (target_lang or "tr").strip().lower()
    if target == "tr":
        return {}
    tr = _LABELS["tr"]
    tgt = _LABELS.get(target) or _LABELS["en"]
    pairs = {}
    for key in tr:
        if key in tgt and tr[key] != tgt[key]:
            pairs[tr[key]] = tgt[key]
    return pairs


def apply_shell_language(html: str, lang_code: str) -> str:
    if (lang_code or "tr").lower() == "tr":
        return html
    pairs = shell_fallback_replacements(lang_code)
    out = html
    for tr_text, target_text in sorted(pairs.items(), key=lambda x: -len(x[0])):
        out = out.replace(tr_text, target_text)
    return out
