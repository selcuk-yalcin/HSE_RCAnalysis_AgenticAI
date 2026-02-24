# 🧪 Kapsamlı Test Paketi - test_all_scenarios.py

## 📋 Genel Bakış

Bu dosya, HSE Kök Neden Analiz sisteminin **3 farklı olay senaryosunu** tek bir test suite'inde toplar:

1. **Yüksekten Düşme** (Fall from Height) - İskele güvenliği ihlali
2. **Elektrik Çarpması** (Electrical Shock) - LOTO prosedür ihlali  
3. **Makine Sıkışması** (Machine Entrapment) - Makine güvenliği ihlali

---

## 🎯 Özellikler

### ✅ Tek Dosyada Tüm Senaryolar
- 3 farklı olay tipi tek komutta test edilebilir
- Her senaryo bağımsız çalıştırılabilir
- Otomatik environment kontrolü

### ✅ Kapsamlı Test Akışı
Her senaryo için:
```
OverviewAgent → AssessmentAgent → RootCauseAgentV2 → SkillBasedDocxAgent
```

### ✅ Çoklu Çıktı Formatı
Her senaryo için:
- ✓ JSON (kök neden analizi)
- ✓ DOCX (profesyonel rapor)
- ✓ HTML (düzenlenebilir rapor)

### ✅ Prompt Caching Optimizasyonu
- İlk test: Cache write
- Sonraki testler: Cache hit (%90 tasarruf)

### ✅ Detaylı Raporlama
- Adım adım ilerleme
- Başarı/başarısızlık durumları
- Dosya boyutları
- Süre metrikleri

---

## 🚀 Kullanım

### Temel Kullanım

```bash
# Tüm senaryoları çalıştır (3 test)
python test_all_scenarios.py

# Sadece yüksekten düşme
python test_all_scenarios.py --fall

# Sadece elektrik çarpması
python test_all_scenarios.py --electrical

# Sadece makine sıkışması
python test_all_scenarios.py --machine

# Birden fazla senaryo
python test_all_scenarios.py --fall --electrical
```

### Yardım

```bash
python test_all_scenarios.py --help
```

---

## 📊 Örnek Çıktı

### Başarılı Test Çıktısı

```
================================================================================
             HSE KÖK NEDEN ANALİZİ
             KAPSAMLI TEST PAKETİ
================================================================================

     Test Sayısı: 3
     Başlangıç: 2026-02-24 01:15:30

================================================================================
                    TEST SENARYOSU: Yüksekten Düşme
================================================================================

     Başlangıç: 2026-02-24 01:15:30

================================================================================
  ADIM 1: Ortam Kontrolü
================================================================================
  ✅ API Key: sk-or-v1-7d2...eb2b
  ✅ Çıktı dizini hazır

================================================================================
  ADIM 2: OverviewAgent
================================================================================
  ✅ Agent başlatıldı
  ✅ Ref No: INC-20260224-011530
  ✅ Olay Tipi: Major injury

================================================================================
  ADIM 3: AssessmentAgent
================================================================================
  ✅ Agent başlatıldı
  ✅ Şiddet: 1. Fatal or major
  ✅ RIDDOR: Y
  ✅ Level: High level

================================================================================
  ADIM 4: RootCauseAgentV2
================================================================================
  ✅ Agent başlatıldı
  ✅ Dallar: 3
  ✅ Kök nedenler: 3
     [1] D3.2 - Eğitim ihtiyaçlarının belirlenmemesi
     [2] D4.1 - Güvenlik kültürü eksikliği
     [3] D1.5 - Risk değerlendirmesi güncel değil
  ✅ JSON: outputs/yuksekten_dusme_20260224_011530.json

================================================================================
  ADIM 5: SkillBasedDocxAgent
================================================================================
  ✅ Agent başlatıldı
  ✅ DOCX: outputs/INC-20260224-011530_yuksekten_dusme.docx (54.2 KB)
  ✅ HTML: outputs/INC-20260224-011530_yuksekten_dusme.html (18.5 KB)

================================================================================
  TEST SONUÇ ÖZETİ
================================================================================
  Toplam Adım: 5
  Başarılı: 5
  Başarısız: 0

  Adım Detayları:
    ✅ environment: PASSED
    ✅ overview: PASSED
    ✅ assessment: PASSED
    ✅ rca: PASSED
    ✅ docx: PASSED

  Oluşturulan Dosyalar:
    📄 outputs/yuksekten_dusme_20260224_011530.json (18.2 KB)
    📄 outputs/INC-20260224-011530_yuksekten_dusme.docx (54.2 KB)
    📄 outputs/INC-20260224-011530_yuksekten_dusme.html (18.5 KB)

  Toplam Süre: 125.4 saniye

[... Diğer 2 senaryo benzer şekilde ...]

================================================================================
                           GENEL ÖZET
================================================================================
  Toplam Test: 3
  Başarılı: 3
  Başarısız: 0
  Toplam Süre: 356.8 saniye
  Ortalama Süre: 118.9 saniye/test

  Test Detayları:
    ✅ PASSED - Yüksekten Düşme (125.4s)
    ✅ PASSED - Elektrik Çarpması (112.7s)
    ✅ PASSED - Makine Sıkışması (118.7s)

  Toplam 9 dosya oluşturuldu:
    📄 outputs/yuksekten_dusme_20260224_011530.json
    📄 outputs/INC-20260224-011530_yuksekten_dusme.docx
    📄 outputs/INC-20260224-011530_yuksekten_dusme.html
    📄 outputs/elektrik_carpmasi_20260224_011732.json
    📄 outputs/INC-20260224-011732_elektrik_carpmasi.docx
    📄 outputs/INC-20260224-011732_elektrik_carpmasi.html
    📄 outputs/makine_sikismasi_20260224_011925.json
    📄 outputs/INC-20260224-011925_makine_sikismasi.docx
    📄 outputs/INC-20260224-011925_makine_sikismasi.html

  💎 Prompt Caching:
    İlk test: Cache write
    Sonraki testler: Cache hit (%90 tasarruf)
    OpenRouter: https://openrouter.ai/activity

🎉 TÜM TESTLER BAŞARILI!
```

---

## 📈 Performans Metrikleri

### Beklenen Süreler (Cache ile)

| Test | İlk Çalışma | Sonraki (Cache) | Tasarruf |
|------|-------------|-----------------|----------|
| Test 1 | ~120s | ~120s (write) | - |
| Test 2 | ~120s | ~95s (hit) | %20.8 |
| Test 3 | ~120s | ~95s (hit) | %20.8 |
| **Toplam** | **360s** | **310s** | **%13.9** |

### Maliyet (Tahmini)

| Senaryo | Token | Maliyet (Cache Yok) | Maliyet (Cache Var) | Tasarruf |
|---------|-------|---------------------|---------------------|----------|
| Test 1 | 64K | $0.089 | $0.089 | - |
| Test 2 | 64K | $0.089 | $0.012 | %86.5 |
| Test 3 | 64K | $0.089 | $0.012 | %86.5 |
| **Toplam** | **192K** | **$0.267** | **$0.113** | **%57.7** |

---

## 🔧 Teknik Detaylar

### Senaryo Yapısı

Her senaryo `ScenarioTest` sınıfından türetilir:

```python
class ScenarioTest:
    def __init__(self, name: str, incident_data: str)
    
    def run(self) -> Dict:
        # 1. Environment check
        # 2. OverviewAgent
        # 3. AssessmentAgent
        # 4. RootCauseAgentV2
        # 5. SkillBasedDocxAgent
```

### Hata Yönetimi

- Her adım try-except ile korunur
- Hata durumunda sonraki adım atlanır
- Detaylı hata mesajları ve traceback
- Exit code: 0 (başarı), 1 (başarısız), 130 (kullanıcı iptali)

### Dosya Organizasyonu

```
outputs/
├── yuksekten_dusme_YYYYMMDD_HHMMSS.json
├── INC-YYYYMMDD-HHMMSS_yuksekten_dusme.docx
├── INC-YYYYMMDD-HHMMSS_yuksekten_dusme.html
├── elektrik_carpmasi_YYYYMMDD_HHMMSS.json
├── INC-YYYYMMDD-HHMMSS_elektrik_carpmasi.docx
├── INC-YYYYMMDD-HHMMSS_elektrik_carpmasi.html
├── makine_sikismasi_YYYYMMDD_HHMMSS.json
├── INC-YYYYMMDD-HHMMSS_makine_sikismasi.docx
└── INC-YYYYMMDD-HHMMSS_makine_sikismasi.html
```

---

## 🐛 Sorun Giderme

### API Credit Yetersiz

**Hata:** `Error code: 402 - insufficient credits`

**Çözüm:**
```bash
# OpenRouter'a kredi ekleyin
open https://openrouter.ai/settings/credits
```

### Import Hatası

**Hata:** `ModuleNotFoundError: No module named 'agents'`

**Çözüm:**
```bash
# Ana dizinden çalıştırın
cd /Users/selcuk/Desktop/HSE_RCAnalysis_AgenticAI-main
python test_all_scenarios.py
```

### Test Timeout

**Belirtiler:** Test 5-10 dakikada bitmiyor

**Çözüm:**
```bash
# Streaming'i kontrol edin (skillbased_docx_agent.py)
# stream: False olmalı
```

---

## 📚 İlgili Dokümanlar

- [TEST_FALL_FROM_HEIGHT.md](./TEST_FALL_FROM_HEIGHT.md) - Düşme senaryosu detayları
- [TEST_ELECTRICAL_SHOCK.md](./TEST_ELECTRICAL_SHOCK.md) - LOTO analizi detayları
- [TEST_MACHINE_ENTRAPMENT.md](./TEST_MACHINE_ENTRAPMENT.md) - Makine güvenliği detayları
- [ANTHROPIC_PROMPT_CACHING.md](./ANTHROPIC_PROMPT_CACHING.md) - Cache optimizasyonu

---

## 🎓 Best Practices

### 1. Cache Optimizasyonu
```bash
# Tüm testleri arka arkaya çalıştırın (5 dk içinde)
python test_all_scenarios.py

# Cache expire etmesin diye 5 dakikadan kısa aralıklarla test edin
```

### 2. Seçici Test
```bash
# Sadece değiştirdiğiniz senaryoyu test edin
python test_all_scenarios.py --fall

# CI/CD'de tümünü çalıştırın
python test_all_scenarios.py
```

### 3. Sonuç Analizi
```bash
# JSON dosyalarını karşılaştırın
diff outputs/yuksekten_dusme_*.json

# Kök neden sayısını kontrol edin
jq '.final_root_causes | length' outputs/yuksekten_dusme_*.json
```

---

## 🚦 CI/CD Entegrasyonu

### GitHub Actions

```yaml
name: HSE Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run all scenarios
        env:
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
        run: python test_all_scenarios.py
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: outputs/
```

---

**Son Güncelleme:** 24 Şubat 2026  
**Versiyon:** 1.0  
**Yazar:** HSE RCA Test Sistemi
