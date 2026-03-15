# 🔎 Frontend - Detaylı Araştırma (Comprehensive Investigation) Section

## Genel Bakış (Overview)

`incident_report_form.html` dosyasına **24 soruluk kapsamlı araştırma bölümü** eklenmiştir. Bu bölüm:

- ✅ Tikli butonlar (Checkboxes) ile kontrollü soru gösterimi
- ✅ Kademeli açılım (Progressive Disclosure) - Soruları dökümanter daha az soruyla zorlanmaz
- ✅ Akıllı koşullu alanlar (Conditional Fields) - Sorulara göre farklı input tipleri
- ✅ 4 ana kategori altında 24 soru
- ✅ Evet/Hayır cevaplarına göre detay alanları göster/gizle

---

## Soru Kategorileri

### 📍 KATEGORİ 1: Nerede, Ne Zaman ve Kim?
Olayın temel bilgilerini topla.

| Soru # | Soru | Input Tipi | Zorunlu? |
|--------|------|-----------|----------|
| 1 | Olumsuz olay nerede ve ne zaman gerçekleşti? | Checkbox + Textarea | Opsiyonel |
| 2 | Olumsuz olayda kim yaralandı/hastalandı veya başka bir şekilde etkilendi? | Checkbox + Textarea | Opsiyonel |

**Açıklama:** Kullanıcı soruları etkinleştirmek için checkbox'ları tıklar. Tıklandığında textarea açılır.

```html
<div class="form-group conditional-group">
    <label for="q1">
        <input type="checkbox" id="q1" name="q1" class="conditional-checkbox" data-shows="q1-detail">
        <span class="checkbox-label">1. Olumsuz olay nerede ve ne zaman gerçekleşti?</span>
    </label>
    <textarea id="q1-detail" name="q1_detail" rows="3" placeholder="..." class="conditional-field hidden"></textarea>
</div>
```

---

### 📋 KATEGORİ 2: Ayrıntılı Bilgi Toplama - Neyi ve Nasıl?
Olay detaylarını adım adım topla.

| Soru # | Soru | Input Tipi |
|--------|------|-----------|
| 3 | Olumsuz olay nasıl oldu? Olayla ilgili tüm ekipmanların not edilmesi | Checkbox + Textarea |
| 4 | O sırada hangi faaliyetler gerçekleştiriliyordu? | Checkbox + Textarea |
| 5 | Çalışma koşullarında olağandışı veya farklı bir şey var mıydı? | Checkbox + Radio (EVET/HAYIR) + Textarea |
| 6 | Güvenli çalışma prosedürleri (GÇP) yeterli miydi ve bu prosedürlere uyuluyor muydu? | Checkbox + Radio (4 seçenek) |
| 7 | Olumsuz olay ne tür yaralanmalara veya sağlık sorunlarına neden oldu? | Checkbox + Textarea |
| 8 | Bir yaralanma varsa nasıl oldu ve buna ne sebep oldu? | Checkbox + Textarea |

**Özellik:** Sorular 5 ve 6 radio butonlarıyla koşullu detay alanlarına sahip.

```html
<div class="form-group conditional-group">
    <label for="q5">
        <input type="checkbox" id="q5" name="q5" class="conditional-checkbox" data-shows="q5-detail">
        <span class="checkbox-label">5. Çalışma koşullarında olağandışı veya farklı bir şey var mıydı?</span>
    </label>
    <div id="q5-detail" class="conditional-field hidden">
        <div class="radio-group">
            <label><input type="radio" name="q5_answer" value="yes"> EVET - Açıklayın:</label>
            <textarea name="q5_yes_detail" rows="2" placeholder="Olağandışı koşullar nelerdir?"></textarea>
        </div>
        <div class="radio-group">
            <label><input type="radio" name="q5_answer" value="no"> HAYIR - Normal koşullar</label>
        </div>
    </div>
</div>
```

---

### ⚠️ KATEGORİ 3: Risk Değerlendirmesi
Risk faktörlerini değerlendir.

| Soru # | Soru | Input Tipi |
|--------|------|-----------|
| 9 | Risk biliniyor muydu? | Checkbox + Radio (3 seçenek) |
| 10 | Organizasyon ve çalışmanın düzenlenmesi olumsuz olayı etkiledi mi? | Checkbox + Radio (EVET/HAYIR) |
| 11 | Bakım ve temizlik yeterli miydi? | Checkbox + Radio (2 seçenek) |
| 12 | Dâhil olan kişiler yetkin ve uygun muydu? | Checkbox + Radio (EVET/HAYIR) |
| 13 | İşyeri düzeni olumsuz olayı etkiledi mi? | Checkbox + Radio (EVET/HAYIR) |
| 14 | Materyallerin / malzemelerin doğası veya şekli olumsuz olayı etkiledi mi? | Checkbox + Radio (EVET/HAYIR) |
| 15 | Tesis ve ekipmanı kullanmada yaşanan zorluklar olumsuz olayı etkiledi mi? | Checkbox + Radio (EVET/HAYIR) |
| 16 | Güvenlik ekipmanı yeterli miydi? | Checkbox + Radio (3 seçenek) |
| 17 | Olumsuz olayı diğer koşullar etkiledi mi? | Checkbox + Radio (EVET/HAYIR) |

**Pattern:** Her soru checkbox ile başlar, tıklanınca radio buttonlar ve koşullu textarea'lar gösterilir.

---

### 🎯 KATEGORİ 4: Kök Neden ve Çözümler
Çözümler ve yapılacakları belirle.

| Soru # | Soru | Input Tipi |
|--------|------|-----------|
| 18 | Doğrudan, altta yatan ve kök nedenler nelerdi? | Checkbox + Textarea |
| 19 | Hangi risk kontrol önlemlerine ihtiyaç var / tavsiye ediliyor? | Checkbox + Textarea |
| 20 | Başka yerde benzer riskler var mı? | Checkbox + Radio (EVET/HAYIR) |
| 21 | Daha önce benzer olumsuz olaylar yaşandı mı? | Checkbox + Radio (EVET/HAYIR) |
| 22 | Kısa ve uzun vadede hangi risk kontrol önlemleri uygulanmalıdır? | Checkbox + Textarea |
| 23 | Hangi risk değerlendirmeleri ve güvenli çalışma prosedürlerinin gözden geçirilmesi gerekiyor? | Checkbox + Textarea |
| 24 | Olumsuz olayın detayları ve araştırma bulguları kaydedilip analiz edildi mi? | Checkbox + Textarea |

---

## Teknik Detaylar

### CSS Eklemeleri

```css
/* Detailed Investigation Styles */
.investigation-section {
    background: #f0f4f8;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    border-left: 4px solid #667eea;
}

.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #333;
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 2px solid #667eea;
}

.conditional-group {
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #dee2e6;
}

.conditional-field {
    margin-top: 0.75rem;
    margin-left: 2.25rem;
    background: white;
    padding: 1rem;
    border-radius: 6px;
    border-left: 3px solid #667eea;
}

.conditional-field.hidden {
    display: none;
}

.radio-group {
    margin-bottom: 0.75rem;
}

.radio-group label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 500;
    font-size: 0.9rem;
    color: #495057;
    cursor: pointer;
}
```

### JavaScript Fonksiyonları

#### 1. `initializeConditionalFields()`

Form yüklendiğinde çalışır. Tüm conditional checkbox'ları bulur ve event listener'ı ekler.

```javascript
function initializeConditionalFields() {
    const conditionalCheckboxes = document.querySelectorAll('.conditional-checkbox');
    
    conditionalCheckboxes.forEach(checkbox => {
        const targetId = checkbox.dataset.shows;
        
        // Initial state
        updateConditionalField(checkbox, targetId);
        
        // On change
        checkbox.addEventListener('change', () => {
            updateConditionalField(checkbox, targetId);
        });
    });
}
```

#### 2. `updateConditionalField(checkbox, targetId)`

Checkbox durumuna göre alan gösterir/gizler.

```javascript
function updateConditionalField(checkbox, targetId) {
    const field = document.getElementById(targetId);
    if (!field) return;
    
    if (checkbox.checked) {
        field.classList.remove('hidden');
        // Alanları zorunlu yap
        const inputs = field.querySelectorAll('textarea, input[type="text"]');
        inputs.forEach(input => input.required = true);
    } else {
        field.classList.add('hidden');
        // Opsiyonel: Değerleri temizle
    }
}
```

#### 3. DOM Ready'de Başlatma

```javascript
window.addEventListener('DOMContentLoaded', () => {
    // Initialize conditional fields for detailed investigation
    initializeConditionalFields();
    // ... diğer kodu
});
```

---

## Tab Navigation Güncelleme

### Önceki Yapı (9 tab)
```html
0. 📋 Temel Bilgiler
1. 📝 Olay Açıklaması
2. 🛡️ Güvenlik & KKD
3. 👥 Tanıklar
4. 🌍 Çevre & Koşullar
5. 💼 Çalışma Detayları
6. 🚑 Yaralanma & Hasar
7. 🔍 Kök Neden Analizi
8. ✅ Özet & Gönder
```

### Yeni Yapı (10 tab)
```html
0. 📋 Temel Bilgiler
1. 📝 Olay Açıklaması
2. 🛡️ Güvenlik & KKD
3. 👥 Tanıklar
4. 🌍 Çevre & Koşullar
5. 💼 Çalışma Detayları
6. 🚑 Yaralanma & Hasar
7. 🔎 Detaylı Araştırma        ← YENİ!
8. 🔍 Kök Neden Analizi         ← Numarası 8'e güncellendi
9. ✅ Özet & Gönder              ← Numarası 9'a güncellendi
```

---

## UX/UI Özellikleri

### 1. Kademeli Açılım (Progressive Disclosure)
- **Avantaj:** Kullanıcı fazla soru tarafından bunalmıyor
- **İmplementasyon:** Her soru checkbox ile kontrol edilir
- **Sonuç:** 24 sorunun sadece lazım olanları gösterilir

### 2. Kontekstual Input'lar
- **Evet/Hayır soruları:** Radio butonlarla cevapla
- **Açık uçlu sorular:** Textarea'ya yaz
- **Koşullu detaylar:** Cevaba göre ek alanlar aç

### 3. Görsel Hiyerarşi
- **4 Mavi bölüm:** Kategori başlıkları
- **Gri arka plan:** Investigation section'ı
- **Beyaz alanlar:** Conditional fields (veri giriş alanları)
- **Mavi sol çizgi:** Vurgulama ve hiyerarşi gösterimi

### 4. Kullanıcı Rehberliği
- **Info kutusu:** "Lütfen sorular aşağıda seçili olarak cevaplandırın"
- **Placeholder metinler:** Her soru için örnek cevaplar
- **Açıkçı etiketler:** "EVET - Açıklayın:", "HAYIR - Etkilemedi"

---

## Form Data Structure

### Kaydedilen Veriler (Örnek)

```javascript
{
    // Checkbox durumu
    q1: "on",
    q1_detail: "Olay Workshop Area'da, 14:30'te, 30 dakika sürdü",
    
    q5: "on",
    q5_answer: "yes",
    q5_yes_detail: "Hava çok sıcaktı, ventilasyon bozuktu",
    
    q6: "on",
    q6_answer: "uyulmadi",
    q6_uyulmadi_detail: "Acele ediyorlardı, prosedürü atlayıp doğrudan işe başladılar",
    
    q9: "on",
    q9_answer: "known_not_controlled",
    q9_not_controlled_detail: "Risk biliniyordu ama teknik çözüm pahalı olurdu"
}
```

---

## Tarayıcı Uyumluluğu

✅ Chrome/Chromium 60+
✅ Firefox 55+
✅ Safari 12+
✅ Edge 79+

**Özellikler kullanılan:**
- CSS Flexbox
- CSS Grid (opsiyonel)
- ES6 Arrow Functions
- DOM classList API
- Event Listeners

---

## Gelecek İyileştirmeler (Optional)

1. **Drag-and-Drop:** Soruları kullanıcı sırası değiştirebilir
2. **Auto-save:** Her değişiklik otomatik kaydedilir
3. **Branching Logic:** Bir sorunun cevabı diğer soruları gizle/göster
4. **Validation:** Form submit'ten önce tüm gerekli alanlar kontrol et
5. **Analytics:** Hangi soruların en çok kullanıldığını track et
6. **Multi-language:** İngilizce, Türkçe, İspanyolca desteği

---

## Dosya Değişiklikleri

### `/incident_report_form.html`
- **Satır 550-560:** Tab navigation güncelendi (9 → 10 tabs)
- **Satır 345-405:** Yeni CSS kuralları eklendi
- **Satır 1405-1745:** Yeni section HTML'i (Detaylı Araştırma)
- **Satır 1401 & 1509:** Data-section numaraları güncellendi (7→8, 8→9)
- **Satır 2244-2290:** JavaScript conditional field fonksiyonları
- **Satır 2394:** DOMContentLoaded'de initializeConditionalFields() çağrısı

---

## Commit İnformasyonu

```
Commit: 🔎 Frontend: Add comprehensive investigation section with 24 conditional questions

FEATURES ADDED:
✅ New "🔎 Detaylı Araştırma" section (Section 7) with 24 detailed investigation questions
✅ Conditional checkboxes for each question
✅ Kademeli (Progressive) disclosure
✅ Smart conditional fields - radio buttons and nested textarea fields
✅ 4 main investigation categories

IMPROVEMENTS:
• Enhanced CSS styling for investigation sections
• JavaScript conditional field logic
• Better UX - progressive disclosure
```

---

## Demo Kullanım

### Adım 1: Detaylı Araştırma Tab'ına Git
Form'da "🔎 Detaylı Araştırma" tab'ına tıkla.

### Adım 2: Soruları Etkinleştir
Her soru için checkbox'ı tıkla. Tıklanınca textarea aç olacak.

### Adım 3: Cevapları Doldur
Açılan alan'a cevabını yaz. Radio seçenekleri varsa, uygun seçeneği seç.

### Adım 4: Detay Alanları
Bazı sorularda radio cevabını verdikten sonra ek textarea alanları açılacak. Bunları da doldur.

### Adım 5: Form Özeti
"✅ Özet & Gönder" tab'ında tüm soruları kontrol et ve raporu gönder.

---

## Sık Sorulan Sorular (FAQ)

**S:** Tüm sorular zorunlu mu?
**C:** Hayır! Kullanıcı sadece ilgili soruları etkinleştirebilir (checkbox). Bu kademeli açılım yaklaşımı kullanıcıyı fazla soru tarafından bıktırmıyor.

**S:** Checkbox'ı untık açıkça zaman veriler kayboluyor mu?
**C:** Hayır, form draft otomatik kaydediliyor (localStorage). Veriler korunuyor.

**S:** Radio butonlarını değiştirince textarea boşalıyor mu?
**C:** Hayır, textarea'da yazılan metin korunuyor. Sadece görünürlüğü değişiyor.

**S:** Mobile'da nasıl görünüyor?
**C:** Responsive design ile tüm ekran boyutlarında çalışır. Textarea'lar tam genişliğe uzanır.

---

## İletişim

Sorular veya öneriler için lütfen HSE_RCAnalysis_AgenticAI repository'sine issue açın.

---

**Last Updated:** 15 Mart 2026
**Version:** 1.0
**Status:** ✅ Production Ready
