"""
Interactive Question System Test - Soru Sorma Sistemi İnteraktif Testi
Kullanıcı girdisine dayalı dinamik soru üretim sistemini test eder.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hitl_test.question_engine import QuestionEngine
from hitl_test.hybrid_input_processor import HybridInputProcessor


def display_header():
    """Başlık göster"""
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "SORU SORMA YAPISI - İNTERAKTİF TEST".center(78) + "║")
    print("║" + "(Interactive Question System Test)".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝\n")


def test_with_sample():
    """Örnek senaryo ile test et"""
    print("\n" + "=" * 80)
    print("ÖRNEK SENARYO TEST")
    print("=" * 80)
    
    scenarios = [
        {
            "name": "Yüksekten Düşme",
            "text": "Bir işçi inşaat alanında çalışırken kefalı iskeleye çıktı. 5 metre yükseklikte iken denge kaybetti ve yere düştü. Güvenlik kemeri takılı değildi. Bacak kırığı ile hastaneye kaldırıldı."
        },
        {
            "name": "Elektrik Çarpması",
            "text": "Elektrik teknisyeni pano kapagında çalışırken terminal kutusuna dokundu. 380V akımına kapıldı. LOTO prosedürü uygulanmamıştı. Şiddetli yanıklar meydana geldi."
        },
        {
            "name": "Makine Kazası",
            "text": "Torna tezgahında çalışan işçinin elbisesi makineye sıkıştı. Acil durdurma butonu aydınlanmıyordu. İşçinin kol ezildi ve ampütasyon gerekti."
        }
    ]
    
    processor = HybridInputProcessor()
    qe = QuestionEngine()
    
    for scenario_idx, scenario in enumerate(scenarios, 1):
        print(f"\n{'─' * 80}")
        print(f"SENARYO {scenario_idx}: {scenario['name']}")
        print(f"{'─' * 80}\n")
        
        print(f"📝 OlAY AÇIKLAMASI:")
        print(f"   {scenario['text']}\n")
        
        # Input analizi
        level, details = processor.detect_input_level(scenario['text'])
        
        print(f"📊 INPUT ANALİZİ:")
        print(f"   • Bilgi Seviyesi: Level {level}")
        print(f"   • Detail Skoru: {details['detail_score']}/13")
        print(f"   • Bilgi Tamlığı: {(details['detail_score']/13)*100:.0f}%")
        
        if details['missing']:
            print(f"   • Eksik Kategoriler ({len(details['missing'])} adet):")
            for i, missing_cat in enumerate(details['missing'], 1):
                print(f"      {i}. {missing_cat}")
        
        # Sorular üret
        questions = qe.generate_questions_for_missing_categories(details['missing'][:3])
        
        print(f"\n❓ ÖNERİLEN SORULAR ({len(questions)} adet):\n")
        
        for q_idx, q in enumerate(questions[:5], 1):
            required_mark = "🔴 ZORUNLU" if q['required'] else "⚪ OPSİYONEL"
            print(f"   {q_idx}. [{required_mark}]")
            print(f"      Kategori: {q['category'].upper()}")
            print(f"      Soru: {q['question']}")
            print(f"      HSG245: {q['hsg245_codes']}")
            print()


def test_code_specific():
    """HSG245 kod spesifik sorular"""
    print("\n" + "=" * 80)
    print("HSG245 KOD SPESİFİK SORULAR")
    print("=" * 80)
    
    qe = QuestionEngine()
    
    # Spesifik kodlar için sorular
    suspected_codes = ['A1.1', 'A3.2', 'D3.1', 'B2.1']
    
    print(f"\n🎯 Şüphelenilen Kodlar: {', '.join(suspected_codes)}\n")
    
    questions = qe.get_code_specific_questions(suspected_codes)
    
    print(f"📋 Toplam {len(questions)} kod spesifik soru üretildi:\n")
    
    for q_idx, q in enumerate(questions, 1):
        print(f"{q_idx}. [{q['hsg245_code']}]")
        print(f"   Soru: {q['question']}")
        print(f"   Açıklama: {q.get('code_description', 'N/A')}")
        print()


def test_followup_questions():
    """Takip soruları (5-Why)"""
    print("\n" + "=" * 80)
    print("TAKIP SORULARI (5-WHY ANALİZİ)")
    print("=" * 80)
    
    qe = QuestionEngine()
    
    test_answers = [
        {
            "answer": "Çalışan prosedürü bilmiyordu ve eğitim almamıştı",
            "category": "prosedür"
        },
        {
            "answer": "Ekipman arızalıydı ama personel yine de kullandı",
            "category": "ekipman"
        },
        {
            "answer": "KKD vardı ama çalışan rahatsızlık buldu ve kullanmadı",
            "category": "ppe"
        },
        {
            "answer": "Bakım planı vardı fakat yapılmamıştı",
            "category": "prosedür"
        }
    ]
    
    for test_idx, test_case in enumerate(test_answers, 1):
        print(f"\n{'─' * 80}")
        print(f"TEST DURUMU {test_idx}:")
        print(f"{'─' * 80}")
        
        print(f"\n💬 KULLANICI CEVABI:")
        print(f"   \"{test_case['answer']}\"")
        
        print(f"\n📂 Kategori: {test_case['category'].upper()}\n")
        
        followups = qe.get_followup_questions(test_case['answer'], test_case['category'])
        
        if followups:
            print(f"🔄 TAKIP SORULARI ({len(followups)} adet):\n")
            for f_idx, followup in enumerate(followups, 1):
                print(f"   {f_idx}. ❓ {followup['question']}")
                print(f"      🏷️  {followup['hsg245_link']}")
                print(f"      📊 Why Seviyesi: {followup['why_level']}")
                print()
        else:
            print("   ℹ️  Takip sorusu bulunmadı\n")


def interactive_mode():
    """İnteraktif mod"""
    print("\n" + "=" * 80)
    print("İNTERAKTİF MOD")
    print("=" * 80)
    print("\nKendi senariyonuzu girin (Çıkmak için 'quit' yazın):\n")
    
    processor = HybridInputProcessor()
    qe = QuestionEngine()
    
    test_count = 0
    
    while True:
        print(f"\n{'─' * 80}")
        print(f"TEST #{test_count + 1}")
        print(f"{'─' * 80}\n")
        
        user_input = input("📝 Olay Açıklaması: ").strip()
        
        if user_input.lower() in ['quit', 'çık', 'exit']:
            print("\n✅ İnteraktif modu kapatıyorum...")
            break
        
        if not user_input:
            print("⚠️  Lütfen bir şeyler yazın!")
            continue
        
        # Analiz et
        level, details = processor.detect_input_level(user_input)
        
        print(f"\n{'─' * 80}")
        print(f"SONUÇLAR")
        print(f"{'─' * 80}\n")
        
        print(f"📊 ANALİZ SONUCU:")
        print(f"   • Bilgi Seviyesi: Level {level}")
        print(f"   • Detail Skoru: {details['detail_score']}/13")
        print(f"   • Completeness: {(details['detail_score']/13)*100:.0f}%")
        
        if details['missing']:
            print(f"\n📌 EKSIK BİLGİLER ({len(details['missing'])} kategori):")
            for i, cat in enumerate(details['missing'][:5], 1):
                print(f"      {i}. {cat}")
        
        # Sorular üret
        questions = qe.generate_questions_for_missing_categories(details['missing'][:2])
        
        if questions:
            print(f"\n❓ SORULACAK SORULAR ({len(questions)} adet):\n")
            
            for q_idx, q in enumerate(questions[:3], 1):
                required = "🔴" if q['required'] else "⚪"
                print(f"   {q_idx}. {required} {q['question']}")
        
        test_count += 1
        
        cont = input("\n\nDevam etmek istiyor musunuz? (e/h): ").strip().lower()
        if cont in ['h', 'n', 'no', 'hayır']:
            break


def main():
    """Ana fonksiyon"""
    display_header()
    
    print("Lütfen test türünü seçin:\n")
    print("1. 📋 Örnek Senaryolar ile Test")
    print("2. 🎯 HSG245 Kod Spesifik Sorular")
    print("3. 🔄 Takip Soruları (5-Why)")
    print("4. 💬 İnteraktif Mod")
    print("5. 📊 Tüm Testleri Çalıştır")
    print("6. 🚪 Çık\n")
    
    choice = input("Seçiminiz (1-6): ").strip()
    
    if choice == '1':
        test_with_sample()
    elif choice == '2':
        test_code_specific()
    elif choice == '3':
        test_followup_questions()
    elif choice == '4':
        interactive_mode()
    elif choice == '5':
        print("\n🔄 Tüm testler çalıştırılıyor...\n")
        test_with_sample()
        test_code_specific()
        test_followup_questions()
    elif choice == '6':
        print("\nGörüşmek üzere! 👋\n")
        return
    else:
        print("\n❌ Geçersiz seçim!")
        return
    
    print("\n" + "=" * 80)
    print("✅ TEST TAMAMLANDI")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()
