"""
HSG245 Knowledge Base - Basit Sözlük Yapısı
RAG/Veritabanı gerektirmez. Doğrudan Python sözlüğü olarak tutulur. No model 
"""


HSG245_TAXONOMY = {
    "immediate_causes_actions": """
A. İLK GÖRÜNÜR NEDENLER – DAVRANIŞLAR (IMMEDIATE CAUSES - ACTIONS)

A1. Prosedür ve Kural İhlali
A1.1 Bireysel kural/prosedür ihlali
A1.2 Grup/takım kural ihlali
A1.3 Gözetim/yönetim kural ihlali
A1.4 Yetkisiz bilinçli sapma
A1.5 Yanlış veya güncel olmayan prosedür kullanımı
A1.6 Prosedür var ancak saha koşullarında uygulanamaz
A1.7 Çelişen prosedürler veya talimatlar
A1.8 Prosedür gerçekçi olmayan varsayımlar içeriyor

A2. Alet, Ekipman, Tesis veya Araçların Uygunsuz Kullanımı
A2.1 Ekipman/tesis/aracın yanlış veya uygunsuz kullanımı
A2.2 El aletlerinin yanlış veya uygunsuz kullanımı
A2.3 Arızası bilinen ekipman/araç kullanımı
A2.4 Arızası bilinen alet kullanımı
A2.5 Alet, ekipman veya malzemelerin yanlış yerleştirilmesi veya depolanması
A2.6 Tasarım limitleri veya çalışma zarfı dışında kullanım
A2.7 Ekipmanın geçici modifikasyonu veya derme çatma kullanımı

A3. Koruyucu Ekipman veya Yöntemlerin Kullanılmaması
A3.1 KKD/koruyucu yöntem ihtiyacının fark edilmemesi
A3.2 Gerekli KKD/koruyucu yöntemlerin kullanılmaması
A3.3 KKD/koruyucu yöntemlerin yanlış kullanımı
A3.4 KKD/koruyucu yöntemlerin mevcut veya uygun olmaması
A3.5 Güvenlik/koruyucu cihazların sökülmesi, baypas edilmesi veya devre dışı bırakılması
A3.6 KKD/korunmanın işin yapılmasına engel olması
A3.7 KKD seçiminin tehlike şiddetiyle eşleşmemesi

A4. İnsan Hatası, Dikkat ve Davranışsal Boşluklar
A4.1 Dikkat dağınıklığı veya bölünmüş dikkat
A4.2 Çevresel tehlikelerin fark edilmemesi
A4.3 Uygunsuz veya güvensiz iş yeri davranışı
A4.4 Diğerlerini uyarmada başarısızlık
A4.5 Kasıtsız insan hatası (sürçme/dalgınlık)
A4.6 Otomatik/rutin eylemlerin bilinçli kontrol olmadan yapılması
A4.7 Görev karmaşıklığının insan kapasitesini aşması
A4.8 Zaman baskısının bilişsel kestirmelere yol açması
""",

    "immediate_causes_conditions": """
B. İLK GÖRÜNÜR NEDENLER – KOŞULLAR (IMMEDIATE CAUSES - CONDITIONS)

B1. Koruyucu ve Uyarıcı Sistem Hataları
B1.1 Koruyucu cihazların etkisiz olması
B1.2 Koruyucu cihazların arızalı olması
B1.3 Arızalı kişisel koruyucu donanım (KKD)
B1.4 Uyarı/alarm sistemlerinin etkisiz olması
B1.5 Uyarı/alarm sistemlerinin arızalı veya mevcut olmaması
B1.6 Koruyucu sistemlerin yönetim kontrolü olmadan devre dışı bırakılması

B2. Ekipman, Alet ve Araç Durumu veya Hazırlığı
B2.1 Ekipman/tesis arızası
B2.2 Yetersiz ekipman/tesis hazırlığı
B2.3 Alet arızası
B2.4 Yetersiz alet hazırlığı
B2.5 Araç arızası
B2.6 Yetersiz araç hazırlığı
B2.7 Operatör tarafından tespit edilemeyen gizli kusur

B3. Tehlikeli Enerji veya Madde Maruziyeti
B3.1 Yangın veya patlama
B3.2 Elektrik enerjisi (enerjili sistemler)
B3.3 Elektriksel olmayan enerji (basınç, mekanik, hidrolik, yerçekimi)
B3.4 Tehlikeli kimyasallar veya toksik maddeler
B3.5 Yanıcı toz / toz patlaması
B3.6 Oksijen eksikliği olan atmosfer
B3.7 Radyasyon (iyonlaştırıcı / iyonlaştırıcı olmayan)
B3.8 Aşırı sıcaklık (sıcak/soğuk)
B3.9 Gürültü veya titreşim
B3.10 Doğal olaylar (fırtına, deprem, sel)
B3.11 Depolanmış enerjinin beklenmedik şekilde açığa çıkması

B4. Çalışma Alanı Düzeni ve Çevresel Koşullar
B4.1 Sıkışık veya kötü düzenlenmiş yerleşim
B4.2 Yetersiz aydınlatma
B4.3 Yetersiz havalandırma
B4.4 Korunmasız yükseklik veya düşme tehlikesi
B4.5 Ekipmanın uygunsuz konuma yerleştirilmesi
B4.6 Kötü tertip/düzen/temizlik (Housekeeping)
B4.7 Kötü veya okunaksız etiketleme/işaretleme
B4.8 Uygunsuz çevresel koşullar (sıcaklık, nem)
B4.9 Çalışma alanı tasarımının hata olasılığını artırması
""",

    "root_causes_personal": """
C. SİSTEMİK NEDENLER - KİŞİSEL FAKTÖRLER (ROOT CAUSES - PERSONAL)

C1. Fiziksel Kapasite ve Sağlık
C1.1 Duyusal bozukluklar (görme, işitme, algılama)
C1.2 Fiziksel kısıtlamalar (güç, uzanma, antropometri)
C1.3 Tıbbi durumlar veya hastalık
C1.4 Yorgunluk (akut veya kronik)
C1.5 İlaç, alkol veya madde etkisi

C2. Bilişsel ve Zihinsel Yetenek
C2.1 Hafıza veya dikkat kısıtlamaları
C2.2 Zayıf koordinasyon veya reaksiyon süresi
C2.3 Zayıf mekanik veya sistem kavrayışı
C2.4 Yetersiz muhakeme veya karar verme yeteneği
C2.5 Performansı etkileyen duygusal durum (stres, korku, kaygı)
C2.6 Göreve özgü zihinsel modellerin eksikliği

C3. Beceri, Yetkinlik ve Davranışsal Şartlanma
C3.1 Yetersiz beceri değerlendirmesi
C3.2 Yetersiz beceri uygulaması
C3.3 Koçluk veya geri bildirim eksikliği
C3.4 Becerinin nadiren uygulanması veya körelmesi
C3.5 Güvensiz davranışın pekiştirilmesi veya düzeltilmemesi
C3.6 Doğru davranışın olumlu pekiştirilmemesi
""",

    "root_causes_organizational": """
D. SİSTEMİK NEDENLER - ORGANİZASYONEL FAKTÖRLER (ROOT CAUSES - ORGANIZATIONAL)

D1. Liderlik, Gözetim ve Güvenlik Kültürü
D1.1 Güvenliğe yönelik zayıf liderlik taahhüdü
D1.2 Yetersiz gözetim veya denetim
D1.3 Hesap verebilirlik eksikliği
D1.4 Üretim baskısının güvenliğin önüne geçmesi
D1.5 Sapmaların normalleşmesi (Kanıksama)
D1.6 Etkisiz İş Durdurma yetkisi
D1.7 Zayıf raporlama ve öğrenme kültürü
D1.8 Yetersiz görünür saha liderliği
D1.9 Yönetimin bilinen sapmalara tolerans göstermesi

D2. İletişim ve Bilgi Yönetimi
D2.1 Etkisiz iletişim (sözlü/yazılı/dijital)
D2.2 Talimatların yanlış anlaşılması veya belirsizliği
D2.3 Standart terminoloji eksikliği
D2.4 İletişim altyapısının kalitesizliği
D2.5 Yetersiz olay raporlama ve takip
D2.6 Vardiya devir tesliminde bilgi aktarım eksikliği
D2.7 Bilgi aşırı yüklemesi veya kötü önceliklendirme

D3. Eğitim, Yetkinlik ve İşgücü Yönetimi
D3.1 Eğitimin sağlanmaması veya yetersiz olması
D3.2 Eğitim ihtiyaçlarının belirlenmemesi
D3.3 Yetersiz pratik/iş başı eğitimi
D3.4 Yetkinliğin doğrulanmaması
D3.5 Yetersiz personel veya iş yükü planlaması
D3.6 Eğitim etkinliğinin değerlendirilmemesi

D4. Risk, Değişim ve İş Kontrol Sistemleri
D4.1 Risk analizinin yapılmaması veya yetersiz olması
D4.2 Risk kontrollerinin uygulanmaması veya takip edilmemesi
D4.3 Değişim yönetiminin etkisiz olması veya atlanması
D4.4 İş izin sisteminin etkisiz olması
D4.5 Enerji izolasyonunun (LOTO) etkisiz olması
D4.6 Geçici risk kontrollerinin kalıcı muamelesi görmesi

D5. Mühendislik, Tasarım ve Teknik Sistemler
D5.1 Tasarım hataları veya uygunsuzlukları
D5.2 Yetersiz tasarım gözden geçirme
D5.3 Kötü HMI/ergonomi/alarm yönetimi
D5.4 Yetersiz tehlikeli alan sınıflandırması
D5.5 Risk çalışmalarının tasarıma yetersiz entegrasyonu
D5.6 Tasarımın insan hatası toleransını dikkate almaması

D6. Bakım, Varlık Bütünlüğü ve Güvenilirlik
D6.1 Yetersiz bakım stratejisi veya planlaması
D6.2 Yetersiz bakım uygulaması veya işçilik
D6.3 Yetersiz muayene, test veya kalibrasyon
D6.4 Yetersiz dokümantasyon veya kayıtlar
D6.5 Tekrarlayan arızalardan ders alınmaması
D6.6 Ertelenmiş bakımın normal kabul edilmesi
D6.7 Atanan bakım tipinin uygunsuz olması

D7. Yüklenici ve Tedarik Zinciri Yönetimi
D7.1 Yetersiz yüklenici ön yeterlilik değerlendirmesi
D7.2 Yetersiz yüklenici gözetimi
D7.3 Yüklenici yetkinliğinin doğrulanmaması
D7.4 Zayıf yüklenici güvenlik kültürü entegrasyonu
D7.5 Hatalı tedarik edilen malzeme/ekipman
D7.6 Yüklenici teşviklerinin güvenlikle uyumsuz olması

D8. Acil Durum Hazırlığı
D8.1 Acil durum planları veya tatbikatlarının yetersizliği
D8.2 Acil durum ekipmanının mevcut olmaması veya etkisizliği
D8.3 Dış kurumlarla zayıf koordinasyon
D8.4 Organizasyonel kontrol dışındaki dış olaylar
D8.5 Acil durum müdahale rollerinin belirsiz olması
"""
}


def get_category_text(category: str) -> str:
    """
    Kategori koduna göre ilgili metni döndürür.
    
    Args:
        category: 'A', 'B', 'C' veya 'D'
    
    Returns:
        str: Kategori metni
    """
    mapping = {
        'A': 'immediate_causes_actions',
        'B': 'immediate_causes_conditions',
        'C': 'root_causes_personal',
        'D': 'root_causes_organizational'
    }
    
    key = mapping.get(category.upper())
    if key:
        return HSG245_TAXONOMY.get(key, "")
    return ""


def get_all_categories() -> str:
    """Tüm kategorileri birleştirilmiş metin olarak döndürür"""
    return "\n\n".join([
        HSG245_TAXONOMY['immediate_causes_actions'],
        HSG245_TAXONOMY['immediate_causes_conditions'],
        HSG245_TAXONOMY['root_causes_personal'],
        HSG245_TAXONOMY['root_causes_organizational']
    ])
