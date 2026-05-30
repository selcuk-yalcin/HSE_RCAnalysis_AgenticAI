"""
P0.9 — Shared report layout / branding configuration for DOCX + HTML renderers.
"""

from __future__ import annotations

import os
from copy import deepcopy
from typing import Any, Dict, List, Optional

# Ordered section ids used by both DOCX and HTML builders.
REPORT_SECTIONS: List[Dict[str, str]] = [
    {"id": "cover", "label_tr": "Kapak", "label_en": "Cover"},
    {"id": "executive_summary", "label_tr": "Yönetici Özeti", "label_en": "Executive Summary"},
    {"id": "incident_details", "label_tr": "Olay Detayları", "label_en": "Incident Details"},
    {"id": "analysis_method", "label_tr": "Analiz Yöntemi", "label_en": "Analysis Method"},
    {"id": "branches", "label_tr": "Kök Neden Dalları", "label_en": "Root Cause Branches"},
    {"id": "root_causes", "label_tr": "Kök Nedenler", "label_en": "Root Causes"},
    {"id": "corrective_actions", "label_tr": "Düzeltici Faaliyetler", "label_en": "Corrective Actions"},
    {"id": "lessons_learned", "label_tr": "Çıkarılan Dersler", "label_en": "Lessons Learned"},
    {"id": "conclusion", "label_tr": "Sonuç", "label_en": "Conclusion"},
]

DEFAULT_LAYOUT: Dict[str, Any] = {
    "cover_template": "standard",
    "show_technical_codes": False,
    "watermark_mode": "final",  # none | draft | final
    "logo_url": "",
    "sections": [s["id"] for s in REPORT_SECTIONS],
}

COVER_TEMPLATES: List[Dict[str, Any]] = [
    {
        "id": "standard",
        "name_tr": "Standart",
        "name_en": "Standard",
        "description_tr": "Kurumsal mavi kapak, klasik HSE rapor düzeni",
        "description_en": "Corporate blue cover, classic HSE layout",
        "accent": "#2563eb",
    },
    {
        "id": "formal",
        "name_tr": "Resmi",
        "name_en": "Formal",
        "description_tr": "Koyu lacivert kapak, denetim ve resmi sunumlar için",
        "description_en": "Dark navy cover for audit and formal submissions",
        "accent": "#1e293b",
    },
    {
        "id": "executive",
        "name_tr": "Yönetici Özeti",
        "name_en": "Executive",
        "description_tr": "Sade üst bant, yönetim kuruluna yönelik özet vurgusu",
        "description_en": "Clean header band focused on executive summary",
        "accent": "#b45309",
    },
    {
        "id": "minimal",
        "name_tr": "Minimal",
        "name_en": "Minimal",
        "description_tr": "Açık zemin, az süsleme; müşteri paylaşımı için",
        "description_en": "Light layout with minimal decoration for client sharing",
        "accent": "#64748b",
    },
]

WATERMARK_OPTIONS: List[Dict[str, Any]] = [
    {"id": "none", "name_tr": "Filigran yok", "name_en": "No watermark"},
    {"id": "draft", "name_tr": "Taslak (DRAFT)", "name_en": "Draft (DRAFT)"},
    {"id": "final", "name_tr": "Kesin (FINAL)", "name_en": "Final (FINAL)"},
]

VALID_COVER_IDS = {t["id"] for t in COVER_TEMPLATES}


def _env_bool(name: str, default: bool = False) -> bool:
    raw = (os.getenv(name) or "").strip().lower()
    if not raw:
        return default
    return raw in ("1", "true", "yes", "on")


def tenant_default_layout(tenant_id: str | None = None) -> Dict[str, Any]:
    """Env-based tenant defaults until per-tenant Mongo config exists."""
    _ = tenant_id
    layout = deepcopy(DEFAULT_LAYOUT)
    layout["show_technical_codes"] = _env_bool("REPORT_SHOW_TECHNICAL_CODES", False)
    layout["watermark_mode"] = (os.getenv("REPORT_WATERMARK_MODE") or "final").strip().lower()
    layout["logo_url"] = (os.getenv("REPORT_TENANT_LOGO_URL") or "").strip()
    cover = (os.getenv("REPORT_COVER_TEMPLATE") or "standard").strip().lower()
    if cover:
        layout["cover_template"] = cover
    return layout


def resolve_report_layout(
    investigation_data: Optional[Dict[str, Any]] = None,
    *,
    tenant_id: str | None = None,
    override: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Merge tenant defaults with incident snapshot and explicit API override."""
    layout = tenant_default_layout(tenant_id)
    inv = investigation_data if isinstance(investigation_data, dict) else {}
    incident_layout = inv.get("report_layout")
    if isinstance(incident_layout, dict):
        layout.update({k: v for k, v in incident_layout.items() if v is not None})
    snap = inv.get("report_layout_snapshot")
    if isinstance(snap, dict):
        layout.update({k: v for k, v in snap.items() if v is not None})
    if isinstance(override, dict):
        layout.update({k: v for k, v in override.items() if v is not None})
    wm = str(layout.get("watermark_mode") or "final").lower()
    if wm not in ("none", "draft", "final"):
        layout["watermark_mode"] = "final"
    sections = layout.get("sections")
    if not isinstance(sections, list) or not sections:
        layout["sections"] = [s["id"] for s in REPORT_SECTIONS]
    return layout


def section_label(section_id: str, lang_code: str = "tr") -> str:
    code = (lang_code or "tr").lower()
    for row in REPORT_SECTIONS:
        if row["id"] == section_id:
            return row["label_en"] if code.startswith("en") else row["label_tr"]
    return section_id


def list_layout_catalog(lang_code: str = "tr") -> Dict[str, Any]:
    """UI catalog for report template picker (P0.9)."""
    code = (lang_code or "tr").lower()
    use_en = code.startswith("en")

    def _label(row: Dict[str, Any]) -> str:
        return (row.get("name_en") if use_en else row.get("name_tr")) or row.get("id", "")

    def _desc(row: Dict[str, Any]) -> str:
        return (row.get("description_en") if use_en else row.get("description_tr")) or ""

    return {
        "default_layout": tenant_default_layout(),
        "cover_templates": [
            {
                "id": t["id"],
                "name": _label(t),
                "description": _desc(t),
                "accent": t.get("accent") or "#2563eb",
            }
            for t in COVER_TEMPLATES
        ],
        "watermark_options": [
            {"id": w["id"], "name": _label(w)} for w in WATERMARK_OPTIONS
        ],
        "sections": [
            {
                "id": s["id"],
                "name": _label(s),
                "default_enabled": True,
            }
            for s in REPORT_SECTIONS
        ],
    }


def normalize_layout_patch(patch: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate user-selected layout fields from API/UI."""
    if not isinstance(patch, dict):
        return {}
    out: Dict[str, Any] = {}
    cover = str(patch.get("cover_template") or "").strip().lower()
    if cover in VALID_COVER_IDS:
        out["cover_template"] = cover
    if "show_technical_codes" in patch:
        out["show_technical_codes"] = bool(patch.get("show_technical_codes"))
    wm = str(patch.get("watermark_mode") or "").strip().lower()
    if wm in ("none", "draft", "final"):
        out["watermark_mode"] = wm
    logo = patch.get("logo_url")
    if isinstance(logo, str):
        out["logo_url"] = logo.strip()[:2048]
    sections = patch.get("sections")
    if isinstance(sections, list) and sections:
        valid_ids = {s["id"] for s in REPORT_SECTIONS}
        filtered = [str(s) for s in sections if str(s) in valid_ids]
        if filtered:
            out["sections"] = filtered
    return out
