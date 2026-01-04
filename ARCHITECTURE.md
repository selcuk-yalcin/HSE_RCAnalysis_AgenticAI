# Multi-Agent Root Cause Investigation System
## Based on HSG245 Framework

## 📋 PDF Analizi Özeti

**Toplam Sayfa**: 14  
**Tablo Sayısı**: 51  
**Ana Bölümler**: 4 Part

### 🎯 HSG245 Yapısı

#### **PART 1: Overview** (Sayfa 1)
- Ref no
- Reported by / Date/time
- Incident type (Ill health, Minor injury, Serious injury, Major injury)
- Brief details (What, where, when, who, emergency measures)
- Forwarded to / Date/Time

#### **PART 2: Initial Assessment** (Sayfa 2)
- Type of event (Accident, Ill health, Near-miss, Undesired circumstance)
- Actual/potential for harm (Fatal/major, Serious, Minor, Damage only)
- RIDDOR reportable? Y/N / Date/time reported
- Entry in accident book Y/N / Date entered/reference
- Investigation level (High, Medium, Low, Basic)
- Initial assessment carried out by / Date
- Further investigation required? Y/N / Priority

#### **PART 3: Investigation Information Gathering** (Sayfa 3-11)
1. Where and when did the adverse event happen?
2. Who was injured/suffered ill health?
3. How did the adverse event happen? (Equipment involved)
4. What activities were being carried out?
5. What injuries or ill health effects were caused?
6. If there was an injury, how did it occur and what caused it?
7. Was the risk known? If so, why wasn't it controlled?
8. Did the organisation and arrangement of the work influence?
9. Was maintenance and cleaning sufficient?
10. Were the people involved competent and suitable?
11. Did the workplace layout influence?
12. Did the nature or shape of materials influence?
13. Did difficulties using plant/equipment influence?
14. Was the safety equipment sufficient?
15. Did other conditions influence?

**18. What were the immediate, underlying and root causes?**
- 5 Why Analysis yapılıyor (Why? → Because → Why? → Because...)
- Immediate causes (unsafe acts, conditions)
- Underlying causes (equipment, procedures, competence)
- Root causes (management systems, organizational)

**19. What risk control measures are needed/recommended?**
**20. Do similar risks exist elsewhere?**
**21. Have similar adverse events happened before?**

#### **PART 4: The Risk Control Action Plan** (Sayfa 12-14)
22. Which risk control measures should be implemented (long/short term)?
    - Control measure / Completion Date / Person responsible
23. Which risk assessments and safe working procedures need review?
24. Cost analysis and trends
25. Signed on behalf of investigation team
26. Members of the investigation team
27. Communication to stakeholders

---

## 🤖 Multi-Agent Sistem Tasarımı

### **Agent 1: Overview Agent**
**Görev**: Part 1 - İlk raporlama
- Olay bilgilerini topla (what, where, when, who)
- Incident type belirle
- Emergency measures kaydet

### **Agent 2: Initial Assessment Agent**
**Görev**: Part 2 - İlk değerlendirme
- Olay tipini kategorize et
- Severity level belirle
- RIDDOR gereksinimini kontrol et
- Investigation level öner (High/Medium/Low/Basic)

### **Agent 3: Investigation Agent**
**Görev**: Part 3 - Detaylı araştırma
- 17 soruyu yanıtla (where, when, who, how, equipment, etc.)
- Evidence topla ve analiz et
- Witness statements işle

### **Agent 4: Root Cause Analysis Agent**
**Görev**: Part 3 - Kök neden analizi
- 5 Why Analysis uygula
- Immediate causes tespit et
- Underlying causes belirle
- Root causes bul
- Causal chain oluştur

### **Agent 5: Recommendation Agent**
**Görev**: Part 3 - Öneri geliştirme
- Risk control measures öner
- Benzer riskleri tespit et
- Past incidents kontrol et

### **Agent 6: Action Plan Agent**
**Görev**: Part 4 - Aksiyon planı
- Short-term ve long-term controls belirle
- Responsibility atama yap
- Timeline oluştur
- Cost estimation yap

### **Agent 7: Report Generator Agent**
**Görev**: Final report oluşturma
- HSG245 formatında Word/PDF rapor
- Tables, diagrams, signatures
- Distribution list

### **Orchestrator Agent**
**Görev**: Tüm agent'ları koordine et
- Workflow yönetimi
- Agent'lar arası veri akışı
- Quality control

---

## 🔄 Workflow

```
User Input
    ↓
Orchestrator
    ↓
1. Overview Agent → Part 1 verileri
    ↓
2. Initial Assessment Agent → Severity & Investigation level
    ↓
3. Investigation Agent → 17 soru cevapları + Evidence
    ↓
4. Root Cause Analysis Agent → 5 Why + Causes (Immediate/Underlying/Root)
    ↓
5. Recommendation Agent → Control measures + Similar risks
    ↓
6. Action Plan Agent → Timeline + Responsibilities + Cost
    ↓
7. Report Generator Agent → HSG245 formatted report (Word/PDF)
    ↓
Final Report Output
```

---

## 📁 Klasör Yapısı

```
rootcause_report/
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py           # Master coordinator
│   ├── overview_agent.py         # Part 1 agent
│   ├── assessment_agent.py       # Part 2 agent
│   ├── investigation_agent.py    # Part 3 questions agent
│   ├── rootcause_agent.py        # Part 3 5-why agent
│   ├── recommendation_agent.py   # Part 3 recommendations
│   ├── actionplan_agent.py       # Part 4 agent
│   └── report_generator.py       # Final report agent
├── templates/
│   ├── hsg245_template.docx      # Word template
│   └── hsg245_template_data.json # Template data structure
├── data/
│   ├── hsg245_structure.json     # Analyzed PDF structure
│   └── sample_incident.json      # Sample incident data
├── outputs/
│   └── reports/                  # Generated reports
├── examples/
│   ├── hsg245-pages-2.pdf        # Reference PDF
│   └── run_investigation.py      # Example usage
├── config.py                     # Configuration
├── requirements.txt              # Dependencies
└── README.md                     # Documentation
```

---

## 📊 Örnek Vaka (PDF'deki olay)

**Incident**: Norman Brown - Edge gluing machine accident

**Part 1 Data**:
- Date: 23.06.03 10:00am
- Location: Woodmachine shop
- Injured: Norman Brown (woodmachinist)
- Injury: Severe laceration to right hand
- Equipment: Wilmatron 440 edge gluing machine

**5 Why Analysis**:
```
Norman lacerates his hand
  ↓ Why?
Norman was working on machine + Saw blade made stroke + Hand in danger area
  ↓ Why?
Norman investigating fault + Machine was 'live' + Guard was open
  ↓ Why?
No procedures for reporting faults + Machine used for aluminium + No isolation procedures
```

**Root Causes**:
1. Inadequate procedures
2. Equipment not suitable for material
3. Easily defeated interlock
4. Inadequate workplace layout
5. Competence gaps

**Recommendations**:
1. Replace interlock switch
2. Rearrange workshop
3. Prepare SWPs for isolation
4. Training & competence assessment
5. Review risk assessments

---

## 🎯 Sonraki Adımlar

1. ✅ PDF analizi tamamlandı
2. ⏳ Agent sınıflarını oluştur
3. ⏳ Orchestrator workflow'u kodla
4. ⏳ Template sistemi hazırla
5. ⏳ Example çalıştır ve test et
