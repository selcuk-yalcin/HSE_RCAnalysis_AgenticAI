"""
OpenRouter model seçimi (agents geneli).

Ayrılmış varsayılanlar:
- Analiz (DSPy, kök neden, overview, değerlendirme, eylem planı vb.):
  `anthropic/claude-haiku-4.5` (ortam/preset ile değişir)
- Yalnızca rapor yazımı (DOCX/HTML: SkillBasedDocxAgent):
  `google/gemini-2.5-flash`

İstek başına analiz kalitesi (DeepWhy form):
- `quality` → güçlü model (varsayılan: Claude Sonnet)
- `economy` → hızlı / düşük maliyet (varsayılan: Gemini Flash)

Ortam önceliği (DSPy / analiz):
- Hepsini test için tek model: OPENROUTER_TEST_MODEL=...
- Analiz özel: OPENROUTER_DSPY_MODEL, OPENROUTER_DEFAULT_MODEL, OPENROUTER_MODEL_PRESET
- İstek içi tier yalnızca yukarıdakiler boşken veya tier geçerliyken resolve_openrouter_dspy_model tarafından uygulanır

DSPy çıktı tavanı: OPENROUTER_DSPY_MAX_TOKENS (varsayılan 32000)
"""

from __future__ import annotations

import contextvars
import os
from contextlib import contextmanager

# --- Analiz / genel ajanlar (DSPy ve chat) ---
_DEFAULT_ANALYSIS_MODEL = "anthropic/claude-haiku-4.5"
# --- Rapor üretimi (yalnızca DOCX/HTML) ---
_DEFAULT_REPORT_MODEL = "google/gemini-2.5-flash"

_MODEL_PRESETS = {
    "flash": "google/gemini-2.5-flash",
    "gemini_flash": "google/gemini-2.5-flash",
    "gemini-2.5-flash": "google/gemini-2.5-flash",
    "sonnet": "anthropic/claude-sonnet-4.5",
    "claude_sonnet": "anthropic/claude-sonnet-4.5",
    "claude-sonnet-4.5": "anthropic/claude-sonnet-4.5",
    "haiku": "anthropic/claude-haiku-4.5",
    "claude_haiku": "anthropic/claude-haiku-4.5",
    "claude-haiku-4.5": "anthropic/claude-haiku-4.5",
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


# Tek istek / tek analyze çağrısı için: "quality" | "economy" (boş = env varsayılanı)
_request_analysis_tier: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_analysis_tier",
    default=None,
)


def _env(name: str) -> str:
    return (os.getenv(name) or "").strip()


@contextmanager
def analysis_tier_context(tier: str):
    """Geçici analiz model katmanı (DSPy resolve_openrouter_dspy_model ile okunur)."""
    t = (tier or "").strip().lower()
    if t not in ("quality", "economy"):
        yield
        return
    token = _request_analysis_tier.set(t)
    try:
        yield
    finally:
        _request_analysis_tier.reset(token)


def _tier_to_model_slug(tier: str) -> str | None:
    if tier == "quality":
        return _MODEL_PRESETS.get("sonnet") or _DEFAULT_ANALYSIS_MODEL
    if tier == "economy":
        return _MODEL_PRESETS.get("flash") or _DEFAULT_ANALYSIS_MODEL
    return None


def _resolve_default_analysis_model() -> str:
    explicit = (_env("OPENROUTER_DEFAULT_MODEL") or "").strip()
    if explicit:
        return explicit
    preset = (_env("OPENROUTER_MODEL_PRESET") or "").strip().lower()
    if preset:
        return _MODEL_PRESETS.get(preset, _DEFAULT_ANALYSIS_MODEL)
    return _DEFAULT_ANALYSIS_MODEL


def resolve_openrouter_chat_model() -> str:
    """Genel chat: TEST > analiz default/preset > kod varsayılanı."""
    return _env("OPENROUTER_TEST_MODEL") or _resolve_default_analysis_model()


OPENROUTER_DEFAULT_CHAT_MODEL = resolve_openrouter_chat_model()
OPENROUTER_DOCX_DEFAULT_MODEL = (_env("OPENROUTER_DOCX_DEFAULT_MODEL") or "").strip() or _DEFAULT_REPORT_MODEL


def resolve_openrouter_dspy_model() -> str:
    """DSPy: TEST > OPENROUTER_DSPY_MODEL > istek-tier > OPENROUTER_DEFAULT_CHAT_MODEL."""
    test = _env("OPENROUTER_TEST_MODEL")
    if test:
        return test
    dspy = _env("OPENROUTER_DSPY_MODEL")
    if dspy:
        return dspy
    tier_raw = _request_analysis_tier.get()
    tier = (tier_raw or "").strip().lower()
    if tier:
        mapped = _tier_to_model_slug(tier)
        if mapped:
            return mapped
    return OPENROUTER_DEFAULT_CHAT_MODEL


def resolve_openrouter_docx_model() -> str:
    """Rapor (DOCX/HTML): TEST > OPENROUTER_DOCX_MODEL > flash (analizden bağımsız)."""
    return _env("OPENROUTER_TEST_MODEL") or _env("OPENROUTER_DOCX_MODEL") or OPENROUTER_DOCX_DEFAULT_MODEL
