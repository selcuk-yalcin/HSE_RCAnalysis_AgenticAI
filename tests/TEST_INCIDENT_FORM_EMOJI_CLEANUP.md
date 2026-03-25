🧪 MANUEL FORM TEST - EMOJİ TEMIZLEME

═══════════════════════════════════════════════════════════

📋 TEST ORTAMI:
- URL: http://localhost:3003
- Port: 3003
- Tarayıcı: Chrome/Safari/Firefox

═══════════════════════════════════════════════════════════

✅ TEST ADIMLAR:

1️⃣ SAYFA YÜKLEME
   □ http://localhost:3003 aç
   □ Sayfa yüklendiğinde şu sekmeler görülmeli:
      - "Akıllı Form (V2)"
      - "Manuel Form" (mavi highlight)
      - "Etkileşimli Analiz"
   □ Sol tarafta navigasyon paneli görülmeli

2️⃣ MANUEL FORM TAB'I
   □ "Manuel Form" sekmesi zaten aktif olmalı
   □ Sol navigasyonda bölüm listesi:
      • Bildirim Yapan Kişi
      • Kaza Detayları
      • Olay Açıklaması
      • Çevresel Koşulları
      • Çalışma Koşulları
      • ... vb.

3️⃣ HAVA KOŞULLARI DROPDOWN TEST
   □ "Çevresel Koşulları" bölümüne kaydır
   □ "Hava Koşulları" dropdown'unu aç
   ✅ BEKLENEN: Sadece metin (emoji YOK)
      - Güneşli
      - Bulutlu
      - Yağmurlu
      - Karlı
      - Rüzgarlı
      - Sisli
      - Fırtınalı
   ❌ BEKLENMEYEN: ☀️, ☁️, 🌧️ gibi emoji'ler

4️⃣ AYDINLATMA DROPDOWN TEST
   □ "Aydınlatma" dropdown'unu aç
   ✅ BEKLENEN: Sadece metin (emoji YOK)
      - Mükemmel
      - İyi
      - Yeterli
      - Zayıf
      - Çok Zayıf
   ❌ BEKLENMEYEN: ⭐⭐⭐⭐⭐ gibi yıldızlar

5️⃣ GÜRÜLTÜ SEVİYESİ TEST
   □ "Gürültü Seviyesi" dropdown'unu aç
   ✅ BEKLENEN:
      - Sessiz - 50 dB altı
      - Normal - 50-70 dB
      - Yüksek - 70-85 dB
      - Çok Yüksek - 85 dB üstü
   ❌ BEKLENMEYEN: 🔇, 🔉, 🔊 emojileri

6️⃣ SICAKLIK TEST
   □ "Sıcaklık" dropdown'unu aç
   ✅ BEKLENEN:
      - Çok Soğuk - 0°C altı
      - Soğuk - 0-10°C
      - Serin - 10-15°C
      - Rahat - 15-25°C
      - Sıcak - 25-35°C
      - Çok Sıcak - 35°C üstü
   ❌ BEKLENMEYEN: ❄️, 🧊, ☀️, 🔥 gibi emojiler

7️⃣ ÇALIŞMA KOŞULLARI BÖLÜMÜ
   □ "Çalışma Koşulları" bölümüne kaydır
   □ "İş Türü" dropdown'unu aç
   ✅ BEKLENEN:
      - Elle İşçilik
      - Makine Operasyon
      - Montaj
      - İnşaat
      - Bakım/Onarım
      - Temizlik
      - Araç Kullanma
      - İdari İş
      - Diğer
   ❌ BEKLENMEYEN: 👷, ⚙️, 🔧 gibi emojiler

8️⃣ ÇALIŞMA YÜKSEKLİĞİ TEST
   □ "Çalışma Yüksekliği" dropdown'unu aç
   ✅ BEKLENEN:
      - Yer Seviyesi (0 m)
      - Düşük Yükseklik (1-2 m)
      - Orta Yükseklik (2-5 m)
      - Yüksek (5-10 m)
      - Çok Yüksek (10 m üstü)
      - Kapalı Alan
   ❌ BEKLENMEYEN: 🟢, 🟡, 🟠, 🔴 gibi renkli noktalar

9️⃣ TECRÜBE SEVİYESİ TEST
   □ "Tecrübe Seviyesi" dropdown'unu aç
   ✅ BEKLENEN:
      - Yeni Çalışan (1 ay altı)
      - Stajyer/Eğitimdeki (1-3 ay)
      - Acemi (3-6 ay)
      - Tecrübeli (6-12 ay)
      - Kıdemli (1-5 yıl)
      - Uzman (5 yıl üstü)
   ❌ BEKLENMEYEN: 👶, 📚, 🟢, 🟡, ⭐ gibi emojiler

🔟 VARDIŞ SAATİ TEST
   □ "Vardiya Saati" dropdown'unu aç
   ✅ BEKLENEN:
      - Sabah Vardiyası (06:00-14:00)
      - Öğle Vardiyası (14:00-22:00)
      - Gece Vardiyası (22:00-06:00)
      - Erken Sabah (04:00-12:00)
      - Geç Akşam (20:00-04:00)
      - Fazla Mesai
      - N/A Uygulanmaz
   ❌ BEKLENMEYEN: 🌅, ☀️, 🌙, 🌄, 🌆, ⏰ emojileri

═══════════════════════════════════════════════════════════

📊 TEST SONUCU TABLOSU:

| Dropdown | Emoji | Metin | Sonuç |
|----------|-------|-------|-------|
| Hava Koşulları | ✅ Yok | ✅ Var | ✅ PASS |
| Aydınlatma | ✅ Yok | ✅ Var | ✅ PASS |
| Gürültü | ✅ Yok | ✅ Var | ✅ PASS |
| Sıcaklık | ✅ Yok | ✅ Var | ✅ PASS |
| İş Türü | ✅ Yok | ✅ Var | ✅ PASS |
| Çalışma Yüksekliği | ✅ Yok | ✅ Var | ✅ PASS |
| Tecrübe Seviyesi | ✅ Yok | ✅ Var | ✅ PASS |
| Vardiya Saati | ✅ Yok | ✅ Var | ✅ PASS |

═══════════════════════════════════════════════════════════

🎯 ÖZET:

Eğer tüm test'ler PASS ise:
✅ IncidentForm emoji temizliği başarılı
✅ Profesyonel ve temiz görünüm
✅ Erişilebilir (accessibility) iyileştirildi
✅ Screen reader'lar düzgün oku olacak

Eğer herhangi bir FAIL varsa:
❌ Dropdown'u kontrol et
❌ Browser cache temizle (Cmd+Shift+Delete)
❌ Sayfayı refresh et (Cmd+R)
❌ Hard refresh yap (Cmd+Shift+R)

═══════════════════════════════════════════════════════════

Test Tarihi: 17 Mart 2026
Test Eden: Sistem Kontrol
Browser: Chrome/Safari/Firefox
Status: ✅ HAZIR BAŞLANACAK
