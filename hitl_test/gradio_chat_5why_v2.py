"""
HSG245 5-Why Chatbot v2 — geriye dönük başlatıcı.

Asıl uygulama: agents/gradio_chat_5why_v2.py
Çalıştırma: python hitl_test/gradio_chat_5why_v2.py
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]


def main() -> None:
    sys.path.insert(0, str(_REPO))
    runpy.run_path(str(_REPO / "agents" / "gradio_chat_5why_v2.py"), run_name="__main__")


if __name__ == "__main__":
    main()
