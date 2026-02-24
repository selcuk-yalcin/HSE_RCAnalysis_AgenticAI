# 📄 HTML Rapor Özellikleri

## 🎯 Genel Bakış

HSE Kök Neden Analiz sistemi artık **gelişmiş HTML raporları** üretiyor! Bu HTML raporları sadece statik dokümanlar değil, **interaktif**, **düzenlenebilir** ve **kullanıcı dostu** web sayfalarıdır.

---

## ✨ Yeni Özellikler

### 1. 📋 Navigasyon Menüsü

**Özellik:**
- Sayfanın sağ üst köşesinde "İçindekiler" butonu
- Tıklandığında açılır/kapanır menü
- Tüm bölümlere hızlı erişim
- Smooth scroll animasyonu
- Hedef bölüm geçici olarak highlight edilir

**Kullanım:**
```javascript
// Sağ üstteki "📋 İçindekiler" butonuna tıklayın
// İstediğiniz bölüme tıklayın
// Otomatik olarak o bölüme kaydırır
```

**Klavye Kısayolu:**
- `ESC` tuşu: Menüyü kapat

---

### 2. 🔧 Düzenleme Toolbar

**Özellik:**
- Sayfanın alt kısmında sabit toolbar
- 5 ana işlev butonu:
  - 🔓/🔒 **Düzenleme Modu**: Açık/Kapalı
  - 💾 **Kaydet**: localStorage'a kaydet
  - 🖨️ **Yazdır**: PDF veya kağıt çıktı
  - 📥 **HTML İndir**: Düzenlenmiş haliyle indir
  - 🔄 **Sıfırla**: Orijinal haline döndür

**Kullanım:**

#### Düzenleme Modu:
```
1. 🔓 "Düzenleme Modu: KAPALI" butonuna tıklayın
2. Mod AÇIK olunca tüm alanlar düzenlenebilir hale gelir
3. İstediğiniz metne tıklayın ve düzenleyin
4. Değişiklikler 2 saniyede bir otomatik kaydedilir
```

#### Kaydetme:
```
1. Değişikliklerinizi yaptıktan sonra
2. 💾 "Kaydet" butonuna tıklayın veya Ctrl+S
3. localStorage'a kaydedilir (tarayıcı kapansa bile kalır)
```

#### Yazdırma / PDF:
```
1. 🖨️ "Yazdır" butonuna tıklayın veya Ctrl+P
2. Tarayıcının yazdırma penceresi açılır
3. "Hedef" kısmından "PDF olarak kaydet" seçin
4. Sayfa numaraları otomatik eklenir
```

#### HTML İndir:
```
1. 📥 "HTML İndir" butonuna tıklayın
2. Düzenlenmiş haliyle HTML dosyası indirilir
3. Başkalarıyla paylaşabilirsiniz
```

**Klavye Kısayolları:**
- `Ctrl+E`: Düzenleme modunu aç/kapat
- `Ctrl+S`: Kaydet
- `Ctrl+P`: Yazdır

---

### 3. ✏️ Düzenlenebilir Alanlar

**Özellik:**
- Tüm önemli metinler `contenteditable`
- Mouse üzerine gelince sarı arka plan
- Tıklayınca "✏️ Düzenlemek için tıklayın" tooltip'i
- Focus olunca turuncu border

**Düzenlenebilir Alanlar:**
- ✅ Başlık ve alt başlıklar
- ✅ Olay özeti
- ✅ Tüm paragraflar
- ✅ Tablo hücreleri
- ✅ Liste öğeleri
- ✅ Kök neden başlıkları
- ✅ Sonuç ve öneriler

**Kullanım:**
```html
<!-- Düzenleme modu AÇIK iken -->
<div contenteditable="true">
  Bu metni doğrudan düzenleyebilirsiniz!
</div>
```

---

### 4. ↑ Scroll to Top (Yukarı Çık)

**Özellik:**
- Sayfanın sağ alt köşesinde sabit buton
- 300px aşağı kaydırınca görünür
- Tıklayınca smooth scroll ile yukarı çıkar
- Yuvarlak mavi buton: `↑`

**Kullanım:**
```
1. Sayfayı aşağı kaydırın
2. Sağ altta ↑ butonu belirir
3. Tıklayın, sayfa başına döner
```

---

### 5. 💾 Otomatik Kaydetme

**Özellik:**
- Her değişiklikten 2 saniye sonra otomatik kayıt
- localStorage kullanır (kalıcı)
- Tarayıcı kapansa bile kayıtlar kalır
- Console'da kayıt zamanı loglanır

**Kontrol:**
```javascript
// Browser Console'da:
localStorage.getItem('hse_report_autosave')
localStorage.getItem('hse_report_autosave_time')
```

---

### 6. 🖨️ Yazdırma için Sayfa Düzenleme

**Özellikler:**
- `@page` kuralları ile sayfa ayarları
- Otomatik sayfa numaraları (alt sağ)
- Rapor referansı (alt sol)
- Her bölüm başında sayfa ayırıcı
- Tablolar ve kutular sayfayı bölmez (`page-break-inside: avoid`)
- Navigation ve toolbar yazdırmada gizlenir

**CSS:**
```css
@page {
    margin: 2cm;
    @bottom-right {
        content: "Sayfa " counter(page) " / " counter(pages);
    }
    @bottom-left {
        content: "HSE Kök Neden Analizi - INC-XXX";
    }
}
```

---

### 7. 🎨 Modern Responsive Tasarım

**Özellikler:**
- Gradient renkli kapak sayfası
- Renkli bilgi kutuları
- Hover efektleri
- Smooth animasyonlar
- Mobil uyumlu (viewport meta tag)
- Maksimum genişlik: 1200px

**Renkler:**
- 🔵 Mavi (`#1B3A5C`): Ana başlıklar, navigasyon
- 🟢 Yeşil (`#27AE60`): Başarı, pozitif mesajlar
- 🟠 Turuncu (`#E67E22`): Uyarılar, kök nedenler
- 🔴 Kırmızı (`#C0392B`): Kritik, acil durumlar

---

### 8. 🔗 Bölüm ID'leri (Anchor Links)

**Özellik:**
- Her bölümün benzersiz ID'si var
- URL hash ile direkt bağlantı
- Navigation menüsü bu ID'leri kullanır

**Bölüm ID'leri:**
```html
#cover                  - Kapak Sayfası
#executive-summary      - Yönetici Özeti
#incident-details       - Olay Bilgileri
#analysis-method        - Analiz Yöntemi
#branches              - 5-Why Dalları
#root-causes           - Kök Nedenler
#contributing-factors  - Katkıda Bulunan Faktörler
#corrective-actions    - Düzeltici Faaliyetler
#lessons-learned       - Çıkarılan Dersler
#conclusion            - Sonuç
#signatures            - İmzalar
```

**Kullanım:**
```html
<!-- Direkt link -->
<a href="#root-causes">Kök Nedenlere Git</a>

<!-- JavaScript ile -->
document.getElementById('root-causes').scrollIntoView();
```

---

### 9. 📱 Bildirimler (Notifications)

**Özellik:**
- Sağ üstte slide-in animasyonlu bildirimler
- 3 saniye sonra otomatik kapanır
- 3 tip: Success (yeşil), Error (kırmızı), Info (mavi)

**Kullanım:**
```javascript
showNotification('✅ İşlem başarılı!', 'success');
showNotification('❌ Hata oluştu!', 'error');
showNotification('ℹ️ Bilgi mesajı', 'info');
```

---

### 10. 💡 Console İpuçları

**Özellik:**
- Sayfa açıldığında console'da kullanım ipuçları
- Son kayıt zamanı gösterilir
- PDF export talimatları

**Console Çıktısı:**
```
💡 KULLANIM İPUÇLARI:
📋 Ctrl+E: Düzenleme modunu aç/kapat
💾 Ctrl+S: Kaydet
🖨️ Ctrl+P: Yazdır / PDF kaydet
📥 HTML İndir: Raporu HTML dosyası olarak indir
🔄 Sıfırla: Tüm değişiklikleri geri al

💾 Son kayıt: 24.02.2026 04:15:30
```

---

## 🚀 Hızlı Başlangıç

### Rapor Oluşturma

```python
from agents.skillbased_docx_agent import SkillBasedDocxAgent

agent = SkillBasedDocxAgent()

combined_data = {
    "part1": overview_data,
    "part2": assessment_data,
    "part3_rca": rca_data
}

# DOCX + HTML oluştur
docx_file = agent.generate_report(
    combined_data,
    output_path="outputs/INC-2026-001.docx"
)

# HTML dosyası: outputs/INC-2026-001.html
```

### HTML'i Tarayıcıda Açma

```bash
# macOS
open outputs/INC-2026-001.html

# Linux
xdg-open outputs/INC-2026-001.html

# Windows
start outputs/INC-2026-001.html
```

---

## 📋 İş Akışı Örneği

### 1️⃣ Rapor Oluştur
```bash
python test_electrical_shock.py
```

### 2️⃣ HTML'i Aç
```bash
open outputs/INC-20260224-XXXXXX_electrical_shock.html
```

### 3️⃣ Düzenle
```
1. 🔓 butonuna tıkla (Düzenleme Modu: AÇIK)
2. Metinleri düzenle
3. Ctrl+S ile kaydet
```

### 4️⃣ PDF Oluştur
```
1. Ctrl+P basın
2. "Hedef: PDF olarak kaydet"
3. Dosya adı girin
4. "Kaydet"
```

### 5️⃣ Paylaş
```
1. 📥 "HTML İndir" butonuna tıkla
2. Dosyayı email ile gönder veya
3. Sharepoint/Drive'a yükle
```

---

## 🔧 Teknik Detaylar

### Dosya Yapısı

```
outputs/
├── INC-20260224-XXXXXX_scenario.docx    # Word rapor
├── INC-20260224-XXXXXX_scenario.html    # HTML rapor (interaktif)
└── scenario_20260224_XXXXXX.json        # JSON (raw data)
```

### HTML Boyutu

- Ortalama: **18-25 KB** (sıkıştırılmamış)
- CSS: ~8 KB
- JavaScript: ~5 KB
- Content: ~10 KB

### Tarayıcı Uyumluluğu

| Özellik | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| contenteditable | ✅ | ✅ | ✅ | ✅ |
| localStorage | ✅ | ✅ | ✅ | ✅ |
| @page rules | ✅ | ⚠️ Kısmi | ⚠️ Kısmi | ✅ |
| CSS Grid | ✅ | ✅ | ✅ | ✅ |
| Smooth scroll | ✅ | ✅ | ✅ | ✅ |

⚠️ **Not:** Sayfa numaralandırma Chrome ve Edge'de en iyi çalışır.

---

## 📊 Performans

### Rapor Oluşturma Süreleri

| Bileşen | İlk Çalışma | Cache Hit |
|---------|-------------|-----------|
| Overview | ~15s | ~12s |
| Assessment | ~20s | ~16s |
| RCA | ~45s | ~35s |
| DOCX/HTML | ~25s | ~20s |
| **TOPLAM** | **~105s** | **~83s** |

### Dosya Boyutları

| Format | Boyut | Sıkıştırılmış |
|--------|-------|---------------|
| JSON | 18 KB | 4 KB |
| DOCX | 54 KB | N/A |
| HTML | 22 KB | 6 KB |

---

## 🐛 Bilinen Sorunlar

### 1. Sayfa Numaraları (Firefox/Safari)

**Sorun:** `@page` kuralları tam desteklenmez.

**Çözüm:** 
- Chrome veya Edge kullanın
- Veya manuel sayfa numarası ekleyin

### 2. localStorage Limiti

**Sorun:** 5-10 MB limit (tarayıcıya göre).

**Çözüm:**
- Eski kayıtları silin:
```javascript
localStorage.clear()
```

### 3. Mobile Responsive

**Durum:** Mobilde düzenleme zor olabilir.

**Çözüm:**
- Desktop'ta düzenleyin
- Mobilde sadece görüntüleme için kullanın

---

## 💡 İpuçları ve Best Practices

### ✅ Yapılması Gerekenler

1. **Düzenlemeden önce kaydedin:**
   ```
   Ctrl+S ile orijinal hali kaydedin
   ```

2. **PDF'e dönüştürün:**
   ```
   Ctrl+P → PDF olarak kaydet
   Kalıcı arşiv için
   ```

3. **Yedek alın:**
   ```
   📥 HTML İndir ile local copy
   ```

4. **Console'u kontrol edin:**
   ```
   F12 → Console
   Hata ve ipuçları için
   ```

### ❌ Yapılmaması Gerekenler

1. **Tarayıcı geçmişini silmeyin:**
   ```
   localStorage temizlenir!
   ```

2. **Çok büyük düzenlemeler yapmayın:**
   ```
   localStorage sınırı var
   ```

3. **Sensitive bilgi eklemeyin:**
   ```
   localStorage şifrelenmez
   ```

---

## 📚 İlgili Dokümanlar

- [TEST_ALL_SCENARIOS.md](./TEST_ALL_SCENARIOS.md) - Test suite dokümantasyonu
- [ANTHROPIC_PROMPT_CACHING.md](./ANTHROPIC_PROMPT_CACHING.md) - Maliyet optimizasyonu
- [TEST_ELECTRICAL_SHOCK.md](./TEST_ELECTRICAL_SHOCK.md) - LOTO analiz örneği

---

## 🎓 Video Tutorial (Yakında)

```
📹 Planlanan:
- HTML rapor oluşturma
- Düzenleme özellikleri
- PDF export
- localStorage kullanımı
```

---

## 🆘 Destek

Sorularınız için:
- GitHub Issues: [RAG_and_Vector_databases/issues]
- Email: [email protected]
- Documentation: `/docs` klasörü

---

**Son Güncelleme:** 24 Şubat 2026  
**Versiyon:** 2.0  
**Yazar:** HSE RCA System
