"""
5-Why Engine - HSG245 Knowledge Base Tabanlı Dinamik Soru Motoru

Akış:
1. Kullanıcı olayı anlatır
2. Immediate Cause (A veya B) kategorisinden seçim yapar
3. Seçime özel derinleştirici sorular adım adım sorulur
4. Her cevap sonraki soruyu/yönü belirler (deterministic değil, cevaba göre branching)
5. Kök neden (C veya D) koduna ulaşılır

Her olayda farklı kök nedene gidilmesini sağlayan mantık:
- Aynı immediate cause → farklı cevaplar → farklı kök nedenler
"""

import sys
import os
import importlib.util

# agents/__init__.py tüm ağır agentları yüklediği için
# knowledge_base'i doğrudan dosya yoluyla import ediyoruz
_kb_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agents", "knowledge_base.py")
_spec = importlib.util.spec_from_file_location("knowledge_base", _kb_path)
_kb_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_kb_module)
HSG245_TAXONOMY = _kb_module.HSG245_TAXONOMY


# ─────────────────────────────────────────────────────────────
# IMMEDIATE CAUSE SEÇENEKLERİ (A + B kategorisi)
# ─────────────────────────────────────────────────────────────
IMMEDIATE_CAUSES = {
    # A - Davranışlar
    "A1.1": "Bireysel kural/prosedür ihlali — çalışan bilerek kuralı çiğnedi",
    "A1.2": "Grup/takım kural ihlali — tüm ekip aynı kuralı uygulamıyordu",
    "A1.5": "Yanlış veya güncel olmayan prosedür kullanımı",
    "A1.6": "Prosedür var ama sahada uygulanamaz durumdaydı",
    "A2.1": "Ekipmanın yanlış veya uygunsuz kullanımı",
    "A2.3": "Arızası bilinen ekipman/araç ile çalışıldı",
    "A2.6": "Tasarım limitleri veya çalışma zarfı dışında kullanım",
    "A3.2": "Gerekli KKD kullanılmadı",
    "A3.4": "KKD mevcut değildi veya uygun değildi",
    "A3.5": "Güvenlik/koruyucu cihaz söküldü veya devre dışı bırakıldı",
    "A4.5": "Kasıtsız insan hatası — sürçme/dalgınlık",
    "A4.8": "Zaman baskısı nedeniyle kontrol adımları atlandı",
    # B - Koşullar
    "B1.2": "Koruyucu cihaz arızalıydı",
    "B2.1": "Ekipman/tesis arızası",
    "B2.7": "Operatör tarafından tespit edilemeyen gizli kusur",
    "B3.2": "Elektrik enerjisine maruz kalma",
    "B4.4": "Korunmasız yükseklik / düşme tehlikesi",
    "B4.6": "Kötü tertip/düzen/temizlik",
}


# ─────────────────────────────────────────────────────────────
# HER IMMEDIATE CAUSE İÇİN 5-WHY SORU AĞACI
# format:
#   "kod" → [ { "why": N, "soru": "...", "yönler": { "anahtar_kelime": "sonraki_kod_veya_not" } } ]
# ─────────────────────────────────────────────────────────────
FIVE_WHY_TREE = {

    "A2.6": [
        {
            "why": 1,
            "soru": "Ekipman veya sistem hangi limiti aştı? (kapasite, sıcaklık, basınç, hız...)",
            "hsg245": "A2.6 — Tasarım zarfı dışı kullanım",
            "yönler": {}   # serbest cevap, why-2 her zaman gelir
        },
        {
            "why": 2,
            "soru": "Çalışan/operatör bu limitin farkında mıydı? Uyarı işareti, etiket veya gösterge var mıydı?",
            "hsg245": "D3.1 / B4.7 / D5.1",
            "yönler": {
                "bilmiyordu|farkında değil|haberdar değil": "→ D3.1 (Eğitim eksikliği) veya B4.7 (Etiket yok)",
                "biliyordu|bilerek|haberi vardı": "→ A2.3 veya A1.1 dalına geç",
                "etiket yok|işaret yok|uyarı yok": "→ B4.7 (Etiketleme) ve D5.1 (Tasarım) ara"
            }
        },
        {
            "why": 3,
            "soru": "Bu limitler teknik dokümanda/kullanma kılavuzunda belirtilmiş miydi? Çalışana verilmiş miydi?",
            "hsg245": "D3.1 / D4.1",
            "yönler": {
                "belirtilmemiş|döküman yok|kılavuz yok": "→ D5.1 (Tasarım eksikliği) veya D4.1 (Risk analizi yok)",
                "var ama verilmemiş|iletilmemiş": "→ D3.1 (Eğitim/bilgi paylaşımı eksik)",
                "verilmiş|biliyordu": "→ A1.1 (Bilinçli ihlal) veya C2.4 (Karar verme sorunu)"
            }
        },
        {
            "why": 4,
            "soru": "Aşırı yükleme/kullanım neden gerçekleşti? Baskı mı vardı, ekipman mı yetersizdi, yoksa başka bir neden mi?",
            "hsg245": "D1.4 / D3.5 / D5.1",
            "yönler": {
                "baskı|yetiştir|üretim|süre": "→ D1.4 (Üretim baskısı kök neden)",
                "yetersiz|başka ekipman yok|alternatif yok": "→ D3.5 (Kaynak yetersizliği) veya D5.1",
                "alışkanlık|hep böyle|her zaman": "→ D1.5 (Sapmanın normalleşmesi)"
            }
        },
        {
            "why": 5,
            "soru": "Bu tür aşımların önlenmesi için sistemde ne eksik? (tasarım kilidi, alarm, prosedür, denetim...)",
            "hsg245": "D5.1 / D5.6 / D4.1 / D1.2",
            "yönler": {
                "tasarım|kilit|otomatik": "→ KÖK NEDEN: D5.1 veya D5.6 (Hata-toleranslı tasarım yok)",
                "alarm|uyarı|gösterge": "→ KÖK NEDEN: D5.3 (HMI/Alarm yönetimi eksik)",
                "prosedür|talimat": "→ KÖK NEDEN: D4.1 (Risk analizi / prosedür eksik)",
                "denetim|gözetim": "→ KÖK NEDEN: D1.2 (Yetersiz gözetim)"
            }
        }
    ],

    "A2.1": [
        {
            "why": 1,
            "soru": "Ekipman tam olarak nasıl yanlış/uygunsuz kullanıldı? Ne amaçla kullanıldı?",
            "hsg245": "A2.1",
            "yönler": {}
        },
        {
            "why": 2,
            "soru": "Doğru ekipman mevcut muydu? Yoksa neden yoktu?",
            "hsg245": "A3.4 / D3.5",
            "yönler": {
                "yoktu|mevcut değil|temin edilmemiş": "→ D3.5 (Kaynak eksikliği) veya D5.1",
                "vardı ama|bilmiyordu|fark etmedi": "→ D3.1 (Eğitim) veya A4.2 (Fark etmeme)"
            }
        },
        {
            "why": 3,
            "soru": "Bu ekipmanın hangi amaçla kullanılabileceği/kullanılamayacağı çalışana öğretilmiş miydi?",
            "hsg245": "D3.1 / D3.3",
            "yönler": {
                "eğitim yok|öğretilmemiş": "→ D3.1 (Eğitim eksikliği) KÖK NEDEN",
                "eğitim var ama|unutmuş": "→ C3.4 (Beceri körelmesi) veya D3.6 (Etkinlik ölçülmemiş)",
                "bilerek|isteyerek": "→ A1.1 (Bilinçli ihlal) veya C2.4"
            }
        },
        {
            "why": 4,
            "soru": "Bu tür yanlış kullanımlar daha önce de oldu mu? Raporlandı mı?",
            "hsg245": "D1.5 / D1.7 / D2.5",
            "yönler": {
                "evet|daha önce de|her zaman böyle": "→ D1.5 (Sapmanın normalleşmesi) KÖK NEDEN",
                "rapor edilmedi|söylemedi": "→ D1.7 (Raporlama kültürü) veya D2.5",
                "hayır|ilk kez": "→ D4.1 (Risk analizi yoktu)"
            }
        },
        {
            "why": 5,
            "soru": "Ekipmanın doğru kullanımını sağlayacak sistem/kontrol mekanizması var mı?",
            "hsg245": "D4.1 / D5.1 / D1.2",
            "yönler": {
                "yok|tanımlanmamış": "→ KÖK NEDEN: D4.1 (Risk analizi eksik)",
                "var ama işlemiyor|kağıtta kalıyor": "→ KÖK NEDEN: D4.2 (Kontrol uygulanmıyor)",
                "gözetim yok": "→ KÖK NEDEN: D1.2 (Yetersiz gözetim)"
            }
        }
    ],

    "A1.1": [
        {
            "why": 1,
            "soru": "Hangi kural veya prosedür çiğnendi? Ne yapılması gerekirdi, ne yapıldı?",
            "hsg245": "A1.1",
            "yönler": {}
        },
        {
            "why": 2,
            "soru": "Çalışan bu kuralı/prosedürü biliyor muydu? Eğitim almış mıydı?",
            "hsg245": "D3.1 / A1.1",
            "yönler": {
                "bilmiyordu|eğitim almamış|haberdar değil": "→ D3.1 (Eğitim eksikliği)",
                "biliyordu|eğitim almış|evet ama": "→ Why-3'e devam et (neden ihlal etti?)"
            }
        },
        {
            "why": 3,
            "soru": "Bu kural daha önce de ihlal edildi mi? Herhangi bir yaptırım uygulandı mı?",
            "hsg245": "D1.5 / D1.9 / D1.3",
            "yönler": {
                "evet|hep böyle|norm haline gelmiş": "→ D1.5 (Normalleşme) veya D1.9 (Göz yumma)",
                "yaptırım yok|kimse bir şey demedi": "→ D1.3 (Hesap verebilirlik eksikliği)",
                "ilk kez|baskı altında": "→ D1.4 (Üretim baskısı) veya A4.8 (Zaman baskısı)"
            }
        },
        {
            "why": 4,
            "soru": "Kuralı uygulamak zor veya engel oluşturuyor muydu? (fiziksel zorluk, zaman kaybı, rahatsızlık...)",
            "hsg245": "A1.6 / A1.8 / A3.6",
            "yönler": {
                "zor|uygulanamaz|zaman alıyor": "→ A1.6 (Uygulanamaz prosedür) → D4.1 incele",
                "hayır|kolay ama": "→ C3.5 (Güvensiz davranış pekiştirilmesi) veya D1.1",
                "baskı|yetiştir": "→ D1.4 (Üretim baskısı) KÖK NEDEN"
            }
        },
        {
            "why": 5,
            "soru": "Bu kuralın neden var olduğu ve tehlikeyi neden önlediği çalışana anlatılmış mıydı?",
            "hsg245": "D3.1 / D3.3 / C2.3",
            "yönler": {
                "anlatılmamış|sadece kural dendi|neden bilmiyordu": "→ KÖK NEDEN: D3.1 (Anlayış odaklı eğitim eksik)",
                "anlatılmış ama önemsemedi": "→ KÖK NEDEN: C3.5 (Pekiştirme eksik) veya D1.1",
                "anlamlı bulmuyor|gereksiz buluyor": "→ KÖK NEDEN: D1.5 (Kültür sorunu)"
            }
        }
    ],

    "A3.2": [
        {
            "why": 1,
            "soru": "Hangi KKD kullanılmadı? (baret, emniyet kemeri, eldiven, gözlük, maske...)",
            "hsg245": "A3.2",
            "yönler": {}
        },
        {
            "why": 2,
            "soru": "KKD sahada mevcut muydu ve erişilebilir miydi?",
            "hsg245": "A3.4 / D3.5",
            "yönler": {
                "yoktu|stok bitmişti|temin edilmemiş": "→ A3.4 (KKD yokluğu) → D3.5 Kaynak sorunu",
                "vardı ama|rahatsız|engel|zorlaştırıyor": "→ A3.6 (Rahatsız edici KKD) → D5.1 incele",
                "vardı|erişilebilirdi|bilinçli": "→ Why-3 devam (neden kullanmadı?)"
            }
        },
        {
            "why": 3,
            "soru": "Daha önce KKD kullanmama nedeniyle uyarı/yaptırım oldu mu?",
            "hsg245": "D1.9 / D1.3 / C3.5",
            "yönler": {
                "olmadı|kimse bir şey demedi|görmezden gelindi": "→ D1.9 (Göz yumma) veya D1.3",
                "oldu ama devam etti": "→ C3.5 (Güvensiz davranış pekiştirilmesi)",
                "ilk kez|acil|olağandışı durum": "→ C2.4 (Karar verme) veya A4.5"
            }
        },
        {
            "why": 4,
            "soru": "Bu işin KKD gerektirdiği risk değerlendirmesinde belirlenmiş miydi ve çalışana bildirilmiş miydi?",
            "hsg245": "D4.1 / D3.1",
            "yönler": {
                "risk değerlendirmesi yok|belirlenmemiş": "→ D4.1 (Risk analizi eksik) KÖK NEDEN",
                "var ama iletilmemiş|çalışan bilmiyordu": "→ D3.1 (Eğitim/iletişim eksik)",
                "biliyordu": "→ D1.5 (Normalleşme) veya D1.4 (Baskı)"
            }
        },
        {
            "why": 5,
            "soru": "KKD kullanımını zorunlu kılacak bir denetim/kontrol mekanizması var mı?",
            "hsg245": "D1.2 / D4.2",
            "yönler": {
                "gözetim yok|denetim yapılmıyor": "→ KÖK NEDEN: D1.2 (Yetersiz gözetim)",
                "var ama işlemiyor": "→ KÖK NEDEN: D4.2 (Kontrol uygulanmıyor)",
                "kültür sorunu|herkes böyle": "→ KÖK NEDEN: D1.1 (Güvenlik kültürü)"
            }
        }
    ],

    "A3.5": [
        {
            "why": 1,
            "soru": "Hangi güvenlik cihazı devre dışı bırakıldı veya söküldü? Nasıl yapıldı?",
            "hsg245": "A3.5",
            "yönler": {}
        },
        {
            "why": 2,
            "soru": "Bu işlemi kim yaptı? Yetkisi var mıydı?",
            "hsg245": "A1.4 / D1.9",
            "yönler": {
                "yönetici|formen|onay ile": "→ D1.4 (Üretim baskısı) veya D1.9 (Yönetim onayı)",
                "yetkisiz|kendi kendine": "→ A1.4 (Yetkisiz sapma) → neden izin istenmedi?",
                "bakım|tamir": "→ D4.5 (LOTO eksikliği) veya D4.4 (İş izni)"
            }
        },
        {
            "why": 3,
            "soru": "Cihazı devre dışı bırakmanın nedeni neydi? (işi yavaşlatıyordu, arızalıydı, başka?)",
            "hsg245": "D1.4 / B1.2 / D6.1",
            "yönler": {
                "yavaşlatıyor|engel|üretim": "→ D1.4 (Üretim baskısı) KÖK NEDEN",
                "arızalıydı|çalışmıyor": "→ B1.2 (Arızalı koruyucu) → D6.1 Bakım sorunu",
                "zaten işe yaramaz|gerekli değil": "→ D3.1 (Tehlike anlayışı eksik) veya D1.5"
            }
        },
        {
            "why": 4,
            "soru": "Bu cihazın neden orada olduğu ve hangi tehlikeye karşı koruduğu çalışana anlatıldı mı?",
            "hsg245": "D3.1 / C2.3",
            "yönler": {
                "anlatılmadı|bilinmiyordu": "→ D3.1 KÖK NEDEN (Tehlike eğitimi eksik)",
                "anlatıldı ama": "→ C3.5 (Güvensiz davranış pekiştirilmesi)"
            }
        },
        {
            "why": 5,
            "soru": "Cihazı sökülemez/devre dışı bırakılamaz hale getirecek teknik veya idari kontrol var mı?",
            "hsg245": "D5.6 / D4.1",
            "yönler": {
                "yok|tasarımda düşünülmemiş": "→ KÖK NEDEN: D5.6 (Hata-toleranslı tasarım yok)",
                "prosedür yok|izin sistemi yok": "→ KÖK NEDEN: D4.4 (İş izin sistemi) veya D4.5 (LOTO)"
            }
        }
    ],

    "B2.1": [
        {
            "why": 1,
            "soru": "Hangi ekipman ne şekilde arızalandı? Arıza nasıl ortaya çıktı?",
            "hsg245": "B2.1",
            "yönler": {}
        },
        {
            "why": 2,
            "soru": "Son bakım ne zaman yapılmıştı? Planlı bakım programı var mıydı?",
            "hsg245": "D6.1 / D6.2",
            "yönler": {
                "bakım yok|program yok|bilinmiyor": "→ D6.1 (Bakım stratejisi eksik) KÖK NEDEN",
                "yapılmış ama yetersiz|hatalı": "→ D6.2 (Bakım işçiliği)",
                "ertelendi|zaman yoktu|bütçe": "→ D6.6 (Ertelenmiş bakım) → D1.4 Baskı"
            }
        },
        {
            "why": 3,
            "soru": "Arıza öncesinde uyarı belirtisi var mıydı? (gürültü, titreşim, performans düşüşü...)",
            "hsg245": "B2.7 / D6.3 / D6.5",
            "yönler": {
                "vardı ama|rapor edilmedi|görmezden gelindi": "→ D1.7 (Raporlama kültürü) veya D2.5",
                "vardı ve rapor edildi ama önlem alınmadı": "→ D4.2 (Kontrol uygulanmıyor) veya D1.4",
                "belirti yoktu|ani arıza|gizli kusur": "→ B2.7 (Gizli kusur) → D6.3 Muayene eksik"
            }
        },
        {
            "why": 4,
            "soru": "Bu ekipman için düzenli muayene/test programı var mıydı?",
            "hsg245": "D6.3 / D6.1",
            "yönler": {
                "yok|yapılmıyor": "→ D6.3 (Muayene eksikliği) KÖK NEDEN",
                "var ama atlandı|ihmal edildi": "→ D6.2 (Bakım uygulaması) veya D1.4 Baskı",
                "yapıldı ama bulamadı": "→ D6.3 (Muayene yöntemi yetersiz)"
            }
        },
        {
            "why": 5,
            "soru": "Aynı veya benzer ekipman daha önce de arızalandı mı? Bu arızadan ders alındı mı?",
            "hsg245": "D6.5 / D1.7",
            "yönler": {
                "evet|tekrarlayan|daha önce de": "→ KÖK NEDEN: D6.5 (Tekrarlayan arızadan ders alınmıyor)",
                "raporlanmadı|kayıt yok": "→ KÖK NEDEN: D1.7 (Raporlama kültürü) veya D2.5",
                "hayır|ilk kez": "→ KÖK NEDEN: D6.1 (Bakım stratejisi yetersiz)"
            }
        }
    ],

    "B4.4": [
        {
            "why": 1,
            "soru": "Düşme tehlikesi neredeydi? Kaç metre yüksekti? Bariyer veya korkuluk var mıydı?",
            "hsg245": "B4.4",
            "yönler": {}
        },
        {
            "why": 2,
            "soru": "Bariyer/korkuluk hiç yoktu mu, yoksa vardı ama yeterli değil miydi?",
            "hsg245": "D5.1 / D4.1 / A1.1",
            "yönler": {
                "hiç yoktu|kurulmamış": "→ D5.1 (Tasarım/kurulum eksik) veya D4.1 (Risk analizi yok)",
                "vardı ama söküldü|kaldırıldı": "→ A3.5 gibi → kim kaldırdı? neden?",
                "yetersizdi|standart altı": "→ D5.1 (Tasarım hatası) veya D4.3 (Değişim yönetimi)"
            }
        },
        {
            "why": 3,
            "soru": "Yüksekte çalışma izni (iş izni sistemi) uygulandı mı? Güvenlik planı yapıldı mı?",
            "hsg245": "D4.4 / D4.1",
            "yönler": {
                "izin yok|sistem yok": "→ D4.4 (İş izin sistemi eksik) KÖK NEDEN",
                "izin var ama koşullar kontrol edilmedi": "→ D4.4 (Etkisiz iş izni)",
                "plan yapıldı ama eksik": "→ D4.1 (Risk analizi yetersiz)"
            }
        },
        {
            "why": 4,
            "soru": "Çalışanlar yüksekte çalışma tehlikeleri ve emniyet ekipmanları hakkında eğitim almış mıydı?",
            "hsg245": "D3.1 / D3.3",
            "yönler": {
                "eğitim yok|almamış": "→ D3.1 KÖK NEDEN",
                "eğitim var ama pratik yok": "→ D3.3 (Yetersiz pratik eğitim)",
                "almış ama uygulamadı": "→ D1.2 (Gözetim eksikliği) veya D1.5"
            }
        },
        {
            "why": 5,
            "soru": "Yüksekte çalışma için kurumsal bir prosedür/standart var mı? Düzenli denetleniyor mu?",
            "hsg245": "D1.2 / D4.1 / D5.2",
            "yönler": {
                "yok|tanımlanmamış": "→ KÖK NEDEN: D4.1 (Prosedür/risk analizi eksik)",
                "var ama denetlenmiyor": "→ KÖK NEDEN: D1.2 (Yetersiz gözetim)",
                "denetleniyor ama eksikler giderilmiyor": "→ KÖK NEDEN: D4.2 (Kontrol takibi yok)"
            }
        }
    ],

    "A4.5": [
        {
            "why": 1,
            "soru": "Hata tam olarak ne oldu? Hangi adımda/anda yanlış yapıldı?",
            "hsg245": "A4.5",
            "yönler": {}
        },
        {
            "why": 2,
            "soru": "Hata anında çalışanın dikkatini dağıtan bir şey var mıydı? (gürültü, konuşma, stres...)",
            "hsg245": "A4.1 / C2.5 / B4.2",
            "yönler": {
                "dikkat dağıtıcı|bölündü|kesildi": "→ A4.1 (Dikkat dağınıklığı) → neden sürekli?",
                "stres|baskı|kaygı": "→ C2.5 (Duygusal durum) veya D1.4 (Baskı)",
                "yorgun|uzun vardiya": "→ C1.4 (Yorgunluk) → D3.5 (İş yükü)"
            }
        },
        {
            "why": 3,
            "soru": "Bu işlem rutin miydi, yoksa nadir yapılan bir görev miydi?",
            "hsg245": "A4.6 / C2.6 / D3.3",
            "yönler": {
                "rutin|her gün|otomatik": "→ A4.6 (Rutin eylem hatası) → D5.3 HMI/tasarım",
                "nadir|ilk kez|yeni": "→ C2.6 (Zihinsel model eksik) → D3.3 eğitim",
                "karmaşık|çok adımlı": "→ A4.7 (Görev karmaşıklığı) → D5.3 tasarım"
            }
        },
        {
            "why": 4,
            "soru": "Görev, hataları önleyecek şekilde tasarlandı mı? (kontrol listesi, çift onay, yanlışlık-korrektör...)",
            "hsg245": "D5.3 / D5.6 / D4.1",
            "yönler": {
                "yok|tasarlanmamış": "→ D5.6 (Hata-toleranslı tasarım eksik) KÖK NEDEN",
                "var ama kullanılmıyor": "→ D4.2 (Kontrol uygulanmıyor) veya D1.2",
                "yetersiz|eski": "→ D5.3 (Kötü HMI/ergonomi) veya D4.3 (Değişim yönetimi)"
            }
        },
        {
            "why": 5,
            "soru": "Benzer hatalar daha önce oldu mu? Ne öğrenildi?",
            "hsg245": "D1.7 / D6.5",
            "yönler": {
                "evet|tekrar|ilk değil": "→ KÖK NEDEN: D6.5 veya D1.7 (Öğrenme kültürü yok)",
                "raporlanmadı": "→ KÖK NEDEN: D1.7 (Raporlama kültürü)",
                "hayır|ilk kez": "→ KÖK NEDEN: D5.6 (Sistem tasarımı insan hatasını önlemiyor)"
            }
        }
    ],

    # Diğer kodlar için basit ama farklılaştırıcı ağaç
    "A1.5": [
        {"why": 1, "soru": "Prosedür ne zaman yazılmıştı? Son güncelleme ne zamandı?", "hsg245": "A1.5", "yönler": {}},
        {"why": 2, "soru": "Prosedürün hatalı/güncel olmayan kısmı neydi? Gerçek saha koşullarını yansıtıyor muydu?", "hsg245": "A1.5/A1.8", "yönler": {"yansıtmıyor|eski|değişmiş": "→ D4.3 (Değişim yönetimi) veya D4.1 (Risk analizi güncellenmemiş)"}},
        {"why": 3, "soru": "Prosedür gözden geçirme/güncelleme süreci var mıydı? Kim sorumlu?", "hsg245": "D4.3/D4.1", "yönler": {"yok|belirlenmemiş": "→ D4.1 KÖK NEDEN", "var ama yapılmadı": "→ D4.3 (Değişim yönetimi eksik)"}},
        {"why": 4, "soru": "Ekipman, süreç veya koşullarda prosedürü güncellemesi gereken bir değişiklik oldu mu?", "hsg245": "D4.3", "yönler": {}},
        {"why": 5, "soru": "Çalışanlar güncel olmayan prosedürü nasıl rapor edebilir? Bu kanallar etkin mi?", "hsg245": "D1.7/D2.5", "yönler": {"yok|kanal yok": "→ KÖK NEDEN: D1.7 (Raporlama kültürü eksik)", "var ama": "→ KÖK NEDEN: D4.2 (Takip mekanizması çalışmıyor)"}},
    ],

    "B3.2": [
        {"why": 1, "soru": "Elektrik enerjisine nasıl maruz kalındı? Enerji kesilmiş miydi?", "hsg245": "B3.2", "yönler": {}},
        {"why": 2, "soru": "LOTO (Kilitleme/Etiketleme) prosedürü uygulandı mı?", "hsg245": "D4.5", "yönler": {"uygulanmadı|yoktu": "→ D4.5 (LOTO eksikliği) KÖK NEDEN", "uygulandı ama|eksik": "→ D4.5 (Etkisiz LOTO)"}},
        {"why": 3, "soru": "LOTO prosedürü hakkında eğitim verilmiş miydi?", "hsg245": "D3.1", "yönler": {"eğitim yok|almamış": "→ D3.1 KÖK NEDEN", "almış ama": "→ D4.4 veya D1.2"}},
        {"why": 4, "soru": "Elektrikli ekipman için risk değerlendirmesi ve güvenli çalışma prosedürü var mıydı?", "hsg245": "D4.1/D4.4", "yönler": {}},
        {"why": 5, "soru": "Bu tür işlerin öncesinde çalışma izninin verilip verilmediğini kim denetliyor?", "hsg245": "D1.2/D4.4", "yönler": {"kimse|denetim yok": "→ KÖK NEDEN: D1.2 (Gözetim eksik)", "var ama": "→ KÖK NEDEN: D4.4 (İş izin sistemi etkisiz)"}},
    ],
}

# Ağaçta tanımlı olmayan kodlar için genel yedek soru seti
GENERIC_FIVE_WHY = [
    {"why": 1, "soru": "Olay tam olarak nasıl gerçekleşti? Kronolojik sırayla anlatabilir misiniz?", "hsg245": "Genel", "yönler": {}},
    {"why": 2, "soru": "Bu duruma yol açan doğrudan tetikleyici faktör neydi?", "hsg245": "Genel", "yönler": {}},
    {"why": 3, "soru": "Neden bu durum oluşabildi? Hangi savunma/kontrol mekanizması çalışmadı?", "hsg245": "D4.1/D4.2", "yönler": {}},
    {"why": 4, "soru": "Bu kontrol mekanizması neden çalışmadı? Kaynak, eğitim veya gözetim eksikliği mi?", "hsg245": "D3.1/D1.2/D3.5", "yönler": {}},
    {"why": 5, "soru": "Organizasyonel düzeyde bu zayıflığın kök nedenini oluşturan temel eksiklik nedir?", "hsg245": "D1.1/D4.1/D5.1", "yönler": {}},
]


def get_five_why_questions(immediate_cause_code: str) -> list:
    """Seçilen immediate cause koduna göre 5-Why soru ağacını döndür"""
    return FIVE_WHY_TREE.get(immediate_cause_code, GENERIC_FIVE_WHY)


def detect_branch_from_answer(answer: str, yonler: dict) -> str:
    """
    Kullanıcı cevabına göre yönlendirme metnini bul.
    Basit anahtar kelime eşleştirme.
    """
    answer_lower = answer.lower()
    for keywords_str, direction in yonler.items():
        keywords = [k.strip() for k in keywords_str.split("|")]
        if any(kw in answer_lower for kw in keywords):
            return direction
    return ""


def get_immediate_cause_list() -> list:
    """Immediate cause listesi"""
    return [f"{code} — {desc}" for code, desc in IMMEDIATE_CAUSES.items()]


# ─────────────────────────────────────────────────────────────
# CLI — İnteraktif Terminal Testi (Gradio gerektirmez)
# ─────────────────────────────────────────────────────────────

def _clr(code: str) -> str:
    """ANSI renk kodları"""
    colors = {"RED": "\033[91m", "YEL": "\033[93m", "GRN": "\033[92m",
              "BLU": "\033[94m", "MAG": "\033[95m", "CYN": "\033[96m",
              "BOLD": "\033[1m", "DIM": "\033[2m", "RST": "\033[0m"}
    return colors.get(code, "")


def _sep(char="─", n=70):
    print(f"{_clr('DIM')}{char * n}{_clr('RST')}")


def _header(text: str):
    _sep("═")
    print(f"{_clr('BOLD')}{_clr('BLU')}  {text}{_clr('RST')}")
    _sep("═")


def _ask(prompt: str) -> str:
    """Kullanıcıdan girdi al, boş bırakılamaz"""
    while True:
        try:
            val = input(f"\n{_clr('YEL')}❓ {prompt}{_clr('RST')}\n   > ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{_clr('RED')}[Çıkış]{_clr('RST')}")
            sys.exit(0)
        if val:
            return val
        print(f"  {_clr('RED')}Boş bırakılamaz, lütfen bir şey yazın.{_clr('RST')}")


def _choose(options: list, title: str) -> tuple:
    """Numaralı liste göster, seçim al. (index, value) döner."""
    print(f"\n{_clr('BOLD')}{title}{_clr('RST')}")
    _sep()
    for i, opt in enumerate(options, 1):
        print(f"  {_clr('CYN')}{i:>2}.{_clr('RST')} {opt}")
    _sep()
    while True:
        try:
            raw = input(f"  Seçiminiz (1-{len(options)}): ").strip()
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return idx, options[idx]
            print(f"  {_clr('RED')}Geçersiz numara.{_clr('RST')}")
        except (ValueError, KeyboardInterrupt, EOFError):
            print(f"\n{_clr('RED')}[Çıkış]{_clr('RST')}")
            sys.exit(0)


def run_cli():
    """Terminal tabanlı interaktif 5-Why analizi"""
    _header("HSG245 — 5-Why Kök Neden Analizi (CLI)")

    # ── Olay açıklaması ──────────────────────────────────────
    print(f"\n{_clr('BOLD')}ADIM 1 — Olay Açıklaması{_clr('RST')}")
    print(f"{_clr('DIM')}  Kısaca ne olduğunu anlat (kim, ne, nerede, sonuç){_clr('RST')}")
    incident = _ask("Olay açıklaması")

    # ── Immediate Cause seçimi ───────────────────────────────
    print(f"\n{_clr('BOLD')}ADIM 2 — Immediate Cause Seç{_clr('RST')}")
    print(f"{_clr('DIM')}  A=Davranış kodları, B=Koşul kodları — Sahadan topladığın bilgiye göre{_clr('RST')}")
    cause_list = get_immediate_cause_list()
    _, selection = _choose(cause_list, "Immediate Cause (İlk Görünür Neden)")
    code = selection.split(" — ")[0].strip()
    desc = IMMEDIATE_CAUSES[code]

    print(f"\n  {_clr('GRN')}✔ Seçildi:{_clr('RST')} {_clr('BOLD')}{code}{_clr('RST')} — {desc}")

    # ── 5-Why soruları ───────────────────────────────────────
    questions = get_five_why_questions(code)
    answers = []
    directions = []

    _sep("─")
    print(f"{_clr('BOLD')}ADIM 3 — 5-Why Derinleştirme{_clr('RST')}")
    print(f"{_clr('DIM')}  Her soruyu dürüstçe cevapla. Cevabın sonraki yönü belirler.{_clr('RST')}")

    for q in questions:
        _sep()
        print(f"  {_clr('BOLD')}{_clr('BLU')}Why-{q['why']} / {len(questions)}{_clr('RST')}")
        print(f"  {_clr('BOLD')}{q['soru']}{_clr('RST')}")
        print(f"  {_clr('DIM')}HSG245 odak: {q['hsg245']}{_clr('RST')}")

        answer = _ask("Cevabınız")
        answers.append(answer)

        direction = detect_branch_from_answer(answer, q.get("yönler", {}))
        directions.append(direction)

        if direction:
            print(f"\n  {_clr('MAG')}🔀 Yönlendirme: {direction}{_clr('RST')}")
        else:
            print(f"  {_clr('DIM')}  (Bu cevap için belirgin bir yön yok, devam){_clr('RST')}")

    # ── Özet ────────────────────────────────────────────────
    _header("ANALİZ ÖZET")

    print(f"\n{_clr('BOLD')}🔴 Immediate Cause:{_clr('RST')} {code} — {desc}")
    print(f"{_clr('BOLD')}📋 Olay:{_clr('RST')} {incident}")

    print(f"\n{_clr('BOLD')}Why Zinciri:{_clr('RST')}")
    for i, (q, a, d) in enumerate(zip(questions, answers, directions), 1):
        print(f"\n  {_clr('CYN')}Why-{i}:{_clr('RST')} {q['soru']}")
        print(f"  {_clr('GRN')}→ {a}{_clr('RST')}")
        if d:
            print(f"  {_clr('MAG')}🔀 {d}{_clr('RST')}")

    # Kök neden tespiti
    all_directions = [d for d in directions if d]
    root_causes = []
    for d in all_directions:
        for part in d.replace("→", "").split("veya"):
            p = part.strip()
            if p and p not in root_causes:
                root_causes.append(p)

    print(f"\n{_clr('BOLD')}🟣 Tespit Edilen Olası Kök Nedenler (HSG245):{_clr('RST')}")
    if root_causes:
        for rc in root_causes:
            print(f"  {_clr('MAG')}• {rc}{_clr('RST')}")
    else:
        print(f"  {_clr('DIM')}Belirgin kök neden yönlendirmesi tespit edilemedi.{_clr('RST')}")

    print(f"\n{_clr('DIM')}⚠️  Bu kodlar cevaplara göre önerilerdir — tam onay için ek araştırma gerekebilir.{_clr('RST')}")

    # Yeni analiz?
    _sep("═")
    again = input(f"\n{_clr('YEL')}🔄 Yeni bir olay analiz etmek ister misin? (e/h): {_clr('RST')}").strip().lower()
    if again in ("e", "evet", "y", "yes"):
        print()
        run_cli()
    else:
        print(f"\n{_clr('GRN')}✅ Analiz tamamlandı. Görüşmek üzere!{_clr('RST')}\n")


if __name__ == "__main__":
    run_cli()


# ─────────────────────────────────────────────────────────────
# HITL → AGENT KÖPRÜSÜ
# Chatbot state'ini RootCauseAgentV2'ye gönderilecek formata çevirir.
# Mevcut engine koduna dokunulmaz — sadece dönüşüm fonksiyonu.
# ─────────────────────────────────────────────────────────────

def build_investigation_data(state: dict) -> dict:
    """
    gradio_chat_5why_v2 chatbot state'inden RootCauseAgentV2'nin
    _prepare_incident_summary() metoduna aktarılacak veri paketini oluşturur.

    Döndürülen dict RootCauseAgentV2.analyze_root_causes(investigation_data=...)
    parametresi olarak kullanılır.

    Kullanıcının her farklı cevabı → farklı kök neden üretilmesini sağlayan
    kilit bilgi "five_why_answers" listesidir.
    """
    answers    = state.get("answers", [])
    questions  = state.get("questions", [])
    directions = state.get("directions", [])

    n = max(len(answers), len(questions))

    five_why_answers = []
    for i in range(n):
        q   = questions[i] if i < len(questions) else {}
        ans = answers[i]   if i < len(answers)   else ""
        d   = directions[i] if i < len(directions) else ""
        five_why_answers.append({
            "why_level":          i + 1,
            "question":           q.get("soru", ""),
            "hsg245_focus":       q.get("hsg245", ""),
            "user_answer":        ans,
            "suggested_direction": d,
        })

    cause_code = state.get("cause_code", "")

    return {
        # Temel olay bilgisi — _prepare_incident_summary önce "description" arar
        "description":            state.get("incident", ""),
        "immediate_cause_code":   cause_code,
        "immediate_cause_desc":   IMMEDIATE_CAUSES.get(cause_code, ""),

        # KILIT: kullanıcının gerçek cevapları
        "five_why_answers":       five_why_answers,

        # Bağlam
        "hitl_context": {
            "questions_asked":     len(questions),
            "answers_collected":   len(answers),
            "keyword_directions":  [d for d in directions if d],
        },
    }
