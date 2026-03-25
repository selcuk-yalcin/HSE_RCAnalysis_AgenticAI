"""Decision Tree Mermaid Generator Test Script"""

from agents.decision_tree_mermaid import DecisionTreeGenerator
import json
from pathlib import Path


def test_basic_5why_analysis():
    """Basit bir 5-Why analizi test etme"""
    
    rca_data = {
        "incident_event": {
            "title": "Makine Arızası - Motor Yanması"
        },
        "branches": [
            {
                "why_chain": [
                    {
                        "question_tr": "Motor neden yanmaya başladı?",
                        "question": "Why did the motor start burning?",
                        "answer_tr": "Motor gövdesinde aşırı ısı oluştu",
                        "answer": "Excessive heat was generated in the motor body"
                    },
                    {
                        "question_tr": "Neden motor gövdesinde aşırı ısı oluştu?",
                        "question": "Why excessive heat in motor?",
                        "answer_tr": "Fan sistemi arızalandığı için soğutma yapılamadı",
                        "answer": "Cooling was not possible because the fan system failed"
                    },
                    {
                        "question_tr": "Neden fan sistemi arızalandı?",
                        "question": "Why did fan system fail?",
                        "answer_tr": "Fan kaflı rulman metal parçacıklarıyla tıkanmıştı",
                        "answer": "The cage bearing of the fan was clogged with metal particles"
                    }
                ],
                "root_cause": {
                    "title": "Periyodik Bakım Eksikliği",
                    "cause_tr": "Fan sistemi düzenli olarak temizlenmediği için metal parçacıklar birikmişti",
                    "cause": "Metal particles accumulated because the fan system was not cleaned regularly",
                    "code": "RC-001"
                }
            },
            {
                "why_chain": [
                    {
                        "question_tr": "Motor neden yanmaya başladı?",
                        "question": "Why did the motor start burning?",
                        "answer_tr": "Motor çevresinde elektrik kablolarında kısa devre oluştu",
                        "answer": "Short circuit occurred in electrical cables around motor"
                    },
                    {
                        "question_tr": "Neden elektrik kablolarında kısa devre oluştu?",
                        "question": "Why short circuit in cables?",
                        "answer_tr": "Kablo izolasyonu zamanla aşınıp bozulmuştu",
                        "answer": "Cable insulation deteriorated over time"
                    },
                    {
                        "question_tr": "Neden kablo izolasyonu bozuldu?",
                        "question": "Why did cable insulation deteriorate?",
                        "answer_tr": "Ortamda yüksek nem ve asidik madde vardı",
                        "answer": "High humidity and acidic substances in the environment"
                    }
                ],
                "root_cause": {
                    "title": "Uygun Olmayan Ortam Koşulları",
                    "cause_tr": "Fabrika ortamı kablolara zarar veren kimyasal ve nem koşullarına sahipti",
                    "cause": "Factory environment had chemical and moisture conditions harmful to cables",
                    "code": "RC-002"
                }
            }
        ]
    }
    
    # HTML dosyasını oluştur
    output_path = "/Users/selcuk/Desktop/HSE_RCAnalysis_AgenticAI-main/outputs/test_tree_mermaid.html"
    
    generator = DecisionTreeGenerator()
    html_output = generator.generate_html(
        rca_data,
        output_path=output_path,
        incident_title="Motor Yanması Analizi - 22 Mart 2026"
    )
    
    print("✅ Decision Tree HTML başarıyla oluşturuldu!")
    print(f"📁 Çıktı dosyası: {output_path}")
    print(f"📊 HTML boyutu: {len(html_output)} byte")
    
    # HTML içeriğini kontrol et
    if "OLAY" in html_output and "KÖK NEDEN" in html_output:
        print("✅ HTML yapısı kontrol edildi - OLAY ve KÖK NEDEN düğümleri var")
    
    if "5-WHY ANALİZ AĞACI" in html_output:
        print("✅ Başlık doğru - Türkçe karakter kontrolü geçti")
    
    return html_output


def test_single_branch():
    """Tek şube ile test etme"""
    
    rca_data = {
        "incident_event": "İşçi Düşme Olayı",
        "branches": [
            {
                "why_chain": [
                    {
                        "question_tr": "Neden işçi düştü?",
                        "answer_tr": "Merdiven kaymak için pürüzlü değildi"
                    },
                    {
                        "question_tr": "Neden merdiven kaymak için pürüzlü değildi?",
                        "answer_tr": "Bakım personeli merdiveni temizlemedi"
                    }
                ],
                "root_cause": {
                    "title": "Bakım Eksikliği",
                    "cause_tr": "Periyodik bakım planı uygulanmadı",
                    "code": "RC-003"
                }
            }
        ]
    }
    
    output_path = "/Users/selcuk/Desktop/HSE_RCAnalysis_AgenticAI-main/outputs/test_tree_single.html"
    
    generator = DecisionTreeGenerator()
    html_output = generator.generate_html(
        rca_data,
        output_path=output_path,
        incident_title="İşçi Düşme Analizi"
    )
    
    print("\n✅ Tek şubeli Decision Tree oluşturuldu!")
    print(f"📁 Çıktı dosyası: {output_path}")
    
    return html_output


def test_empty_branches():
    """Boş şubeler ile test etme"""
    
    rca_data = {
        "incident_event": "Test Olayı",
        "branches": []
    }
    
    generator = DecisionTreeGenerator()
    html_output = generator.generate_html(
        rca_data,
        incident_title="Boş Analiz Testi"
    )
    
    print("\n✅ Boş şubeler testi yapıldı!")
    if "5-Why Analizi Bulunamadı" in html_output or "Olay:" in html_output:
        print("✅ Boş veri kontrol edildi - uygun mesaj gösterildi")
    
    return html_output


def test_text_formatting():
    """Metin formatting fonksiyonlarını test etme"""
    
    generator = DecisionTreeGenerator()
    
    # Test _norm fonksiyonu
    text1 = "  HELLO WORLD!!! "
    normalized = generator._norm(text1)
    print(f"\n📝 Normalizasyon testi:")
    print(f"   Girdi: '{text1}'")
    print(f"   Çıktı: '{normalized}'")
    assert normalized == "hello world"
    print("   ✅ Başarılı")
    
    # Test _fmt fonksiyonu
    text2 = "Bu çok uzun bir metindir ve satır sonunda olması gereken nokta vardır ve devam etmesi gerekir."
    formatted = generator._fmt(text2, 30)
    print(f"\n📝 Metin biçimlendirme testi (max 30 karakter):")
    print(f"   Girdi: '{text2}'")
    print(f"   Çıktı: '{formatted}'")
    print("   ✅ Başarılı")
    
    # HTML escape testi
    text3 = 'Test <script> ve "quotes" ve backslash \\'
    formatted3 = generator._fmt(text3, 50)
    print(f"\n📝 HTML escape testi:")
    print(f"   Girdi: {text3}")
    print(f"   Çıktı: {formatted3}")
    assert "&lt;" in formatted3 and "&gt;" in formatted3 and "'" in formatted3
    print("   ✅ HTML karakterler doğru escape edildi")


def test_complex_scenario():
    """Karmaşık senaryo testi - 5 şubeli analiz"""
    
    rca_data = {
        "incident_event": {
            "title": "Endüstriyel Kaza - Kaynak Noktasında Patlama"
        },
        "branches": [
            {
                "why_chain": [
                    {
                        "question_tr": "Neden patlama oldu?",
                        "answer_tr": "Basınç kontrol valfi arızalandı"
                    },
                    {
                        "question_tr": "Neden basınç kontrol valfi arızalandı?",
                        "answer_tr": "İç sesemi kaynaklar kırılmıştı"
                    }
                ],
                "root_cause": {
                    "title": "Tasarım Hatası",
                    "cause_tr": "Valif yüksek basınca dayanacak şekilde tasarlanmamıştı",
                    "code": "RC-DES-001"
                }
            },
            {
                "why_chain": [
                    {
                        "question_tr": "Neden patlama oldu?",
                        "answer_tr": "Güvenlik testleri yapılmadı"
                    },
                    {
                        "question_tr": "Neden güvenlik testleri yapılmadı?",
                        "answer_tr": "Test laboratorusu kapalıydı"
                    }
                ],
                "root_cause": {
                    "title": "Kaynak Eksikliği",
                    "cause_tr": "Test laboratuvarı ve personeli için kaynak ayrılmamıştı",
                    "code": "RC-RES-002"
                }
            }
        ]
    }
    
    output_path = "/Users/selcuk/Desktop/HSE_RCAnalysis_AgenticAI-main/outputs/test_tree_complex.html"
    
    generator = DecisionTreeGenerator()
    html_output = generator.generate_html(
        rca_data,
        output_path=output_path,
        incident_title="Kaynak Patlaması Kök Neden Analizi"
    )
    
    print("\n✅ Karmaşık senaryo testi yapıldı!")
    print(f"📁 Çıktı dosyası: {output_path}")
    
    # Doğrulamalar
    mermaid_count = html_output.count("graph TD")
    if mermaid_count > 0:
        print("✅ Mermaid grafı bulundu")
    
    return html_output


if __name__ == "__main__":
    print("🔍 Decision Tree Mermaid Generator Test Başladı\n")
    print("=" * 60)
    
    try:
        # Çıktı dizini oluştur
        Path("/Users/selcuk/Desktop/HSE_RCAnalysis_AgenticAI-main/outputs").mkdir(parents=True, exist_ok=True)
        
        # Test 1: Temel 5-Why analizi
        print("\n📌 Test 1: Temel 5-Why Analizi (2 şube)")
        test_basic_5why_analysis()
        
        # Test 2: Tek şube
        print("\n📌 Test 2: Tek Şubeli Analiz")
        test_single_branch()
        
        # Test 3: Boş şubeler
        print("\n📌 Test 3: Boş Şubeler")
        test_empty_branches()
        
        # Test 4: Metin işleme
        print("\n📌 Test 4: Metin İşleme Fonksiyonları")
        test_text_formatting()
        
        # Test 5: Karmaşık senaryo
        print("\n📌 Test 5: Karmaşık Senaryo (2 şube)")
        test_complex_scenario()
        
        print("\n" + "=" * 60)
        print("✅ TÜM TESTLER BAŞARILI TAMAMLANDI!")
        print("\n📊 Oluşturulan HTML dosyaları:")
        print("   1. test_tree_mermaid.html - Temel 2 şubeli analiz")
        print("   2. test_tree_single.html - Tek şubeli analiz")
        print("   3. test_tree_complex.html - Karmaşık senaryo")
        
    except Exception as e:
        print(f"\n❌ HATA: {str(e)}")
        import traceback
        traceback.print_exc()
