# 🔄 Agentic AI Yapısı + RAG Entegrasyonu

## ✅ Son Durum

### Yapısal Karar
❌ **V2 Hiyerarşik Yapı** → Geri alındı
✅ **Eski Agentic 5-Why Yapısı** → Aktif
✅ **RAG Entegrasyonu** → Eklendi

## 🎯 Çalışma Prensibi

### Agentic AI Yapısı Korundu
```python
RootCauseAgent.analyze_root_causes()
  ↓
1. Immediate Causes Belirleme (AI + RAG A/B)
  ↓
2. Her Immediate Cause için 5-Why Zinciri (AI + RAG C/D)
  ↓
3. Underlying ve Root Causes Çıkarma
  ↓
4. Final Rapor Oluşturma
```

### RAG Entegrasyonu
```
add_knowledge.py (Kategori Bilgileri)
    ↓
RAG Sistemi (Vector DB)
    ↓
├─→ Immediate Causes için: A/B kategorileri
└─→ Root Causes için: C/D kategorileri
```

## 📊 Kategori Kullanımı

### ADIM 1: Immediate Causes (A/B'den)
```python
def _identify_immediate_causes(self, incident_summary):
    # RAG'den A/B kategorileri çek
    rag_context_a = self.rag.query("A kategorisi davranışsal...")
    rag_context_b = self.rag.query("B kategorisi koşullar...")
    
    # AI'a prompt'ta kategori bilgilerini ver
    prompt = f"""
    A KATEGORİSİ: {rag_context_a}
    B KATEGORİSİ: {rag_context_b}
    
    Bu kategorilerden en uygunlarını seç...
    """
```

**Kategoriler:**
- **A**: Davranışsal Nedenler (Actions)
  - A1: Prosedür İhlali
  - A2: Ekipman Yanlış Kullanım
  - A3: KKD Kullanılmaması
  - A4: İnsan Hatası

- **B**: Koşullar (Conditions)
  - B1: Koruyucu Sistem Hataları
  - B2: Ekipman Arızası
  - B3: Tehlikeli Enerji
  - B4: Alan Düzeni

### ADIM 2: Root Causes (C/D'den)
```python
def _perform_5why_for_cause(self, immediate_cause, incident_summary):
    # RAG'den C/D kategorileri çek
    rag_context_c = self.rag.query("C kategorisi kişisel...")
    rag_context_d = self.rag.query("D kategorisi organizasyonel...")
    
    # 5-Why analizinde kök neden için C/D kullan
    prompt = f"""
    C KATEGORİSİ: {rag_context_c}
    D KATEGORİSİ: {rag_context_d}
    
    Why 5 (ROOT CAUSE) → C veya D kategorisinden seç...
    """
```

**Kategoriler:**
- **C**: Kişisel Faktörler (Personal)
  - C1: Fiziksel Kapasite
  - C2: Bilişsel Yetenek
  - C3: Beceri/Yetkinlik

- **D**: Organizasyonel Faktörler (Organizational)
  - D1: Liderlik/Güvenlik Kültürü
  - D2: İletişim
  - D3: Eğitim
  - D4: Risk Kontrol
  - D5: Mühendislik
  - D6: Bakım
  - D7: Yüklenici
  - D8: Acil Durum

## 🔧 Teknik Detaylar

### RAG Kontrolü
```python
def __init__(self):
    try:
        from shared.rag_system import get_rag_system
        self.rag = get_rag_system()
        self.use_rag = True
        print("✅ RAG aktif - Kategori bilgisi yüklü")
    except:
        self.rag = None
        self.use_rag = False
        print("✅ RAG olmadan çalışıyor")
```

### Fallback Mekanizması
RAG yoksa hardcoded örnekler kullanılır:
```python
if self.use_rag:
    rag_context_a = self.rag.query("A kategorisi...")
else:
    rag_context_a = "A1.1 Kural ihlali, A1.4 Yetkisiz sapma..."
```

## 📋 Çıktı Yapısı

### Aynı Kaldı (Geriye Uyumlu)
```json
{
  "incident_summary": "...",
  "immediate_causes": [
    {
      "cause": "Operatör yetkisiz müdahale etti",
      "cause_tr": "Operatör yetkisiz müdahale etti",
      "evidence": "...",
      "evidence_tr": "..."
    }
  ],
  "five_why_chains": [
    {
      "immediate_cause": {...},
      "why_chain": [
        {"level": 1, "cause_type": "immediate", ...},
        {"level": 2, "cause_type": "underlying", ...},
        {"level": 3, "cause_type": "underlying", ...},
        {"level": 4, "cause_type": "underlying", ...},
        {"level": 5, "cause_type": "root", ...}
      ],
      "root_cause": {
        "root": "Yetersiz bakım stratejisi (D6.1)",
        "root_tr": "Yetersiz bakım stratejisi (D6.1)"
      }
    }
  ],
  "underlying_causes": [...],
  "root_causes": [...],
  "final_report_tr": "Türkçe rapor..."
}
```

## 🔄 Değişiklik Özeti

### Geri Alınan (V2)
❌ Hiyerarşik dal yapısı
❌ `analysis_branches` field
❌ Kod-bazlı kategori eşleştirme
❌ `_print_branch_tree()` fonksiyonu
❌ `_generate_hierarchical_report()` fonksiyonu

### Korunan (Eski Agentic)
✅ `analyze_root_causes()` main flow
✅ `_identify_immediate_causes()`
✅ `_perform_5why_for_cause()`
✅ `_extract_underlying_from_chain()`
✅ `_extract_root_from_chain()`
✅ `_generate_final_report()`
✅ Aynı JSON çıktı yapısı

### Eklenen (RAG)
✅ RAG sistemi entegrasyonu
✅ A/B kategorileri RAG'den
✅ C/D kategorileri RAG'den
✅ Kategori bilgisi promptlarda
✅ Fallback mekanizması

## 📝 Commit Geçmişi

1. `708acce` - V2 hiyerarşik yapı oluşturuldu
2. `5fc26a7` - V2 entegre edildi
3. `74e14ce` - Temizlik dökümantasyonu
4. **`4e2b915`** - ✅ **Eski agentic yapı geri yüklendi + RAG eklendi**

### Commit 4e2b915 Detayları:
```
- 1 file changed
- 255 insertions(+)
- 275 deletions(-)
- NET: -20 satır (temizlik)
```

## 🚀 Kullanım

### Kod Değişikliği Yok
Eski kullanım aynen çalışır:

```python
from agents.rootcause_agent import RootCauseAgent

agent = RootCauseAgent()
result = agent.analyze_root_causes(part1, part2, investigation)

# Aynı çıktı
result["immediate_causes"]
result["five_why_chains"]
result["root_causes"]
result["final_report_tr"]
```

### RAG Avantajı
Artık AI:
- ✅ A/B kategorilerini kullanarak immediate causes belirler
- ✅ C/D kategorilerini kullanarak root causes belirler
- ✅ Tutarlı kategori kodları üretir
- ✅ `add_knowledge.py`'deki bilgileri kullanır

## 🎯 Sonuç

**Karışıklık Önlendi:**
- ✅ Tek bir temiz rootcause_agent.py
- ✅ Agentic yapı korundu
- ✅ RAG sadece kategori bilgisi için kullanılıyor
- ✅ Geriye tam uyumlu
- ✅ API değişmedi

**Kategori Bilgisi Akışı:**
```
add_knowledge.py → RAG → Prompts → AI → Analysis → Results
```

Sistem artık tam istediğiniz gibi! 🎉
