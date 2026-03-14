#!/usr/bin/env python
"""Hızlı stream testi"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.overview_agent import OverviewAgent

incident = """
KAZA: Confined Space - Oksijen eksikliği
Kazazede: 3 kişi bayıldı
Neden: İzinsiz giriş, atmosfer testi yok
"""

print("=" * 80)
print("🔍 OVERVIEW AGENT - STREAM TEST")
print("=" * 80)
print()

agent = OverviewAgent()
print("Agent oluşturuldu, stream başlıyor...\n")

try:
    result = agent.run(incident, stream=True)
    print("\n" + "=" * 80)
    print("✅ STREAM TAMAMLANDI")
    print("=" * 80)
    print(f"\nSonuç: {result}")
except Exception as e:
    print(f"\n❌ HATA: {e}")
    import traceback
    traceback.print_exc()
