"""
OpenRouter üzerinden kullanılan varsayılan sohbet modeli (agents geneli).

Tek model (DeepSeek V3.2 Speciale): RCA, DSPy, DOCX/HTML ve diğer agent çağrıları.
Override: OPENROUTER_DSPY_MODEL (V3.1), OPENROUTER_DOCX_MODEL (DOCX/HTML).
Genel varsayılanı değiştirmek için bu dosyadaki _DEFAULT değerini güncelleyin.
"""

_DEFAULT = "google/gemini-2.5-flash"

OPENROUTER_DEFAULT_CHAT_MODEL = _DEFAULT
OPENROUTER_DOCX_DEFAULT_MODEL = _DEFAULT
