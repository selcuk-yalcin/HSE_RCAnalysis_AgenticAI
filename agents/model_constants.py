"""
OpenRouter varsayilan model secimi (agents geneli).

Kullanim:
- Varsayilan (kod): anthropic/claude-sonnet-4.5
- Preset ile hizli gecis: OPENROUTER_MODEL_PRESET=gemini_flash
- Tam model override: OPENROUTER_DEFAULT_MODEL=google/gemini-2.5-flash

Not:
- DSPy icin OPENROUTER_DSPY_MODEL,
- DOCX/HTML icin OPENROUTER_DOCX_MODEL
degiskenleri halen en yuksek oncelikli override olarak calisir.

Tum sistemi test amacli tek degiskenle zorlamak icin:
- OPENROUTER_TEST_MODEL=google/gemini-2.5-flash
"""

import os

_DEFAULT_MODEL = "anthropic/claude-sonnet-4.5"
_MODEL_PRESETS = {
    "sonnet": "anthropic/claude-sonnet-4.5",
    "claude_sonnet": "anthropic/claude-sonnet-4.5",
    "gemini_flash": "google/gemini-2.5-flash",
    "gemini-2.5-flash": "google/gemini-2.5-flash",
}


def _resolve_default_model() -> str:
    # 1) explicit model override
    explicit = (os.getenv("OPENROUTER_DEFAULT_MODEL") or "").strip()
    if explicit:
        return explicit

    # 2) preset-based override
    preset = (os.getenv("OPENROUTER_MODEL_PRESET") or "").strip().lower()
    if preset:
        return _MODEL_PRESETS.get(preset, _DEFAULT_MODEL)

    # 3) code default
    return _DEFAULT_MODEL


def _env(name: str) -> str:
    return (os.getenv(name) or "").strip()


def resolve_openrouter_chat_model() -> str:
    """Genel chat modeli: TEST > DEFAULT_MODEL/preset > kod default."""
    return _env("OPENROUTER_TEST_MODEL") or _resolve_default_model()


OPENROUTER_DEFAULT_CHAT_MODEL = resolve_openrouter_chat_model()
OPENROUTER_DOCX_DEFAULT_MODEL = OPENROUTER_DEFAULT_CHAT_MODEL


def resolve_openrouter_dspy_model() -> str:
    """DSPy modeli: TEST > DSPY_MODEL > genel varsayilan."""
    return (
        _env("OPENROUTER_TEST_MODEL")
        or _env("OPENROUTER_DSPY_MODEL")
        or OPENROUTER_DEFAULT_CHAT_MODEL
    )


def resolve_openrouter_docx_model() -> str:
    """DOCX modeli: TEST > DOCX_MODEL > genel varsayilan."""
    return (
        _env("OPENROUTER_TEST_MODEL")
        or _env("OPENROUTER_DOCX_MODEL")
        or OPENROUTER_DOCX_DEFAULT_MODEL
    )
