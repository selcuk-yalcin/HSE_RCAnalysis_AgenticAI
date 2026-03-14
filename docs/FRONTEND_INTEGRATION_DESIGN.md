# Frontend Entegrasyon Tasarımı - Infera Platform

## 📋 Genel Bakış

Bu belge, **HITL (Human-in-the-Loop)** sisteminin **Infera frontend** platformuna nasıl entegre edileceğini detaylandırır.

---

## 🎨 Mevcut Infera Yapısı (Ekran Görüntülerinden)

### **Mevcut Akış:**
```
Part 1: Overview → Part 2: Assessment → Part 3: Info Gathering → Part 4: Risk Control
```

### **Part 3: Info Gathering (Kök Neden İncelemesi)**
- Yapay Zeka Analizi (AI Powered) butonu var ✅
- **3 Alan:**
  1. **Immediate Causes** (Doğrudan Nedenler)
  2. **Underlying Causes** (Altta Yatan Nedenler)
  3. **Root Causes** (Kök Nedenler)

### **Part 4: Risk Control Action Plan**
- AI Generated Analysis (Root Causes) butonu var ✅
- Aynı 3 alan tekrar ediliyor

---

## 🔄 Önerilen HITL Entegrasyonu

### **Senaryo 1: Minimal Entegrasyon (Sadece AI Butonu Değişikliği)**

#### Mevcut Durum:
```
[AI Powered] butonu → Direkt AI analiz → Sonuç doldurulur
```

#### Yeni Durum:
```
[AI Powered + HITL] butonu → Modal açılır → Kullanıcı soruları yanıtlar → Sonuç doldurulur
```

**Değişiklik:**
- `Part 1: Overview` ekranındaki "Brief details" textarea'sı **girdi kaynağı** olur
- AI butonu modal açar
- Modal içinde HITL sorgulama yapar
- Sonuçlar Part 3 ve Part 4'e otomatik doldurulur

---

### **Senaryo 2: Tam Entegrasyon (Yeni Tab Ekleme)**

#### Yeni Akış:
```
Part 1: Overview 
  ↓
Part 2: Assessment
  ↓
Part 2.5: HITL Interactive Analysis (YENİ!)  ← Burada sorgulama yapılır
  ↓
Part 3: Info Gathering (Otomatik doldurulur)
  ↓
Part 4: Risk Control (Otomatik doldurulur)
```

**Avantaj:**
- Kullanıcı deneyimi daha iyi
- Sorgulama süreci görünür
- Kullanıcı her aşamayı görebilir

---

## 🛠️ Teknik Entegrasyon (API Bazlı)

### **Backend API Endpoint'leri (FastAPI)**

```python
# api/main.py içine eklenecek

@app.post("/api/hitl/analyze-input")
async def analyze_input(incident_data: IncidentInput):
    """
    Part 1'deki brief details'i analiz eder.
    Girdi seviyesini tespit eder.
    """
    processor = HybridInputProcessor()
    level, details = processor.detect_input_level(incident_data.brief_details)
    
    return {
        "input_level": level,
        "missing_categories": details["missing"],
        "present_categories": details["present"],
        "needs_questions": level > 1,
        "questions": generate_questions(details["missing"]) if level > 1 else []
    }


@app.post("/api/hitl/get-next-question")
async def get_next_question(context: QuestionContext):
    """
    Bir sonraki soruyu üretir.
    """
    engine = QuestionEngine()
    question = engine.generate_contextual_question(
        context=context.dict(),
        current_code=context.last_code,
        incident_type=context.incident_type
    )
    
    return question


@app.post("/api/hitl/submit-answer")
async def submit_answer(answer: UserAnswer):
    """
    Kullanıcı cevabını işler ve sonraki adımı belirler.
    """
    # Cevabı kaydet
    # Bir sonraki soruyu belirle veya kök neden analizi yap
    
    if answer.is_final:
        # Kök neden analizi yap
        rca_agent = RootCauseAgentV2()
        result = rca_agent.analyze_root_causes(...)
        
        return {
            "status": "completed",
            "root_causes": result["final_root_causes"],
            "branches": result["analysis_branches"]
        }
    else:
        # Sonraki soru
        next_q = get_next_question(...)
        return {
            "status": "next_question",
            "question": next_q
        }


@app.post("/api/hitl/generate-report")
async def generate_report(approved_data: ApprovedData):
    """
    Onaylanmış verilerle rapor oluşturur.
    """
    agent = SkillBasedDocxAgent()
    result = agent.generate_report(approved_data.dict(), ...)
    
    return {
        "docx_path": result,
        "html_path": result.replace('.docx', '.html')
    }
```

---

## 🎨 Frontend Tasarım (Infera Platformu)

### **Option A: Modal ile Entegrasyon**

#### **Part 3: Info Gathering** Ekranı

Mevcut durumda:
```html
<button class="ai-powered-btn">
  🤖 AI Powered
</button>

<textarea id="olay-detaylari">
  Örn: Operatör makine çalışırken güvenlik koruyucusunu açtı...
</textarea>
```

Yeni durum:
```html
<button class="ai-hitl-btn" onclick="openHITLModal()">
  🤖 AI + Interactive Analysis
</button>

<div id="hitl-modal" class="modal">
  <div class="modal-content">
    <h3>🔍 Interaktif Kök Neden Analizi</h3>
    
    <!-- Adım göstergesi -->
    <div class="progress-bar">
      <div class="step active">Analiz</div>
      <div class="step">Sorgulama</div>
      <div class="step">Onay</div>
      <div class="step">Rapor</div>
    </div>
    
    <!-- Dinamik içerik alanı -->
    <div id="hitl-content">
      <!-- ADIM 1: Girdi Analizi -->
      <div class="analysis-result">
        <p>📊 Girdi Seviyesi: <strong>Level 2 (Orta)</strong></p>
        <p>Eksik Bilgiler: Prosedür, Eğitim, Yönetim</p>
        <button onclick="startQuestioning()">Sorgulamaya Başla →</button>
      </div>
    </div>
  </div>
</div>
```

**JavaScript Örneği:**
```javascript
async function openHITLModal() {
  const briefDetails = document.getElementById('olay-detaylari').value;
  
  // API çağrısı
  const response = await fetch('/api/hitl/analyze-input', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({brief_details: briefDetails})
  });
  
  const data = await response.json();
  
  if (data.needs_questions) {
    showQuestions(data.questions);
  } else {
    directlyAnalyze();
  }
}

async function showQuestions(questions) {
  const container = document.getElementById('hitl-content');
  
  questions.forEach((q, index) => {
    const questionHTML = `
      <div class="question-card">
        <h4>❓ Soru ${index + 1}/${questions.length}</h4>
        <p>${q.question_text}</p>
        
        <div class="options">
          ${q.options.map(opt => `
            <label>
              <input type="radio" name="q_${index}" value="${opt.code}">
              ${opt.label}
            </label>
          `).join('')}
        </div>
        
        <button onclick="submitAnswer(${index})">İlerle →</button>
      </div>
    `;
    
    container.innerHTML = questionHTML;
  });
}

async function submitAnswer(questionIndex) {
  const selectedOption = document.querySelector(`input[name="q_${questionIndex}"]:checked`);
  
  const response = await fetch('/api/hitl/submit-answer', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      question_id: questionIndex,
      selected_code: selectedOption.value,
      // ... diğer context bilgileri
    })
  });
  
  const result = await response.json();
  
  if (result.status === 'completed') {
    // Kök nedenler bulundu!
    fillRootCauses(result.root_causes);
    closeModal();
  } else {
    // Sonraki soru
    showQuestions([result.question]);
  }
}

function fillRootCauses(rootCauses) {
  // Part 3'teki textarea'lara doldur
  document.getElementById('immediate-causes').value = rootCauses.immediate.join('\n');
  document.getElementById('underlying-causes').value = rootCauses.underlying.join('\n');
  document.getElementById('root-causes').value = rootCauses.root.join('\n');
}
```

---

### **Option B: Yeni Tab (Part 2.5) Ekleme**

#### **Yeni Sayfa: Part 2.5 - Interactive Root Cause Analysis**

```html
<div class="part-container">
  <h2>Bölüm 2.5: Interaktif Kök Neden Analizi</h2>
  
  <div class="ai-analysis-status">
    <span class="status-badge">✅ Analiz Tamamlandı</span>
    <button class="re-analyze-btn">🔄 Yeniden Analiz Et</button>
  </div>
  
  <!-- Girdi Seviye Göstergesi -->
  <div class="input-level-indicator">
    <h3>📊 Girdi Değerlendirmesi</h3>
    <div class="level-badge level-2">
      <strong>Level 2:</strong> Orta Detay
    </div>
    <p>Mevcut Bilgiler: Olay özeti, yaralanma bilgisi</p>
    <p>Eksik Bilgiler: Prosedür durumu, eğitim, yönetim faktörleri</p>
  </div>
  
  <!-- Soru-Cevap Kartları -->
  <div class="question-flow">
    <div class="question-card completed">
      <div class="question-header">
        <span class="q-number">❓ Soru 1/3</span>
        <span class="q-status">✅ Yanıtlandı</span>
      </div>
      <p class="question-text">LOTO prosedürü şirkette mevcut muydu?</p>
      <div class="answer-selected">
        ✓ Evet, prosedür vardı ama uygulanmıyordu → [D4.2]
      </div>
    </div>
    
    <div class="question-card active">
      <div class="question-header">
        <span class="q-number">❓ Soru 2/3</span>
        <span class="q-status">⏳ Bekliyor</span>
      </div>
      <p class="question-text">Prosedür neden uygulanmıyordu?</p>
      <div class="answer-options">
        <label class="option-card">
          <input type="radio" name="q2" value="D3.1">
          <div class="option-content">
            <strong>Eğitim verilmemişti</strong>
            <span class="code-badge">D3.1</span>
          </div>
        </label>
        
        <label class="option-card">
          <input type="radio" name="q2" value="D1.4">
          <div class="option-content">
            <strong>Zaman baskısı/üretim hedefi</strong>
            <span class="code-badge">D1.4</span>
          </div>
        </label>
        
        <label class="option-card">
          <input type="radio" name="q2" value="D1.9">
          <div class="option-content">
            <strong>Yönetim tolerans gösteriyordu</strong>
            <span class="code-badge">D1.9</span>
          </div>
        </label>
      </div>
      
      <div class="question-actions">
        <button class="btn-secondary">← Geri</button>
        <button class="btn-primary">İlerle →</button>
        <button class="btn-link">Atla (AI Tahmini)</button>
      </div>
    </div>
    
    <div class="question-card pending">
      <div class="question-header">
        <span class="q-number">❓ Soru 3/3</span>
        <span class="q-status">⏸️ Beklemede</span>
      </div>
      <p class="question-text">...</p>
    </div>
  </div>
  
  <!-- İlerleme Çubuğu -->
  <div class="progress-bar">
    <div class="progress-fill" style="width: 66%;"></div>
  </div>
  <p class="progress-text">2/3 Soru Tamamlandı</p>
  
  <!-- Navigasyon -->
  <div class="page-navigation">
    <button class="btn-secondary">← Part 2: Assessment</button>
    <button class="btn-primary" disabled>Part 3: Info Gathering →</button>
  </div>
</div>
```

**CSS Örneği:**
```css
.question-card {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  margin: 15px 0;
  background: #fff;
}

.question-card.active {
  border-color: #4A90E2;
  box-shadow: 0 4px 12px rgba(74, 144, 226, 0.15);
}

.question-card.completed {
  border-color: #4CAF50;
  background: #f1f8f4;
}

.option-card {
  display: block;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  padding: 15px;
  margin: 10px 0;
  cursor: pointer;
  transition: all 0.2s;
}

.option-card:hover {
  border-color: #4A90E2;
  background: #f5f9ff;
}

.option-card input:checked + .option-content {
  color: #4A90E2;
  font-weight: bold;
}

.code-badge {
  background: #FFE5B4;
  color: #8B4513;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.level-badge {
  display: inline-block;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 16px;
}

.level-badge.level-1 {
  background: #4CAF50;
  color: white;
}

.level-badge.level-2 {
  background: #FFC107;
  color: #333;
}

.level-badge.level-3 {
  background: #FF9800;
  color: white;
}
```

---

## 📋 Veri Akışı Şeması

```
┌─────────────────────────────────────────────────────────┐
│ Part 1: Overview                                        │
│ • Brief details (textarea)                              │
│ • Date/time                                             │
│ • Location                                              │
└─────────────────────────────────────────────────────────┘
                        ▼
                 [Next Butonu]
                        ▼
┌─────────────────────────────────────────────────────────┐
│ Part 2: Assessment                                      │
│ • Severity classification                               │
│ • RIDDOR check                                          │
│ • Investigation level                                   │
└─────────────────────────────────────────────────────────┘
                        ▼
            [Next + AI Trigger]
                        ▼
┌─────────────────────────────────────────────────────────┐
│ Part 2.5: HITL Interactive Analysis (YENİ!)             │
│                                                          │
│ ADIM 1: Girdi Analizi                                   │
│ ├─ Brief details'den seviye tespit                      │
│ └─ Eksik bilgileri listele                              │
│                                                          │
│ ADIM 2: Sorgulama (Eğer Level 2/3 ise)                 │
│ ├─ Soru 1: Prosedür var mıydı?                         │
│ ├─ Soru 2: Eğitim verilmiş miydi?                      │
│ └─ Soru 3: Yönetim neden müdahale etmedi?              │
│                                                          │
│ ADIM 3: Kod Onayı                                       │
│ ├─ AI önerisi göster                                    │
│ ├─ Kullanıcı onayla/düzelt                              │
│ └─ Nihai kodları belirle                                │
└─────────────────────────────────────────────────────────┘
                        ▼
              [Otomatik Doldurma]
                        ▼
┌─────────────────────────────────────────────────────────┐
│ Part 3: Info Gathering (Otomatik Doldurulur)           │
│ • Immediate Causes ← AI tarafından doldurulur           │
│ • Underlying Causes ← AI tarafından doldurulur          │
│ • Root Causes ← Kullanıcının onayladığı kodlar          │
└─────────────────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────┐
│ Part 4: Risk Control (Otomatik Öneriler)               │
│ • Corrective actions ← AI önerileri                     │
│ • Preventive actions ← AI önerileri                     │
│ • Responsibilities ← Kullanıcı düzenler                 │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Uygulama Planı

### **Faz 1: Backend API (1 hafta)**
- [x] `hybrid_input_processor.py` - Girdi analizi
- [x] `question_engine.py` - Soru üretimi
- [ ] FastAPI endpoint'leri (`api/main.py`)
- [ ] Test senaryoları

### **Faz 2: Frontend Modal (1 hafta)**
- [ ] Modal component tasarımı
- [ ] API entegrasyonu (fetch/axios)
- [ ] Soru-cevap akışı UI
- [ ] Otomatik doldurma mantığı

### **Faz 3: Yeni Tab (Opsiyonel - 1 hafta)**
- [ ] Part 2.5 sayfası oluşturma
- [ ] Navigation güncelleme
- [ ] Responsive tasarım
- [ ] Kullanıcı testleri

### **Faz 4: Entegrasyon Testi (3 gün)**
- [ ] Part 1 → Part 2.5 → Part 3 akışı
- [ ] Veri kalıcılığı (session/localStorage)
- [ ] Error handling
- [ ] Performance optimization

---

## 📌 Ana Sistemde Değişecek Dosyalar

### ✅ **DEĞİŞECEK** (Minimal):
```
api/main.py
├─ Yeni endpoint'ler eklenecek:
   ├─ POST /api/hitl/analyze-input
   ├─ POST /api/hitl/get-next-question
   ├─ POST /api/hitl/submit-answer
   └─ POST /api/hitl/generate-report
```

### ❌ **DEĞİŞMEYECEK**:
```
agents/
├─ overview_agent.py
├─ assessment_agent.py
├─ rootcause_agent_v2.py
└─ skillbased_docx_agent.py

tests/
└─ Tüm test dosyaları
```

**Neden değişmeyecek?**  
HITL sistemi mevcut agent'ları **wrapper** gibi kullanacak. Agent'ların kendisinde değişiklik yok!

---

## 🎯 Sonuç

### **Önerilen Yaklaşım: Modal (Option A)**

**Neden?**
- ✅ Minimal kod değişikliği
- ✅ Mevcut akışı bozmaz
- ✅ Kullanıcı alışkanlıklarını korur
- ✅ Hızlı uygulama
- ✅ Test edilmesi kolay

### **Gelecek İyileştirme: Part 2.5 Tab (Option B)**
- Kullanıcı geri bildirimine göre
- A/B testi yapılabilir
- Daha zengin UX deneyimi

---

**SON GÜNCELLEME:** 1 Mart 2026  
**DURUM:** Tasarım tamamlandı ✅
