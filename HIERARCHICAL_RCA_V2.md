# 🌳 Hiyerarşik Kök Neden Analizi V2

## 📋 Genel Bakış

Bu sistem, HSG245 metodolojisini kullanarak **hiyerarşik 5-Why analizi** yapar ve kök nedenlere ulaşır.

## 🎯 Yapısal Akış

```
🔴 OLAY (INCIDENT)
│   ↓
│   1. Olay Özeti Hazırla
│   ↓
├───────────────────────────────────────────
│   ADIM 1: DOĞRUDAN NEDENLERİ BELİRLE
│   (A/B Kategorilerinden)
├───────────────────────────────────────────
│
├───⚡ DAL 1: MEKANİK/FİZİKSEL (B Kategorisi)
│   │
│   ├── 📌 Doğrudan Neden [KOD: B1.6]
│   │   └── Güvenlik switch'i baypas edilmiş
│   │
│   ├── ❓ Neden 1?
│   │   └── Switch arızalıydı, üretim durmasın diye kısa devre yapıldı
│   │
│   ├── ❓ Neden 2?
│   │   └── Yedek parça stokta yoktu
│   │
│   ├── ❓ Neden 3?
│   │   └── Kritik parça takibi yapılmıyordu
│   │
│   ├── ❓ Neden 4?
│   │   └── Bakım planlaması yoktu
│   │
│   └── 🎯 KÖK NEDEN [KOD: D6.1]
│       └── Yetersiz Bakım Stratejisi ve Envanter Yönetimi
│
│
└───⚡ DAL 2: DAVRANIŞSAL (A Kategorisi)
    │
    ├── 📌 Doğrudan Neden [KOD: A1.4]
    │   └── Operatör yetkisiz müdahale etti
    │
    ├── ❓ Neden 1?
    │   └── Bakımcı gece vardiyasında yoktu
    │
    ├── ❓ Neden 2?
    │   └── Üretim hedefi tutturma baskısı vardı
    │
    ├── ❓ Neden 3?
    │   └── "Üretim her şeyden önemli" algısı
    │
    └── 🎯 KÖK NEDEN [KOD: D1.4]
        └── Üretim Baskısının Güvenliğin Önüne Geçmesi
```

## 📚 Kategori Hiyerarşisi

### Seviye 1: DOĞRUDAN NEDENLER (Immediate Causes)

#### A Kategorisi - DAVRANIŞSAL (Actions)
- **A1**: Prosedür ve Kural İhlali
  - A1.1: Bireysel kural ihlali
  - A1.4: Yetkisiz bilinçli sapma
  - A1.6: Prosedür uygulanamaz
- **A2**: Ekipman Uygunsuz Kullanımı
- **A3**: Koruyucu Ekipman Kullanılmaması
- **A4**: İnsan Hatası

#### B Kategorisi - KOŞULLAR (Conditions)
- **B1**: Koruyucu Sistem Hataları
  - B1.2: Koruyucu cihazlar arızalı
  - B1.6: Koruyucu sistemler devre dışı
- **B2**: Ekipman Durumu
- **B3**: Tehlikeli Enerji Maruziyeti
- **B4**: Çalışma Alanı Düzeni

### Seviye 2: KÖK NEDENLER (Root Causes)

#### C Kategorisi - KİŞİSEL FAKTÖRLER (Personal)
- **C1**: Fiziksel Kapasite
- **C2**: Bilişsel Yetenek
- **C3**: Beceri ve Yetkinlik

#### D Kategorisi - ORGANİZASYONEL (Organizational)
- **D1**: Liderlik ve Güvenlik Kültürü
  - D1.4: Üretim baskısı > Güvenlik
- **D2**: İletişim ve Bilgi Yönetimi
- **D3**: Eğitim ve Yetkinlik
- **D4**: Risk ve Değişim Kontrolleri
- **D5**: Mühendislik ve Tasarım
- **D6**: Bakım ve Varlık Bütünlüğü
  - D6.1: Yetersiz bakım stratejisi
- **D7**: Yüklenici Yönetimi
- **D8**: Acil Durum Hazırlığı

## 🔧 Kullanım

### Temel Kullanım

```python
from agents.rootcause_agent_v2 import RootCauseAgentV2

# Agent'i başlat
agent = RootCauseAgentV2()

# Analiz yap
result = agent.analyze_root_causes(
    part1_data=part1_data,
    part2_data=part2_data,
    investigation_data=investigation_data
)

# Sonuçlar
print(result["final_report_tr"])
```

### Çıktı Yapısı

```json
{
  "incident_summary": "Olay özeti...",
  "analysis_branches": [
    {
      "branch_number": 1,
      "immediate_cause": {
        "code": "B1.6",
        "category_type": "MEKANİK/FİZİKSEL",
        "cause_tr": "Güvenlik switch'i baypas edilmiş",
        "evidence_tr": "..."
      },
      "why_chain": [
        {"level": 1, "question_tr": "...", "answer_tr": "..."},
        {"level": 2, "question_tr": "...", "answer_tr": "..."},
        ...
      ],
      "root_cause": {
        "code": "D6.1",
        "category_type": "ORGANİZASYONEL",
        "cause_tr": "Yetersiz Bakım Stratejisi",
        "explanation_tr": "..."
      }
    },
    {
      "branch_number": 2,
      ...
    }
  ],
  "final_root_causes": [...],
  "final_report_tr": "Türkçe rapor metni..."
}
```

## 🎨 Özellikler

✅ **Hiyerarşik Yapı**: A/B → 5-Why → C/D akışı
✅ **Otomatik Kodlama**: Her neden için kategori kodu (A1.4, D6.1, vb.)
✅ **Çoklu Dallar**: Her immediate cause için ayrı 5-Why zinciri
✅ **Türkçe Çıktı**: Tüm analiz Türkçe
✅ **RAG Opsiyonel**: Kategori bilgisi RAG veya hardcoded
✅ **Görsel Ağaç**: ASCII art ile dal yapısı

## 📊 Örnek Çıktı

```
🔴 OLAY: Operatörün eli pres makinesinde sıkıştı

⚡ DAL 1: MEKANİK/FİZİKSEL
📌 [B1.6] Güvenlik switch'i baypas edilmişti
   ↓
❓ Neden 1? → Arızalıydı
❓ Neden 2? → Yedek parça yoktu
❓ Neden 3? → Takip yapılmıyordu
❓ Neden 4? → Bakım planı yoktu
   ↓
🎯 [D6.1] Yetersiz Bakım Stratejisi

⚡ DAL 2: DAVRANIŞSAL
📌 [A1.4] Operatör yetkisiz müdahale etti
   ↓
❓ Neden 1? → Bakımcı yoktu
❓ Neden 2? → Üretim baskısı
❓ Neden 3? → Hedef tutturma zorunluluğu
   ↓
🎯 [D1.4] Üretim > Güvenlik kültürü
```

## 🚀 Sonraki Adımlar

1. ✅ V2 agent oluşturuldu
2. ✅ Test başarılı
3. ⏳ `main.py`'de aktif et
4. ⏳ Admin panelde görselleştir
5. ⏳ PDF raporuna entegre et

## 📝 Not

Bu yapı HSG245 standardına tam uyumludur ve CLC/ABS Master Root Cause Taxonomy kullanır.
