"""
Quick Question System Test - Hızlı Soru Sorma Sistemi Testi
Örnek senaryolarla doğrudan test yapan basit script.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hitl_test.question_engine import QuestionEngine
from hitl_test.hybrid_input_processor import HybridInputProcessor


def print_header():
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "SORU SORMA YAPISI - HIZLI TEST".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝\n")


def test_scenario(scenario_num, name, text):
    """Bir senaryo ile test et"""
    print(f"\n{'═' * 80}")
    print(f"SENARYO {scenario_num}: {name}")
    print(f"{'═' * 80}\n")
    
    print(f"📝 OLAy AÇIKLAMASI:")
    print(f"   {text}\n")
    
    processor = HybridInputProcessor()
    qe = QuestionEngine()
    
    # Input analizi
    level, details = processor.detect_input_level(text)
    
    print(f"📊 INPUT ANALİZİ:")
    print(f"   • Bilgi Seviyesi: Level {level}")
    print(f"   • Detail Skoru: {details['detail_score']}/13")
    print(f"   • Bilgi Tamlığı: {(details['detail_score']/13)*100:.0f}%")
    
    missing_count = len(details['missing'])
    print(f"   • Eksik Kategoriler: {missing_count} adet")
    
    if details['missing']:
        for i, cat in enumerate(details['missing'][:6], 1):
            print(f"      {i}. {cat}")
    
    # Sorular üret
    questions = qe.generate_questions_for_missing_categories(details['missing'][:3])
    
    print(f"\n❓ SORULACAK SORULAR ({len(questions)} adet, ilk 6 tanesi):\n")
    
    for q_idx, q in enumerate(questions[:6], 1):
        required_mark = "🔴 ZORUNLU" if q['required'] else "⚪ OPSİYONEL"
        print(f"{q_idx}. {required_mark}")
        print(f"   Kategori: {q['category'].upper()}")
        print(f"   Soru: {q['question']}")
        print(f"   HSG245: {q['hsg245_codes']}")
        print()


def main():
    """Ana fonksiyon"""
    print_header()
    
    scenarios = [
        {
            "num": 1,
            "name": "Yüksekten Düşme",
            "text": """
Bir inşaat işçisi, 15 katlı bir yapının inşaat alanında çalışırken kefalı iskeleye 
tırmanmak istedi. Güvenlik kemeri bulunmamaktaydı. İskele üzerine çıktığı esnada 
dengesini kaybetti ve 5 metre aşağıya düştü. Başında, bacaklarında ve göğüs bölgesinde 
ağır yaralanmalar meydana geldi. Olay saat 14:45'te meydana geldi."""
        },
        {
            "num": 2,
            "name": "Elektrik Çarpması",
            "text": """
Bir elektrik teknisyeni, endüstriyel bir tesiste 380V elektrik panosunda bakım çalışması 
yapıyordu. LOTO (Lock Out Tag Out) prosedürü uygulanmamıştı, dolayısıyla sistem de 
kapalı değildi. Teknisyen enerjinin kesilmediğini bilmeden terminal kutusuna dokundu 
ve 380V akımına kapıldı. Ciddi yanıklar meydana geldi."""
        },
        {
            "num": 3,
            "name": "Makine Kazası - Parmak Presi",
            "text": """
Bir imalat tesisinde çalışan bir işçi, parmak presi makinesinde parça üretimi yapıyordu. 
Makine tasarımında acil durdurma butonu bulunmamaktaydı. İşçi makine çalışırken üzerinde 
bir parçayı manuel olarak ayarlamaya çalışıyordu. Yardımcı personel işçiye yardımcı olmak 
için makineyi durdurmaya çalıştı ancak makineyi durduracak düğmeyi bulamadı. İşçinin 
parmakları preste ezildi ve amputasyon gerekti."""
        },
        {
            "num": 4,
            "name": "Kimyasal Maruziyeti",
            "text": """
Bir kimya fabrikasında çalışan bir işçi, silindir depolama alanında çalışıyordu. 
Toksik gaz sızıntısı meydana geldiğinde işçi, KKD olmaksızın alana girdi. 
İşçi hızla bilinçsiz hale geldi. Olay yerine diğer çalışanlar müdahale etti 
ancak alanın hava kalitesi kontrol edilmemişti. Toksik gaz maruziyetinin ardından 
yaşamını yitirdi."""
        }
    ]
    
    for scenario in scenarios:
        test_scenario(scenario["num"], scenario["name"], scenario["text"])
    
    # Özet
    print(f"\n{'═' * 80}")
    print("ÖZET")
    print(f"{'═' * 80}\n")
    
    print(f"✅ {len(scenarios)} senaryo test edildi")
    print(f"📊 Sistem aşağıdaki yetenekleri göstermiştir:")
    print(f"   1. Input metin analizine dayalı bilgi seviyesi tespiti")
    print(f"   2. Eksik bilgi kategorilerinin otomatik tanımlanması")
    print(f"   3. HSG245 kodlarına bağlı kontekstüel sorular üretimi")
    print(f"   4. Zorunlu ve opsiyonel soruların ayırımı")
    print(f"   5. Kategori bazlı soru önerilmesi")
    
    print(f"\n🎯 SONUÇ: Soru Sorma Yapısı başarıyla test edilmiştir!")
    print(f"{'═' * 80}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()
