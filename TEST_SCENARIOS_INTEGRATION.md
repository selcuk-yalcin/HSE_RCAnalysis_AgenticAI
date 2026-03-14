# Test Senaryoları Entegrasyonu

## 📋 Genel Bakış

Frontend manuel formuna **test senaryolarını otomatik yükleme** özelliği eklendi. Kullanıcılar artık gerçek test verilerinden örnekleri tek tıkla forma yükleyebilir.

## 🎯 Eklenen Özellikler

### 1. Test Senaryoları Veri Deposu
**Dosya:** `frontend/src/utils/testScenarios.js`

**İçerik:**
- ✅ **4 Ana Test Senaryosu:**
  - `fall_from_height` - Yüksekten Düşme (6m iskele)
  - `electrical_shock` - Elektrik Çarpması (380V)
  - `machine_entrapment` - Makine Sıkışması (konveyör)
  - `excavation_collapse` - Kazı Göçüğü (MAOG projesi)

- ✅ **Her Senaryo İçin:**
  - Çok dilli isimler (TR, EN)
  - 45+ form alanı verisi
  - Gerçek test dosyalarından alınmış detaylar
  - 5W1H yapısına uygun açıklamalar

### 2. Form Yükleme Arayüzü
**Dosya:** `frontend/src/components/IncidentForm.jsx`

**Özellikler:**
```jsx
// Test senaryosu yükleme
handleLoadTestScenario(scenarioId)

// Formu temizleme
handleClearForm()

// Test butonları UI
<div className="test-scenario-section">
  <label>Test Senaryosu Yükle</label>
  <div className="test-scenario-buttons">
    {testScenarios.map(scenario => (
      <button onClick={...}>
        {scenario.name}
      </button>
    ))}
    <button onClick={handleClearForm}>
      Formu Temizle
    </button>
  </div>
</div>
```

### 3. Stil Güncellemeleri
**Dosya:** `frontend/src/components/IncidentForm.css`

**Eklenen Stiller:**
- `.test-scenario-section` - Kapsayıcı alan (gri arka plan, kesik çizgi border)
- `.test-scenario-btn` - Mavi gradient butonlar + hover efektleri
- `.clear-form-btn` - Kırmızı outline buton

### 4. Çoklu Dil Desteği
**Dosya:** `frontend/src/utils/translations.js`

**Eklenen Çeviriler:**
```javascript
tr: {
  load_test_scenario: 'Test Senaryosu Yükle (Test Amaçlı)',
  clear_form: 'Formu Temizle',
}

en: {
  load_test_scenario: 'Load Test Scenario (Testing Purpose)',
  clear_form: 'Clear Form',
}
```

## 📊 Test Senaryoları Detayları

### 1. Yüksekten Düşme (Fall from Height)
```javascript
{
  reportedBy: 'Mustafa Çelik - Şantiye Şefi',
  incidentDate: '2026-02-18',
  location: 'Yapı İnşaat Şantiyesi - 4. Kat İskele Alanı',
  whatHappened: 'İşçi iskele kenarında çalışırken dengesini kaybetti...',
  rootCauseInitial: '1. Emniyet kemeri takılmamış\n2. Korkuluk montajı tamamlanmadan...',
  // + 40 alan daha
}
```

**Öne Çıkan Detaylar:**
- İskele yüksekliği: 6 metre
- Emniyet kemeri: Yok ❌
- Korkuluk: Montaj tamamlanmamış ❌
- Yaralanma: L2 omurga kırığı, pelvis, dalak
- Kök neden: Üretim baskısı, prosedür ihlali

### 2. Elektrik Çarpması (Electrical Shock)
```javascript
{
  reportedBy: 'İbrahim Aydın - Elektrik Bakım Sorumlusu',
  incidentDate: '2026-02-20',
  location: 'Üretim Tesisi - Ana Elektrik Panosu (MDB-02)',
  whatHappened: 'Teknisyen elektrik panosuna enerjili halde müdahale etti...',
  rootCauseInitial: '1. LOTO prosedürü uygulanmadı\n2. Üretim baskısı...',
  // + 40 alan daha
}
```

**Öne Çıkan Detaylar:**
- Voltaj: 380V 3-faz
- LOTO: Uygulanmadı ❌
- Yalıtımlı eldiven: Kullanılmadı ❌
- Yaralanma: Kardiyak arrest 30s, 2. derece yanık
- Kök neden: Risk normalleşmesi, "duruş olmasın" kültürü

### 3. Makine Sıkışması (Machine Entrapment)
```javascript
{
  reportedBy: 'Ayşe Demir - Hat Şefi',
  incidentDate: '2026-02-22',
  location: 'Ambalaj Hattı 3 - Konveyör Bandı Sistemi',
  whatHappened: 'Operatör çalışan konveyör bandına elle müdahale etti...',
  rootCauseInitial: '1. Makine çalışır durumdayken müdahale\n2. Koruyucu kapak yok...',
  // + 40 alan daha
}
```

**Öne Çıkan Detaylar:**
- Makine: Konveyör bandı (çalışır durumda)
- Koruyucu kapak: Yok ❌
- Acil durdurma: Kullanılmadı ❌
- Yaralanma: 3 parmak kırık/ezilme
- Kök neden: Kronik sıkışma sorunu, verimlilik baskısı

### 4. Kazı Göçüğü (Excavation Collapse)
```javascript
{
  reportedBy: 'Niyazi Tanrıverdi - Alt İşveren Santiye Şefi',
  incidentDate: '2026-02-12',
  location: 'MAOG Projesi, Mersin-Adana Kesimi KM 359+300',
  whatHappened: 'Yağış sonrası kazı yüzeyinde çatlak oluştu...',
  rootCauseInitial: '1. Yağış sonrası stabilite değerlendirmesi yok\n2. Yetkisiz yeniden başlatma...',
  // + 40 alan daha
}
```

**Öne Çıkan Detaylar:**
- Kazı derinliği: ~2.5m
- Hava: Şiddetli yağmur (14:30-15:15)
- Yetkisiz çalışma: Durdurulmuş iş yeniden başlatıldı ❌
- Yaralanma: Göçük altında kalma, gövde/bacak ezilme
- Kök neden: Hava koşulları göz ardı, şev açısı yetersiz

## 🎨 Kullanıcı Arayüzü

### Form Başlığı Altında:
```
┌─────────────────────────────────────────────────────────┐
│ İş Kazası Rapor Formu                                   │
│ HSG245 standartlarına göre detaylı kaza raporu          │
│                                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Test Senaryosu Yükle (Test Amaçlı)                  │ │
│ │                                                      │ │
│ │ [Yüksekten Düşme] [Elektrik Çarpması]               │ │
│ │ [Makine Sıkışması] [Kazı Göçüğü]                    │ │
│ │                              [Formu Temizle]        │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Buton Renkleri:
- **Test Butonları:** Mavi gradient (#3b82f6 → #2563eb)
- **Temizle Butonu:** Kırmızı outline (#dc2626)
- **Hover Efekti:** Yukarı kayma (translateY -1px)

## 💻 Kullanım

### 1. Kullanıcı Perspektifi
```
1. Forma gir
2. "Test Senaryosu Yükle" bölümünde butona tıkla
3. Tüm alanlar otomatik doldurulur
4. İstersen düzenle
5. "Analize Gönder" ile chat'e aktar
```

### 2. Geliştirici Perspektifi
```javascript
// Test senaryosu ekle
import { TEST_SCENARIOS } from '../utils/testScenarios';

TEST_SCENARIOS.new_scenario_id = {
  id: 'new_scenario_id',
  name: { tr: 'Yeni Senaryo', en: 'New Scenario' },
  formData: {
    reportedBy: '...',
    incidentDate: '...',
    // ... tüm alanlar
  },
};

// Kullan
const data = loadTestScenario('new_scenario_id');
```

## 📈 İstatistikler

- **Test Senaryoları:** 4 adet
- **Doldurulabilen Alan:** 45+ alan
- **Desteklenen Dil:** TR, EN (genişletilebilir)
- **Kod Satırı:** ~400 satır (testScenarios.js)
- **Form Güncelleme:** 2 fonksiyon eklendi

## 🔮 Gelecek Geliştirmeler

### Öncelik 1: Daha Fazla Senaryo
- [ ] Kimyasal sızıntı (test_chemical_spill.py)
- [ ] Rafineri patlaması (test_refinery_explosion_english.py)
- [ ] Sabotaj olayı (test_sabotage_english.py)
- [ ] Kişisel faktörler (test_personal_factors_c_category.py)

### Öncelik 2: Kategorize Edilmiş Senaryo Seçimi
```javascript
// Dropdown kategoriler
categories: {
  construction: ['fall_from_height', 'excavation_collapse'],
  electrical: ['electrical_shock'],
  machinery: ['machine_entrapment'],
  chemical: ['chemical_spill'],
  fire: ['refinery_explosion'],
}
```

### Öncelik 3: Kısmi Yükleme
```javascript
// Sadece belirli bölümleri yükle
loadSection(scenarioId, sectionName)

// Örnek: Sadece "Tanıklar" bölümünü yükle
loadSection('fall_from_height', 'witnesses')
```

### Öncelik 4: Senaryo Karşılaştırma
```javascript
// İki senaryoyu yan yana göster
compareScenarios('fall_from_height', 'electrical_shock')

// Ortak kök nedenleri bul
findCommonRootCauses([...scenarioIds])
```

## 🎯 Entegrasyon Noktaları

### Backend API (Gelecek)
```python
# /api/test-scenarios
GET /api/test-scenarios/list
GET /api/test-scenarios/{scenario_id}
POST /api/test-scenarios/random  # Rastgele senaryo
```

### Chat Entegrasyonu
```javascript
// Form → Chat geçişi
onSubmit(formData) {
  switchToChat();
  analyzeFormData(formData);
}
```

## 📝 Test Dosyaları Referansı

Test senaryoları şu dosyalardan çıkarıldı:
1. `test_fall_from_height.py` → Yüksekten Düşme
2. `test_electrical_shock.py` → Elektrik Çarpması
3. `test_machine_entrapment.py` → Makine Sıkışması
4. `test_reca_maog_detailed.py` → Kazı Göçüğü

Her test dosyası `INCIDENT_DATA` dictionary'sinde 15-20 detaylı alan içerir.

## 🏁 Özet

✅ **Tamamlanan:**
- 4 gerçekçi test senaryosu
- Tek tıkla form doldurma
- Çoklu dil desteği
- Temizleme fonksiyonu
- Profesyonel UI/UX

⏳ **Bekleyen:**
- Daha fazla senaryo eklenmesi
- Backend API entegrasyonu
- Kategori bazlı filtreleme
- Senaryo karşılaştırma özelliği

---

**Güncellenme:** 2025-05-XX  
**Versiyon:** 1.0  
**Katkıda Bulunanlar:** Copilot AI Assistant
