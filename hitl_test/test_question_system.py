"""
Test Question System - Soru Sorma Yapısı Testi
Sistemin soru üretim, kategorilendirme ve uyarlama yeteneklerini test eder.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hitl_test.question_engine import QuestionEngine
from hitl_test.hybrid_input_processor import HybridInputProcessor


def test_question_generation():
    """Test 1: Temel Soru Üretimi"""
    print("\n" + "=" * 80)
    print("TEST 1: TEMEL SORU ÜRETİMİ")
    print("=" * 80)
    
    qe = QuestionEngine()
    
    # Test Senaryosu 1: Düşme
    scenario1 = """
    Bir işçi 5 metreden düşerek bacağını kırdı.
    Olay saat 14:30'de meydana geldi.
    İnşaat alanında gerçekleşti.
    """
    
    print("\n📝 SENARYO 1 (Düşme):")
    print(scenario1)
    
    # Input analizi
    processor = HybridInputProcessor()
    level, details = processor.detect_input_level(scenario1)
    
    print(f"\n📊 INPUT ANALİZİ:")
    print(f"   • Bilgi Seviyesi: Level {level}")
    print(f"   • Detail Score: {details['detail_score']}/13")
    print(f"   • Eksik Kategoriler: {', '.join(details['missing'])}")
    
    # Soru üretimi
    questions = qe.generate_questions_for_missing_categories(details['missing'][:3])
    
    print(f"\n❓ ÜRETİLEN SORULAR ({len(questions)} adet):")
    for i, q in enumerate(questions, 1):
        print(f"\n   {i}. 🏷️ Kod: {q.get('hsg245_codes', 'N/A')}")
        print(f"      ❓ {q['question']}")
        print(f"      � Kategori: {q.get('category', 'N/A')}")
        print(f"      �🔗 HSG245 Link: {q.get('hsg245_link', 'N/A')[:60]}...")
        print(f"      ⭐ Gerekli: {'Evet' if q.get('required') else 'Hayır'}")
    
    print("\n✅ Test 1 Başarılı!")
    return True


def test_multi_scenario_questions():
    """Test 2: Çok Senaryolu Soru Üretimi"""
    print("\n" + "=" * 80)
    print("TEST 2: ÇOK SENARYOLU SORU ÜRETİMİ")
    print("=" * 80)
    
    scenarios = [
        {
            "name": "Elektrik Şoku",
            "text": "Elektrik teknisyeni terminal kutusunda çalışırken şok aldı."
        },
        {
            "name": "Makine Ezilmesi",
            "text": "Işın kaynağında parmak presi makinesine sıkıştı."
        },
        {
            "name": "Kimyasal Maruziyeti",
            "text": "Depoda kimyasal buharlarına maruz kaldı ve baygınlık geçirdi."
        }
    ]
    
    processor = HybridInputProcessor()
    qe = QuestionEngine()
    
    for scenario in scenarios:
        print(f"\n{'─' * 80}")
        print(f"📌 SENARYO: {scenario['name']}")
        print(f"{'─' * 80}")
        print(f"Metin: {scenario['text']}")
        
        level, details = processor.detect_input_level(scenario['text'])
        
        print(f"\n📊 Level {level} | Detail Score: {details['detail_score']}/13")
        print(f"   Eksik: {', '.join(details['missing'][:3])}")
        
        questions = qe.generate_questions_for_missing_categories(
            details['missing'][:2]
        )
        
        print(f"\n   Sorular:")
        for i, q in enumerate(questions[:2], 1):
            print(f"      {i}. {q['question'][:65]}...")
    
    print("\n✅ Test 2 Başarılı!")
    return True


def test_question_filtering():
    """Test 3: Soru Filtreleme ve Önceliklendirme"""
    print("\n" + "=" * 80)
    print("TEST 3: SORU FİLTRELEME VE ÖNCELİKLENDİRME")
    print("=" * 80)
    
    qe = QuestionEngine()
    
    # Test: Tüm sorular ve kategoriler
    print("\n🔴 TÜM SORULAR VE KATEGORİLER:")
    
    all_questions = qe.generate_questions_for_missing_categories(
        list(qe.question_templates.keys())
    )
    
    print(f"   Toplam: {len(all_questions)} soru")
    required_count = sum(1 for q in all_questions if q['required'])
    optional_count = sum(1 for q in all_questions if not q['required'])
    print(f"   Zorunlu: {required_count} | Opsiyonel: {optional_count}")
    
    for i, q in enumerate(all_questions[:5], 1):
        print(f"   {i}. {q['question'][:60]}... ({q['category']})")
    
    # Test: Kategori Bazlı Sorular
    print("\n📂 KATEGORİ BAZLI SORULAR:")
    
    print(f"   Toplam Kategori: {len(qe.question_templates)}")
    for i, (cat_name, cat_data) in enumerate(list(qe.question_templates.items())[:5], 1):
        q_count = len(cat_data['questions'])
        print(f"   {i}. {cat_name.upper()} - {q_count} soru - HSG245: {cat_data['hsg245_codes']}")
        for q in cat_data['questions'][:1]:
            print(f"      • {q['question'][:55]}...")
    
    print("\n✅ Test 3 Başarılı!")
    return True


def test_adaptive_questioning():
    """Test 4: Uyarlamalı Soru Üretimi"""
    print("\n" + "=" * 80)
    print("TEST 4: UYARLAMALI SORU ÜRETİMİ")
    print("=" * 80)
    
    processor = HybridInputProcessor()
    qe = QuestionEngine()
    
    # Test Case 1: Minimal Bilgi
    minimal = "Bir işçi düştü ve yaralandı."
    level1, details1 = processor.detect_input_level(minimal)
    
    print(f"\n💡 DURUM 1 - MİNİMAL BİLGİ")
    print(f"   Input: '{minimal}'")
    print(f"   Level: {level1} | Detay: {details1['detail_score']}/13")
    
    q1 = qe.generate_questions_for_missing_categories(details1['missing'][:2])
    print(f"   Önerilen Sorular: {len(q1)}")
    
    # Test Case 2: Orta Seviye Bilgi
    medium = """
    Bir işçi inşaat alanında 14:30'de 5 metreden düştü.
    Bacak ve göğüs bölgesinde yaralanma var.
    Kefalı iskele kullanıyordu.
    """
    level2, details2 = processor.detect_input_level(medium)
    
    print(f"\n💡 DURUM 2 - ORTA SEVİYE BİLGİ")
    print(f"   Level: {level2} | Detay: {details2['detail_score']}/13")
    
    q2 = qe.generate_questions_for_missing_categories(details2['missing'][:2])
    print(f"   Önerilen Sorular: {len(q2)}")
    
    # Test Case 3: Detaylı Bilgi
    detailed = """
    2024-02-15 saat 14:30'de Ahmet B. (40 yaş) inşaat alanında çalışırken kefalı iskeleye 
    çıktı. Güvenlik kemeri takılı değildi. İskele 5 metre yükseklikte idi. Bir alet düşmesi
    neticesinde denge kaybetti ve yere düştü. Görgü tanıkları oradaydı. Kefalı iskele 
    standartlara uygun yapıldığı tespit edildi fakat emniyet takılı değildi.
    """
    level3, details3 = processor.detect_input_level(detailed)
    
    print(f"\n💡 DURUM 3 - DETAYLI BİLGİ")
    print(f"   Level: {level3} | Detay: {details3['detail_score']}/13")
    
    q3 = qe.generate_questions_for_missing_categories(details3['missing'][:2])
    print(f"   Önerilen Sorular: {len(q3)}")
    
    print(f"\n📊 ÖZET:")
    print(f"   Minimal (L{level1}) → {len(q1)} soru")
    print(f"   Orta (L{level2}) → {len(q2)} soru")
    print(f"   Detaylı (L{level3}) → {len(q3)} soru")
    
    print("\n✅ Test 4 Başarılı!")
    return True


def test_hsg245_integration():
    """Test 5: HSG245 Kodları ile Entegrasyon"""
    print("\n" + "=" * 80)
    print("TEST 5: HSG245 KOD ENTEGRASİYONU")
    print("=" * 80)
    
    qe = QuestionEngine()
    
    print("\n🔗 SORU-HSG245 LİNKLEMESİ:")
    
    # Tüm kategorileri kontrol et
    categories = qe.question_templates
    
    for cat_name in list(categories.keys())[:3]:
        cat = categories[cat_name]
        print(f"\n📂 {cat_name.upper()}")
        print(f"   Açıklama: {cat['description']}")
        print(f"   HSG245 Kodları: {', '.join(cat['hsg245_codes'])}")
        
        for i, q in enumerate(cat['questions'][:2], 1):
            print(f"   Soru {i}:")
            print(f"      ❓ {q['question']}")
            print(f"      🏷️  HSG245: {q.get('hsg245_link', 'N/A')[:50]}...")
    
    print("\n✅ Test 5 Başarılı!")
    return True


def test_performance():
    """Test 6: Performans Testi"""
    print("\n" + "=" * 80)
    print("TEST 6: PERFORMANS TESTİ")
    print("=" * 80)
    
    import time
    
    qe = QuestionEngine()
    processor = HybridInputProcessor()
    
    test_text = """
    Bir işçi düşerek yaralandı. 14:30'de meydana geldi.
    İnşaat alanında çalışıyordu.
    """
    
    # 1. Input analizi hızı
    print("\n⏱️  INPUT ANALİZİ HIZI:")
    start = time.time()
    for _ in range(100):
        level, details = processor.detect_input_level(test_text)
    elapsed = time.time() - start
    print(f"   100 analiz: {elapsed:.3f} saniye ({elapsed/100*1000:.2f}ms/analiz)")
    
    # 2. Soru üretim hızı
    print("\n⏱️  SORU ÜRETİMİ HIZI:")
    start = time.time()
    for _ in range(50):
        questions = qe.generate_questions_for_missing_categories(['prosedür', 'ekipman'])
    elapsed = time.time() - start
    print(f"   50 üretim: {elapsed:.3f} saniye ({elapsed/50*1000:.2f}ms/üretim)")
    
    print("\n✅ Test 6 Başarılı!")
    return True


def main():
    """Ana Test Fonksiyonu"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "SORU SORMA YAPISI TEST PAKETI".center(78) + "║")
    print("║" + "(Question System Test Suite)".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    
    tests = [
        ("Test 1: Temel Soru Üretimi", test_question_generation),
        ("Test 2: Çok Senaryolu Sorular", test_multi_scenario_questions),
        ("Test 3: Soru Filtreleme", test_question_filtering),
        ("Test 4: Uyarlamalı Soru Üretimi", test_adaptive_questioning),
        ("Test 5: HSG245 Entegrasyon", test_hsg245_integration),
        ("Test 6: Performans", test_performance),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} Başarısız: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Özet
    print("\n" + "=" * 80)
    print("📋 TEST ÖZETİ")
    print("=" * 80)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "✅ BAŞARILI" if result else "❌ BAŞARISIZ"
        print(f"{status} | {test_name}")
    
    print(f"\n{'─' * 80}")
    print(f"Toplam: {passed}/{total} test başarılı")
    print(f"Başarı Oranı: {passed/total*100:.1f}%")
    print("=" * 80)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
