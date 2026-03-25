# 🧪 BROWSER TEST KLAVUZU

**Server:** ✅ http://localhost:3003 - ÇALIŞIYOR

---

## 📋 TEST ADIMLARI (MANUEL)

### 1️⃣ SAYFA YÜKLENMESINI KONTROL ET
- [ ] Sayfa açılmış mı?
- [ ] 3 tab görünüyor mu?
  - "Akıllı Form (V2)"
  - "Manuel Form"
  - "Etkileşimli Analiz"
- [ ] Başlık görünüyor mu: "Root Cause Analysis"

---

### 2️⃣ "MANUEL FORM" TAB'INDA EMOJİ TESTİ

Şu anda bu tab'da olmalısın. Sol navigasyonda bölümler görünüyor mu?

**Çevresel Koşulları bölümüne kaydır:**

1. **Hava Koşulları dropdown'unu aç**
   - [ ] ✅ "Güneşli" (emoji ❌)
   - [ ] ✅ "Bulutlu" (emoji ❌)
   - [ ] ✅ "Yağmurlu" (emoji ❌)
   - [ ] ✅ "Karlı"
   - [ ] ✅ "Rüzgarlı"
   - [ ] ✅ "Sisli"
   - [ ] ✅ "Fırtınalı"

2. **Aydınlatma dropdown'unu aç**
   - [ ] ✅ "Mükemmel" (yıldız ❌)
   - [ ] ✅ "İyi"
   - [ ] ✅ "Yeterli"
   - [ ] ✅ "Zayıf"
   - [ ] ✅ "Çok Zayıf"

3. **Gürültü Seviyesi dropdown'unu aç**
   - [ ] ✅ "Sessiz - 50 dB altı" (speaker ❌)
   - [ ] ✅ "Normal - 50-70 dB"
   - [ ] ✅ "Yüksek - 70-85 dB"
   - [ ] ✅ "Çok Yüksek - 85 dB üstü"

4. **Sıcaklık dropdown'unu aç**
   - [ ] ✅ "Çok Soğuk - 0°C altı" (❄️ ❌)
   - [ ] ✅ "Soğuk - 0-10°C"
   - [ ] ✅ "Serin - 10-15°C"
   - [ ] ✅ "Rahat - 15-25°C"
   - [ ] ✅ "Sıcak - 25-35°C"
   - [ ] ✅ "Çok Sıcak - 35°C üstü"

**Çalışma Koşulları bölümüne kaydır:**

5. **İş Türü dropdown'unu aç**
   - [ ] ✅ "Elle İşçilik" (👷 ❌)
   - [ ] ✅ "Makine Operasyon"
   - [ ] ✅ "Montaj"
   - [ ] ✅ "İnşaat"
   - [ ] ✅ "Bakım/Onarım"
   - [ ] ✅ "Temizlik"
   - [ ] ✅ "Araç Kullanma"
   - [ ] ✅ "İdari İş"
   - [ ] ✅ "Diğer"

6. **Çalışma Yüksekliği dropdown'unu aç**
   - [ ] ✅ "Yer Seviyesi (0 m)"
   - [ ] ✅ "Düşük Yükseklik (1-2 m)"
   - [ ] ✅ "Orta Yükseklik (2-5 m)"
   - [ ] ✅ "Yüksek (5-10 m)"
   - [ ] ✅ "Çok Yüksek (10 m üstü)"
   - [ ] ✅ "Kapalı Alan"

7. **Tecrübe Seviyesi dropdown'unu aç**
   - [ ] ✅ "Yeni Çalışan (1 ay altı)"
   - [ ] ✅ "Stajyer/Eğitimdeki (1-3 ay)"
   - [ ] ✅ "Acemi (3-6 ay)"
   - [ ] ✅ "Tecrübeli (6-12 ay)"
   - [ ] ✅ "Kıdemli (1-5 yıl)"
   - [ ] ✅ "Uzman (5 yıl üstü)"

8. **Vardiya Saati dropdown'unu aç**
   - [ ] ✅ "Sabah Vardiyası (06:00-14:00)"
   - [ ] ✅ "Öğle Vardiyası (14:00-22:00)"
   - [ ] ✅ "Gece Vardiyası (22:00-06:00)"
   - [ ] ✅ "Erken Sabah (04:00-12:00)"
   - [ ] ✅ "Geç Akşam (20:00-04:00)"
   - [ ] ✅ "Fazla Mesai"
   - [ ] ✅ "N/A Uygulanmaz"

---

### 3️⃣ "AKILLI FORM (V2)" TAB'INDA TEMA TOGGLE TESTİ

"Akıllı Form (V2)" tab'ını tıkla:

1. **Sayfayı gözle:**
   - [ ] Başlık: "🎯 Akıllı Soruşturma Sistemi"
   - [ ] Alt başlık: "Olay hakkında sistemli bilgi toplayarak kök nedene ulaşın"
   - [ ] 15 genel soru var mı?
   - [ ] Progress bar: "0 / 15 Soru"

2. **Tema Toggle Butonu:**
   - [ ] Sağ üstte 🌙 (Moon) ikonu görünüyor mu?
   - [ ] TIŞLA: Moon ikonu
   - [ ] Sayfa KARANLIK MODA dönmeli:
     - [ ] Arka plan koyu (#2d2d44)
     - [ ] Yazı beyaz (#e8e8e8)
     - [ ] Sun (☀️) ikonu görünmeli
   - [ ] TIŞLA: Sun ikonu
   - [ ] Sayfa AYDINLIQ MODA dönmeli:
     - [ ] Arka plan açık (#f8f9fa)
     - [ ] Yazı koyu (#2c3e50)
     - [ ] Moon (🌙) ikonu görünmeli

3. **Renk Geçişi (Transition):**
   - [ ] Renk değişimi pürüzsüz mü? (0.3 saniye)
   - [ ] Titreme/flicker var mı? (varsa BUG)

4. **Tab Geçişleri:**
   - [ ] "Genel Sorular" tab'ını tıkla
   - [ ] "Detaylı Analiz" tab'ını tıkla
   - [ ] Tema toggle'ı her iki tab'da da çalışıyor mu?

---

### 4️⃣ "ETKILEŞIMLI ANALIZ" TAB'INDA TEST

- [ ] Chat interface yükleniyor mu?
- [ ] Mesaj yazılabiliyor mu?
- [ ] Tema toggle çalışıyor mu?

---

## ✅ BAŞARILI TEST KRİTERİLERİ

### Manuel Form:
- ✅ Tüm 8 dropdown'da emoji YOK
- ✅ Sadece metin var
- ✅ Seçim yapılabiliyor

### Akıllı Form V2:
- ✅ Tema toggle butonu görünüyor
- ✅ Moon tıklanınca koyu tema
- ✅ Sun tıklanınca açık tema
- ✅ Smooth transition (titremesiz)
- ✅ Her tab'da çalışıyor

---

## ❌ HATA DURUMUNDA

**F12 aç → Console tab'ında hata mesajını kopyala:**

Örnek:
```
Uncaught ReferenceError: setDarkMode is not defined
Cannot read property 'data-theme' of null
...
```

Hata mesajını buraya yapıştır ve çözüm bul.

---

## 📝 TEST SONUCU

**Tarih:** 17 Mart 2026
**Saat:** 16:30
**Browser:** Chrome/Safari/Firefox
**Status:** [ ] PASS / [ ] FAIL

**Notlar:**
```
(Burada test sonuçlarını yaz)
```

---

**Test tamamlandı mı? Sonuç nedir?**
