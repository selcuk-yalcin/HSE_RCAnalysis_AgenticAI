# 🚀 Railway Deployment Checklist - RAG System

## ✅ TAMAMLANAN ADIMLAR
- [x] PostgreSQL eklendi (Railway Dashboard)
- [x] RAG sistem kodu hazır (shared/rag_system.py)
- [x] HSG245 taxonomy eklendi (add_knowledge.py)
- [x] Kod GitHub'a push edildi
- [x] Railway otomatik deploy başladı

---

## ⏳ ŞİMDİ YAPILACAKLAR

### **ADIM 1: DATABASE_URL Backend'e Ekle** ⚠️ ZORUNLU

Railway Dashboard:
1. **Backend Service** (HSE_RCAnalysis_AgenticAI) tıklayın
2. **Variables** sekmesi
3. **+ New Variable**
   - **Name:** `DATABASE_URL`
   - **Value:** `${{Postgres.DATABASE_URL}}` (Variable Reference kullanın)
4. **Add** → Railway yeniden deploy edecek

### **ADIM 2: pgvector Extension Etkinleştir**

Railway Dashboard:
1. **PostgreSQL Service** tıklayın
2. **Query** sekmesi
3. Şu komutu çalıştırın:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

4. ✅ "CREATE EXTENSION" mesajını göreceksiniz

### **ADIM 3: Deploy Loglarını Kontrol Et**

Backend service deploy edildikten sonra:
1. **Deployments** sekmesi
2. En son deployment'a tıklayın
3. **View Logs**

Aranacak mesajlar:
```
✅ Database schema initialized
✅ RAG System initialized with 0 documents
```

**EĞER HATA VARSA:**
- "could not connect" → DATABASE_URL doğru mu kontrol edin
- "extension vector does not exist" → ADIM 2'yi tekrar yapın

---

## 📤 ADIM 4: HSG245 Taxonomy'yi Yükle

Deploy başarılı olduktan sonra:

### **Yöntem A: Railway CLI (Önerilen)**

```bash
# Railway CLI yükleyin
npm install -g @railway/cli

# Login
railway login

# Backend service'i seçin
railway link

# Knowledge yükleyin
railway run python add_knowledge.py
```

### **Yöntem B: Railway Dashboard Terminal**

1. Backend service → **Settings** sekmesi
2. **Deploy** bölümü → **Open Terminal** butonu
3. Terminal'de:

```bash
python add_knowledge.py
```

Beklenen çıktı:
```
============================================================
HSG245 Knowledge Upload
============================================================

📊 Current Knowledge Base:
   Total chunks: 0
   Sources: 0

📤 Uploading documents...

   📄 Processing: hsg245_immediate_causes_actions
📄 Processing 25 chunks from hsg245_immediate_causes_actions...
✅ Added 25 chunks to knowledge base

   📄 Processing: hsg245_immediate_causes_conditions
📄 Processing 28 chunks from hsg245_immediate_causes_conditions...
✅ Added 28 chunks to knowledge base

   📄 Processing: hsg245_systemic_causes_personal
📄 Processing 15 chunks from hsg245_systemic_causes_personal...
✅ Added 15 chunks to knowledge base

   📄 Processing: hsg245_systemic_causes_organizational
📄 Processing 45 chunks from hsg245_systemic_causes_organizational...
✅ Added 45 chunks to knowledge base

============================================================
✅ Upload Complete!
============================================================

📊 Final Knowledge Base Stats:
   Total chunks: 113
   Sources: 4
   - hsg245_immediate_causes_actions
   - hsg245_immediate_causes_conditions
   - hsg245_systemic_causes_personal
   - hsg245_systemic_causes_organizational

🔍 Testing query: 'accident investigation'

   Result 1 [Similarity: 85%]:
   D4. Risk, Change, and Work Control Systems...
```

---

## 🔍 ADIM 5: RAG Sistemi Test Et

Railway terminal'de:

```bash
# Test query
python load_knowledge.py --test "workplace accident"

# İstatistikleri görüntüle
python -c "from shared.rag_system import get_rag_system; print(get_rag_system().stats())"
```

---

## 🎯 SONRAKI ADIM: Agent Entegrasyonu

Knowledge yüklendikten sonra agent'lara entegre edeceğiz:

### Değiştirilecek Dosyalar:
- `agents/rootcause_agent.py`
- `agents/overview_agent.py`
- `agents/assessment_agent.py`
- `agents/actionplan_agent.py`

### Entegrasyon Pattern:
```python
from shared.rag_system import get_rag_system

def analyze_root_causes(incident_data):
    # RAG'den ilgili HSG245 bilgisini al
    rag = get_rag_system()
    context = rag.get_context_for_incident(
        incident_data['description'],
        n_results=5
    )
    
    # LLM'e context ile birlikte gönder
    prompt = f"""
{context}

Based on the HSG245 taxonomy above, analyze this incident:
{incident_data['description']}

Identify:
1. Immediate causes (A/B categories)
2. Systemic causes (C/D categories)
3. Root organizational factors
"""
    
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response
```

---

## 📊 Beklenen Sonuç

RAG entegrasyonu sonrası:
- ✅ AI analizi HSG245 taxonomy'sine göre yapılacak
- ✅ Her cause için spesifik A1.1, B2.3, D4.5 kodları verilecek
- ✅ Tutarlı, standardize raporlar
- ✅ Kalite 10x artacak

---

## ❓ Sorun Giderme

### "DATABASE_URL not found"
→ Backend service'de DATABASE_URL variable eklediniz mi?

### "extension vector does not exist"
→ PostgreSQL Query sekmesinde `CREATE EXTENSION IF NOT EXISTS vector;` çalıştırın

### "could not connect to server"
→ PostgreSQL service online mı? Railway Dashboard'dan kontrol edin

### "No module named 'pgvector'"
→ requirements.txt push edildi mi? Railway yeniden deploy edildi mi?

---

## 📞 Yardım Gerekirse

Railway logs'ta hata görürseniz:
1. Backend service → Deployments → View Logs
2. Hatayı kopyalayın
3. Bana gönderin, birlikte çözelim

---

## ✅ Özet: Sıradaki 3 Adım

1. **DATABASE_URL ekle** (Backend Variables → ${{Postgres.DATABASE_URL}})
2. **pgvector enable** (PostgreSQL Query → CREATE EXTENSION)
3. **Knowledge yükle** (Railway terminal → python add_knowledge.py)

Şu an hangi adımdasınız? 🚀
