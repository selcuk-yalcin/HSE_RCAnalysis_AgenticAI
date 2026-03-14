# 🗺️ RECA AI — Ürün Yol Haritası & İş Planı

**Oluşturulma:** 05.03.2026  
**Ürün:** AI Destekli Kaza Soruşturma & Kök Neden Analizi (RCA) Rapor Sistemi  
**Teknoloji:** Claude Sonnet (Anthropic) + HSG245 Taksonomisi  
**Repo:** HSE_RCAnalysis_AgenticAI (main branch)  
**Sorumlu:** selcuk-yalcin

---

## 📊 Mevcut Durum Özeti (5 Mart 2026)

### Teknik Olgunluk

| Metrik | Değer | Notlar |
|--------|-------|--------|
| AI Rapor Kalitesi (Bağımsız Test) | **78 / 100** | RECA MAOG kazı göçüğü senaryosu |
| İnsan Uzman Kalitesi (Aynı Senaryo) | **88 / 100** | Referans: RECA-MAOG-IRP-26-00765 |
| RCA Bölümü Karşılaştırması | **22/25 vs 22/25** | Eşit — en kritik bölüm |
| Ortalama Rapor Süresi | **~900 sn** | Step 1-4 toplamı |
| Desteklenen Dil | **6** | TR, EN, AR, DE, FR, RU |
| Test Senaryosu Sayısı | **9** | Tüm senaryolar PASSED |
| Gerçek API Maliyeti | **~$1.00 / rapor** | 12 API çağrısı, ~162K token |

### Pipeline Durumu

```
OverviewAgent → AssessmentAgent → RootCauseAgentV2 → SkillBasedDocxAgent
    (Part 1)         (Part 2)           (Part 3)          (DOCX + HTML)
      ✅                ✅                 ✅                  ✅
```

### Test Dosyaları (PASSED)

| Dosya | Senaryo | Dil |
|-------|---------|-----|
| `test_fall_from_height.py` | Yüksekten düşme | Türkçe |
| `test_fall_from_height_spanish.py` | Yüksekten düşme | İspanyolca |
| `test_fall_from_height_arabic.py` | Yüksekten düşme | Arapça |
| `test_chemical_mixing_noise_english.py` | Kimyasal karışım | İngilizce |
| `test_forklift_pesticide_english.py` | Forklift + pestisit | İngilizce |
| `test_earthquake_english.py` | Deprem | İngilizce |
| `test_sabotage_english.py` | Sabotaj | İngilizce |
| `test_machine_entrapment.py` | Makine sıkışması | Türkçe |
| `test_reca_maog_kazi_goçugu.py` | Kazı göçüğü (LTI) | Türkçe |

---

## 🟢 FAZ 1 — Hızlı Kazanımlar (Hafta 1-2)

> **Hedef:** Rapor kalitesini 78 → 88+ puana çıkarmak. Sıfır altyapı değişikliği.

### 1.1 Tanık İfadeleri — Birebir Alıntı Formatı

**Problem:** AI, tanık ifadelerini kendi cümlelerine dönüştürüyor; orijinal güç kayboluyor.

**Çözüm:**
- [ ] `rootcause_agent_v2.py` promptuna kural ekle:  
  *"Tanık ifadelerini birebir alıntı olarak koru. Asla yeniden ifade etme."*
- [ ] `skillbased_docx_agent.py`'de tanık bölümüne tırnak işareti + isim formatı ekle
- [ ] Test: RECA MAOG senaryosunda Adem Toslak, Gürkan Demir ifadelerini kontrol et

**Beklenen kazanım:** +3 puan (tanık ifadeleri 5→8/10)

---

### 1.2 Spesifik İstatistikler — Kayıp Veri Tespiti

**Problem:** "777 uygunsuzluk", "94 mm yağış", "54 iş durdurma" gibi veriler bazen genel ifadelere dönüşüyor.

**Çözüm:**
- [ ] `overview_agent.py` promptuna ekle:  
  *"Tüm sayısal verileri, tarihleri, kodları ve istatistikleri değiştirmeden koru."*
- [ ] Regex doğrulama: raporda geçen sayılar input verisindekiyle eşleşmeli
- [ ] Test: RECA MAOG 777, 94mm, 566.300 TL → raporda aynen geçmeli

**Beklenen kazanım:** +2 puan (istatistik doğruluğu 7→9/10)

---

### 1.3 Düzeltici Aksiyon Detaylandırma

**Problem:** Aksiyonlar fazla genel: "eğitim ver", "denetim artır" gibi.

**Çözüm:**
- [ ] `skillbased_docx_agent.py` aksiyon tablosuna zorunlu alan ekle:
  - `sorumlu_kisi` (pozisyon değil, isim veya unvan)
  - `spesifik_tarih` ("30 gün" yerine "DD.MM.YYYY")
  - `tamamlanma_kriteri` (nasıl doğrulanacak)
- [ ] Minimum aksiyon madde sayısını 8 → 12 olarak güncelle
- [ ] Proje geneli ders paylaşımı maddesini şablona sabit ekle

**Beklenen kazanım:** +2 puan (aksiyon 6→8/10)

---

### 1.4 Kronoloji Tamamlama

**Problem:** Zaman çizelgesinde bazı ara olaylar atlanıyor.

**Çözüm:**
- [ ] `overview_agent.py` zaman çizelgesi promptuna ekle:  
  *"Tüm ara olayları koru, hiçbir zaman dilimini atlama"*
- [ ] Structured input şemasına `timeline_events[]` alanı tanımla
- [ ] Test: kronoloji bütünlüğünü doğrula (RECA MAOG: 08:00 → 17:00)

**Beklenen kazanım:** +1 puan (zaman çizelgesi 9→10/10)

---

### 1.5 HTML Rapor — Balık Kılçığı + Grafikler + Bölüm Silme

**Problem:** HTML rapor tablolar arası boşluklar, grafik yok, silme özelliği yok.

**Çözüm:**
- [ ] `skillbased_docx_agent.py` → `_generate_html_template()` metoduna ekle:
  - SVG tabanlı **Ishikawa (balık kılçığı) diyagramı** — kök nedenler görsel
  - **Chart.js** pasta + bar grafikler:
    - Kök neden kategorisi dağılımı (D1/D3/D5/D6 oranları)
    - Aksiyon öncelik dağılımı (ACİL/YÜKSEK/ORTA/DÜŞÜK)
  - **Bölüm × butonu** — düzenleme modunda her bölümün sağ üstünde çarpı
  - Tablo satır silme: her satır sonuna `×` butonu
- [ ] CSS: tablo hücreleri `border`, `padding` düzeltmesi
- [ ] RTL dil desteği: Arapça tablolar sağdan sola

**Beklenen kazanım:** HTML kalitesi 6→9/10

---

## 🟡 FAZ 2 — Teknik Altyapı (Hafta 3-6)

> **Hedef:** Sistemi çok kullanıcılı ve production-ready hale getirmek.

### 2.1 Rapor Üretim Süresini Kısaltma (~900s → ~300s)

**Problem:** ~900 saniye pipeline → Railway 300s HTTP timeout aşılıyor.

**Çözüm:**
- [ ] `skillbased_docx_agent.py` içinde `_generate_full_report_content()` metodu:
  - 7 ayrı API çağrısını → 1 mega API çağrısına indir
  - Tüm bölümleri tek promptta üret, JSON olarak dön
- [ ] `generate_report()` metodunu yeni metodu kullanacak şekilde refactor et
- [ ] Performans testi: 3 senaryo ile süre karşılaştırması

**Beklenen kazanım:** ~420s tasarruf (Step 5: 500s → 80s)

---

### 2.2 Async Job Queue — Multi-User Desteği

**Problem:** Railway HTTP timeout = 300s. Pipeline = ~900s. Senkron endpoint çalışmıyor.  
**Çözüm:** Async job queue — `POST /investigate` anında `job_id` döner, Worker arka planda çalışır.

```
KULLANICI
    │
    ▼
POST /api/investigate  ──→  {"job_id": "abc-123"}   (anında döner)
    │
    ▼
GET /api/status/abc-123  ──→  {"status": "processing", "step": 3, "progress": 60%}
    │                         (3 saniyede bir polling)
    ▼
GET /api/report/abc-123?format=html  ──→  FileResponse
```

**Yapılacaklar:**
- [ ] `requirements.txt`'e ekle: `redis`, `celery`, `flower`
- [ ] `worker/worker.py` oluştur: `brpop("job_queue")` loop
- [ ] `api/main.py`'ye endpoint'ler ekle:
  - `POST /api/investigate` → `{"job_id": "abc123"}` (anında döner)
  - `GET /api/status/{job_id}` → progress + durum
  - `GET /api/report/{job_id}?format=html|docx|json` → FileResponse
- [ ] Redis job TTL: 24 saat
- [ ] Load test: 20 eş zamanlı istek

**Beklenen kazanım:** 1-2 → 50+ eş zamanlı kullanıcı

---

### 2.3 QuotaMiddleware — Kota Sistemi

**Problem:** Sınırsız plan opsiyonuyla $1/rapor maliyet, 649+ raporda zarar.

```python
PLAN_LIMITS   = {"basic": 5, "pro": 30, "enterprise": 150, "enterprise_plus": 500, "unlimited": 999999}
OVERAGE_RATES = {"basic": 15.00, "pro": 9.00, "enterprise": 6.00, "enterprise_plus": 4.00}  # $/rapor

def check_quota(user_id, plan) → {"allowed": True, "overage": False, "overage_cost": 0.0}
def increment_usage(user_id) → Redis monthly counter, 35 gün TTL
```

**Yapılacaklar:**
- [ ] `api/quota.py` oluştur: QuotaMiddleware class
- [ ] `api/main.py`'de her `/investigate` çağrısında quota kontrolü
- [ ] Aşım faturası: `overage_cost` Stripe'a ilet
- [ ] Dashboard: "Bu ay X rapor ürettiniz, Y rapor kaldı"

---

### 2.4 Authentication & Kullanıcı Yönetimi

- [ ] `requirements.txt`'e ekle: `python-jose`, `passlib`, `bcrypt`
- [ ] `api/auth.py`: JWT token sistemi
- [ ] Kullanıcı modeli: email, plan (basic/pro/enterprise), quota, usage
- [ ] Tüm `/investigate` endpoint'leri auth gerektirsin
- [ ] `api/models.py` veya PostgreSQL ile kullanıcı DB

---

### 2.5 Railway + Vercel Deploy Mimarisi

> Railway HTTP timeout = **300s** → Async job queue **ZORUNLU**. Senkron pipeline production'da çalışmaz.

```
┌─────────────────────────────────────────────────────────────┐
│  VERCEL (Frontend — $0/ay Hobby)                            │
│  Next.js/React                                              │
│  Form → POST /api/investigate → job_id alır                 │
│  Polling → GET /api/status/{job_id} (3 sn)                  │
│  İndir  → GET /api/report/{job_id}?format=html|docx         │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS
┌──────────────────────────▼──────────────────────────────────┐
│  RAILWAY (Backend — ~$20/ay)                                │
│                                                             │
│  ┌─────────────────┐   ┌──────────────────────────────────┐ │
│  │  API Service    │   │  Worker Service                  │ │
│  │  FastAPI $5/ay  │   │  (SERVICE=worker) $5/ay          │ │
│  │                 │   │                                  │ │
│  │  POST /invest.  │──▶│  brpop("job_queue")              │ │
│  │  GET /status/{}  │◀──│  OverviewAgent                  │ │
│  │  GET /report/{}  │   │  AssessmentAgent                │ │
│  └────────┬────────┘   │  RootCauseAgentV2               │ │
│           │            │  SkillBasedDocxAgent             │ │
│  ┌────────▼────────┐   └──────────────┬───────────────────┘ │
│  │  Redis $5/ay    │◀─────────────────┘                     │
│  │  job status     │   progress tracking                     │
│  └─────────────────┘                                        │
│  ┌─────────────────┐                                        │
│  │  PostgreSQL     │   kullanıcı, plan, kota, fatura        │
│  │  $5/ay          │                                        │
│  └─────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
```

**Dockerfile — Tek Image, Env Var ile Mod:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD if [ "$SERVICE" = "worker" ]; then \
      python worker/worker.py; \
    else \
      uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}; \
    fi
```

**Frontend TypeScript Polling Hook:**
```typescript
// hooks/useInvestigation.ts
export function useInvestigation() {
  const [jobId, setJobId]       = useState<string | null>(null);
  const [status, setStatus]     = useState<string>("idle");
  const [progress, setProgress] = useState<number>(0);

  async function startInvestigation(formData: Record<string, string>) {
    const res = await fetch(`${API_URL}/api/investigate`, {
      method: "POST", body: JSON.stringify(formData)
    });
    const { job_id } = await res.json();
    setJobId(job_id);
  }

  useEffect(() => {
    if (!jobId || status === "completed") return;
    const interval = setInterval(async () => {
      const res  = await fetch(`${API_URL}/api/status/${jobId}`);
      const data = await res.json();
      setStatus(data.status);
      setProgress(data.progress ?? 0);
      if (data.status === "completed" || data.status === "failed")
        clearInterval(interval);
    }, 3000);  // 3 saniyede bir polling
    return () => clearInterval(interval);
  }, [jobId, status]);

  return { startInvestigation, status, progress, jobId };
}
```

**Railway Deploy Kontrol Listesi:**
```
☐ Railway: Yeni proje oluştur
☐ Railway: Redis plugin ekle → REDIS_URL otomatik set edilir
☐ Railway: PostgreSQL plugin ekle → DATABASE_URL otomatik set edilir
☐ Railway: API servisi → GitHub repo bağla, SERVICE=api
☐ Railway: Worker servisi → aynı repo, SERVICE=worker
☐ Railway: OPENROUTER_API_KEY, SECRET_KEY env var ekle
☐ Vercel: Next.js frontend deploy, NEXT_PUBLIC_API_URL set et
☐ Test: POST /api/investigate → job_id → poll → rapor indir
☐ Test: 5 eş zamanlı istek → hepsi kuyrukta sıralanmalı
```

---

## 🔴 FAZ 3 — Ticari Hazırlık (Ay 2-3)

> **Hedef:** Yasal, iş ve ölçek altyapısı. İlk ücretli müşteri.

### 3.1 Yasal Çerçeve & Disclaimer

- [ ] Her rapor çıktısına zorunlu disclaimer ekle:  
  *"Bu rapor yapay zeka tarafından üretilmiştir. Yetkili HSE uzmanı onayı olmadan resmi belge olarak kullanılamaz."*
- [ ] Kullanım Şartları (ToS) metni hazırla
- [ ] Gizlilik Politikası (Privacy Policy) hazırla
- [ ] Hukuk danışmanı ile KVKK/GDPR uyum kontrolü

---

### 3.2 KVKK / GDPR Uyumu

- [ ] Kişisel veri işleme kaydı oluştur (kazazede adı, doğum tarihi vb.)
- [ ] Veri anonimleştirme seçeneği: isimler → "Çalışan A"
- [ ] Veri silme endpoint'i: `DELETE /api/jobs/{job_id}`
- [ ] Sunucu lokasyonu: AB veya Türkiye (KVKK açısından tercih)
- [ ] Veri saklama: Basic=30 gün, Pro=1 yıl, Enterprise=5 yıl

---

### 3.3 Faturalama Sistemi

- [ ] Stripe veya iyzico entegrasyonu
- [ ] Aylık abonelik + overage (aşım) ücretlendirmesi
- [ ] Plan yükseltme/düşürme akışı
- [ ] Fatura PDF üretimi
- [ ] Aylık kullanım raporu: kaç rapor, ne kadar ödendi

---

### 3.4 Ülkeye Özel Regülasyon Şablonları (Pro Özelliği)

- [ ] 🇹🇷 Türkiye: 6331 sayılı İSG Kanunu + SGK bildirimi
- [ ] 🇬🇧 UK: RIDDOR formatı + HSE notification fields
- [ ] 🇸🇦 Suudi: SASO / Saudi Aramco GI-7.001
- [ ] 🇩🇪 Almanya: DGUV formatı
- [ ] 🇫🇷 Fransa: CERFA formatı
- [ ] Template seçici: rapor oluştururken ülke seçimi

---

### 3.5 White-Label Altyapısı (Enterprise Özelliği)

- [ ] Multi-tenant: her müşteri kendi subdomain'i
- [ ] Logo / renk paleti özelleştirme: config ile
- [ ] API key yönetimi: müşteri kendi API key'ini bağlayabilsin
- [ ] White-label fiyatı: $15.000 setup + aylık royalty

---

## 🎯 FAZ 4 — Büyüme (Ay 4-12)

### 4.1 Uzman Onay Modülü (Pro/Enterprise)

- [ ] Rapor üretilince → HSE uzmanına email bildirimi
- [ ] Uzman web arayüzünde raporu inceler, yorumlar, onaylar
- [ ] Onaylanan rapor → "Onaylandı" damgası + uzman imzası
- [ ] Onay süreci audit trail: kim, ne zaman, ne değiştirdi
- [ ] **Bu modül hem yasal riski sıfırlar hem premium gelir sağlar**

---

### 4.2 Benchmark & Trend Analizi (Pro/Enterprise)

- [ ] Şirket bazında: aylık kaza türü dağılımı
- [ ] Kök neden frekans analizi: hangi D-kodları en çok çıkıyor
- [ ] Öngörücü uyarı: "Bu ay 3 D1.9 tespit edildi, sistematik sorun var"
- [ ] Dashboard: grafik + CSV export

---

### 4.3 Ses / Video Transkripsiyon (Enterprise)

- [ ] Tanık görüşmesini kaydet → otomatik transkript → rapora aktar
- [ ] Whisper API entegrasyonu
- [ ] 6 dil: Türkçe, İngilizce, Arapça, Almanca, Fransızca, Rusça
- [ ] **Bu özellik tanık bölümünü 6/10 → 10/10'a taşır**

---

### 4.4 Mobil Uygulama (Saha Kullanımı)

- [ ] Saha görevlisi: kaza fotoğrafı + sesli not → AI rapor başlatır
- [ ] Offline mod: internet olmadan veri topla, bağlanınca gönder
- [ ] GPS koordinatı: kaza yerini otomatik işaretle
- [ ] React Native veya Flutter

---

## 💰 Fiyatlandırma Modeli (Kota Sistemi ile)

> ⚠️ **"Sınırsız" Enterprise tehlikelidir.** Gerçek API maliyeti ~$1.00/rapor. 649. raporda $799 Enterprise zarar eder.  
> Çözüm: Kota + aşım ücretlendirmesi.

| PLAN | FİYAT | RAPOR/AY (dahil) | EK RAPOR | BREAK-EVEN |
|------|-------|-----------------|----------|------------|
| **Basic** | $49/ay | 5 | $15/rapor | 5 rapor |
| **Pro** | $199/ay | 30 | $9/rapor | 20 rapor |
| **Enterprise** | $799/ay | 150 | $6/rapor | 80 rapor |
| **Enterprise+** | $1.999/ay | 500 | $4/rapor | 200 rapor |
| **Unlimited** | $4.999/ay | ∞ | — | 500 rapor |
| **Rapor başı** | $50 | 1 | — | Abonelik olmayanlar |

### Kota Risk Analizi

| Segment | Tipik Kullanım | Uygun Plan | Risk |
|---------|---------------|------------|------|
| Türk orta ölçek müteahhit | 10-50 rapor/ay | Pro | ✅ Güvenli |
| Büyük inşaat firması (TR) | 50-300 rapor/ay | Enterprise | ✅ Güvenli |
| Global mega firma | 1.000+ rapor/ay | Unlimited | ✅ Güvenli |
| Enterprise $799 break-even | 649 rapor/ay | — | ⚠️ Üstü zararlı |

### Overage ücretlendirmesi:
- Aşım geliri ARR'ye **%15-25 ek katkı** sağlar
- Kota sistemi olmadan bu gelir kaybolur

---

## 📈 Gelir Hedefleri

| Dönem | Hedef ARR | Müşteri | Karışım |
|-------|-----------|---------|---------|
| Ay 3 (Pilot) | $15K | 20 | 15 Pro + 5 Enterprise |
| Ay 6 | $120K | 200 | 100 Basic + 80 Pro + 20 Enterprise |
| Yıl 1 | $250K | 500 | 250 Basic + 200 Pro + 50 Enterprise |
| Yıl 2 | $1.4M | 1.050 | 6 dil × her pazarda 175 müşteri |
| Yıl 3 | $4.9M | 3.880 | 10 ülke × 388 müşteri |

> Aşım ücretleri (overage) gelire %15-25 ek katkı sağlar.

---

## 🌍 Küresel Pazar Analizi

### Pazar Büyüklüğü

| Pazar | 2024 | 2029 Tahmini | CAGR |
|-------|------|-------------|------|
| EHS Yazılım Pazarı (Toplam) | $6.1 milyar | $11.5 milyar | %7.6 |
| AI-destekli RCA segmenti | Yeni kategori | — | Blue Ocean |

*Kaynak: MarketsandMarkets, Nisan 2024*

### Rakip Analizi

| Rakip | Fiyat | Ne Yapıyor | Bizden Farkı |
|-------|-------|-----------|--------------|
| Intelex | $50K+/yıl | AI-assisted form doldurma | Biz serbest metin → tam rapor yazıyoruz |
| Sphera | $100K+/yıl | Root cause dropdown seçimi | Form bazlı, AI yazma yok |
| Cority | $200K+/yıl | Toyota/NASA müşteri | Enterprise only, SMB erişemez |
| SafetyCulture | $24/kullanıcı/ay | Mobil checklist | Kaza raporu yazma yok |
| **BİZİM ÜRÜN** | **$49-4.999/ay** | **Ham metin → HSG245 raporu** | **Dünyada tam benzeri yok** |

### Hedef Müşteri Sayısı

| Pazar | Potansiyel |
|-------|-----------|
| Türkiye (C-D sınıfı ISG uzmanları) | ~15.000 |
| Körfez/MENA bölgesi EPC müteahhitleri | ~8.000 |
| UK + Almanya mid-market | ~12.000 |
| **Toplam adreslenebilir pazar** | **~50.000+** |

**%1 pazar payı** = 500 müşteri × $200/ay ort. = **$100K MRR = $1.2M ARR**

### Neden Alırlar? — 5 Güçlü Satın Alma Sebebi

1. **⏱️ Yasal Zorunluluk + Deadline:** Her LTI için SGK/ÇSGB 72 saat bildirimi. ISG uzmanı 1 kişi, 5 şantiye → zaman yok.
2. **💰 Maliyet:** Danışmana verilen rapor 1.500-5.000 TL. Bizimle ~160 TL/rapor (Pro plan).
3. **📊 Kalite Tutarlılığı:** İnsan yorgun/aceleci → değişken kalite. AI: her rapor aynı standartta.
4. **🌐 Dil Engeli:** Global projelerde Türk/Arap/Rus karışık. İngilizce rapor zorunluluğu.
5. **🏢 Küçük Firma Erişimi:** Cority/Sphera → min $50K/yıl. Bizim ürün → bu gece kayıt ol, sabah rapor al.

---

## ⚠️ Riskler & Önlemler

| Risk | Olasılık | Etki | Önlem |
|------|---------|------|-------|
| "AI raporu yasal geçersiz" itirazı | Yüksek | Yüksek | Uzman onay modülü + disclaimer |
| Claude API fiyat artışı | Orta | Yüksek | Model soyutlama katmanı |
| Rakip (Intelex, Sphera) AI ekler | Yüksek | Orta | 6 dil + Türkçe uzmanlık = diff; 18 ay pencere |
| "Sınırsız" plan zarar | Yüksek | Yüksek | Kota sistemi — Faz 2.3 **öncelikli** |
| 20+ kullanıcı crash | Yüksek | Yüksek | Faz 2.2 Job Queue — **öncelikli** |
| KVKK cezası | Düşük | Çok Yüksek | Faz 3.2 tamamlanmadan TR'de pazarlama yapma |

---

## 🔑 En Kritik 3 Yapılacak (Bu Hafta)

```
1. ── PROMPT İYİLEŞTİRMESİ (1-2 gün)
   Tanık birebir alıntı + istatistik koruma kuralları
   → Rapor kalitesi 78 → 88+
   → Hemen deploy edilebilir, sıfır altyapı değişikliği

2. ── JOB QUEUE (3-4 gün)
   Redis + Worker + async endpoint
   → Multi-user hazır, Railway deploy mümkün
   → Bu olmadan genel piyasaya çıkma

3. ── YASAL DİSCLAIMER (2 saat)
   Her rapora "Uzman onayı gereklidir" notu
   → Hukuki riski minimize et
   → Pilot müşterilere hemen sunulabilir
```

---

## 🚀 Piyasaya Çıkış Eşiği

```
BUGÜN (78/100):
  ✅ Beta pilot müşteriye verilebilir
  ✅ $49-199/ay ücretlendirilebilir
  ✅ 5-10 pilot müşteri bulunabilir

88/100 KALİTEDE (2-3 hafta):
  ✅ Türkiye pazarına resmi lansman
  ✅ PR: "İlk Türk AI kaza raporu sistemi"
  ✅ $199-799/ay ücretlendirilebilir

95/100 KALİTEDE (1-2 ay):
  ✅ Suudi/UAE pazarına giriş
  ✅ UK/RIDDOR uyumlu versiyon
  ✅ $500K ARR hedefi gerçekçi
```

---

*Son güncelleme: 05.03.2026*  
*Sorumlu: selcuk-yalcin*  
*Repo: HSE_RCAnalysis_AgenticAI (main branch)*
