# HSG245 Knowledge Upload Guide

## 📋 3 Kolay Yöntem

---

### **METHOD 1: Quick Script (En Hızlı)** ⭐

1. `add_knowledge.py` dosyasını açın
2. KNOWLEDGE_TEXTS içine metninizi yapıştırın
3. Çalıştırın:

```bash
python add_knowledge.py
```

**Örnek:**
```python
KNOWLEDGE_TEXTS = {
    "hsg245_main": """
    HSG245 investigating accidents and incidents
    A workbook for employers, unions, safety representatives and safety professionals
    
    This guidance is for employers and those with health and safety responsibilities.
    ...
    """,
}
```

---

### **METHOD 2: Text Dosyası**

1. Metninizi `.txt` dosyasına kaydedin
2. Workspace'e ekleyin (örn: `knowledge/hsg245.txt`)
3. Yükleyin:

```bash
python load_knowledge.py knowledge/hsg245.txt
```

**Birden fazla dosya için:**
```bash
# Tüm .txt dosyalarını klasöre koyun
python load_knowledge.py --dir ./knowledge
```

---

### **METHOD 3: Railway Terminal'de**

Railway Backend service'inden:

1. Settings → Deploy → "Open Terminal"
2. Script çalıştırın:

```bash
# Yöntem 1
python add_knowledge.py

# Yöntem 2
python load_knowledge.py knowledge/hsg245.txt
```

---

## 🔍 Test Etme

Veri yüklendikten sonra test edin:

```bash
python load_knowledge.py --test "workplace accident"
```

Beklenen çıktı:
```
🔍 Testing query: workplace accident

📋 Top 3 Results:

   Result 1 [Source: hsg245_main | Similarity: 87%]:
   HSG245 investigating accidents and incidents...
```

---

## 📊 İstatistikleri Görme

```bash
python -c "from shared.rag_system import get_rag_system; print(get_rag_system().stats())"
```

Çıktı:
```
✅ Database schema initialized
✅ RAG System initialized with 245 documents
{'total_chunks': 245, 'sources': ['hsg245_main', 'riddor_2013'], 'source_count': 2}
```

---

## ✅ Hangi Yöntemi Kullanmalı?

| Durum | Önerilen Yöntem |
|-------|----------------|
| **Kısa metin** (1-2 sayfa) | Yöntem 1: `add_knowledge.py` |
| **Uzun doküman** (10+ sayfa) | Yöntem 2: `.txt` dosyası |
| **Birden fazla doküman** | Yöntem 2: `--dir` klasör |
| **Railway'de test** | Yöntem 3: Railway terminal |

---

## 🚀 Sonraki Adım: Agent Entegrasyonu

Veri yükledikten sonra agent'lara entegre edeceğiz:

```python
# agents/rootcause_agent.py
from shared.rag_system import get_rag_system

def analyze(incident):
    rag = get_rag_system()
    context = rag.get_context_for_incident(incident['description'])
    
    # Context + Incident → LLM
    prompt = f"{context}\n\nAnalyze: {incident}"
    ...
```

Bu sayede AI, **sizin HSG245 dokümanınıza** göre analiz yapacak! 🎯
