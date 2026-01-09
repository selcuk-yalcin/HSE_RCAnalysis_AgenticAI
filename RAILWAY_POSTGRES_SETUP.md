# Railway PostgreSQL + RAG System Setup

## ✅ Avantajlar
- **Kalıcı (Persistent)**: Railway restart olsa bile veriler kaybolmaz
- **Ücretsiz**: PostgreSQL 500MB'a kadar ücretsiz
- **Production-Ready**: ChromaDB'den çok daha güvenilir
- **Ölçeklenebilir**: Milyonlarca doküman eklenebilir

---

## 📋 ADIM ADIM KURULUM

### **1️⃣ Railway'e PostgreSQL Ekleyin**

1. Railway Dashboard açın: https://railway.app
2. `hsercanalysisagenticai-production` projenizi seçin
3. **"+ New"** butonuna tıklayın
4. **"Database"** sekmesine geçin
5. **"Add PostgreSQL"** seçin
6. PostgreSQL oluşturuldu! ✅

### **2️⃣ DATABASE_URL'i Kopyalayın**

1. PostgreSQL service'ine tıklayın
2. **"Variables"** sekmesine geçin
3. **"DATABASE_URL"** değerini kopyalayın
   - Format: `postgresql://postgres:xxxxx@xxxxx.railway.app:5432/railway`

### **3️⃣ Backend Service'e DATABASE_URL Ekleyin**

1. Backend service'inize geri dönün (FastAPI service)
2. **"Variables"** sekmesine geçin
3. **"+ New Variable"** butonuna tıklayın
4. İsim: `DATABASE_URL`
5. Değer: Az önce kopyaladığınız PostgreSQL URL'i
6. **"Add"** butonuna tıklayın
7. Railway otomatik redeploy edecek ✅

---

## 🔧 Yerel Test (İsteğe Bağlı)

Eğer local'de test etmek isterseniz:

```bash
# 1. Dependencies yükleyin
pip install -r requirements.txt

# 2. .env dosyasına Railway DATABASE_URL'i ekleyin
# DATABASE_URL=postgresql://postgres:xxxxx@xxxxx.railway.app:5432/railway

# 3. Test edin
python load_knowledge.py --test "accident investigation"
```

---

## 📝 Metin Yükleme

### **Yöntem 1: Dosyadan Yükle**

```bash
# Metninizi .txt dosyasına kaydedin
# Örnek: hsg245_regulations.txt

# Yükleyin
python load_knowledge.py hsg245_regulations.txt
```

### **Yöntem 2: Birden Fazla Dosya**

```bash
# Tüm .txt dosyalarını bir klasöre koyun
# Örnek: ./knowledge_docs/

# Yükleyin
python load_knowledge.py --dir ./knowledge_docs
```

### **Yöntem 3: Railway'de Script Çalıştır**

Railway Dashboard'dan:
1. PostgreSQL service'ine gidin
2. **"Query"** sekmesine geçin
3. pgvector extension'ı etkinleştirin:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

4. Backend service'inde terminal açın
5. Script çalıştırın:

```bash
python load_knowledge.py hsg245_regulations.txt
```

---

## ✅ Doğrulama

### **Test 1: Database Bağlantısı**

```bash
python -c "from shared.rag_system import get_rag_system; rag = get_rag_system(); print(rag.stats())"
```

Beklenen çıktı:
```
✅ Database schema initialized
✅ RAG System initialized with 0 documents
{'total_chunks': 0, 'sources': [], 'source_count': 0}
```

### **Test 2: Metin Yükleme**

```bash
echo "HSG245 incident investigation requires systematic approach." > test.txt
python load_knowledge.py test.txt
```

Beklenen çıktı:
```
📂 Loading: test.txt
📄 Processing 1 chunks from test...
✅ Added 1 chunks to knowledge base
✅ Successfully loaded 1 chunks

📊 Knowledge Base Stats:
   Total chunks: 1
   Sources: 1
   - test
```

### **Test 3: Query Test**

```bash
python load_knowledge.py --test "workplace accident"
```

Beklenen çıktı:
```
🔍 Testing query: workplace accident

📋 Top 3 Results:

   Result 1 [Source: test]:
   HSG245 incident investigation requires systematic approach.
```

---

## 🚀 Railway'e Deploy

1. Git commit yapın:

```bash
git add .
git commit -m "feat: PostgreSQL + pgvector RAG system"
git push
```

2. Railway otomatik deploy edecek
3. Backend loglarını kontrol edin:
   - "✅ Database schema initialized" görmeli

---

## 📊 Sonraki Adım: Agent Entegrasyonu

RAG sistem hazır olduğunda, agent'lara entegre edeceğiz:

```python
# agents/rootcause_agent.py örneği
from shared.rag_system import get_rag_system

def analyze_root_causes(incident_data):
    rag = get_rag_system()
    
    # RAG'den ilgili bilgiyi al
    context = rag.get_context_for_incident(incident_data['description'])
    
    # LLM'e gönder
    prompt = f"{context}\n\nIncident: {incident_data['description']}"
    response = openai.chat.completions.create(...)
```

---

## ❓ Sorun Giderme

### "DATABASE_URL not found"
- `.env` dosyasında DATABASE_URL var mı kontrol edin
- Railway'de environment variable eklenmiş mi kontrol edin

### "could not connect to server"
- DATABASE_URL doğru mu kontrol edin
- Railway PostgreSQL service running mi kontrol edin

### "pgvector extension not found"
- Railway PostgreSQL Query sekmesinde şunu çalıştırın:
  ```sql
  CREATE EXTENSION IF NOT EXISTS vector;
  ```

---

## 🎯 Özet

✅ **PostgreSQL Railway'de hazır**  
✅ **pgvector extension enabled**  
✅ **DATABASE_URL backend'e eklendi**  
✅ **RAG system kodu hazır**  
✅ **Metin yükleme scripti hazır**  

**ŞİMDİ YAPILACAK:**
1. Railway'e PostgreSQL ekleyin
2. DATABASE_URL'i backend'e ekleyin
3. Metninizi yükleyin
4. Agent'lara entegre edin
