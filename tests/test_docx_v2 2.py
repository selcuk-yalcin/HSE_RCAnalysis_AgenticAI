"""Test script: SkillBasedDocxAgent V2 (OpenRouter + python-docx)"""
import json
from pathlib import Path
from agents.skillbased_docx_agent import SkillBasedDocxAgent

# JSON bul
json_files = sorted(Path("outputs").glob("*.json"))
print("Bulunan JSON dosyaları:", [f.name for f in json_files])

if not json_files:
    print("❌ JSON bulunamadı!")
    exit(1)

# Tercihli olarak chemical_spillage kullan
target = None
for jf in json_files:
    if "chemical" in jf.name:
        target = jf
        break
if not target:
    target = json_files[-1]

print(f"\n📂 Kullanılan dosya: {target}")
with open(target, encoding="utf-8") as f:
    data = json.load(f)
print(f"Veri anahtarları: {list(data.keys())}")

# Agent
agent = SkillBasedDocxAgent()
output = agent.generate_report(data, "outputs/HSE_FULL_REPORT_V2.docx")
print(f"\n🎉 BAŞARILI! Rapor: {output}")
