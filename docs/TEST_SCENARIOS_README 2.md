# 🧪 Test Senaryoları - HSE Kök Neden Analiz Sistemi

Bu dizin, HSE (Health, Safety & Environment) Kök Neden Analiz sisteminin farklı olay tipleri için kapsamlı test senaryolarını içermektedir.

---

## 📚 Test Senaryoları

### 1. Yüksekten Düşme (Fall from Height)
**Dosya:** `test_fall_from_height.py`  
**Dokümantasyon:** [TEST_FALL_FROM_HEIGHT.md](./TEST_FALL_FROM_HEIGHT.md)

**Olay Özeti:**
- İnşaat şantiyesinde **6 metre yükseklikten** iskele düşmesi
- Emniyet kemeri takılmamış, korkuluk eksik
- L2 omurga kırığı, pelvis çatlağı

**Odak Noktaları:**
- ✓ Yüksekte çalışma güvenliği
- ✓ Prosedür ihlali (A kategorisi)
- ✓ Eğitim eksikliği (D3.2)
- ✓ Üretim baskısı kültürü (D4.1)

**Beklenen Çıktı:**
- RIDDOR: Y (>2m düşme)
- Investigation Level: High
- 3-4 organizasyonel kök neden

---

### 2. Elektrik Çarpması (Electrical Shock)
**Dosya:** `test_electrical_shock.py`  
**Dokümantasyon:** [TEST_ELECTRICAL_SHOCK.md](./TEST_ELECTRICAL_SHOCK.md)

**Olay Özeti:**
- **380V panoda LOTO prosedürü uygulanmadan** çalışma
- Kardiyak arrest (30 saniye), 2. derece yanıklar
- Enerji kaynağı açık, test cihazı kullanılmadı

**Odak Noktaları:**
- ✓ LOTO (Lockout/Tagout) prosedürü
- ✓ Elektrik güvenliği
- ✓ LOTO eğitimi eksikliği (D3.2)
- ✓ "Üretimi durdurmayalım" kültürü (D4.1)
- ✓ İzleme ve denetim eksikliği (D1.4)

**Beklenen Çıktı:**
- RIDDOR: Y (hospitalization >24h)
- Investigation Level: High
- LOTO prosedür ihlali odaklı 3-4 kök neden

---

### 3. Makine Sıkışması (Machine Entrapment)
**Dosya:** `test_machine_entrapment.py`  
**Dokümantasyon:** [TEST_MACHINE_ENTRAPMENT.md](./TEST_MACHINE_ENTRAPMENT.md)

**Olay Özeti:**
- Konveyör bandında **çalışan makineye müdahale**
- 3 parmak ezilmesi ve açık kırık
- Koruyucu (guard) çıkarılmış, kronik sıkışma sorunu

**Odak Noktaları:**
- ✓ Makine güvenliği (BS EN ISO 12100)
- ✓ Guard/barrier eksikliği (B2.1)
- ✓ Güvenlik kültürü (D4.1) - Guard sökme normalize
- ✓ Önleyici bakım yetersizliği (D2.2)
- ✓ Risk değerlendirmesi güncel değil (D1.5)

**Beklenen Çıktı:**
- RIDDOR: Y (>7 gün, kırık)
- Investigation Level: Medium-High
- Guard eksikliği + kronik bakım sorunları kök nedenleri

---

## 🔄 Ortak Test Akışı

Tüm testler aynı 5 adımlı yapıyı takip eder:

```
┌────────────────────────────────────────────────────────────────┐
│ ADIM 1: Ortam Kontrolü                                         │
│  • API anahtarları (OPENROUTER_API_KEY)                        │
│  • Python paketleri (openai, docx, requests, agents)           │
│  • outputs/ dizini hazırlığı                                   │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│ ADIM 2: OverviewAgent                                          │
│  • Olay tipi sınıflandırması                                   │
│  • Referans numarası üretimi (INC-YYYYMMDD-XXXXXX)             │
│  • Brief details extraction (what/where/when/who)              │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│ ADIM 3: AssessmentAgent                                        │
│  • Şiddet değerlendirmesi (Fatal/Major/Minor)                  │
│  • RIDDOR uygunluğu (Y/N)                                      │
│  • Investigation level (High/Medium/Low)                       │
│  • Investigation team belirleme                                │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│ ADIM 4: RootCauseAgentV2                                       │
│  • HSG245 metodolojisi ile hiyerarşik 5-Why analizi            │
│  • Doğrudan nedenler (A/B kategorisi)                          │
│  • Her dal için 5-Why zinciri                                  │
│  • Kök nedenler (C/D kategorisi - organizasyonel)              │
│  • JSON çıktı: outputs/<incident>_TIMESTAMP.json               │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│ ADIM 5: SkillBasedDocxAgent                                    │
│  • OpenRouter Claude Sonnet 4.5 API                            │
│  • max_tokens: 32000, temperature: 0.3, stream: False          │
│  • DOCX rapor (18-22 sayfa, 50-60 KB)                          │
│  • HTML rapor (düzenlenebilir, 15-23 KB)                       │
│  • outputs/INC-XXXXXXXX_<incident_type>.(docx|html)            │
└────────────────────────────────────────────────────────────────┘
```

---

## 📊 Beklenen Çıktılar

Her test şu dosyaları üretmelidir:

### 1. JSON Analiz Dosyası
- Dosya: `outputs/<incident>_YYYYMMDD_HHMMSS.json`
- Boyut: 16-24 KB
- İçerik: Analysis branches, why chains, final root causes

### 2. DOCX Rapor
- Dosya: `outputs/INC-XXXXXXXX_<incident>.docx`
- Boyut: 50-64 KB
- Sayfa: 18-22 sayfa
- Bölümler: 11 (Kapak, Özet, Detaylar, Metodoloji, Analiz, Kök Nedenler, Düzeltici, Dersler, Sonuç, İmzalar)

### 3. HTML Rapor (Düzenlenebilir)
- Dosya: `outputs/INC-XXXXXXXX_<incident>.html`
- Boyut: 15-23 KB
- Özellikler: contenteditable, localStorage, print-friendly

---

## ✅ Başarı Kriterleri

Test başarılı sayılır eğer:

1. ✅ Tüm 5 adım PASSED durumunda
2. ✅ RIDDOR doğru tespit edildi (Y/N)
3. ✅ Investigation level doğru (High/Medium/Low)
4. ✅ Kök neden sayısı 3-4 (organizasyonel, D kategorisi)
5. ✅ DOCX boyutu >50 KB (tam içerik)
6. ✅ HTML boyutu >15 KB
7. ✅ JSON geçerli ve ayrıştırılabilir

---

## 🚀 Testleri Çalıştırma

### Tek Test

```bash
# Virtual environment aktif et
source .venv/bin/activate

# Yüksekten düşme testi
python test_fall_from_height.py

# Elektrik testi
python test_electrical_shock.py

# Makine testi
python test_machine_entrapment.py
```

### Tüm Testler

```bash
# Tüm testleri sırayla çalıştır
for test in test_fall_from_height test_electrical_shock test_machine_entrapment; do
    echo "Running $test..."
    python ${test}.py
    echo "---"
done
```

### Çıktıları Kontrol Et

```bash
# Son 3 raporu listele
ls -lht outputs/INC-* | head -6

# JSON dosyalarını kontrol et
ls -lh outputs/*_202*.json

# Kök neden sayısını kontrol et
jq '.final_root_causes | length' outputs/fall_from_height_*.json
```

---

## 🐛 Sorun Giderme

### API Kredi Yetersiz
**Hata:** `Error code: 402 - insufficient credits`  
**Çözüm:**
```bash
# OpenRouter hesabınıza kredi ekleyin
open https://openrouter.ai/settings/credits
```

### DOCX Sadece Kapak Sayfası
**Hata:** Rapor 37 KB, içerik eksik  
**Kontrol:**
```bash
# agents/skillbased_docx_agent.py içinde:
# - stream: False olmalı (line 974)
# - max_tokens: 32000 (line 972)
# - timeout: 600 (line 987)
```

### Import Hatası
**Hata:** `ModuleNotFoundError: No module named 'agents'`  
**Çözüm:**
```bash
# Ana dizinden çalıştırın
cd /Users/selcuk/Desktop/HSE_RCAnalysis_AgenticAI-main
python test_fall_from_height.py
```

### Agent Metod Hatası
**Hata:** `AttributeError: ... object has no attribute 'analyze'`  
**Çözüm:** Test dosyalarındaki agent metod çağrılarını düzeltin:
```python
# Yanlış:
result = agent.analyze(incident_data)

# Doğru (agent kaynak kodunu kontrol edin):
result = agent.process_initial_report(incident_dict)
```

---

## 📚 Ek Kaynaklar

### Dokümantasyon
- [HSG245 Methodology](../docs/HSG245_methodology.md)
- [RIDDOR Reporting Guide](../docs/RIDDOR_guide.md)
- [5-Why Technique](../docs/5why_technique.md)
- [OpenRouter API Guide](https://openrouter.ai/docs)

### Standartlar
- **RIDDOR 2013** - UK injury reporting regulations
- **HSG245** - UK HSE hierarchical root cause analysis
- **BS EN ISO 12100:2010** - Machinery safety
- **OSHA 1910.147** - LOTO standard
- **IEC 61508** - Functional safety

### HSE Kaynakları
- [HSE UK Official Site](https://www.hse.gov.uk/)
- [IOSH UK](https://iosh.com/)
- [Institution of Occupational Safety and Health](https://www.iosh.com/)

---

## 🔧 Sistem Gereksinimleri

### Python Paketleri
```bash
pip install openai python-docx requests
```

### API Anahtarları
```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
```

### Minimum Kaynaklar
- **API Kredisi:** ~64,000 tokens/test
- **Disk Alanı:** ~100 KB/test çıktısı
- **RAM:** 2 GB
- **İnternet:** API çağrıları için stabil bağlantı

---

## 📈 Test Kapsama Matrisi

| Test                   | RIDDOR | Şiddet        | Olay Tipi          | Odak Kök Nedenler         |
|------------------------|--------|---------------|--------------------|---------------------------|
| Fall from Height       | Y      | Major/Fatal   | Height work        | D3.2, D4.1, D1.5          |
| Electrical Shock       | Y      | Major/Fatal   | Electrical         | D3.2, D4.1, D1.4          |
| Machine Entrapment     | Y      | Major         | Machinery          | D4.1, D2.2, D1.5          |

### Kök Neden Kategorileri (HSG245)
- **A (Human):** İnsan hataları, prosedür ihlalleri
- **B (Conditional):** Koşulsal faktörler, ekipman durumu
- **C (Task):** Görev ve iş talimatları
- **D (Organizational):** Organizasyonel sistemler (hedef kök nedenler)

---

## 📞 Destek

**Proje Sahibi:** HSE RCA Test Sistemi  
**Versiyon:** 1.0  
**Son Güncelleme:** 23 Şubat 2026  

**Sorunlar için:**
1. Önce ilgili test dokümantasyonunu inceleyin
2. Sorun giderme bölümüne bakın
3. Agent kaynak kodunu kontrol edin (`agents/` dizini)
4. OpenRouter API durumunu kontrol edin

---

**Not:** Bu testler **gerçek HSE olayları** için kullanılabilir ancak burada verilen senaryolar **eğitim amaçlı örnek olaylar**dır.
