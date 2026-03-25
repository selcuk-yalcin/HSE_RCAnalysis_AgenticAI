"""
Decision Tree Test Script
"""
import json
from pathlib import Path
from agents.decision_tree_generator import generate_decision_tree_html

# Test dosyasını yükle
test_file = Path("/Users/selcuk/Desktop/HSE_RCAnalysis_AgenticAI-main/outputs/forklift_pesticide_B_20260304_172237.json")

with open(test_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Decision tree oluştur
output_path = "/Users/selcuk/Desktop/HSE_RCAnalysis_AgenticAI-main/outputs/test_decision_tree_output.html"

print("Decision tree oluşturuluyor...")
html = generate_decision_tree_html(
    rca_data=data,
    output_path=output_path,
    incident_title="Forklift - Pestisit Varil Çarpışması"
)

print(f"✓ Decision tree oluşturuldu: {output_path}")
print(f"✓ HTML boyutu: {Path(output_path).stat().st_size / 1024:.1f} KB")
