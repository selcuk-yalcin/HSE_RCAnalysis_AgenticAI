# 🎯 HSG245 Taxonomy Entegrasyonu - Root Cause Analysis

## ✅ Yapılan Değişiklikler

### **Önceki Durum:**
- ❌ Immediate causes kategorilerden çekilmiyordu
- ❌ Root causes tek bir maddeden (örn: sadece D1.4) geliyordu
- ❌ HSG245 kategori kodları (A1.1, B2.3, D1.4) rapordan temizleniyordu
- ❌ Knowledge base kullanılmıyordu

### **Yeni Durum:**
- ✅ **Immediate Causes:** A ve B tablolarından otomatik çekiliyor
- ✅ **Root Causes:** C ve D tablolarından **birden fazla farklı madde** çekiliyor
- ✅ **HSG245 Kodları:** Rapora dahil ediliyor (örn: `A4.1 Dikkat dağınıklığı`)
- ✅ **Knowledge Base:** `shared/knowledge_base.py` kullanılıyor
- ✅ **Olay Bazlı Açıklama:** Her kod için olaya özel detaylı açıklama yapılıyor

---

## 📋 Yeni Rapor Formatı

### **1. Doğrudan Nedenler (Immediate Causes)**
Olayın gerçekleşmesine neden olan güvensiz hareketler ve güvensiz durumlar.

- **Güvensiz Davranış (A Tablosu):** 
  - **A4.1 Dikkat dağınıklığı veya bölünmüş dikkat:** İşçinin emniyet kemeri üzerinde taşımasına rağmen yaşam halatını (lanyard) ankraj noktasına bağlamaması dikkat eksikliğinden kaynaklanmıştır.

- **Güvensiz Durum (B Tablosu):** 
  - **B4.4 Korunmasız yükseklik veya düşme tehlikesi:** İskele platformunda düşmeyi engelleyici korkulukların bulunmaması güvensiz durum oluşturmuştur.

- **Tetikleyici Faktör:** 
  - Şantiye şefinin yarattığı zaman baskısı nedeniyle acele çalışma (güvensiz hıza teşvik).

---

### **2. Alt Nedenler / Katkıda Bulunan Faktörler (Underlying Causes)**
Doğrudan nedenlerin ortaya çıkmasına izin veren faktörler.

- **Operasyonel Baskı:** Proje takvimindeki gecikmeler nedeniyle üst yönetimden gelen baskının, şantiye şefi tarafından işçilere "acele edin" şeklinde yansıtılması (öğle paydosuna yetişme hedefi).

- **Denetim Eksikliği:** Güvenlik önlemleri (korkuluk montajı) tamamlanmadan çalışmaya izin verilmesi ve bu ihlalin denetim mekanizmasınca durdurulmaması.

- **Prosedür İhlali:** İşin hızlandırılması adına güvenlik prosedürlerinin (korkuluk takma, halat bağlama) bilinçli olarak atlanması.

---

### **3. Kök Nedenler (Root Causes)**
Sistemsel ve yönetimsel eksiklikler (Sorunun kaynağı).

- **[D1.4] Üretim Baskısının Güvenliğin Önüne Geçmesi:** Kurumsal kültürde, proje teslim tarihlerinin çalışan güvenliğinden daha öncelikli tutulması ve zaman baskısının güvenlik prosedürlerini atlatmaya yol açması.

- **[D1.1] Güvenliğe Yönelik Zayıf Liderlik Taahhüdü:** Yönetimin (şantiye şefi ve üst yönetim) sahada "önce güvenlik" kültürünü benimsetememesi ve güvensiz çalışmaya göz yumması.

- **[D4.1] Risk Analizinin Yapılmaması veya Yetersiz Olması:** İş programının, güvenlik önlemlerinin (korkuluk montajı gibi) tam olarak uygulanmasına zaman tanımayacak kadar sıkışık olması.

---

## 🔧 Teknik Değişiklikler

### **rootcause_agent.py**

#### **1. Immediate Causes - A ve B Tabloları**
```python
# AGENT 2-3: Search + Validation Loop (Immediate Causes - A ve B)
immediate_causes = self._search_validate_loop(
    incident=incident_summary,
    categories=['A', 'B'],  # ← A: Davranışlar, B: Durumlar
    agent_name="Immediate Causes",
    expected_count=3
)
```

**Çıktı Formatı:**
```json
{
  "category_code": "A4.1",
  "category_title": "Dikkat dağınıklığı veya bölünmüş dikkat",
  "cause": "İşçinin emniyet kemeri üzerinde...",
  "evidence": "Olay sonrası yapılan incelemede..."
}
```

---

#### **2. Root Causes - C ve D Tabloları**
```python
# AGENT 2-3: Search + Validation Loop (Root Causes - C ve D)
root_causes = self._search_validate_loop(
    incident=incident_summary,
    categories=['C', 'D'],  # ← C: Kişisel, D: Organizasyonel
    agent_name="Root Causes",
    expected_count=3  # ← Birden fazla farklı kök neden
)
```

**Önemli:** Root causes için **SADECE BİR MADDEDEN DEĞİL**, birden fazla farklı maddeden (örn: D1.4, D1.1, D4.1) seçiliyor.

---

#### **3. Search Agent Güncellemesi**
```python
def _search_agent(self, incident: str, categories: List[str]) -> List[Dict]:
    # Immediate Causes için (A ve B tabloları)
    if 'A' in categories or 'B' in categories:
        prompt = """
        GÖREV: Olayın DOĞRUDAN NEDENLERİNİ (Immediate Causes) bul.
        
        KURALLAR:
        1. A tablosundan (Güvensiz Davranışlar) ve B tablosundan (Güvensiz Durumlar) seç
        2. HSG245 kategori kodunu ve başlığını belirt (örn: "A4.1 Dikkat dağınıklığı")
        3. Olaya özgü detaylı açıklama ekle (en az 2-3 cümle)
        """
    
    # Root Causes için (C ve D tabloları)
    else:
        prompt = """
        GÖREV: SİSTEMİK KÖK NEDENLERİ (Root Causes) bul.
        
        KURALLAR:
        1. C ve D tablolarından FARKLI maddelerden seç
        2. SADECE BİR MADDEDEN DEĞİL, birden fazla farklı kök neden
        3. Her neden için HSG245 kodunu belirt (örn: "D1.4 Üretim baskısı")
        4. Sistemsel/yönetimsel eksikliklere odaklan
        """
```

---

#### **4. Validation Agent Güncellemesi**
```python
KONTROL LİSTESİ:
1. ✓ Neden sayısı uygun mu?
2. ✓ Her neden en az 2 cümle mi?
3. ✓ HSG245 kategori kodu var mı? (category_code ve category_title)
4. ✓ Olayla alakalı mı?
5. ✓ Kanıt var mı?
6. ✓ Root causes için: Birden fazla FARKLI maddeden mi? ← YENİ!
```

---

#### **5. Synthesis Agent - Yeni Format**
```python
# Immediate causes formatla (HSG245 kodlarıyla)
for cause in immediate_causes:
    code = cause.get("category_code", "")  # A4.1
    title = cause.get("category_title", "")  # Dikkat dağınıklığı
    desc = cause.get("cause", "")  # Olaya özel açıklama
    formatted.append(f"**{code} {title}:** {desc}")

# Root causes formatla (HSG245 kodlarıyla)
for root in root_causes:
    code = root.get("category_code", "")  # D1.4
    title = root.get("category_title", "")  # Üretim baskısı
    desc = root.get("cause", "")  # Sistemsel açıklama
    formatted.append(f"**[{code}] {title}:** {desc}")
```

---

## 📚 Knowledge Base Entegrasyonu

### **shared/knowledge_base.py**

```python
HSG245_TAXONOMY = {
    "immediate_causes_actions": """
    A. İLK GÖRÜNÜR NEDENLER – DAVRANIŞLAR (IMMEDIATE CAUSES - ACTIONS)
    
    A1. Prosedür ve Kural İhlali
    A1.1 Bireysel kural/prosedür ihlali
    A1.2 Grup/takım kural ihlali
    ...
    
    A4. İnsan Hatası, Dikkat ve Davranışsal Boşluklar
    A4.1 Dikkat dağınıklığı veya bölünmüş dikkat
    A4.2 Çevresel tehlikelerin fark edilmemesi
    ...
    """,
    
    "immediate_causes_conditions": """
    B. İLK GÖRÜNÜR NEDENLER – KOŞULLAR (IMMEDIATE CAUSES - CONDITIONS)
    
    B4. Çalışma Alanı Düzeni ve Çevresel Koşullar
    B4.4 Korunmasız yükseklik veya düşme tehlikesi
    ...
    """,
    
    "root_causes_organizational": """
    D. SİSTEMİK NEDENLER - ORGANİZASYONEL FAKTÖRLER (ROOT CAUSES - ORGANIZATIONAL)
    
    D1. Liderlik, Gözetim ve Güvenlik Kültürü
    D1.1 Güvenliğe yönelik zayıf liderlik taahhüdü
    D1.4 Üretim baskısının güvenliğin önüne geçmesi
    
    D4. Risk, Değişim ve İş Kontrol Sistemleri
    D4.1 Risk analizinin yapılmaması veya yetersiz olması
    ...
    """
}
```

**Kullanım:**
```python
from shared.knowledge_base import get_category_text

# A tablosunu çek
a_table = get_category_text('A')

# D tablosunu çek
d_table = get_category_text('D')
```

---

## 🧪 Test Senaryosu

Railway deploy tamamlandıktan sonra admin panelde:

1. **Yeni Incident Oluştur**
2. **Analyze with AI** butonuna tıkla
3. **Beklenilen Sonuç:**

```
✅ Immediate Causes:
   - A4.1 Dikkat dağınıklığı: [Olaya özel açıklama]
   - B4.4 Korunmasız yükseklik: [Olaya özel açıklama]

✅ Root Causes:
   - [D1.4] Üretim baskısı: [Sistemsel açıklama]
   - [D1.1] Liderlik taahhüdü: [Sistemsel açıklama]
   - [D4.1] Risk analizi: [Sistemsel açıklama]
```

---

## 📊 Karşılaştırma

| Özellik | Önceki | Yeni |
|---------|--------|------|
| **Immediate Causes** | Manuel yazılıyor | A ve B tablolarından otomatik |
| **Root Causes** | Tek madde (D1.4) | Birden fazla madde (D1.4, D1.1, D4.1) |
| **HSG245 Kodları** | Temizleniyor ❌ | Korunuyor ✅ |
| **Knowledge Base** | Kullanılmıyor | Kullanılıyor ✅ |
| **Açıklama** | Genel | Olaya özel ✅ |

---

## ✅ Deployment

```bash
Commit: 8208961
Branch: main
Status: ✅ Pushed to GitHub
Railway: 🔄 Auto-deploy başladı (~2-3 dakika)
```

---

## 🎯 Sonuç

Artık HSG245 raporu **profesyonel standardlarda** üretiliyor:

1. ✅ **Immediate Causes:** A ve B tablolarından kategori kodlarıyla
2. ✅ **Underlying Causes:** 5-Why zincirinden (mevcut yapı)
3. ✅ **Root Causes:** C ve D tablolarından birden fazla farklı maddeden
4. ✅ Her madde için **olaya özel detaylı açıklama**
5. ✅ **HSG245 kodları korunuyor** (A4.1, B4.4, D1.4, D1.1, D4.1)

**Örnek Çıktı:**
```
## Doğrudan Nedenler (Immediate Causes)
• **A4.1 Dikkat dağınıklığı:** İşçinin emniyet kemeri üzerinde...
• **B4.4 Korunmasız yükseklik:** İskele platformunda korkuluk...

## Kök Nedenler (Root Causes)
• **[D1.4] Üretim baskısı:** Kurumsal kültürde teslim tarihleri...
• **[D1.1] Liderlik taahhüdü:** Yönetimin "önce güvenlik" kültürü...
• **[D4.1] Risk analizi:** İş programının güvenlik önlemlerine...
```

🚀 **Railway'de deploy tamamlandığında test edebilirsiniz!**
