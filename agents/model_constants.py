"""
OpenRouter model seçimi (agents geneli).

Ayrılmış varsayılanlar:
- Analiz (DSPy, kök neden, overview, değerlendirme, eylem planı vb.):
  `qwen/qwen3.6-flash`
- Yalnızca rapor yazımı (DOCX/HTML: SkillBasedDocxAgent):
  `google/gemini-2.5-flash`

Ortam önceliği (özet):
- Hepsini test için tek model: OPENROUTER_TEST_MODEL=...
- Analiz özel: OPENROUTER_DEFAULT_MODEL, OPENROUTER_MODEL_PRESET, OPENROUTER_DSPY_MODEL
- DSPy çıktı tavanı (5-Why kesilmesin): OPENROUTER_DSPY_MAX_TOKENS (varsayılan 32000, `rootcause_agent_v3_1`)
- Sadece rapor özel: OPENROUTER_DOCX_MODEL (ve isteğe OPENROUTER_DOCX_DEFAULT_MODEL ile
  modüldeki rapor varsayılanını geçersizleştirmek; tipik kullanım OPENROUTER_DOCX_MODEL)
"""

import os

# --- Analiz / genel ajanlar (DSPy ve chat) ---
_DEFAULT_ANALYSIS_MODEL = "qwen/qwen3.6-flash"
# --- Rapor üretimi (yalnızca DOCX/HTML) ---
_DEFAULT_REPORT_MODEL = "google/gemini-2.5-flash"

_MODEL_PRESETS = {
    "flash": "google/gemini-2.5-flash",
    "gemini_flash": "google/gemini-2.5-flash",
    "gemini-2.5-flash": "google/gemini-2.5-flash",
    "sonnet": "anthropic/claude-sonnet-4.5",
    "claude_sonnet": "anthropic/claude-sonnet-4.5",
    "deepseek": "deepseek/deepseek-v4-pro",
    "v4pro": "deepseek/deepseek-v4-pro",
    "qwen": "qwen/qwen3.6-flash",
    "qwen3": "qwen/qwen3.6-flash",
    "qwen-thinking": "qwen/qwen3.6-flash",
}


def _resolve_default_analysis_model() -> str:
    # 1) explicit model override (analiz)
    explicit = (os.getenv("OPENROUTER_DEFAULT_MODEL") or "").strip()
    if explicit:
        return explicit

    # 2) preset-based override
    preset = (os.getenv("OPENROUTER_MODEL_PRESET") or "").strip().lower()
    if preset:
        return _MODEL_PRESETS.get(preset, _DEFAULT_ANALYSIS_MODEL)

    # 3) code default
    return _DEFAULT_ANALYSIS_MODEL


def _env(name: str) -> str:
    return (os.getenv(name) or "").strip()


def resolve_openrouter_chat_model() -> str:
    """Genel chat: TEST > analiz default/preset > Qwen (varsayılan)."""
    return _env("OPENROUTER_TEST_MODEL") or _resolve_default_analysis_model()


OPENROUTER_DEFAULT_CHAT_MODEL = resolve_openrouter_chat_model()
OPENROUTER_DOCX_DEFAULT_MODEL = (os.getenv("OPENROUTER_DOCX_DEFAULT_MODEL") or "").strip() or _DEFAULT_REPORT_MODEL


def resolve_openrouter_dspy_model() -> str:
    """DSPy: TEST > OPENROUTER_DSPY_MODEL > analiz genel varsayılanı (Qwen)."""
    return (
        _env("OPENROUTER_TEST_MODEL")
        or _env("OPENROUTER_DSPY_MODEL")
        or OPENROUTER_DEFAULT_CHAT_MODEL
    )


def resolve_openrouter_docx_model() -> str:
    """Rapor (DOCX/HTML): TEST > OPENROUTER_DOCX_MODEL > flash (varsayılan, analizden bağımsız)."""
    return (
        _env("OPENROUTER_TEST_MODEL")
        or _env("OPENROUTER_DOCX_MODEL")
        or OPENROUTER_DOCX_DEFAULT_MODEL
    )
