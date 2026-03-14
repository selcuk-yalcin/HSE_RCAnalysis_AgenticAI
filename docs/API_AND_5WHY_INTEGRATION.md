# 🔗 API Kullanımı ve 5-Why Entegrasyonu

**Tarih:** 1 Mart 2026  
**Sistem:** HSE_RCAnalysis_AgenticAI  
**Versiyon:** V2.2

---

## 🌐 Kullanılan API

### 1️⃣ OpenRouter API
**Base URL:** `https://openrouter.ai/api/v1`  
**API Key:** `OPENROUTER_API_KEY` (environment variable)  
**Fallback:** `OPENAI_API_KEY` (eğer OpenRouter yoksa)

### 2️⃣ Kullanılan Modeller

#### RootCauseAgentV2 (2 farklı model)

**A/B Kategorisi (Immediate Causes):**
```python
model="anthropic/claude-sonnet-4.5"
temperature=0.4
max_tokens=3000
```

**5-Why Analizi (Root Causes):**
```python
model="anthropic/claude-opus-4.6"  # Daha güçlü model
temperature=0.6
max_tokens=4000
```

#### Diğer Agentlar
- **OverviewAgent:** `anthropic/claude-sonnet-4.5`
- **AssessmentAgent:** `anthropic/claude-sonnet-4.5`
- **SkillBasedDocxAgent:** `anthropic/claude-sonnet-4.5`

---

## 🔍 Mevcut 5-Why Sistem Mimarisi

### Hiyerarşik Yapı (HSG245 Taxonomy)

```
┌─────────────────────────────────────────────┐
│         OLAY RAPORU (İnput)                 │
│  - Incident description                     │
│  - Investigation data (part1, part2)        │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  ADIM 1: Immediate Causes (A/B)            │
│  Model: claude-sonnet-4.5                   │
│  Temperature: 0.4                           │
│                                             │
│  A - DAVRANIŞLAR (Actions)                 │
│    A1.x: Prosedür ihlali                   │
│    A2.x: Ekipman kullanımı                 │
│    A3.x: KKD kullanımı                     │
│    A4.x: Fiziksel/zihinsel durum           │
│    A5.x: Pozisyon/hareket                  │
│                                             │
│  B - KOŞULLAR (Conditions)                 │
│    B1.x: Çevresel faktörler                │
│    B2.x: Ekipman arızaları                 │
│    B3.x: Çalışma ortamı                    │
│    B4.x: Housekeeping                      │
│                                             │
│  Output: Max 3 immediate cause             │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  ADIM 2: 5-Why Zinciri (Her cause için)   │
│  Model: claude-opus-4.6                     │
│  Temperature: 0.6                           │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ Immediate Cause [A1.1]              │   │
│  │                                     │   │
│  │ Why 1? → Ara faktör                │   │
│  │ Why 2? → Ara faktör                │   │
│  │ Why 3? → Daha derin faktör         │   │
│  │ Why 4? → Sistemik faktör           │   │
│  │ Why 5? → ROOT CAUSE [C/D]          │   │
│  │                                     │   │
│  │ C - KİŞİSEL FAKTÖRLER              │   │
│  │   C1.x: Yeterlilik                 │   │
│  │   C2.x: Yorgunluk                  │   │
│  │   C3.x: Sağlık                     │   │
│  │                                     │   │
│  │ D - ORGANİZASYONEL FAKTÖRLER       │   │
│  │   D1.x: Liderlik                   │   │
│  │   D2.x: İletişim                   │   │
│  │   D3.x: Eğitim                     │   │
│  │   D4.x: Prosedür                   │   │
│  │   D5.x: Tasarım                    │   │
│  │   D6.x: Bakım                      │   │
│  │   D7.x: Organizasyon               │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  Output: 5-level Why chain per cause       │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  ADIM 3: Final Report Generation           │
│  - Tüm dallar birleştirilir                │
│  - HSG245 kodları ile eşleştirilir         │
│  - Türkçe rapor oluşturulur                │
└─────────────────────────────────────────────┘
```

---

## 💡 Mevcut 5-Why Özellikleri

### ✅ Sistemdeki Mevcut Fonksiyonlar

#### 1. `analyze_root_causes(part1_data, part2_data, investigation_data)`
**Dosya:** `agents/rootcause_agent_v2.py` (satır 82-150)

**Input:**
- `part1_data`: OverviewAgent çıktısı (incident classification)
- `part2_data`: AssessmentAgent çıktısı (severity, RIDDOR)
- `investigation_data`: Ham olay verisi

**Output:**
```json
{
  "incident_summary": "...",
  "analysis_branches": [
    {
      "immediate_cause": {...},
      "five_why_chain": {...},
      "root_cause": {...}
    }
  ],
  "final_root_causes": [...],
  "analysis_method": "HSG245 Hierarchical 5-Why (A/B → C/D)"
}
```

#### 2. `_identify_immediate_causes_with_codes(incident_summary)`
**Dosya:** `agents/rootcause_agent_v2.py` (satır 158-270)

**Görev:**
- A/B kategorilerinden max 3 immediate cause seç
- Her cause için HSG245 kodu belirle
- Spesifiklik kontrolü (jenerik kodlar önlenmiş)

**AI Prompt Kuralları:**
```python
1. SADECE RAPORDA YAZANLARI KULLAN
   - Raporda olmayan ekipman/kişi ekleme
   
2. DOĞRUDAN NEDENLER
   - Dolaylı faktörleri (eğitim, risk değ.) seçme
   
3. MAX 3 ADET
   - Zorla doldurma
   
4. ÇEŞİTLİLİK
   - Hem A (davranış) hem B (koşul) seç
   
5. SPESİFİKLİK
   - "Risk değerlendirmesi eksik" gibi genel ifadeler kullanma
```

#### 3. `_perform_5why_chain(immediate_cause, incident_summary, used_root_codes)`
**Dosya:** `agents/rootcause_agent_v2.py` (satır 272-420)

**Görev:**
- Bir immediate cause için 5-Why zinciri oluştur
- Root cause C/D kategorisinden seç
- Kod tekrarını engelle (used_root_codes)

**AI Prompt Kuralları:**
```python
A) SADECE RAPORDA YAZANLARA DAYAN
   - Her why sorusu rapordaki bulgulara dayanmalı
   
B) YASAK KODLAR
   - Önceki dallarda kullanılan root cause'ları tekrar seçme
   
C) SPESİFİKLİK KURALI
   - Jenerik kodlar yerine spesifik kodlar seç
   
D) ZİNCİR TUTARLILIĞI
   - Root cause, 5-Why'ın mantıksal sonucu olmalı
```

**5-Why Zinciri Yapısı:**
```json
{
  "whys": [
    {"level": 1, "question_tr": "Neden X oldu?", "answer_tr": "..."},
    {"level": 2, "question_tr": "Neden Y oldu?", "answer_tr": "..."},
    {"level": 3, "question_tr": "Neden Z oldu?", "answer_tr": "..."},
    {"level": 4, "question_tr": "Neden W oldu?", "answer_tr": "..."},
    {"level": 5, "question_tr": "Neden V oldu?", "answer_tr": "..."}
  ],
  "root_cause": {
    "code": "D3.1",
    "standard_title_tr": "Yetersiz veya eksik eğitim",
    "custom_description_tr": "Elektrik işlerinde LOTO prosedürü eğitimi verilmemiş"
  }
}
```

---

## 🆕 HITL Sistemi ile Entegrasyon Fırsatı

### Mevcut Durum

**Şu anda sistem:**
1. ✅ Ham olay verisi alıyor
2. ✅ AI otomatik olarak immediate causes tespit ediyor
3. ✅ AI otomatik olarak 5-Why zinciri kuruyor
4. ✅ AI otomatik olarak root cause seçiyor

**Sorun:**
- ❌ Kullanıcı müdahale edemiyor
- ❌ Eğer AI yanlış immediate cause seçerse, tüm analiz yanlış gider
- ❌ 5-Why soruları kullanıcıya sorulmuyor, AI kendi cevaplıyor

### 🎯 Önerilen HITL Entegrasyonu

#### Senaryo 1: Immediate Causes Onayı (Basit)

```python
# 1. AI immediate causes önerir
immediate_causes = agent._identify_immediate_causes_with_codes(incident_summary)

# 2. Kullanıcıya göster (Gradio TAB 2.5)
# "Bu doğrudan nedenleri onaylıyor musunuz?"
# [A1.1] Prosedür ihlali ✅ Onayla | ✏️ Düzenle | ❌ Sil

# 3. Kullanıcı onayladıktan sonra 5-Why devam eder
for cause in approved_causes:
    branch = agent._perform_5why_chain(cause, incident_summary)
```

#### Senaryo 2: 5-Why Sorularını Kullanıcıya Sor (İdeal)

```python
# 1. AI immediate cause tespit eder: [A1.1] Prosedür ihlali

# 2. Question Engine soruları üretir:
questions = question_engine.get_code_specific_questions(['A1.1'])
# → "Çalışan kuralı/prosedürü biliyor muydu?"
# → "İhlal daha önce de yapılmış mıydı?"

# 3. Kullanıcı cevapları TAB 2'de verir (HITL)
answers = {
    "Çalışan kuralı biliyor muydu?": "Hayır, eğitim almamış",
    "İhlal daha önce de yapılmış mıydı?": "Evet, sık yapılıyor"
}

# 4. AI bu cevaplarla 5-Why zinciri kurar
five_why_chain = agent._perform_5why_chain_with_user_input(
    immediate_cause={'code': 'A1.1', ...},
    user_answers=answers,
    incident_summary=incident_summary
)

# → Why 1: "Çalışan neden prosedürü ihlal etti?"
#   Answer: "Çalışan prosedürü bilmiyordu (kullanıcı cevabı)"
#
# → Why 2: "Neden bilmiyordu?"
#   Answer: "Eğitim almamış (kullanıcı cevabı)"
#
# → Why 3-5: AI mantıksal zinciri tamamlar
#   → Root Cause: [D3.1] Yetersiz eğitim
```

#### Senaryo 3: Tam HITL (Gelişmiş)

```python
# 1. TAB 1: Olay girişi → Level tespit
# 2. TAB 2: Question Engine soruları → Kullanıcı cevaplar
# 3. TAB 2.5: AI immediate causes önerir → Kullanıcı onaylar/düzenler
# 4. TAB 3: Her cause için 5-Why → Kullanıcı her why'ı doğrular
# 5. TAB 3.5: Root causes → Kullanıcı onaylar
# 6. TAB 4: Final report
```

---

## 🔧 Entegrasyon Kod Örnekleri

### Örnek 1: Gradio TAB 3'e 5-Why Gösterimi

```python
# gradio_app_test.py - TAB 3 eklentisi

def show_5why_analysis():
    """RootCauseAgentV2'den gelen 5-Why zincirini göster"""
    
    if not state["generated_questions"]:
        return "Önce TAB 2'de soruları yanıtlayın!"
    
    # Kullanıcı cevaplarını topla
    user_answers = state["answers"]
    incident_text = state["incident_text"]
    
    # RootCauseAgentV2 başlat
    from agents.rootcause_agent_v2 import RootCauseAgentV2
    agent = RootCauseAgentV2()
    
    # Part1, Part2 verisi (basitleştirilmiş - gerçekte OverviewAgent'tan gelir)
    part1 = {"description": incident_text}
    part2 = {"severity": "Major"}
    
    # Kök neden analizi
    rca_result = agent.analyze_root_causes(part1, part2)
    
    # Sonuçları formatla
    output = "## 🔍 5-Why Analiz Sonuçları\n\n"
    
    for branch in rca_result["analysis_branches"]:
        immediate = branch["immediate_cause"]
        five_why = branch["five_why_chain"]
        
        output += f"### [{immediate['code']}] {immediate['cause_tr']}\n\n"
        
        for why in five_why["whys"]:
            output += f"**Why {why['level']}:** {why['question_tr']}\n"
            output += f"→ {why['answer_tr']}\n\n"
        
        root = five_why["root_cause"]
        output += f"**🎯 Root Cause:** [{root['code']}] {root['standard_title_tr']}\n"
        output += f"{root['custom_description_tr']}\n\n"
        output += "---\n\n"
    
    return output
```

### Örnek 2: QuestionEngine'den 5-Why'a Veri Akışı

```python
# question_engine.py - Yeni fonksiyon

def prepare_5why_input(category_answers: dict, incident_text: str) -> dict:
    """
    Kullanıcı cevaplarını 5-Why analizi için hazırla
    
    Args:
        category_answers: {
            "prosedür": "Prosedür vardı ama uygulanmadı",
            "ekipman": "Ekipman arızalıydı, rapor edilmemiş",
            ...
        }
        incident_text: Olay metni
    
    Returns:
        {
            "immediate_cause_hints": ["A1.1", "A2.3"],
            "context_for_why": {
                "prosedür_durumu": "var ama uygulanmadı",
                "ekipman_durumu": "arızalı, raporsuz"
            }
        }
    """
    
    code_hints = []
    context = {}
    
    # Cevaplardan HSG245 kod ipuçları çıkar
    for category, answer in category_answers.items():
        if "prosedür" in category.lower():
            if "yoktu" in answer.lower():
                code_hints.append("D4.1")  # Prosedür yokluğu
            elif "ihlal" in answer.lower():
                code_hints.append("A1.1")  # Prosedür ihlali
            elif "eski" in answer.lower():
                code_hints.append("A1.5")  # Güncel olmayan
            
            context["prosedür_durumu"] = answer
        
        elif "ekipman" in category.lower():
            if "arızalı" in answer.lower():
                code_hints.append("A2.3")  # Arızası bilinen ekipman
            elif "bakım" in answer.lower():
                code_hints.append("D6.1")  # Bakım eksikliği
            
            context["ekipman_durumu"] = answer
        
        elif "eğitim" in category.lower():
            if "almamış" in answer.lower():
                code_hints.append("D3.1")  # Yetersiz eğitim
            
            context["eğitim_durumu"] = answer
    
    return {
        "immediate_cause_hints": list(set(code_hints)),
        "context_for_why": context
    }
```

### Örnek 3: Hybrid 5-Why (AI + User Input)

```python
# rootcause_agent_v2.py - Yeni fonksiyon

def _perform_5why_chain_hybrid(
    self,
    immediate_cause: Dict,
    incident_summary: str,
    user_context: Dict = None,
    used_root_codes: List[str] = None
) -> Dict:
    """
    Kullanıcı cevaplarıyla zenginleştirilmiş 5-Why analizi
    
    Args:
        immediate_cause: AI'ın tespit ettiği immediate cause
        incident_summary: Olay özeti
        user_context: QuestionEngine'den gelen kullanıcı cevapları
        used_root_codes: Daha önce kullanılan root cause kodları
    """
    
    # Standart prompt'u hazırla
    base_prompt = self._get_5why_prompt(immediate_cause, incident_summary, used_root_codes)
    
    # Eğer kullanıcı cevapları varsa, prompt'a ekle
    if user_context and "context_for_why" in user_context:
        context_str = "\n\nKULLANICI CEVAPLARI (5-Why zincirinde MUTLAKA kullan):\n"
        for key, value in user_context["context_for_why"].items():
            context_str += f"- {key}: {value}\n"
        
        base_prompt += context_str
        base_prompt += "\n⚠️ Bu kullanıcı cevaplarını Why chain'inde kullan!\n"
    
    # API çağrısı (mevcut kod ile aynı)
    response = self.client.chat.completions.create(
        model="anthropic/claude-opus-4.6",
        messages=[{"role": "user", "content": base_prompt}],
        temperature=0.6,
        max_tokens=4000
    )
    
    # Parse ve return (mevcut kod ile aynı)
    ...
```

---

## 📊 Veri Akış Diyagramı (Önerilen HITL Entegrasyonu)

```
┌────────────────────────┐
│ TAB 1: Olay Girişi     │
│ - Incident text        │
│ - HybridInputProcessor │
│ - Level tespit         │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────────────────────┐
│ TAB 2: HSG245 Sorular (QuestionEngine)│
│ - Eksik kategoriler için sorular      │
│ - Kullanıcı cevaplar                  │
│ - prepare_5why_input() → context      │
└───────────┬────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│ TAB 2.5: Immediate Causes (AI Öneri)   │
│ - RCA._identify_immediate_causes()     │
│ - Kullanıcı onaylar/düzenler           │
│ - [A1.1] ✅  [A2.3] ✏️  [B2.1] ❌     │
└───────────┬─────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────┐
│ TAB 3: 5-Why Analizi (Hybrid)           │
│ - Her immediate cause için:             │
│   ├─ User context inject edilir         │
│   ├─ RCA._perform_5why_chain_hybrid()  │
│   ├─ AI Why 1-5 üretir                 │
│   └─ Kullanıcı her why'ı doğrular      │
│                                          │
│ [A1.1] Prosedür ihlali                  │
│ Why 1: Çalışan prosedürü bilmiyordu     │
│        (user: "eğitim almamış")          │
│ Why 2: Eğitim planlanmamış              │
│ ...                                      │
│ Why 5: [D3.1] Yetersiz eğitim sistemi   │
│                                          │
│ ✅ Onayla | ✏️ Düzenle | 🔄 Yeniden Üret│
└───────────┬──────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│ TAB 4: Final Report                     │
│ - SkillBasedDocxAgent                   │
│ - DOCX + HTML export                    │
│ - HSG245 kodları dahil                  │
└─────────────────────────────────────────┘
```

---

## ✅ Önerilen Geliştirme Adımları

### Hafta 1: Basit Entegrasyon
1. [ ] TAB 3 oluştur: `show_5why_analysis()` fonksiyonu
2. [ ] RootCauseAgentV2'yi Gradio'ya import et
3. [ ] 5-Why sonuçlarını görselleştir
4. [ ] Test: Minimal input ile end-to-end akış

### Hafta 2: Context Injection
1. [ ] `prepare_5why_input()` fonksiyonu ekle
2. [ ] QuestionEngine cevaplarını RCA'ya gönder
3. [ ] `_perform_5why_chain_hybrid()` fonksiyonu yaz
4. [ ] Test: User context'in why chain'e yansımasını doğrula

### Hafta 3: User Validation
1. [ ] TAB 2.5: Immediate causes onay ekranı
2. [ ] TAB 3: Her why için edit/approve butonu
3. [ ] State management (onaylanmış vs pending)
4. [ ] Test: Kullanıcı düzeltme akışı

### Hafta 4: Final Integration
1. [ ] TAB 4: Final report preview
2. [ ] API endpoints (`api/main.py`)
3. [ ] Frontend (Infera) entegrasyonu
4. [ ] E2E test senaryoları

---

## 🔑 Kritik Noktalar

### ✅ Avantajlar
1. **Mevcut sistem zaten çalışıyor** - Sadece kullanıcı validasyonu eklenecek
2. **HSG245 taxonomy entegreli** - QuestionEngine kodları AI'ın kodlarıyla uyumlu
3. **2-stage model kullanımı** - Immediate causes için Sonnet, Root cause için Opus
4. **Kod tekrarı önleniyor** - `used_root_codes` mekanizması var

### ⚠️ Dikkat Edilecekler
1. **State senkronizasyonu** - Gradio state ile RCA output'u eşleşmeli
2. **Prompt injection** - User input'u prompt'a eklerken sanitize et
3. **API cost** - Her immediate cause için Opus çağrısı maliyetli
4. **Türkçe/İngilizce** - Language detection tüm sistemde tutarlı olmalı

---

## 📞 Teknik Detaylar

**API Provider:** OpenRouter  
**Model 1:** anthropic/claude-sonnet-4.5 (Immediate Causes)  
**Model 2:** anthropic/claude-opus-4.6 (5-Why Analysis)  
**Knowledge Base:** HSG245 Taxonomy (Python dict, no RAG needed)  
**5-Why Method:** Hierarchical (A/B → C/D)  
**Code Diversity:** `used_root_codes` tracking  
**Prompt Versiyonu:** V2.2 (Incident summary fix applied)

---

**Son Güncelleme:** 1 Mart 2026  
**Durum:** ✅ Sistem analizi tamamlandı  
**Sonraki Adım:** TAB 3 - 5-Why görselleştirme implementasyonu
