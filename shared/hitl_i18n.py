"""
P0.12 — HITL question shell labels, drift checks, safe fallbacks.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

SUPPORTED_HITL_LANGS = ("tr", "en")

_TR_CHARS = set("çğıöşüÇĞİÖŞÜ")

_UI: Dict[str, Dict[str, str]] = {
    "tr": {
        "yes_no_hint": "Evet, Hayır veya Bilinmiyor seçin.",
        "free_text_hint": "Kısa ve somut bilgi yazın (Enter ile gönderin).",
        "choice_hint": "Listeden seçin; gerekirse birden fazla seçim yapılabilir.",
        "choice_other_hint": "Diğer seçeneği işaretlediyseniz kısa açıklama yazın.",
    },
    "en": {
        "yes_no_hint": "Choose Yes, No, or Unknown.",
        "free_text_hint": "Enter a short, concrete answer (press Enter to submit).",
        "choice_hint": "Select from the list; multiple selections may apply.",
        "choice_other_hint": "If you chose Other, add a brief explanation.",
    },
}

_SAFE_FALLBACK: Dict[str, Dict[str, str]] = {
    "tr": {
        "disambiguation": "Bu tehlike için risk değerlendirmesi veya kontrol önlemi olay öncesinde uygulanıyor muydu?",
        "taxonomy_gap": "Bu olayla ilgili prosedür, eğitim veya saha uygulaması hakkında somut bir kanıt paylaşabilir misiniz?",
        "why_probe": "Bu why seviyesinde katkıda bulunan somut bir iş yeri veya organizasyonel koşul nedir?",
        "why_probe_llm": "Kök neden analizini netleştirmek için olaya özgü bir kanıt veya ayrıntı ekleyebilir misiniz?",
        "generic": "Kök neden analizini netleştirmek için olaya özgü kısa bir ayrıntı paylaşın.",
    },
    "en": {
        "disambiguation": "Was a risk assessment or control measure in place for this hazard before the incident?",
        "taxonomy_gap": "What concrete evidence can you share about procedures, training, or field practice related to this incident?",
        "why_probe": "What specific workplace or organizational condition may have contributed at this why level?",
        "why_probe_llm": "Can you add incident-specific evidence or detail to clarify the root cause analysis?",
        "generic": "Please share one incident-specific detail to clarify the root cause analysis.",
    },
}


def normalize_hitl_lang(code: Optional[str]) -> str:
    c = (code or "tr").strip().lower()
    if c.startswith("tr"):
        return "tr"
    if c.startswith("en"):
        return "en"
    return "en"


def has_turkish_chars(text: str) -> bool:
    return any(ch in _TR_CHARS for ch in (text or ""))


def hitl_ui_label(lang: str, key: str) -> str:
    bucket = _UI.get(normalize_hitl_lang(lang)) or _UI["en"]
    return bucket.get(key) or _UI["en"].get(key, key)


def response_guidance(response_mode: str, lang: str) -> str:
    mode = (response_mode or "").strip().lower()
    if mode == "free_text":
        return hitl_ui_label(lang, "free_text_hint")
    if mode == "choice":
        return hitl_ui_label(lang, "choice_hint")
    return hitl_ui_label(lang, "yes_no_hint")


def safe_fallback_question(lang: str, source: str = "generic") -> str:
    code = normalize_hitl_lang(lang)
    bucket = _SAFE_FALLBACK.get(code) or _SAFE_FALLBACK["en"]
    src = (source or "generic").strip().lower()
    if src in bucket:
        return bucket[src]
    for key in ("why_probe_llm", "why_probe", "disambiguation", "taxonomy_gap", "generic"):
        if key in src and key in bucket:
            return bucket[key]
    return bucket.get("generic", "")


def pick_choice_options(q: dict, lang: str) -> Tuple[List[str], List[str]]:
    tr_opts = list(q.get("choice_options") or q.get("options") or [])
    en_opts = list(q.get("choice_options_en") or q.get("options_en") or [])
    if len(en_opts) != len(tr_opts) or not en_opts:
        en_opts = tr_opts[:]
    code = normalize_hitl_lang(lang)
    if code == "en" and en_opts:
        return en_opts, en_opts
    return tr_opts, en_opts


def display_question_text(q: dict, lang: str) -> str:
    code = normalize_hitl_lang(lang)
    tr = str(q.get("question_tr") or q.get("soru") or "").strip()
    en = str(q.get("question_en") or q.get("soru_en") or "").strip()
    if code == "en":
        return en or tr
    return tr or en


def question_batch_has_language_drift(questions: List[dict], lang: str) -> bool:
    code = normalize_hitl_lang(lang)
    for q in questions or []:
        text = display_question_text(q, code)
        if not text:
            continue
        if code == "en" and has_turkish_chars(text):
            return True
        if code == "tr" and not has_turkish_chars(text):
            low = text.lower()
            if re.search(r"\b(was|were|what|which|when|where|why|how|please|describe)\b", low):
                return True
    return False


def shape_bilingual_question_fields(
    soru: str,
    soru_en: str,
    lang: str,
    *,
    source: str = "generic",
) -> Tuple[str, str]:
    """Return (question_tr, question_en) for API payload."""
    tr = (soru or "").strip()
    en = (soru_en or "").strip()
    target = normalize_hitl_lang(lang)

    if target == "en":
        if not en or has_turkish_chars(en):
            if tr and not has_turkish_chars(tr):
                en = tr
            else:
                en = ensure_hitl_english_text(tr, source=source)
        if not tr:
            tr = soru or en
        return tr, en

    if not tr:
        tr = en or safe_fallback_question("tr", source)
    if not en or has_turkish_chars(en):
        en = en if en and not has_turkish_chars(en) else ""
    return tr, en or tr


_TRANSLATION_CACHE: Dict[str, str] = {}


def ensure_hitl_english_text(text: str, source: str = "generic") -> str:
    """Translate TR HITL shell text to EN with cache + LLM retry + safe fallback."""
    src = (text or "").strip()
    if not src:
        return safe_fallback_question("en", source)
    if not has_turkish_chars(src):
        return src
    cache_key = src[:500]
    if cache_key in _TRANSLATION_CACHE:
        return _TRANSLATION_CACHE[cache_key]

    translated = _llm_translate_to_english([src], retries=1)
    out = (translated[0] if translated else "").strip()
    if not out or has_turkish_chars(out):
        out = safe_fallback_question("en", source)
    _TRANSLATION_CACHE[cache_key] = out
    return out


def _llm_translate_to_english(texts: List[str], retries: int = 1) -> List[str]:
    import json
    import os

    api_key = (os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY") or "").strip()
    if not api_key:
        return []
    if (os.getenv("HITL_USE_LLM") or "1").strip().lower() not in ("1", "true", "yes", "on"):
        return []
    try:
        from openai import OpenAI
        from agents.model_constants import resolve_openrouter_chat_model

        model = resolve_openrouter_chat_model()
        if not model.startswith("openrouter/"):
            model = f"openrouter/{model}"
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key, timeout=10.0)
        payload = json.dumps(texts, ensure_ascii=False)
        prompt = (
            "Translate each Turkish HSE investigation question to English. "
            "Keep technical HSE terms accurate. Return JSON array of strings only, same order.\n"
            f"{payload}"
        )
        for _ in range(max(1, retries + 1)):
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=800,
            )
            content = (resp.choices[0].message.content or "").strip()
            if content.startswith("```"):
                content = re.sub(r"^```(?:json)?\s*", "", content)
                content = re.sub(r"\s*```$", "", content)
            try:
                data = json.loads(content)
                if isinstance(data, list) and data:
                    return [str(x).strip() for x in data]
            except Exception:
                continue
    except Exception:
        return []
    return []
