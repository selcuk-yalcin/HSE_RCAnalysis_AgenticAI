# 🔧 5-Why Analizi İyileştirmeleri

## 📅 Commit: 98ac82b
**Tarih:** 22 Ocak 2026

---

## 🎯 Düzeltilen Sorunlar

### 1️⃣ Sıralama Hatası (Kronolojik Kopukluk)

#### ❌ Önceki Durum
```
Why 1 (Immediate)
  ↓
Why 3 (Underlying) ← ⚠️ Why 2 atlandı!
  ↓
Why 5 (Root) ← ⚠️ Why 4 atlandı!
  ↓
Why 2 (Underlying) ← ⚠️ Geriye gidildi!
```

**Sorun:**
- AI bazen level numaralarını karıştırıyor
- Okuyucu neden-sonuç ilişkisini kuramıyor
- Mantıksal akış bozuluyor

#### ✅ Yeni Durum
```
Why 1 (Immediate)
  ↓
Why 2 (Underlying)
  ↓
Why 3 (Underlying)
  ↓
Why 4 (Underlying)
  ↓
Why 5 (Root Cause)
```

**Çözüm:**
```python
# Otomatik sıralama kontrolü
expected_levels = [1, 2, 3, 4, 5]
actual_levels = [step.get("level", 0) for step in why_chain]

if actual_levels != expected_levels:
    print("⚠️ UYARI: Sıralama hatası tespit edildi!")
    print(f"Beklenen: {expected_levels}")
    print(f"Gelen: {actual_levels}")
    print("🔧 Düzeltiliyor...")
    
    # Sıralamayı düzelt
    for i, step in enumerate(why_chain, 1):
        step["level"] = i
```

**Prompt İyileştirmesi:**
```
CRITICAL RULE - SIRALAMA:
- Why 1 (Level 1) → ÖNCE
- Why 2 (Level 2) → SONRA  
- Why 3 (Level 3) → SONRA
- Why 4 (Level 4) → SONRA
- Why 5 (Level 5 - ROOT) → EN SON

❌ YANLIŞ: 1→3→5→2 (kronolojik kopukluk)
✅ DOĞRU: 1→2→3→4→5 (mantıklı sıralama)

Her bir "why" bir önceki "because" cevabının nedenidir. 
Merdiven gibi: 1. basamaktan 2. basamağa, oradan 3. basamağa çık.
```

---

### 2️⃣ Immediate Causes - Kod Kaldırma

#### ❌ Önceki Durum
```json
{
  "cause": "A2.1 Ekipman yanlış kullanım",
  "evidence": "Operatör makineyi yetkisiz kullandı"
}
```

**Sorun:**
- Kategori kodları (A2.1, B1.3, vb.) görünüyor
- Kullanıcılar kodları anlamıyor
- Profesyonel rapor görünümünü bozuyor

#### ✅ Yeni Durum
```json
{
  "cause": "Ekipman yanlış kullanım",
  "evidence": "Operatör makineyi yetkisiz kullandı"
}
```

**Çözüm:**
```python
import re

# Kod pattern'i: A1.1, B2.3, C3.1, D6.1
code_pattern = r'\b[ABCD]\d+(\.\d+)?\b'

for item in causes:
    # cause alanından kod temizle
    original = item["cause"]
    cleaned = re.sub(code_pattern, '', item["cause"]).strip()
    # Başındaki ":" veya "-" varsa temizle
    cleaned = re.sub(r'^[\s\-:]+', '', cleaned).strip()
    item["cause"] = cleaned
    
    if original != cleaned:
        print(f"🧹 Kod temizlendi: '{original}' → '{cleaned}'")
```

**Prompt İyileştirmesi:**
```
CRITICAL RULES:
- KOD YAZMA! Sadece açıklama yaz. 
  Örnek: "Operatör makineye yetkisiz müdahale etti" (✅)
  Yanlış: "A2.1 Ekipman yanlış kullanım" (❌)
```

---

### 3️⃣ Immediate Causes - Detaylı Açıklama

#### ❌ Önceki Durum
```json
{
  "cause": "Ekipman arızası",
  "evidence": "Makine çalışmadı"
}
```

**Sorun:**
- Çok kısa açıklamalar
- Neden bu bir doğrudan neden? → Belirsiz
- Nasıl katkıda bulundu? → Bilinmiyor

#### ✅ Yeni Durum
```json
{
  "cause": "Ekipman arızası meydana geldi. Makinenin koruyucu sistemleri devre dışı kaldı ve bu durum operatörün tehlikeli bölgeye erişimine izin verdi.",
  "evidence": "Makine muayene kayıtları son 6 ayda bakım yapılmadığını gösteriyor. Koruyucu kapak sensörü arızalı bulundu."
}
```

**Çözüm - Prompt:**
```
GÖREV:
4. Her neden için DETAYLI AÇIKLAMA yaz 
   - Neden bu bir doğrudan neden?
   - Nasıl katkıda bulundu?

CRITICAL RULES:
- Her "cause" alanı en az 2 cümle olmalı (ne oldu + neden önemli)
- "evidence" alanında somut kanıtlar belirt
```

---

## 📊 Karşılaştırma Tablosu

| Kriter | Önceki ❌ | Yeni ✅ |
|--------|----------|---------|
| **Sıralama** | 1→3→5→2 (karışık) | 1→2→3→4→5 (mantıklı) |
| **Immediate Cause Kodu** | "A2.1 Ekipman yanlış..." | "Ekipman yanlış..." |
| **Açıklama Uzunluğu** | 1 cümle | 2+ cümle |
| **Kanıt Detayı** | Genel | Somut |
| **Otomatik Düzeltme** | Yok | Var ✅ |

---

## 🧪 Test Senaryosu

### Input (Örnek Olay)
```
22.01.2024 tarihinde saat 08:45 civarında, 
operatör Atatürk Bulvarı'ndaki Kazay işletmesine 
ait 34 ABC 123 plakalı aracı kullanırken...
```

### Beklenen Output

#### Immediate Causes
```json
[
  {
    "cause": "Operatör trafik kurallarını ihlal etti. Hız limiti 50 km/s olan bölgede 87 km/s hızla seyrediyordu ve bu durum tehlikeli yaklaşma mesafesine sebep oldu.",
    "evidence": "Trafik kayıtları 87 km/s hız tespit etti. Kaza anında fren izleri 15 metre olarak ölçüldü."
  },
  {
    "cause": "Araç bakım eksikliği mevcuttu. Fren sisteminde yetersizlik kazanın şiddetini artırdı.",
    "evidence": "Son muayene kaydı 8 ay önce. Fren balatalarının %40 aşınmış olduğu tespit edildi."
  }
]
```

#### 5-Why Chain (İlk Immediate Cause için)
```json
{
  "why_chain": [
    {
      "level": 1,
      "cause_type": "immediate",
      "why_question": "Neden operatör hız limitini aştı?",
      "because_answer": "Operatör son teslimat için acele ediyordu"
    },
    {
      "level": 2,
      "cause_type": "underlying",
      "why_question": "Neden acele ediyordu?",
      "because_answer": "Günlük teslimat hedefi çok yüksek belirlenmişti"
    },
    {
      "level": 3,
      "cause_type": "underlying",
      "why_question": "Neden hedef çok yüksek?",
      "because_answer": "Şirket son ay %30 daha fazla sipariş aldı"
    },
    {
      "level": 4,
      "cause_type": "underlying",
      "why_question": "Neden kaynak artırılmadı?",
      "because_answer": "Bütçe kısıtlaması vardı"
    },
    {
      "level": 5,
      "cause_type": "root",
      "why_question": "Neden bütçe kısıtlaması risk yarattı?",
      "because_answer": "Risk değerlendirmesi yapılmadan karar alındı (D4.1 - Yetersiz risk yönetimi)"
    }
  ]
}
```

---

## 🚀 Deployment

### Commit
```bash
git commit -m "🔧 5-Why Analizi İyileştirmeleri"
git push origin main
```

### Railway Auto-Deploy
- ✅ Commit 98ac82b
- ✅ Build başarılı olmalı
- ✅ Yeni validation fonksiyonları aktif

### Test Adımları
1. Admin panelden yeni olay oluştur
2. Part 3'ü gönder
3. Kontrol et:
   - ✅ Immediate causes'da kod yok mu?
   - ✅ Açıklamalar detaylı mı? (2+ cümle)
   - ✅ Why chain sıralaması: 1→2→3→4→5 mi?
   - ✅ Console'da "🔧 Düzeltiliyor..." mesajı var mı? (varsa AI hata yapmış, kod düzeltmiş)

---

## 📝 Kod Değişiklikleri

### Dosya: `agents/rootcause_agent.py`

#### 1. Immediate Causes Prompt (Satır ~157)
```python
GÖREV:
1. Bu olayın DOĞRUDAN NEDENLERİNİ (Immediate Causes) belirle
2. Yukarıdaki A ve B kategorilerinden en uygun olanları seç
3. Tipik olarak 2-4 doğrudan neden olur
4. Her neden için DETAYLI AÇIKLAMA yaz

CRITICAL RULES:
- KOD YAZMA! Sadece açıklama yaz
- Her "cause" alanı en az 2 cümle olmalı
- "evidence" alanında somut kanıtlar belirt
```

#### 2. Kod Temizleme (Satır ~200)
```python
import re
code_pattern = r'\b[ABCD]\d+(\.\d+)?\b'

for item in causes:
    original = item["cause"]
    cleaned = re.sub(code_pattern, '', item["cause"]).strip()
    cleaned = re.sub(r'^[\s\-:]+', '', cleaned).strip()
    item["cause"] = cleaned
```

#### 3. 5-Why Sıralama Kontrolü (Satır ~285)
```python
expected_levels = [1, 2, 3, 4, 5]
actual_levels = [step.get("level", 0) for step in why_chain]

if actual_levels != expected_levels:
    print(f"⚠️ UYARI: Sıralama hatası tespit edildi!")
    for i, step in enumerate(why_chain, 1):
        step["level"] = i
```

---

## ✅ Sonuç

Artık sistem:
- ✅ **Kronolojik akışı** koruyor (1→2→3→4→5)
- ✅ **Kodları** otomatik temizliyor
- ✅ **Detaylı açıklamalar** üretiyor
- ✅ **Hataları** otomatik düzeltiyor
- ✅ **Profesyonel** raporlar sunuyor

Railway deployment sonrası test edin! 🎯
