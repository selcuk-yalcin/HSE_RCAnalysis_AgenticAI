# 📋 Kapsamlı İş Kazası Rapor Formu - HTML Standalone

## 🎯 Genel Bakış

Tüm test senaryolarını analiz ederek oluşturulmuş, **standalone (bağımsız) HTML** incident rapor formu. Hiçbir framework/kütüphane gerektirmez, doğrudan tarayıcıda çalışır.

## ✨ Öne Çıkan Özellikler

### 1. **Çok Kapsamlı Alan Yapısı**
- ✅ **100+ Form Alanı**
  - 10 zorunlu alan
  - 90+ opsiyonel alan
- ✅ **9 Ana Sekme**
  - Temel Bilgiler
  - Olay Açıklaması (5W1H)
  - Güvenlik & KKD
  - Tanıklar
  - Çevre & Koşullar
  - Çalışma Detayları
  - Yaralanma & Hasar
  - Kök Neden Analizi
  - Özet & Gönder

### 2. **Olay Türüne Özel Dinamik Alanlar**
Seçilen kaza türüne göre otomatik açılan özel alanlar:

#### ⬇️ Yüksekten Düşme
- Düşüş yüksekliği (metre)
- Çalışma platformu türü (iskele, merdiven, çatı, lift)
- Korkuluk durumu (mevcut, yetersiz, yok, söküldü)

#### ⚡ Elektrik Çarpması
- Voltaj seviyesi (380V, 24V vb.)
- Akım tipi (AC tek/üç faz, DC)
- LOTO prosedürü (evet, kısmen, hayır)
- ✅ Elektrik izolasyonu
- ✅ Kilitleme cihazı
- ✅ Etiketleme
- ✅ Voltaj testi

#### ⚙️ Makine Sıkışması
- Makine türü (konveyör, pres, testere)
- Koruyucu kapak durumu (mevcut, çıkarılmış, yok, arızalı)
- Acil durdurma butonu (kullanıldı, kullanılmadı, çalışmadı)
- ✅ Makine çalışır durumdaydı
- ✅ İnterlock sistemi
- ✅ Işık perdesi
- ✅ İki el kumanda

#### 🏗️ Kazı Göçüğü
- Kazı derinliği (metre)
- Toprak tipi (stabil kaya, Tip A/B/C)
- Şev açısı (derece)
- ✅ Destek sistemi kurulu
- ✅ Şevleme uygulandı
- ✅ Yeraltı suyu mevcut
- ✅ Son 24 saatte yağış

### 3. **Test Senaryoları Otomatik Yükleme**
4 gerçek test senaryosu tek tıkla yüklenebilir:

| Senaryo | İçerik | Alan Sayısı |
|---------|--------|-------------|
| 🔵 Yüksekten Düşme | 6m iskele düşüşü, emniyet kemeri yok | 45+ alan |
| 🟡 Elektrik Çarpması | 380V akıma kapılma, LOTO yok | 43+ alan |
| 🟢 Makine Sıkışması | Konveyör bandı, 3 parmak kırığı | 42+ alan |
| 🟠 Kazı Göçüğü | 2.5m derinlik, yağış sonrası göçük | 40+ alan |

### 4. **KKD (Kişisel Koruyucu Donanım) Seçimi**
10 farklı KKD checkbox ile seçilebilir:
- 🪖 Baret
- 🧤 İş Eldiveni
- 👞 İş Ayakkabısı
- 🥽 Koruyucu Gözlük
- 🎧 Kulak Koruyucu
- 😷 Solunum Maskesi
- 🦺 İkaz Yeleği
- ⚡ Yalıtımlı Eldiven
- 🛡️ Yüz Siperi
- 👔 Koruyucu Giysi

### 5. **Güvenlik Sistemleri & Prosedürler**
6 sistem checkbox:
- 📋 İş İzin Sistemi
- ⚠️ Risk Değerlendirmesi
- 💬 Güvenlik Brifingi
- 📊 JSA (İş Güvenlik Analizi)
- 🚪 Kapalı Alan İzni
- 🔥 Sıcak İş İzni

### 6. **Kök Neden Kategorileri**
12 yaygın kök neden kategorisi:
- 📋 Prosedür/Talimat Eksikliği
- 🎓 Eğitim Yetersizliği
- 🔧 Ekipman/Araç Arızası
- 🛡️ KKD Eksikliği/Uygunsuz
- 👁️ Gözetim/Denetim Eksikliği
- 📞 İletişim Sorunu
- 📐 Tasarım/Planlama Hatası
- 🔨 Bakım Yetersizliği
- 🏢 Güvenlik Kültürü Zayıf
- ⏱️ Üretim/Zaman Baskısı
- 😴 Yorgunluk/Stres
- 🌦️ Çevresel Faktörler

### 7. **Görsel Kullanıcı Arayüzü**

#### Gradient Tema
- **Header:** Mor gradient (#667eea → #764ba2)
- **Test Butonları:** 4 farklı renk gradient
  - Yüksekten Düşme: Pembe-kırmızı
  - Elektrik: Sarı-kırmızı
  - Makine: Turkuaz-pembe
  - Kazı: Mor-sarı

#### İlerleme Göstergeleri
- **Progress Bar:** Sekme ilerlemesini gösterir (0-100%)
- **Tamamlanma Oranı:** Özet sekmesinde
  - Doldurulma oranı: X%
  - Zorunlu alanlar: X/10
  - Toplam alanlar: X/100

#### Sekme Navigasyonu
9 sekme, renkli ikonlarla:
```
📋 Temel Bilgiler → 📝 Olay Açıklaması → 🛡️ Güvenlik & KKD
     ↓                       ↓                     ↓
👥 Tanıklar → 🌍 Çevre & Koşullar → 💼 Çalışma Detayları
     ↓                       ↓                     ↓
🚑 Yaralanma → 🔍 Kök Neden → ✅ Özet & Gönder
```

## 📊 Teknik Detaylar

### Dosya Yapısı
```
incident_report_form.html (tek dosya, 1200+ satır)
├── HTML (yapı)
├── CSS (embedded, 500+ satır)
│   ├── Modern gradient tasarım
│   ├── Responsive (mobil uyumlu)
│   ├── Print-friendly stiller
│   └── Animasyonlar (fadeIn, hover)
└── JavaScript (embedded, 400+ satır)
    ├── Sekme navigasyonu
    ├── Test senaryosu yükleme
    ├── Form istatistikleri
    ├── Auto-save (2 dakikada bir)
    ├── Draft yönetimi (localStorage)
    └── Form validasyonu
```

### Tarayıcı Desteği
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ⚠️ IE11 desteklenmez (modern CSS/JS)

### Performans
- **İlk Yükleme:** ~50KB (gzip ile ~12KB)
- **Hiçbir harici kaynak yok:** 0 HTTP request
- **Offline çalışır:** Tam standalone
- **Auto-save:** LocalStorage kullanır

## 🎨 Kullanım Senaryoları

### 1. Eğitim ve Demo
```javascript
// Test senaryosu yükle
loadTestScenario('fall')      // Yüksekten düşme
loadTestScenario('electrical') // Elektrik çarpması
loadTestScenario('machine')    // Makine sıkışması
loadTestScenario('excavation') // Kazı göçüğü

// Formu temizle
clearForm()
```

### 2. Gerçek Vaka Girişi
1. Tarayıcıda aç: `file:///path/to/incident_report_form.html`
2. Sekmeler arasında ilerle
3. Zorunlu alanları doldur
4. "Taslak Kaydet" ile ara kayıt
5. "Analize Gönder" ile tamamla

### 3. Offline Kullanım
- İnternetsiz ortamlarda çalışır
- LocalStorage ile veri saklama
- Taslak otomatik kaydedilir
- Sonra online olunca backend'e gönderilebilir

## 📋 Alan Listesi (Kategori Bazında)

### Temel Bilgiler (15 alan)
- [x] Bildiren kişi *(zorunlu)*
- [x] Bildirim tarihi/saati *(zorunlu)*
- [x] Olay tarihi/saati *(zorunlu)*
- [x] Konum *(zorunlu)*
- [x] Departman
- [x] Olay kategorisi *(zorunlu)*
- [x] Olay türü
- [x] **Yüksekten düşme özel alanları (3)**
- [x] **Elektrik özel alanları (7)**
- [x] **Makine özel alanları (7)**
- [x] **Kazı özel alanları (7)**

### 5W1H Açıklaması (8 alan)
- [x] Genel olay açıklaması *(zorunlu)*
- [x] Ne oldu? (What)
- [x] Nerede oldu? (Where)
- [x] Ne zaman oldu? (When)
- [x] Kimler dahil? (Who)
- [x] Nasıl oldu? (How)
- [x] Neden oldu? (Why)
- [x] Acil müdahale

### Güvenlik & KKD (18 alan)
- [x] Düşme koruması
- [x] Emniyet kemeri
- [x] Güvenlik eğitimi
- [x] **10 KKD checkbox**
- [x] KKD detayları
- [x] **6 güvenlik sistemi checkbox**

### Tanıklar (4 alan)
- [x] Tanık var mı?
- [x] Tanık isimleri
- [x] Tanık ifadeleri
- [x] Süpervizör görüşleri

### Çevre & Koşullar (10 alan)
- [x] Hava koşulları (8 seçenek)
- [x] Aydınlatma (6 seçenek)
- [x] Gürültü seviyesi (4 seçenek)
- [x] Sıcaklık
- [x] Nem oranı
- [x] Rüzgar hızı
- [x] **5 zemin koşulu checkbox**
- [x] Çevresel tehlikeler

### Çalışma Detayları (11 alan)
- [x] İş türü
- [x] Çalışma yüksekliği
- [x] Deneyim seviyesi
- [x] Vardiya (4 seçenek)
- [x] Çalışma süresi
- [x] Son mola zamanı
- [x] **5 çalışma baskısı checkbox**
- [x] Çalışma koşulları notlar

### Yaralanma & Hasar (21 alan)
- [x] Yaralanma türü (13 seçenek, multiple)
- [x] Yaralanma şiddeti *(zorunlu)* (6 seçenek)
- [x] **12 vücut bölgesi checkbox**
- [x] Yaralanma detayları
- [x] Tıbbi müdahale
- [x] İş kaybı süresi
- [x] Maddi hasar var mı?
- [x] Maddi hasar detayları

### Kök Neden Analizi (17 alan)
- [x] İlk kök neden değerlendirmesi *(zorunlu)* (5 Neden)
- [x] **12 kök neden kategorisi checkbox**
- [x] Düzeltici aksiyonlar *(zorunlu)*
- [x] Önleyici tedbirler
- [x] Sorumlu kişi/birim
- [x] Tamamlanma tarihi
- [x] Ek notlar

### Özet & Gönder (3 alan)
- [x] Rapor kategorisi (3 seçenek)
- [x] Gizlilik seviyesi (3 seçenek)
- [x] Form istatistikleri (otomatik)

## 🔧 Özelleştirme

### Test Senaryosu Ekleme
```javascript
// testScenarios objesine yeni senaryo ekle
testScenarios.chemical = {
    reportedBy: 'Kimyasal Güvenlik Sorumlusu',
    incidentType: 'chemical_exposure',
    // ... diğer alanlar
};

// HTML'de yeni buton ekle
<button class="test-btn" onclick="loadTestScenario('chemical')">
    ☣️ Kimyasal Maruziy et
</button>
```

### Yeni Alan Ekleme
```html
<!-- HTML -->
<div class="form-group">
    <label>Yeni Alan</label>
    <input type="text" name="newField" placeholder="Açıklama">
</div>
```

### Stil Değiştirme
```css
/* CSS - Header rengi değiştir */
.header {
    background: linear-gradient(135deg, #your-color-1, #your-color-2);
}
```

## 💾 Veri Saklama

### LocalStorage (Taslak)
```javascript
// Otomatik kayıt (2 dakikada bir)
setInterval(saveDraft, 120000);

// Manuel kayıt
saveDraft() // "💾 Taslak Kaydet" butonu

// Taslak yükleme
// Sayfa açıldığında otomatik sorar
```

### Backend Entegrasyonu
```javascript
// Form submit event'inde
document.getElementById('incidentForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);
    
    // Backend'e gönder
    const response = await fetch('/api/incident-reports', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    
    if (response.ok) {
        alert('✅ Rapor başarıyla kaydedildi!');
        localStorage.removeItem('incidentReportDraft');
    }
});
```

## 📱 Responsive Tasarım

### Desktop (>768px)
- 2 sütunlu grid
- Tam genişlik sekmeler
- Yan yana butonlar

### Tablet (768px)
- 1 sütun grid
- Kaydırılabilir sekmeler
- Butonlar hala yan yana

### Mobil (<768px)
- 1 sütun (tüm alanlar)
- Yatay kaydırmalı sekmeler
- Butonlar alt alta

## 🖨️ Yazdırma Desteği

Print yapıldığında:
- Test yükleme bölümü gizlenir
- Sekme navigasyonu gizlenir
- Butonlar gizlenir
- Tüm bölümler gösterilir
- Sayfa sonları optimize edilir

```css
@media print {
    .test-loader, .tabs, .button-group {
        display: none !important;
    }
    .section {
        display: block !important;
        page-break-inside: avoid;
    }
}
```

## 🎯 Kullanım İpuçları

### 1. Hızlı Doldurma
- Test senaryosu yükle
- İstediğin alanları düzenle
- Gönder

### 2. Detaylı Rapor
- Tüm sekmeleri sırayla doldur
- 5W1H'yi eksiksiz yaz
- Tanık ifadelerini detaylandır
- 5 Neden analizi yap

### 3. Taslak Kullanımı
- Yarım bırakılan formlar otomatik kaydedilir
- Sayfa yenilendiğinde "Tasla yükle" sorusu çıkar
- Taslağı silmek için "Formu Temizle"

### 4. Navigasyon
- **Sekmelere tıkla:** Direkt o bölüme git
- **Sonraki/Önceki:** Adım adım ilerle
- **Progress Bar:** İlerlemeyi takip et

## 📈 İstatistikler

### Form Özellikleri
- **Toplam Sekme:** 9
- **Toplam Alan:** 100+
- **Zorunlu Alan:** 10
- **Checkbox Grubu:** 8
- **Radio Grubu:** 6
- **Select Dropdown:** 12
- **Text/Textarea:** 50+
- **Dinamik Alan:** 24 (olay türüne göre)

### Kod Satırları
- **HTML:** ~400 satır
- **CSS:** ~500 satır
- **JavaScript:** ~400 satır
- **Toplam:** ~1300 satır

### Test Senaryoları
- **Hazır Senaryo:** 4
- **Alan/Senaryo:** ~43
- **Toplam Test Verisi:** ~170 alan x değer

## 🚀 Gelecek Geliştirmeler

### Öncelik 1: Daha Fazla Senaryo
- [ ] Kimyasal sızıntı
- [ ] Yangın/patlama
- [ ] Araç kazası
- [ ] Manuel taşıma yaralanması
- [ ] Kayma/takılma/düşme

### Öncelik 2: Fotoğraf Ekleme
- [ ] Drag & drop fotoğraf yükleme
- [ ] Çoklu fotoğraf desteği
- [ ] Fotoğraf önizleme
- [ ] Fotoğraf açıklama alanı

### Öncelik 3: PDF Export
- [ ] "PDF İndir" butonu
- [ ] Tüm alanları içeren PDF
- [ ] Şirket logosu ekleme
- [ ] Dijital imza alanı

### Öncelik 4: Multi-Language
- [ ] İngilizce
- [ ] Almanca
- [ ] Fransızca
- [ ] İspanyolca
- [ ] Arapça

### Öncelik 5: Offline PWA
- [ ] Progressive Web App
- [ ] Service Worker
- [ ] Offline-first mimari
- [ ] Sync when online

## 🎓 Eğitim Kullanımı

### Senario 1: İSG Eğitimi
1. Katılımcılara formu aç
2. "Yüksekten Düşme" senaryosunu yükle
3. Her sekmeyi inceleyin
4. Kök neden analizini tartışın

### Senario 2: Kaza İncelemesi Pratiği
1. Gerçek kaza senaryosu ver (sözlü)
2. Katılımcılar formu doldursun
3. Sonuçları karşılaştırın
4. En iyi kök neden analizini seçin

### Senario 3: 5 Neden Tekniği Öğretimi
1. Test senaryosu yükle
2. Sadece "Kök Neden" sekmesine odaklan
3. "Neden?" sorusunu 5 kez sorun
4. Gerçek kök nedene ulaşın

## 📞 Destek ve Katkı

### Hata Bildirimi
- Tarayıcı konsolu (F12) hatalarını kontrol edin
- localStorage dolu mu kontrol edin
- Tarayıcı önbelleğini temizleyin

### Özellik Talebi
- GitHub Issues kullanın
- Detaylı açıklama ekleyin
- Mockup/screenshot paylaşın

## 📄 Lisans ve Kullanım

- ✅ Eğitim amaçlı kullanım serbest
- ✅ Şirket içi kullanım serbest
- ✅ Değiştirme ve özelleştirme serbest
- ℹ️ Ticari kullanım için iletişime geçin

---

## 🏁 Hızlı Başlangıç

```bash
# 1. HTML dosyasını aç
open incident_report_form.html

# 2. Test senaryosu yükle
Butona tıkla: "Yüksekten Düşme"

# 3. Sekmeleri incele
9 sekme arasında gezin

# 4. Form gönder
"Analize Gönder" butonu

# 5. Taslak kaydet (isteğe bağlı)
"Taslak Kaydet" butonu
```

## 📊 Hızlı İstatistikler

| Özellik | Değer |
|---------|-------|
| 📝 Toplam Alan | 100+ |
| ⭐ Zorunlu Alan | 10 |
| 🎯 Olay Türü | 11 |
| 🧪 Test Senaryosu | 4 |
| 📑 Sekme | 9 |
| 🎨 Gradient Buton | 5 |
| ✅ Checkbox Grup | 8 |
| 🔘 Radio Grup | 6 |
| 📊 Dropdown | 12 |
| 💾 Auto-Save | 2 dk |

---

**Güncellenme:** 11 Mart 2026  
**Versiyon:** 2.0 Standalone  
**Dosya Boyutu:** ~50KB  
**Tarayıcı Desteği:** Chrome 90+, Firefox 88+, Safari 14+

