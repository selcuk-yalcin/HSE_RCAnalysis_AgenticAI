"""
HSG245 Knowledge Base - Basit Sözlük Yapısı
RAG/Veritabanı gerektirmez. Doğrudan Python sözlüğü olarak tutulur.

V2 DEĞİŞİKLİKLER:
- Her koda "Tipik Senaryo" ve "Bu Kodu Seçme" notları eklendi
- Model artık kodları birbirinden ayırt edebilir
- Jenerik/genel kodların yanlış seçimi önlenir
"""


HSG245_TAXONOMY = {
    "immediate_causes_actions": """
A. İLK GÖRÜNÜR NEDENLER – DAVRANIŞLAR (IMMEDIATE CAUSES - ACTIONS)

A1. Prosedür ve Kural İhlali

A1.1 Bireysel kural/prosedür ihlali
  → Tipik: Tek bir çalışan bilinen bir kuralı veya yazılı prosedürü bilerek çiğnedi
  → Seçme: İhlal kasıtsızsa veya prosedürden habersizse → A4.5 veya A1.5

A1.2 Grup/takım kural ihlali
  → Tipik: Tüm ekip aynı kurala uymadı; norm haline gelmiş sapma
  → Seçme: Sadece bir kişi ihlal ettiyse → A1.1; yönetim farkındaysa → D1.5

A1.3 Gözetim/yönetim kural ihlali
  → Tipik: Yönetici veya formen bizzat güvensiz uygulamayı yaptı ya da onayladı
  → Seçme: Yönetim sadece göz yumuyorsa → D1.9

A1.4 Yetkisiz bilinçli sapma
  → Tipik: Çalışan, yetkisi olmadığını bilerek makineye müdahale etti, alanı değiştirdi
  → Seçme: Sapma kasıtsızsa → A4.5; prosedür yoksa → A1.5

A1.5 Yanlış veya güncel olmayan prosedür kullanımı
  → Tipik: Çalışan var olan prosedürü takip etti ama prosedür hatalı/eskimiş
  → Seçme: Prosedür yoksa → D4.1; çalışan prosedürü bilmiyorsa → D3.1

A1.6 Prosedür var ancak saha koşullarında uygulanamaz
  → Tipik: Yazılı talimat sahada fiziksel olarak uygulanamaz durumdaydı
  → Seçme: Prosedür uygulanabilirdi ama uygulanmadıysa → A1.1

A1.7 Çelişen prosedürler veya talimatlar
  → Tipik: İki farklı talimat birbirine zıt şey söylüyordu, çalışan birini seçmek zorunda kaldı
  → Seçme: Tek bir prosedür varsa ve yanlışsa → A1.5

A1.8 Prosedür gerçekçi olmayan varsayımlar içeriyor
  → Tipik: Prosedür masa başında yazılmış, sahada insan kapasitesini aşan varsayımlar içeriyor
  → Seçme: Prosedür gerçekçiyse ama uygulanmadıysa → A1.1

A2. Alet, Ekipman, Tesis veya Araçların Uygunsuz Kullanımı

A2.1 Ekipman/tesis/aracın yanlış veya uygunsuz kullanımı
  → Tipik: Ekipman amacı dışında kullanıldı (örn: yük asansörü insan taşımak için)
  → Seçme: Ekipman arızalıysa → B2.1; yanlış seçildiyse → D5.1

A2.2 El aletlerinin yanlış veya uygunsuz kullanımı
  → Tipik: Tornavida keski gibi kullanıldı; anahtar yerine pense kullanıldı
  → Seçme: Alet arızalıysa → B2.3; uygun alet yoksa → A3.4

A2.3 Arızası bilinen ekipman/araç kullanımı
  → Tipik: "Biraz sorunlu ama idare eder" denerek arızalı ekipmanla çalışıldı
  → Seçme: Arıza bilinmiyorsa → B2.7; bakım yapılmadıysa → D6.1

A2.4 Arızası bilinen alet kullanımı
  → Tipik: Kırık, çatlak veya hasarlı el aleti kullanımına devam edildi
  → Seçme: Arıza gizliyse → B2.7

A2.5 Alet, ekipman veya malzemelerin yanlış yerleştirilmesi veya depolanması
  → Tipik: Kimyasal yanlış konteynerde saklandı; ekipman geçit üzerine bırakıldı
  → Seçme: Depolama alanı yetersizse → B4.1

A2.6 Tasarım limitleri veya çalışma zarfı dışında kullanım
  → Tipik: Ekipman max kapasitesinin üzerinde yüklendi veya izin verilen sıcaklık aşıldı
  → Seçme: Limit bilinmiyorsa → D3.1; tasarım hatalıysa → D5.1

A2.7 Ekipmanın geçici modifikasyonu veya derme çatma kullanımı
  → Tipik: Tel, bant, tahta parçasıyla geçici onarım yapıldı ve kullanılmaya devam edildi
  → Seçme: Modifikasyon onaylıysa → D4.3

A3. Koruyucu Ekipman veya Yöntemlerin Kullanılmaması

A3.1 KKD/koruyucu yöntem ihtiyacının fark edilmemesi
  → Tipik: Çalışan tehlikeyi göremedi, KKD gerektiğini bilmiyordu
  → Seçme: Tehlike biliniyordu ama KKD kullanılmadıysa → A3.2

A3.2 Gerekli KKD/koruyucu yöntemlerin kullanılmaması
  → Tipik: KKD vardı, tehlike biliniyordu ama çalışan takmadı/uygulamadı
  → Seçme: KKD mevcut değilse → A3.4; rahatsızlık veriyorsa → A3.6

A3.3 KKD/koruyucu yöntemlerin yanlış kullanımı
  → Tipik: Baret yanlış takıldı, emniyet kemeri yanlış bağlandı
  → Seçme: KKD hiç kullanılmadıysa → A3.2

A3.4 KKD/koruyucu yöntemlerin mevcut veya uygun olmaması
  → Tipik: İstasyon KKD stoku boştu; mevcut KKD göreve uygun değildi
  → Seçme: KKD vardı ama kullanılmadıysa → A3.2

A3.5 Güvenlik/koruyucu cihazların sökülmesi, baypas edilmesi veya devre dışı bırakılması
  → Tipik: Makine koruyucusu "işi yavaşlatıyor" diye söküldü
  → Seçme: Cihaz arızalandıysa → B1.2; yönetim onayıyla yapıldıysa → D1.4

A3.6 KKD/korunmanın işin yapılmasına engel olması
  → Tipik: Eldiven hassas işi zorlaştırdığı için çıkarıldı
  → Seçme: KKD uygunsa ama tercih meselesiyse → A3.2

A3.7 KKD seçiminin tehlike şiddetiyle eşleşmemesi
  → Tipik: Kimyasal sıçramaya karşı normal gözlük kullanıldı, kimyasal gözlük yerine
  → Seçme: Hiç KKD yoksa → A3.4

A4. İnsan Hatası, Dikkat ve Davranışsal Boşluklar

A4.1 Dikkat dağınıklığı veya bölünmüş dikkat
  → Tipik: Telefon, gürültü veya başka bir kişinin müdahalesiyle dikkat bölündü
  → Seçme: Dikkat dağınıklığı sistematikse (sürekli kesintiler) → D5.3

A4.2 Çevresel tehlikelerin fark edilmemesi
  → Tipik: Islak zemin, düşük tavan, dönen parça görülmedi
  → Seçme: Tehlike işaretlenmemişse → B4.7; aydınlatma yetersizse → B4.2

A4.3 Uygunsuz veya güvensiz iş yeri davranışı
  → Tipik: Koşmak, şakalaşmak, dikkat dağıtıcı davranış
  → Seçme: Kasıtlı kural ihlaliyse → A1.1

A4.4 Diğerlerini uyarmada başarısızlık
  → Tipik: Tehlikeli bir durumu gören çalışan diğerlerini uyarmadı
  → Seçme: Uyarı sistemi yoksa → B1.4

A4.5 Kasıtsız insan hatası (sürçme/dalgınlık)
  → Tipik: Yanlış düğmeye basıldı, adım atlandı, yanlış valf açıldı — kasıt yok
  → Seçme: Hata kasıtlıysa → A1.1; yorgunluktan kaynaklıyorsa → C1.4

A4.6 Otomatik/rutin eylemlerin bilinçli kontrol olmadan yapılması
  → Tipik: Her gün yapılan rutin iş "uyku modunda" yapıldı, kritik adım atlandı
  → Seçme: İlk kez yapılan bir görevse → C2.6

A4.7 Görev karmaşıklığının insan kapasitesini aşması
  → Tipik: Aynı anda çok fazla değişken izlenmesi gerekiyordu
  → Seçme: Karmaşıklık tasarımdan kaynaklanıyorsa → D5.3; eğitim eksikse → D3.1

A4.8 Zaman baskısının bilişsel kestirmelere yol açması
  → Tipik: "Hızlı bitir" baskısıyla kontrol adımları atlandı
  → Seçme: Baskı yönetimden geliyorsa → D1.4
""",

    "immediate_causes_conditions": """
B. İLK GÖRÜNÜR NEDENLER – KOŞULLAR (IMMEDIATE CAUSES - CONDITIONS)

B1. Koruyucu ve Uyarıcı Sistem Hataları

B1.1 Koruyucu cihazların etkisiz olması
  → Tipik: Bariyer vardı ama tehlikeyi gerçekte durduramıyordu
  → Seçme: Cihaz tamamen arızalıysa → B1.2; kasıtlı devre dışıysa → A3.5

B1.2 Koruyucu cihazların arızalı olması
  → Tipik: Makine guard'ı kırık, limit switch yanmış, emniyet valfi sıkışmış
  → Seçme: Cihaz işlevsel ama yetersizse → B1.1; bakım yapılmamışsa → D6.1

B1.3 Arızalı kişisel koruyucu donanım (KKD)
  → Tipik: Baret çatlak, emniyet kemeri kopuk, eldiven delik
  → Seçme: KKD kullanılmadıysa → A3.2; yanlış seçildiyse → A3.7

B1.4 Uyarı/alarm sistemlerinin etkisiz olması
  → Tipik: Alarm vardı ama çok sık çalıştığı için kimse dikkate almıyordu
  → Seçme: Alarm hiç yoksa → B1.5; alarm arızalıysa → B1.5

B1.5 Uyarı/alarm sistemlerinin arızalı veya mevcut olmaması
  → Tipik: Dedektör pili bitmiş; o bölgede alarm sistemi hiç kurulmamış
  → Seçme: Alarm varsa ama etkisizse → B1.4

B1.6 Koruyucu sistemlerin yönetim kontrolü olmadan devre dışı bırakılması
  → Tipik: Bakım için devre dışı bırakılan sistem izinsiz ve habersiz açık kaldı
  → Seçme: Çalışan bilerek kapattıysa → A3.5; yönetim onayıyla yapıldıysa → D4.4

B2. Ekipman, Alet ve Araç Durumu veya Hazırlığı

B2.1 Ekipman/tesis arızası
  → Tipik: Konveyör durdu, kompresör patladı, vinç halatı koptu
  → Seçme: Arıza öngörülebilirdi ve bakım yapılmadıysa → D6.1; kullanıcı kaynaklıysa → A2.1

B2.2 Yetersiz ekipman/tesis hazırlığı
  → Tipik: Ekipman göreve hazır değildi; gerekli kontroller yapılmamıştı
  → Seçme: Ekipman arızalıysa → B2.1; bakım prosedürü yoksa → D6.1

B2.3 Alet arızası
  → Tipik: Tornavida kırıldı, matkap bitti, ölçüm aleti hatalı okuma yaptı
  → Seçme: Alet yanlış kullanıldıysa → A2.2; bakım yapılmamışsa → D6.3

B2.4 Yetersiz alet hazırlığı
  → Tipik: Alet göreve uygun değildi, eksik donanımla başlandı
  → Seçme: Alet arızalıysa → B2.3

B2.5 Araç arızası
  → Tipik: Forklift freni tutmadı, kamyon lastiği patladı
  → Seçme: Bakım yapılmamışsa → D6.1; yanlış kullanıldıysa → A2.1

B2.6 Yetersiz araç hazırlığı
  → Tipik: Araç günlük kontrol yapılmadan kullanıma alındı
  → Seçme: Araç arızalıysa → B2.5

B2.7 Operatör tarafından tespit edilemeyen gizli kusur
  → Tipik: Malzeme içinde çatlak, kaynak altında korozyon — görsel incelemeyle bulunamaz
  → Seçme: Kusur görünürse ve fark edilmediyse → A4.2; muayene yapılmadıysa → D6.3

B3. Tehlikeli Enerji veya Madde Maruziyeti

B3.1 Yangın veya patlama
  → Tipik: Tutuşma kaynağı yanıcı maddeyle temas etti
  → Seçme: Elektrik kaynaklıysa → B3.2; kimyasal kaynaklıysa → B3.4

B3.2 Elektrik enerjisi (enerjili sistemler)
  → Tipik: Enerji kesilmeden çalışma yapıldı; açık pano temas
  → Seçme: LOTO uygulanmadıysa → D4.5; izolasyon yetersizse → D5.1

B3.3 Elektriksel olmayan enerji (basınç, mekanik, hidrolik, yerçekimi)
  → Tipik: Basınçlı hava deşarj edilmeden müdahale; yük düştü
  → Seçme: Enerji izolasyonu yapılmadıysa → D4.5

B3.4 Tehlikeli kimyasallar veya toksik maddeler
  → Tipik: Kimyasal sıçraması, soluma veya cilt teması
  → Seçme: KKD kullanılmadıysa → A3.2; depolama hatalıysa → A2.5

B3.5 Yanıcı toz / toz patlaması
  → Tipik: Toz birikimi tutuşma kaynağıyla temas etti
  → Seçme: Temizlik yapılmamışsa → B4.6; havalandırma yetersizse → B4.3

B3.6 Oksijen eksikliği olan atmosfer
  → Tipik: Kapalı alanda gaz birikmesi sonucu oksijen düştü
  → Seçme: Gaz testi yapılmadıysa → D4.1; havalandırma yetersizse → B4.3

B3.7 Radyasyon (iyonlaştırıcı / iyonlaştırıcı olmayan)
  → Tipik: Kaynak ışığına maruziyet; radyasyon kaynağına yaklaşım
  → Seçme: KKD yoksa → A3.4

B3.8 Aşırı sıcaklık (sıcak/soğuk)
  → Tipik: Sıcak yüzeye dokunma; aşırı soğukta çalışma
  → Seçme: İzolasyon yoksa → D5.1; KKD yoksa → A3.4

B3.9 Gürültü veya titreşim
  → Tipik: Uzun süreli gürültüye maruziyet, titreşimli alet kullanımı
  → Seçme: KKD yoksa → A3.4; ölçüm yapılmadıysa → D4.1

B3.10 Doğal olaylar (fırtına, deprem, sel)
  → Tipik: Dış doğal olay altyapıyı etkiledi
  → Seçme: Acil durum planı yoksa → D8.1; öngörülebilirdi ve önlem alınmadıysa → D4.1

B3.11 Depolanmış enerjinin beklenmedik şekilde açığa çıkması
  → Tipik: Yay, hidrolik akümülatör veya kondansatör boşaltılmadan çalışıldı
  → Seçme: LOTO yoksa → D4.5

B4. Çalışma Alanı Düzeni ve Çevresel Koşullar

B4.1 Sıkışık veya kötü düzenlenmiş yerleşim
  → Tipik: Geçiş yolları malzemeyle dolu; ekipmanlar arası mesafe yetersiz
  → Seçme: Tasarım kaynaklıysa → D5.1; temizlik sorunuysa → B4.6

B4.2 Yetersiz aydınlatma
  → Tipik: Karanlık ortamda çalışma; lamba yanmıyor
  → Seçme: Kişi tehlikeyi fark edemediyse → A4.2

B4.3 Yetersiz havalandırma
  → Tipik: Duman, buhar veya gaz birikmesi
  → Seçme: KKD yoksa → A3.4; kapalı alan prosedürü yoksa → D4.1

B4.4 Korunmasız yükseklik veya düşme tehlikesi
  → Tipik: Bariyer yok, korkuluk eksik, çatı kenarı açık
  → Seçme: Bariyer vardı ama aşıldıysa → A1.1; tasarım hatasıysa → D5.1

B4.5 Ekipmanın uygunsuz konuma yerleştirilmesi
  → Tipik: Makine geçit üzerinde; acil stop ulaşılamaz yerde
  → Seçme: Çalışan yanlış yerleştirdiyse → A2.5

B4.6 Kötü tertip/düzen/temizlik (Housekeeping)
  → Tipik: Dökülen yağ temizlenmemiş; kablo karmaşası; atık yığını
  → Seçme: Temizlik prosedürü yoksa → D4.1; gözetim yoksa → D1.2

B4.7 Kötü veya okunaksız etiketleme/işaretleme
  → Tipik: Valf etiketi yok; tehlike uyarısı solmuş; yönlendirme eksik
  → Seçme: Tasarım aşamasında atlandıysa → D5.1

B4.8 Uygunsuz çevresel koşullar (sıcaklık, nem)
  → Tipik: Aşırı sıcak/soğuk ortamda çalışma; nem ekipmana zarar verdi
  → Seçme: Kişisel maruziyet sorunuysa → B3.8

B4.9 Çalışma alanı tasarımının hata olasılığını artırması
  → Tipik: Benzer görünümlü valfler yan yana; kritik buton erişilmez konumda
  → Seçme: Tasarım onaylıysa ama ergonomi kötüyse → D5.3
""",

    "root_causes_personal": """
C. SİSTEMİK NEDENLER - KİŞİSEL FAKTÖRLER (ROOT CAUSES - PERSONAL)

C1. Fiziksel Kapasite ve Sağlık

C1.1 Duyusal bozukluklar (görme, işitme, algılama)
  → Tipik: Görme/işitme sorunu tehlikeyi fark etmeyi engelledi
  → Seçme: Sorun geçiciyse (yorgunluk vb.) → C1.4; çevresel nedenliyse → B4.2

C1.2 Fiziksel kısıtlamalar (güç, uzanma, antropometri)
  → Tipik: Çalışanın boyu/kolu göreve uygun değil; yeterli güç yok
  → Seçme: Ergonomi tasarım sorunuysa → D5.3; iş ataması hatalıysa → D3.5

C1.3 Tıbbi durumlar veya hastalık
  → Tipik: Ani rahatsızlık (bayılma, kramp); kronik hastalık performansı etkiledi
  → Seçme: İlaç etkisiyse → C1.5; muayene yapılmadıysa → D3.4

C1.4 Yorgunluk (akut veya kronik)
  → Tipik: Uzun vardiya, uyku yoksunluğu, aşırı iş yükü dikkat düşürdü
  → Seçme: Yorgunluk organizasyon kaynaklıysa (fazla mesai zorunluluğu) → D3.5

C1.5 İlaç, alkol veya madde etkisi
  → Tipik: Reçeteli ilaç uyarı verdi; alkol etkisiyle iş yapıldı
  → Seçme: Test yapılmadıysa → D3.4; politika yoksa → D1.1

C2. Bilişsel ve Zihinsel Yetenek

C2.1 Hafıza veya dikkat kısıtlamaları
  → Tipik: Adım unutuldu; çok adımlı görevde kaybolundu
  → Seçme: Dikkat dağınıklığı anlık olaysa → A4.1; görev tasarımı sorunuysa → D5.3

C2.2 Zayıf koordinasyon veya reaksiyon süresi
  → Tipik: Tehlikeye yeterince hızlı tepki verilemedi
  → Seçme: Yaş/sağlık kaynaklıysa → C1.3

C2.3 Zayıf mekanik veya sistem kavrayışı
  → Tipik: Çalışan sistemin nasıl çalıştığını yanlış anladı
  → Seçme: Eğitim verilmediyse → D3.1; bilgi aktarılmadıysa → D2.6

C2.4 Yetersiz muhakeme veya karar verme yeteneği
  → Tipik: Kritik anda yanlış değerlendirme yapıldı
  → Seçme: Baskı altındaysa → D1.4; bilgi eksikse → D3.1

C2.5 Performansı etkileyen duygusal durum (stres, korku, kaygı)
  → Tipik: Baskı, kaygı veya korku konsantrasyonu bozdu
  → Seçme: Stres kaynağı organizasyonsa → D1.4; kişisel faktörse burada kal

C2.6 Göreve özgü zihinsel modellerin eksikliği
  → Tipik: Çalışan o sistem veya görev için zihinsel model oluşturamamış
  → Seçme: Eğitim eksikse → D3.1; deneyim eksikse → C3.4

C3. Beceri, Yetkinlik ve Davranışsal Şartlanma

C3.1 Yetersiz beceri değerlendirmesi
  → Tipik: Çalışan göreve uygun olmayan beceriyle atandı
  → Seçme: Değerlendirme yapılmadıysa → D3.4; iş ataması hatalıysa → D3.5

C3.2 Yetersiz beceri uygulaması
  → Tipik: Eğitim alındı ama pratikte uygulama yanlış
  → Seçme: Hiç eğitim verilmediyse → D3.1; pratik eğitim yoksa → D3.3

C3.3 Koçluk veya geri bildirim eksikliği
  → Tipik: Çalışan yanlış yapıyor ama kimse düzeltmiyor
  → Seçme: Gözetim yoksa → D1.2

C3.4 Becerinin nadiren uygulanması veya körelmesi
  → Tipik: Acil durum prosedürü yıllardır uygulanmadı; yetkinlik köreldi
  → Seçme: Tatbikat yapılmadıysa → D8.1

C3.5 Güvensiz davranışın pekiştirilmesi veya düzeltilmemesi
  → Tipik: Kural ihlali sürekli görmezden gelindi, çalışan "bu normal" sandı
  → Seçme: Yönetim farkındaysa → D1.9; kültür sorunuysa → D1.5

C3.6 Doğru davranışın olumlu pekiştirilmemesi
  → Tipik: Güvenli davranış hiç ödüllendirilmedi/takdir edilmedi
  → Seçme: Kültür sorunuysa → D1.1
""",

    "root_causes_organizational": """
D. SİSTEMİK NEDENLER - ORGANİZASYONEL FAKTÖRLER (ROOT CAUSES - ORGANIZATIONAL)

D1. Liderlik, Gözetim ve Güvenlik Kültürü

D1.1 Güvenliğe yönelik zayıf liderlik taahhüdü
  → Tipik: Üst yönetim güvenliği söylemde destekliyor ama davranışta değil;
           güvenlik bütçesi sürekli kesiliyor; yöneticiler sahaya inmiyor
  → Seçme: Sadece tek bir yöneticinin tutumuysa → D1.2; üretim baskısı somutsa → D1.4

D1.2 Yetersiz gözetim veya denetim
  → Tipik: Formen/yönetici sahada yoktu; çalışanlar denetimsiz uzun süre çalıştı
  → Seçme: Gözetim vardı ama sapmalara göz yumulduysa → D1.9

D1.3 Hesap verebilirlik eksikliği
  → Tipik: Önceki ihlallerin sonucu olmadı; kimse sorumlu tutulmadı
  → Seçme: Sorumluluk tanımsızsa → D2.1; kültür sorunuysa → D1.1

D1.4 Üretim baskısının güvenliğin önüne geçmesi
  → Tipik: "Durma, yetiştir" baskısıyla güvenlik adımları atlandı;
           güvenlik için iş durdurulduğunda çalışan cezalandırıldı
  → Seçme: Baskı bireysel yönetici davranışıysa → D1.2; sistem genelindeyse burada kal

D1.5 Sapmaların normalleşmesi (Kanıksama)
  → Tipik: "Hep böyle yapıyoruz, hiç bir şey olmadı" kültürü yerleşmiş
  → Seçme: Yönetim bunu bilerek onaylıyorsa → D1.9; tek seferlik sapmaysa → A1.1

D1.6 Etkisiz İş Durdurma yetkisi
  → Tipik: Çalışanlar tehlikeli gördükleri işi durduramıyor veya korktukları için durdurmuyorlar
  → Seçme: Yetki yoksa → D1.1; yetki var ama kullanılmıyorsa burada kal

D1.7 Zayıf raporlama ve öğrenme kültürü
  → Tipik: Ramak kala olaylar raporlanmıyor; geçmiş kazalardan ders alınmıyor
  → Seçme: Raporlama sistemi yoksa → D2.5; cezalandırma korkusu varsa → D1.1

D1.8 Yetersiz görünür saha liderliği
  → Tipik: Yöneticiler ofisten çıkmıyor; saha turu yapılmıyor
  → Seçme: Genel kültür sorunuysa → D1.1

D1.9 Yönetimin bilinen sapmalara tolerans göstermesi
  → Tipik: Yönetici ihlali gördü, kayıt altına almadı veya düzeltmedi
  → Seçme: Yönetici bilmiyorsa → D1.2; kültür genelindeyse → D1.5

D2. İletişim ve Bilgi Yönetimi

D2.1 Etkisiz iletişim (sözlü/yazılı/dijital)
  → Tipik: Talimat yanlış iletildi; önemli bilgi ulaşmadı
  → Seçme: Terminoloji sorunuysa → D2.3; altyapı sorunuysa → D2.4

D2.2 Talimatların yanlış anlaşılması veya belirsizliği
  → Tipik: "Makineyi temizle" talimatı enerjiyi kesmeden yapıldı — belirsizlik yüzünden
  → Seçme: Talimat net ama uyulmadıysa → A1.1; terminoloji sorunuysa → D2.3

D2.3 Standart terminoloji eksikliği
  → Tipik: "Kapat" komutu kişiye göre farklı anlaşılıyor; ortak dil yok
  → Seçme: Genel iletişim sorunuysa → D2.1

D2.4 İletişim altyapısının kalitesizliği
  → Tipik: Telsiz çekmiyor; gürültüde sözlü iletişim kurulamıyor
  → Seçme: İçerik sorunuysa → D2.1

D2.5 Yetersiz olay raporlama ve takip
  → Tipik: Ramak kala kaydedilmedi; düzeltici eylem takip edilmedi
  → Seçme: Raporlama kültürü yoksa → D1.7

D2.6 Vardiya devir tesliminde bilgi aktarım eksikliği
  → Tipik: Gece vardiyası devre dışı bırakılan sistemi gündüz vardiyasına iletmedi
  → Seçme: Devir teslim prosedürü yoksa → D4.1

D2.7 Bilgi aşırı yüklemesi veya kötü önceliklendirme
  → Tipik: Çalışana aynı anda çok fazla kritik bilgi verildi; hangisi önemli belli değil
  → Seçme: İletişim içeriği sorunuysa → D2.1

D3. Eğitim, Yetkinlik ve İşgücü Yönetimi

D3.1 Eğitimin sağlanmaması veya yetersiz olması
  → Tipik: Çalışan o ekipman veya prosedür için hiç eğitim almamış;
           eğitim sadece işe girişte bir kez verilmiş, güncellenmemiş
  → Seçme: Eğitim verildi ama ihtiyaç belirlenmemişse → D3.2;
           pratik eğitim yoksa → D3.3; etkinlik ölçülmemişse → D3.6

D3.2 Eğitim ihtiyaçlarının belirlenmemesi
  → Tipik: Hangi çalışanın hangi konuda eğitime ihtiyacı olduğu analiz edilmemiş
  → Seçme: Eğitim hiç verilmemişse → D3.1

D3.3 Yetersiz pratik/iş başı eğitimi
  → Tipik: Sadece sınıf eğitimi verildi; sahada uygulamalı gösterim yapılmadı
  → Seçme: Hiç eğitim yoksa → D3.1; yetkinlik doğrulanmadıysa → D3.4

D3.4 Yetkinliğin doğrulanmaması
  → Tipik: Çalışan eğitim aldı ama gerçekten öğrenip öğrenmediği test edilmedi
  → Seçme: Eğitim yoksa → D3.1

D3.5 Yetersiz personel veya iş yükü planlaması
  → Tipik: Bir kişi iki kişilik iş yapıyordu; kritik görev için yeterli personel yoktu
  → Seçme: Yorgunluk sorunuysa → C1.4; gözetim sorunuysa → D1.2

D3.6 Eğitim etkinliğinin değerlendirilmemesi
  → Tipik: Eğitimler veriliyor ama kazayı önleyip önlemediği hiç ölçülmüyor
  → Seçme: Eğitim hiç yoksa → D3.1

D4. Risk, Değişim ve İş Kontrol Sistemleri

D4.1 Risk analizinin yapılmaması veya yetersiz olması
  → Tipik: O görev veya ekipman için hiç risk değerlendirmesi yapılmamış;
           yapıldıysa ama kritik tehlikeyi kaçırdıysa
  → Seçme: Risk analizi yapıldı ve tehlike belirlendi ama önlem uygulanmadıysa → D4.2;
           değişim sonrası güncellenmemişse → D4.3;
           iş izni sistemindeyse → D4.4;
           LOTO konusundaysa → D4.5.
           BU KOD jenerik "hep uygulanabilir" değildir — sadece analiz GERÇEKTEN
           yapılmamışsa seç.

D4.2 Risk kontrollerinin uygulanmaması veya takip edilmemesi
  → Tipik: Risk değerlendirmesi yapıldı, kontroller belirlendi ama sahaya yansımadı
  → Seçme: Analiz hiç yoksa → D4.1; takip sistemi yoksa → D1.3

D4.3 Değişim yönetiminin etkisiz olması veya atlanması
  → Tipik: Ekipman/proses/personel değişikliği yapıldı ama risk analizi güncellenmedi
  → Seçme: Değişim yoksa bu kodu seçme; ilk kurulumda yapılmamışsa → D4.1

D4.4 İş izin sisteminin etkisiz olması
  → Tipik: İzin belgesi vardı ama yeterince detaylı değildi;
           imzalandı ama koşullar sahada kontrol edilmedi
  → Seçme: İzin sistemi hiç yoksa → D4.1; LOTO konusundaysa → D4.5

D4.5 Enerji izolasyonunun (LOTO) etkisiz olması
  → Tipik: Enerji izolasyonu prosedürü yok veya eksik;
           kilit takılmadı; enerji kaynakları tamamı izole edilmedi
  → Seçme: Prosedür vardı ama uyulmadıysa → A1.1; genel iş izni sorunuysa → D4.4

D4.6 Geçici risk kontrollerinin kalıcı muamelesi görmesi
  → Tipik: "Geçici" bariyer yıllarca kaldı; bant ile kapatılan tehlike kalıcı çözüm gibi bırakıldı
  → Seçme: Kalıcı çözüm hiç planlanmadıysa → D6.6

D5. Mühendislik, Tasarım ve Teknik Sistemler

D5.1 Tasarım hataları veya uygunsuzlukları
  → Tipik: Ekipman güvenli kullanım için gerekli koruyucu özelliği taşımıyor;
           tasarım aşamasında tehlike gözden kaçırıldı
  → Seçme: Tasarım sonradan kötü uygulandıysa → D6.2; ergonomi sorunuysa → D5.3

D5.2 Yetersiz tasarım gözden geçirme
  → Tipik: Yeni ekipman/tesis devreye alınmadan önce güvenlik incelemesi yapılmadı
  → Seçme: İnceleme yapıldı ama eksikse → D5.5; operasyonel sorunsa → D4.1

D5.3 Kötü HMI/ergonomi/alarm yönetimi
  → Tipik: Arayüz karmaşık; benzer düğmeler yan yana; alarm seli operatörü bunalttı
  → Seçme: Fiziksel yerleşimse → B4.9; tasarım hatasıysa → D5.1

D5.4 Yetersiz tehlikeli alan sınıflandırması
  → Tipik: Patlayıcı atmosfer alanı yanlış sınıflandırıldı; uygun olmayan ekipman kullanıldı
  → Seçme: Sınıflandırma doğruysa ama ekipman seçimi hatalıysa → D5.1

D5.5 Risk çalışmalarının tasarıma yetersiz entegrasyonu
  → Tipik: HAZOP/risk analizi yapıldı ama bulgular tasarıma yansımadı
  → Seçme: Risk analizi hiç yapılmadıysa → D4.1

D5.6 Tasarımın insan hatası toleransını dikkate almaması
  → Tipik: Sistem tek bir insan hatasında bile felakete yol açacak şekilde tasarlanmış;
           hata-toleranslı tasarım yok
  → Seçme: Ergonomi sorunuysa → D5.3; operasyonel hata ise → A4.5

D6. Bakım, Varlık Bütünlüğü ve Güvenilirlik

D6.1 Yetersiz bakım stratejisi veya planlaması
  → Tipik: O ekipman için bakım planı/takvimi hiç oluşturulmamış;
           hangi ekipmanın ne zaman bakım gerektirdiği belirsiz
  → Seçme: Plan var ama uygulanmadıysa → D6.2;
           muayene yapılmadıysa → D6.3;
           sadece ertelendiyse → D6.6;
           tekrarlayan arızaysa → D6.5.
           BU KOD "genel bakım eksikliği" için değil, strateji/planlama
           GERÇEKTEN yoksa kullan.

D6.2 Yetersiz bakım uygulaması veya işçilik
  → Tipik: Bakım planı var, teknisyen geldi ama iş hatalı/eksik yapıldı
  → Seçme: Plan yoksa → D6.1; işçilik kalitesiyse burada kal; yetkinlik sorunuysa → D3.1

D6.3 Yetersiz muayene, test veya kalibrasyon
  → Tipik: Güvenlik ventili test edilmemiş; ölçüm aleti kalibre edilmemiş
  → Seçme: Muayene programı yoksa → D6.1; muayene yapıldı ama gözden kaçtıysa → B2.7

D6.4 Yetersiz dokümantasyon veya kayıtlar
  → Tipik: Bakım geçmişi kaydedilmemiş; hangi parçanın ne zaman değiştirildiği bilinmiyor
  → Seçme: Kayıt sistemi yoksa → D4.1; kasıtlı saklandıysa → D1.3

D6.5 Tekrarlayan arızalardan ders alınmaması
  → Tipik: Aynı ekipman 3. kez aynı şekilde arızalandı; kök neden hiç araştırılmadı
  → Seçme: İlk arıza ise → D6.1 veya D6.3; raporlama kültürü sorunuysa → D1.7

D6.6 Ertelenmiş bakımın normal kabul edilmesi
  → Tipik: "Şimdi zaman yok, sonra yaparız" kültürü; erteleme listesi sürekli büyüyor
  → Seçme: Bütçe/kaynak sorunuysa → D3.5; liderlik onayıyla yapılıyorsa → D1.4

D6.7 Atanan bakım tipinin uygunsuz olması
  → Tipik: Kritik ekipman için reaktif bakım seçilmiş; önleyici/öngörücü bakım olması gerekirdi
  → Seçme: Strateji hiç yoksa → D6.1

D7. Yüklenici ve Tedarik Zinciri Yönetimi

D7.1 Yetersiz yüklenici ön yeterlilik değerlendirmesi
  → Tipik: Yüklenici güvenlik kapasitesi sorgulanmadan seçildi; referans kontrolü yapılmadı
  → Seçme: Seçim sonrası gözetim sorunuysa → D7.2

D7.2 Yetersiz yüklenici gözetimi
  → Tipik: Yüklenici sahada çalışıyor ama kimse denetlemiyor
  → Seçme: Seçim aşamasında sorunsa → D7.1; yetkinlik sorunuysa → D7.3

D7.3 Yüklenici yetkinliğinin doğrulanmaması
  → Tipik: Yüklenici "yapabilirim" dedi ama gerçekte o iş için yeterliliği yoktu
  → Seçme: Gözetim sorunuysa → D7.2

D7.4 Zayıf yüklenici güvenlik kültürü entegrasyonu
  → Tipik: Yüklenici kendi kurallarını uyguladı; tesis güvenlik kurallarına uymadı
  → Seçme: Oryantasyon verilmediyse → D3.1; gözetim yoksa → D7.2

D7.5 Hatalı tedarik edilen malzeme/ekipman
  → Tipik: Sipariş edilen spec'te olmayan malzeme geldi; sahte/kalitesiz parça kullanıldı
  → Seçme: Muayene yapılmadıysa → D6.3; tasarım hatasıysa → D5.1

D7.6 Yüklenici teşviklerinin güvenlikle uyumsuz olması
  → Tipik: Sözleşme sadece hız/maliyet ödüllendiriyor; güvenlik performansı değerlendirme dışı
  → Seçme: Kültür sorunuysa → D7.4

D8. Acil Durum Hazırlığı

D8.1 Acil durum planları veya tatbikatlarının yetersizliği
  → Tipik: Acil durum planı yok veya çok eski; son tatbikat yıllar önce yapılmış
  → Seçme: Plan var ama müdahale ekipmanı yoksa → D8.2; koordinasyon sorunuysa → D8.3

D8.2 Acil durum ekipmanının mevcut olmaması veya etkisizliği
  → Tipik: Yangın tüpü süresi dolmuş; ilk yardım çantası eksik; AED çalışmıyor
  → Seçme: Plan sorunuysa → D8.1

D8.3 Dış kurumlarla zayıf koordinasyon
  → Tipik: İtfaiye/ambulans ile ortak tatbikat yapılmamış; iletişim protokolü yok
  → Seçme: İç plan sorunuysa → D8.1

D8.4 Organizasyonel kontrol dışındaki dış olaylar
  → Tipik: Komşu tesisin olayı etkiledi; altyapı kesintisi dışarıdan geldi
  → Seçme: Önlem alınabilirdi ama alınmadıysa → D4.1 veya D8.1

D8.5 Acil durum müdahale rollerinin belirsiz olması
  → Tipik: Kriz anında kim ne yapacak belli değildi; çakışan sorumluluklar
  → Seçme: Plan yoksa → D8.1; iletişim sorunuysa → D2.1
"""
}


def get_category_text(category: str) -> str:
    """
    Kategori koduna göre ilgili metni döndürür.

    Args:
        category: 'A', 'B', 'C' veya 'D'

    Returns:
        str: Kategori metni (tipik senaryo ve seçme notları dahil)
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
