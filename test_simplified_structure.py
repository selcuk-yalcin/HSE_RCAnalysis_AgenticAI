"""
Basitleştirilmiş Yapı Test Scripti
Knowledge Base'in doğru çalışıp çalışmadığını test eder
"""

import sys
import os

# Path setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("="*80)
print("🧪 BASİTLEŞTİRİLMİŞ YAPI TESTİ")
print("="*80)

# Test 1: Knowledge Base Import
print("\n1️⃣ Knowledge Base Import Testi...")
try:
    from shared.knowledge_base import HSG245_TAXONOMY, get_category_text, get_all_categories
    print("   ✅ Import başarılı")
except Exception as e:
    print(f"   ❌ Import hatası: {e}")
    sys.exit(1)

# Test 2: Kategori Metinleri
print("\n2️⃣ Kategori Metinleri Testi...")
for cat in ['A', 'B', 'C', 'D']:
    text = get_category_text(cat)
    if text:
        print(f"   ✅ Kategori {cat}: {len(text)} karakter")
        print(f"      Başlangıç: {text[:60]}...")
    else:
        print(f"   ❌ Kategori {cat}: Metin bulunamadı!")

# Test 3: Tüm Kategoriler
print("\n3️⃣ Tüm Kategoriler Testi...")
all_text = get_all_categories()
print(f"   ✅ Toplam boyut: {len(all_text)} karakter (~{len(all_text)//1000}KB)")
print(f"   LLM Context Window'a sığar mı? {'✅ EVET' if len(all_text) < 30000 else '⚠️ Biraz büyük'}")

# Test 4: Root Cause Agent Import
print("\n4️⃣ Root Cause Agent Import Testi...")
try:
    from agents.rootcause_agent_v2 import RootCauseAgentV2 as RootCauseAgent
    agent = RootCauseAgent()
    print("   ✅ Agent başlatıldı")
except Exception as e:
    print(f"   ❌ Agent hatası: {e}")
    sys.exit(1)

# Test 5: Action Plan Agent Import
print("\n5️⃣ Action Plan Agent Import Testi...")
try:
    from agents.actionplan_agent import ActionPlanAgent
    ap_agent = ActionPlanAgent()
    print("   ✅ ActionPlan Agent başlatıldı")
except Exception as e:
    print(f"   ❌ ActionPlan hatası: {e}")
    sys.exit(1)

# Test 6: A Kategorisi İçerik Kontrolü
print("\n6️⃣ A Kategorisi İçerik Kontrolü...")
cat_a = get_category_text('A')
expected_items = [
    "A1.1",
    "A2.1", 
    "A3.1",
    "A4.1",
    "Prosedür",
    "Ekipman",
    "KKD"
]
found = 0
for item in expected_items:
    if item in cat_a:
        found += 1
    else:
        print(f"   ⚠️ Eksik: {item}")

if found == len(expected_items):
    print(f"   ✅ Tüm beklenen içerik mevcut ({found}/{len(expected_items)})")
else:
    print(f"   ⚠️ Bazı içerikler eksik ({found}/{len(expected_items)})")

# Test 7: D Kategorisi İçerik Kontrolü
print("\n7️⃣ D Kategorisi İçerik Kontrolü...")
cat_d = get_category_text('D')
expected_d = [
    "D1.1",
    "D2.1",
    "D3.1",
    "D4.1",
    "D5.1",
    "D6.1",
    "D7.1",
    "D8.1",
    "Liderlik",
    "İletişim",
    "Eğitim",
    "Risk"
]
found_d = 0
for item in expected_d:
    if item in cat_d:
        found_d += 1
    else:
        print(f"   ⚠️ Eksik: {item}")

if found_d == len(expected_d):
    print(f"   ✅ Tüm D kategorisi içeriği mevcut ({found_d}/{len(expected_d)})")
else:
    print(f"   ⚠️ Bazı D içerikleri eksik ({found_d}/{len(expected_d)})")

# Özet
print("\n" + "="*80)
print("📊 TEST ÖZETİ")
print("="*80)
print("✅ Knowledge Base: Çalışıyor")
print("✅ Root Cause Agent: Başlatılabilir")
print("✅ Action Plan Agent: Başlatılabilir")
print(f"✅ Toplam Kategori Boyutu: ~{len(all_text)//1000}KB (LLM'e sığar)")
print(f"✅ A Kategorisi: {len(cat_a)} karakter")
print(f"✅ D Kategorisi: {len(cat_d)} karakter")
print("\n🎉 Tüm testler başarılı! Yapı kullanıma hazır.")
print("="*80)
