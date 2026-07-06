"""
OpenRouter model seçimi (agents geneli).

Tek kaynak: bu dosya. Ortam değişkenleri yalnızca override içindir.

Sabit ayrım (üretim varsayılanı):
- Analiz (HITL, overview, assessment, aksiyon planı, chat):
  `anthropic/claude-haiku-4.5`
- RCA / DSPy (V3.2 varsayılan kök neden motoru — RootCauseAgentV3_2 → V3.1 DSPy LM):
  `anthropic/claude-haiku-4.5` (OPENROUTER_DSPY_MODEL ile override)
- Rapor (DOCX/HTML — SkillBasedDocxAgentV32 / SkillBasedDocxAgent):
  `google/gemini-2.5-flash`

RCA motoru (agents/v3_2): ROOTCAUSE_AGENT_VERSION=3.2 (varsayılan).
Model seçimi yine resolve_openrouter_dspy_model() üzerinden — v3_2 ayrı model tanımlamaz.

Ortam önceliği (HITL, overview, assessment, chat):
- Hepsini test için tek model: OPENROUTER_TEST_MODEL=...
- Genel analiz override: OPENROUTER_DEFAULT_MODEL
- OPENROUTER_MODEL_PRESET

RCA / DSPy (V3.2 + V3.1):
- OPENROUTER_DSPY_MODEL
- OPENROUTER_TEST_MODEL (tüm hattı tek modele çeker)

Rapor:
- OPENROUTER_DOCX_MODEL veya varsayılan Flash

DSPy çıktı tavanı: OPENROUTER_DSPY_MAX_TOKENS (varsayılan 32000)
"""

from __future__ import annotations

import contextvars
import os
from contextlib import contextmanager

_HAIKU_MODEL = "anthropic/claude-haiku-4.5"
_FLASH_MODEL = "google/gemini-2.5-flash"
_SONNET_MODEL = "anthropic/claude-sonnet-5"

_DEFAULT_ANALYSIS_MODEL = _HAIKU_MODEL
_DEFAULT_DSPY_MODEL = _HAIKU_MODEL
_DEFAULT_REPORT_MODEL = _FLASH_MODEL

_MODEL_PRESETS = {
    "flash": _FLASH_MODEL,
    "gemini_flash": _FLASH_MODEL,
    "gemini-2.5-flash": _FLASH_MODEL,
    "sonnet": "anthropic/claude-sonnet-4.5",
    "claude_sonnet": "anthropic/claude-sonnet-4.5",
    "claude-sonnet-4.5": "anthropic/claude-sonnet-4.5",
    "sonnet5": _SONNET_MODEL,
    "claude_sonnet_5": _SONNET_MODEL,
    "claude-sonnet-5": _SONNET_MODEL,
    "haiku": _HAIKU_MODEL,
    "claude_haiku": _HAIKU_MODEL,
    "claude-haiku-4.5": _HAIKU_MODEL,
    "deepseek": "deepseek/deepseek-v4-pro",
    "v4pro": "deepseek/deepseek-v4-pro",
    "qwen": "qwen/qwen3.6-flash",
    "qwen3": "qwen/qwen3.6-flash",
    "qwen-thinking": "qwen/qwen3.6-flash",
    "qwen-vl-thinking": "qwen/qwen3-vl-30b-a3b-thinking",
    "qwen3-vl": "qwen/qwen3-vl-30b-a3b-thinking",
    "maestro": "arcee-ai/maestro-reasoning",
    "maestro-reasoning": "arcee-ai/maestro-reasoning",
    "gpt-5.4-mini": "openai/gpt-5.4-mini",
    "gpt54mini": "openai/gpt-5.4-mini",
    "kimi": "moonshotai/kimi-k2-thinking",
    "kimi-k2-thinking": "moonshotai/kimi-k2-thinking",
}

_request_analysis_tier: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_analysis_tier",
    default=None,
)


def _env(name: str) -> str:
    return (os.getenv(name) or "").strip()


@contextmanager
def analysis_tier_context(tier: str):
    """İstek bağlamı (şimdilik analiz modeli Haiku; tier ileride profil için)."""
    t = (tier or "").strip().lower()
    if t not in ("quality", "economy"):
        yield
        return
    token = _request_analysis_tier.set(t)
    try:
        yield
    finally:
        _request_analysis_tier.reset(token)


def _resolve_from_preset_or_default() -> str:
    preset = (_env("OPENROUTER_MODEL_PRESET") or "").strip().lower()
    if preset and preset in _MODEL_PRESETS:
        # Preset flash ise bile analizde Haiku kullan (flash yalnızca rapor)
        slug = _MODEL_PRESETS[preset]
        if slug == _FLASH_MODEL:
            return _HAIKU_MODEL
        return slug
    return _HAIKU_MODEL


def _resolve_analysis_model() -> str:
    """HITL, overview, assessment, aksiyon planı — varsayılan Haiku."""
    test = _env("OPENROUTER_TEST_MODEL")
    if test:
        return test
    explicit = _env("OPENROUTER_DEFAULT_MODEL")
    if explicit:
        return explicit
    return _resolve_from_preset_or_default()


def _resolve_dspy_model() -> str:
    """RCA / DSPy (V3.2 + V3.1) — OPENROUTER_DSPY_MODEL veya varsayılan Haiku."""
    test = _env("OPENROUTER_TEST_MODEL")
    if test:
        return test
    explicit = _env("OPENROUTER_DSPY_MODEL")
    if explicit:
        return explicit
    return _DEFAULT_DSPY_MODEL


def resolve_openrouter_chat_model() -> str:
    return _resolve_analysis_model()


OPENROUTER_DEFAULT_CHAT_MODEL = resolve_openrouter_chat_model()
OPENROUTER_DOCX_DEFAULT_MODEL = (_env("OPENROUTER_DOCX_DEFAULT_MODEL") or "").strip() or _DEFAULT_REPORT_MODEL


def resolve_openrouter_dspy_model() -> str:
    """DSPy kök neden — OPENROUTER_DSPY_MODEL veya varsayılan Haiku."""
    return _resolve_dspy_model()


def resolve_openrouter_docx_model() -> str:
    """Rapor (DOCX/HTML): TEST > OPENROUTER_DOCX_MODEL > Flash."""
    return _env("OPENROUTER_TEST_MODEL") or _env("OPENROUTER_DOCX_MODEL") or _DEFAULT_REPORT_MODEL


def resolve_models_for_health() -> dict:
    """Health / debug — aktif model slug'ları (V3.2 RCA dahil)."""
    try:
        from agents.root_cause_factory import resolve_root_cause_agent_version
        rca_version = resolve_root_cause_agent_version()
    except Exception:  # noqa: BLE001
        rca_version = "unknown"
    return {
        "rca_agent_version": rca_version,
        "chat": resolve_openrouter_chat_model(),
        "dspy_rca": resolve_openrouter_dspy_model(),
        "docx_report": resolve_openrouter_docx_model(),
        "defaults": {
            "analysis": _DEFAULT_ANALYSIS_MODEL,
            "dspy": _DEFAULT_DSPY_MODEL,
            "report": _DEFAULT_REPORT_MODEL,
        },
    }
