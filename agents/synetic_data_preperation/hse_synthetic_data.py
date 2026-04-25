"""
HSE 5 Why — Sentetik Veri Üretim Pipeline'ı
============================================

Strateji:
  1. Seed taxonomy  — sektör × olay tipi × kök neden kategorisi kombinasyonları
  2. Olay üretimi   — her kombinasyon için gerçekçi olay senaryosu üret
  3. 5 Why üretimi  — uzman kalitesinde zincir üret (teacher modeli)
  4. Kalite filtresi — generic/zayıf cevapları temizle
  5. Negatif örnek  — kasıtlı yanlış zincirler + neden yanlış açıklaması
  6. Export         — DSPy'ın beklediği formatta JSONL kaydet

Kullanım:
  Gerçek API çağrısı için:  python hse_synthetic_data.py --mode real --n 100
  Mock test için:           python hse_synthetic_data.py --mode mock --n 10
"""

import argparse
import json
import os
import random
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


def _clean_env_secret(value: Optional[str]) -> str:
    """Dashboard'dan kopyalanan tırnak/boşluk gibi gürültüyü temizle."""
    if not value:
        return ""
    v = str(value).strip()
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        v = v[1:-1].strip()
    return v


def _resolve_llm_api_key(explicit: Optional[str] = None) -> str:
    """OPENROUTER_API_KEY veya OPENAI_API_KEY; explicit CLI değeri önceliklidir."""
    if explicit:
        k = _clean_env_secret(explicit)
        if k:
            return k
    for name in ("OPENROUTER_API_KEY", "OPENAI_API_KEY"):
        k = _clean_env_secret(os.getenv(name))
        if k:
            return k
    raise RuntimeError(
        "API anahtarı yok. OPENROUTER_API_KEY veya OPENAI_API_KEY tanımlayın "
        "veya --api-key ile geçin."
    )


def _openrouter_api_base() -> str:
    base = (os.getenv("OPENROUTER_API_BASE") or "https://openrouter.ai/api/v1").strip().rstrip("/")
    while "/v1/v1" in base:
        base = base.replace("/v1/v1", "/v1", 1)
    return base

# ─────────────────────────────────────────────
# 1. SEED TAXONOMY
# ─────────────────────────────────────────────

SECTORS = [
    "inşaat", "kimya tesisi", "madencilik", "depo / lojistik",
    "imalat / üretim hattı", "petrol & gaz", "elektrik / enerji",
    "tarım", "gıda işleme", "atık yönetimi",
]

INCIDENT_TYPES = [
    "kayma / düşme (aynı seviye)",
    "yüksekten düşme",
    "cisim çarpması",
    "kimyasal maruziyet",
    "elektrik çarpması",
    "sıkışma / ezilme",
    "yangın / patlama",
    "ergonomik yaralanma (zorlanma)",
    "tehlikeli madde sızıntısı",
    "araç-yaya çarpışması",
]

# Kök neden KATEGORİLERİ (model bunlara takılmamalı — spesifik olmalı)
ROOT_CAUSE_CATEGORIES = [
    "fiziksel / çevresel koşul",
    "ekipman / makine arızası",
    "prosedür / sistem eksikliği",
    "yönetim / organizasyon faktörü",
    "tasarım hatası",
    "bakım yetersizliği",
    "iletişim / koordinasyon kopukluğu",
]

# Generic cevap KALIPLARI — bunlar filtreden geçmemeli
GENERIC_PATTERNS = [
    "eğitim eksikliği",
    "dikkatsizlik",
    "insan hatası",
    "ihmal",
    "prosedüre uymama",
    "farkındalık eksikliği",
    "kural ihlali",
]


# ─────────────────────────────────────────────
# 2. VERİ YAPILARI
# ─────────────────────────────────────────────

@dataclass
class WhyStep:
    depth: int           # 1–5
    question: str        # "Neden X oldu?"
    answer: str          # Spesifik, gözlemlenebilir neden
    is_root_cause: bool  # Bu adım kök neden mi?


@dataclass
class HSEIncident:
    incident_id: str
    sector: str
    incident_type: str
    root_cause_category: str
    description: str          # Ham olay anlatımı
    location: str
    time_of_day: str
    contributing_factors: list[str]
    why_chain: list[WhyStep]
    root_cause: str
    corrective_actions: list[str]
    preventive_measures: list[str]
    severity: str             # "minör" / "orta" / "ciddi" / "ölümcül"
    is_negative_example: bool = False
    negative_reason: Optional[str] = None  # Neden yanlış örnek?

    def to_dspy_example(self) -> dict:
        """DSPy trainset formatına çevir"""
        return {
            "incident_description": self.description,
            "sector": self.sector,
            "why_chain": [
                {
                    "depth": w.depth,
                    "question": w.question,
                    "answer": w.answer,
                    "is_root_cause": w.is_root_cause,
                }
                for w in self.why_chain
            ],
            "root_cause": self.root_cause,
            "contributing_factors": self.contributing_factors,
            "corrective_actions": self.corrective_actions,
            "severity": self.severity,
            "is_negative_example": self.is_negative_example,
            "negative_reason": self.negative_reason,
        }


# ─────────────────────────────────────────────
# 3. MOCK ÜRETİCİ (API olmadan test için)
# ─────────────────────────────────────────────

class MockHSEGenerator:
    """
    Gerçek LLM API çağrısı yapmadan deterministik sentetik veri üretir.
    Pipeline'ı test etmek ve yapıyı anlamak için kullanılır.
    """

    SCENARIO_TEMPLATES = [
        {
            "sector": "depo / lojistik",
            "incident_type": "kayma / düşme (aynı seviye)",
            "root_cause_category": "fiziksel / çevresel koşul",
            "description": "Sabah vardiyasında depo giriş koridorunda forklift operatörü zemin ıslak olduğu için kaydı ve sol bileği kırıldı.",
            "location": "Depo B giriş koridoru, kapı no:3",
            "time_of_day": "06:45 (sabah vardiyası başlangıcı)",
            "severity": "orta",
            "why_chain": [
                WhyStep(1, "Neden zemin ıslaktı?", "Gece temizlik ekibi zemin yıkadıktan sonra 'ıslak zemin' uyarı levhası koymamıştı.", False),
                WhyStep(2, "Neden uyarı levhası konulmamıştı?", "Temizlik prosedürü bu adımı açıkça tanımlamamıştı; sadece 'zemin temizle' yazıyordu.", False),
                WhyStep(3, "Neden prosedürde bu adım yoktu?", "Temizlik prosedürü en son 8 yıl önce yazılmış, o dönemden bu yana revize edilmemişti.", False),
                WhyStep(4, "Neden prosedür revize edilmemişti?", "Periyodik prosedür gözden geçirme sistemi 2019'dan beri inaktifti; sorumlu pozisyon boş kalmıştı.", False),
                WhyStep(5, "Neden sorumlu pozisyon boş kalmıştı?", "HSE yönetim sistemi organizasyon yapısı değişince güncellenmemişti; sorumluluk atanmamıştı.", True),
            ],
            "root_cause": "HSE yönetim sisteminde rol ve sorumluluk ataması, organizasyon değişikliklerine göre güncel tutulmamakta; bu nedenle kritik prosedür revizyonları sahipsiz kalmaktadır.",
            "contributing_factors": [
                "8 yıldır güncellenmemiş temizlik prosedürü",
                "Kaydırmaz zemin kaplama yokluğu",
                "Sabah vardiyası başlangıcında yeterli aydınlatma eksikliği",
                "Operatör bireysel koruyucu ekipman (kaydırmaz bot) kullanmıyordu",
            ],
            "corrective_actions": [
                "Tüm koridorlara sabit ıslak zemin sensörü ve otomatik uyarı sistemi kur",
                "Temizlik prosedürünü 30 gün içinde güncelle: uyarı levhası adımını zorunlu kıl",
                "HSE sorumlusu pozisyonunu 2 hafta içinde ata",
                "Forklift operatörleri için kaydırmaz bot standart KKD olarak belirle",
            ],
            "preventive_measures": [
                "Yıllık prosedür gözden geçirme takvimi oluştur",
                "Organizasyon değişikliği prosedürüne HSE sorumluluk güncelleme adımı ekle",
            ],
        },
        {
            "sector": "kimya tesisi",
            "incident_type": "kimyasal maruziyet",
            "root_cause_category": "ekipman / makine arızası",
            "description": "Reaktör 4'te boru bağlantısından HCl çözeltisi sızdı; operatör 20 dakika boyunca fark etmedi ve cilt tahrişi yaşadı.",
            "location": "Reaktör binası, hat B, Reaktör-4",
            "time_of_day": "14:20 (öğleden sonra vardiyası)",
            "severity": "ciddi",
            "why_chain": [
                WhyStep(1, "Neden boru bağlantısından sızıntı oldu?", "Flanş contası 6 ay önce servis ömrünü tamamlamıştı ancak değiştirilmemişti.", False),
                WhyStep(2, "Neden conta zamanında değiştirilmemişti?", "Bakım yönetim sistemi (CMMS) conta değişim aralığını yanlış parametrize etmişti: 12 ay yerine 24 ay girmişti.", False),
                WhyStep(3, "Neden yanlış parametre girilmişti?", "CMMS veri girişi ekipman üreticisi spesifikasyonu değil, dahili standart tablosundan yapılmıştı; bu tablo güncellenmemişti.", False),
                WhyStep(4, "Neden dahili standart tablosu güncellenmemişti?", "Üretici 2021'de bakım aralığını revize etmiş ancak teknik dökümanlar CMMS güncelleme sürecine dahil edilmemişti.", True),
            ],
            "root_cause": "Üretici teknik döküman güncellemelerinin bakım yönetim sistemine (CMMS) entegrasyon prosedürü tanımlı değil; değişiklik yönetimi süreci ekipman bakım parametrelerini kapsamamakta.",
            "contributing_factors": [
                "Reaktör alanında gaz/sıvı sızıntı dedektörü eksikliği",
                "Operatör visör içeren tam yüz maskesi yerine yarım maske kullanıyordu",
                "Acil duş ve göz yıkama istasyonu 25 metre uzakta konumlanmıştı",
            ],
            "corrective_actions": [
                "Reaktör-4 contasını derhal değiştir (kritik aksiyon, bugün)",
                "CMMS'teki tüm HCl hattı ekipmanı bakım aralıklarını üretici spesifikasyonuyla karşılaştır",
                "Değişiklik yönetimi prosedürüne CMMS güncelleme zorunluluğunu ekle",
                "Reaktör binasına otomatik sızıntı dedektörü kur",
            ],
            "preventive_measures": [
                "Üretici döküman güncellemelerini takip eden aylık tarama prosedürü oluştur",
                "CMMS veri girişini çift-kişi onay sürecine al",
            ],
        },
        {
            "sector": "inşaat",
            "incident_type": "yüksekten düşme",
            "root_cause_category": "prosedür / sistem eksikliği",
            "description": "4. katta form işçisi iskele kenarından 3.2 metre yüksekten düştü; sağ bacak kırığı ve kaburga hasarı.",
            "location": "A Blok, 4. kat doğu cephesi iskelesi",
            "time_of_day": "09:15",
            "severity": "ciddi",
            "why_chain": [
                WhyStep(1, "Neden işçi düştü?", "İskele kenarında korkuluk yoktu; knar güvenliği sağlanmamıştı.", False),
                WhyStep(2, "Neden korkuluk yoktu?", "Bir önceki gün rüzgar nedeniyle korkuluk bölümü sökülmüş, sabah vardiyası başlamadan tekrar kurulmamıştı.", False),
                WhyStep(3, "Neden kurulmamıştı?", "İskele sökme/takma işlemleri için gece ekibinden gündüz ekibine resmi teslim prosedürü tanımlı değildi.", False),
                WhyStep(4, "Neden teslim prosedürü tanımlı değildi?", "Proje güvenlik planı iskele değişikliklerini kapsayan güvenlik sağlama prosedürü içermiyordu.", True),
            ],
            "root_cause": "Proje güvenlik planında iskele bileşeni değişikliklerinden sonra yeniden devreye alma ve güvenlik doğrulama prosedürü tanımlı değil.",
            "contributing_factors": [
                "İşçi emniyet kemeri takmıyordu",
                "Ankraj noktaları yetersiz konumlanmıştı",
                "Güvenlik denetimi sabah vardiyası başlamadan önce yapılmamıştı",
            ],
            "corrective_actions": [
                "Derhal tüm iskele kenarlarını denetle, eksik korkulukları kur",
                "Proje güvenlik planına iskele değişiklik prosedürü ekle (1 hafta)",
                "Vardiya teslim formuna iskele bütünlük kontrolü ekle",
            ],
            "preventive_measures": [
                "İskele sertifikasyonu olan lider görevlendir",
                "Sabah güvenlik denetimi standart çalışma prosedürü olarak tanımla",
            ],
        },
    ]

    def generate(
        self,
        sector: str,
        incident_type: str,
        root_cause_category: str,
        incident_id: str,
    ) -> HSEIncident:
        """Şablondan seçerek ya da varyasyon üretir"""
        # Matching template bul yoksa ilki kullan
        template = next(
            (t for t in self.SCENARIO_TEMPLATES if t["sector"] == sector),
            random.choice(self.SCENARIO_TEMPLATES),
        )
        return HSEIncident(
            incident_id=incident_id,
            sector=sector,
            incident_type=incident_type,
            root_cause_category=root_cause_category,
            description=template["description"],
            location=template["location"],
            time_of_day=template["time_of_day"],
            severity=template["severity"],
            why_chain=template["why_chain"],
            root_cause=template["root_cause"],
            contributing_factors=template["contributing_factors"],
            corrective_actions=template["corrective_actions"],
            preventive_measures=template["preventive_measures"],
        )

    def generate_negative(
        self,
        base: HSEIncident,
        incident_id: str,
    ) -> HSEIncident:
        """Aynı olaydan generic/yanlış bir 5 Why zinciri üretir"""
        generic_chain = [
            WhyStep(1, "Neden kaza oldu?", "Çalışan dikkatsizdi.", False),
            WhyStep(2, "Neden dikkatsizdi?", "Yeterli eğitim almamıştı.", False),
            WhyStep(3, "Neden eğitim almamıştı?", "Eğitim programı yetersizdi.", False),
            WhyStep(4, "Neden program yetersizdi?", "İnsan kaynakları bütçesi kısıtlıydı.", False),
            WhyStep(5, "Neden bütçe kısıtlıydı?", "Yönetimin güvenliğe öncelik vermemesi.", True),
        ]
        return HSEIncident(
            incident_id=incident_id,
            sector=base.sector,
            incident_type=base.incident_type,
            root_cause_category=base.root_cause_category,
            description=base.description,
            location=base.location,
            time_of_day=base.time_of_day,
            severity=base.severity,
            why_chain=generic_chain,
            root_cause="Yönetimin güvenlik kültürünü benimsememesi",
            contributing_factors=["Eğitim eksikliği", "Dikkatsizlik"],
            corrective_actions=["Daha fazla eğitim ver", "Çalışanları uyar"],
            preventive_measures=["Farkındalık artır"],
            is_negative_example=True,
            negative_reason=(
                "Bu 5 Why zinciri geçersizdir çünkü: "
                "(1) Her adım gözlemlenebilir fiziksel/sistem kanıtına dayanmıyor, "
                "(2) 'Dikkatsizlik' ve 'eğitim eksikliği' kök neden değil belirti, "
                "(3) Kök neden bireysel davranışa atfediliyor, sistem nedeni araştırılmıyor, "
                "(4) Düzeltici aksiyonlar tekrar eğitim vermekten ibaret — kausal zincirle bağlantılı değil."
            ),
        )


# ─────────────────────────────────────────────
# 4. GERÇEK LLM ÜRETİCİ (DSPy tabanlı)
# ─────────────────────────────────────────────

# DSPy import — kurulu değilse mock'a düş
try:
    import dspy

    class IncidentGenerator(dspy.Signature):
        """HSE uzmanı olarak gerçekçi iş kazası senaryosu üret."""
        sector: str = dspy.InputField(desc="İş sektörü")
        incident_type: str = dspy.InputField(desc="Kaza tipi")
        root_cause_category: str = dspy.InputField(desc="Kök neden kategorisi")
        incident_description: str = dspy.OutputField(
            desc="2-3 cümle, spesifik detaylı olay anlatımı. Yer, zaman, etkilenen kişi içermeli."
        )
        location: str = dspy.OutputField(desc="Spesifik konum (bina, kat, hat no)")
        time_of_day: str = dspy.OutputField(desc="Saat ve vardiya")
        severity: str = dspy.OutputField(desc="minör / orta / ciddi / ölümcül")

    class FiveWhyGenerator(dspy.Signature):
        """
        HSE uzmanı olarak derinlemesine 5 Why analizi yap.
        KURALI: Her cevap somut, gözlemlenebilir ve doğrulanabilir olmalı.
        YASAK: 'dikkatsizlik', 'eğitim eksikliği', 'insan hatası' — bunlar neden değil belirti.
        YASAK: Erken durma — 'prosedür yoktu' bir neden değil, bir sonraki why sorusunu gerektirir.
        """
        incident_description: str = dspy.InputField()
        sector: str = dspy.InputField()
        root_cause_category: str = dspy.InputField(
            desc="Kök neden bu kategoride olmalı"
        )
        why_1_q: str = dspy.OutputField(desc="1. neden sorusu")
        why_1_a: str = dspy.OutputField(desc="1. neden cevabı — somut, gözlemlenebilir")
        why_2_q: str = dspy.OutputField(desc="2. neden sorusu")
        why_2_a: str = dspy.OutputField(desc="2. neden cevabı")
        why_3_q: str = dspy.OutputField(desc="3. neden sorusu")
        why_3_a: str = dspy.OutputField(desc="3. neden cevabı")
        why_4_q: str = dspy.OutputField(desc="4. neden sorusu")
        why_4_a: str = dspy.OutputField(desc="4. neden cevabı")
        why_5_q: str = dspy.OutputField(desc="5. neden sorusu (kök neden)")
        why_5_a: str = dspy.OutputField(desc="Kök neden — sistem veya organizasyon düzeyinde")
        root_cause_summary: str = dspy.OutputField(
            desc="Kök nedenin 1 cümlelik özeti"
        )
        corrective_actions: str = dspy.OutputField(
            desc="3-5 madde, JSON array formatında: [\"aksiyon1\", \"aksiyon2\"]"
        )

    class NegativeExampleGenerator(dspy.Signature):
        """
        Verilen olayın YANLIŞ bir 5 Why analizini üret.
        Zincir kasıtlı olarak generic, yüzeysel ve bireysel hataya odaklanan bir
        örnek olmalı. Sonra neden yanlış olduğunu açıkla.
        """
        incident_description: str = dspy.InputField()
        correct_root_cause: str = dspy.InputField()
        bad_why_chain: str = dspy.OutputField(
            desc="Yanlış/generic 5 Why zinciri JSON formatında"
        )
        why_its_wrong: str = dspy.OutputField(
            desc="Bu analizin neden yetersiz olduğunun 3-4 madde açıklaması"
        )

    class DSPyHSEGenerator:
        def __init__(
            self,
            model: str = "openrouter/google/gemini-2.5-flash",
            api_key: Optional[str] = None,
        ):
            key = _resolve_llm_api_key(api_key)
            if model.startswith("openrouter/"):
                api_base = _openrouter_api_base()
                os.environ["OPENROUTER_API_KEY"] = key
                os.environ["OPENAI_API_KEY"] = key
                os.environ["OPENROUTER_API_BASE"] = api_base
                self.lm = dspy.LM(
                    model=model,
                    api_key=key,
                    api_base=api_base,
                    max_tokens=4000,
                )
            else:
                os.environ["OPENAI_API_KEY"] = key
                self.lm = dspy.LM(model=model, api_key=key, max_tokens=4000)
            dspy.configure(lm=self.lm)
            self.incident_gen = dspy.ChainOfThought(IncidentGenerator)
            self.why_gen = dspy.ChainOfThought(FiveWhyGenerator)
            self.negative_gen = dspy.ChainOfThought(NegativeExampleGenerator)

        def generate(
            self,
            sector: str,
            incident_type: str,
            root_cause_category: str,
            incident_id: str,
        ) -> HSEIncident:
            # Adım 1: Olay üret
            inc = self.incident_gen(
                sector=sector,
                incident_type=incident_type,
                root_cause_category=root_cause_category,
            )
            # Adım 2: 5 Why zinciri üret
            why = self.why_gen(
                incident_description=inc.incident_description,
                sector=sector,
                root_cause_category=root_cause_category,
            )
            # Cevapları parse et
            chain = []
            for d in range(1, 6):
                q = getattr(why, f"why_{d}_q", f"Why {d}?")
                a = getattr(why, f"why_{d}_a", "—")
                chain.append(WhyStep(
                    depth=d,
                    question=q,
                    answer=a,
                    is_root_cause=(d == 5),
                ))
            # Düzeltici aksiyonları parse et
            try:
                actions = json.loads(why.corrective_actions)
            except Exception:
                actions = [why.corrective_actions]

            return HSEIncident(
                incident_id=incident_id,
                sector=sector,
                incident_type=incident_type,
                root_cause_category=root_cause_category,
                description=inc.incident_description,
                location=inc.location,
                time_of_day=inc.time_of_day,
                severity=inc.severity,
                why_chain=chain,
                root_cause=why.root_cause_summary,
                contributing_factors=[],
                corrective_actions=actions,
                preventive_measures=[],
            )

        def generate_negative(
            self, base: HSEIncident, incident_id: str
        ) -> HSEIncident:
            neg = self.negative_gen(
                incident_description=base.description,
                correct_root_cause=base.root_cause,
            )
            try:
                raw = json.loads(neg.bad_why_chain)
                chain = [
                    WhyStep(
                        depth=i + 1,
                        question=item.get("q", f"Why {i+1}?"),
                        answer=item.get("a", "—"),
                        is_root_cause=(i == 4),
                    )
                    for i, item in enumerate(raw[:5])
                ]
            except Exception:
                chain = [WhyStep(i + 1, f"Why {i+1}?", "generic", i == 4) for i in range(5)]

            return HSEIncident(
                incident_id=incident_id,
                sector=base.sector,
                incident_type=base.incident_type,
                root_cause_category=base.root_cause_category,
                description=base.description,
                location=base.location,
                time_of_day=base.time_of_day,
                severity=base.severity,
                why_chain=chain,
                root_cause="generic / yüzeysel kök neden",
                contributing_factors=[],
                corrective_actions=["eğitim ver", "uyar"],
                preventive_measures=[],
                is_negative_example=True,
                negative_reason=neg.why_its_wrong,
            )

    DSPY_AVAILABLE = True

except ImportError:
    DSPY_AVAILABLE = False


# ─────────────────────────────────────────────
# 5. KALİTE FİLTRESİ
# ─────────────────────────────────────────────

def quality_score(incident: HSEIncident) -> tuple[float, list[str]]:
    """
    0–1 arası kalite skoru ve sorun listesi döner.
    DSPy metriğinde de benzer mantık kullanılır.
    """
    issues = []
    score = 1.0

    # Causal chain bağlantısı (basit heuristik)
    for i, step in enumerate(incident.why_chain[1:], 1):
        prev_answer = incident.why_chain[i - 1].answer.lower()
        curr_question = step.question.lower()
        # Önceki cevaptaki anahtar kelimeler sonraki soruda geçmeli
        prev_keywords = set(prev_answer.split()) - {"bir", "ve", "de", "da", "ile"}
        curr_keywords = set(curr_question.split())
        overlap = len(prev_keywords & curr_keywords)
        if overlap == 0:
            issues.append(f"Why {i}→{i+1}: zayıf causal bağlantı")
            score -= 0.1

    # Generic cevap kontrolü
    for step in incident.why_chain:
        for pattern in GENERIC_PATTERNS:
            if pattern in step.answer.lower():
                if not incident.is_negative_example:
                    issues.append(f"Why {step.depth}: generic cevap içeriyor ({pattern!r})")
                    score -= 0.2
                break

    # Kök neden sistem/organizasyon düzeyinde mi?
    root = incident.root_cause.lower()
    system_keywords = ["sistem", "prosedür", "organizasyon", "yönetim", "tasarım",
                       "standart", "politika", "süreç", "altyapı"]
    if not any(kw in root for kw in system_keywords):
        if not incident.is_negative_example:
            issues.append("Kök neden bireysel düzeyde, sistem/org düzeyinde değil")
            score -= 0.15

    # Minimum derinlik kontrolü
    if len(incident.why_chain) < 3:
        issues.append("5 Why zinciri çok kısa (< 3 adım)")
        score -= 0.3

    # Düzeltici aksiyon kalitesi
    if len(incident.corrective_actions) < 2:
        issues.append("Düzeltici aksiyon yetersiz")
        score -= 0.1

    return max(0.0, round(score, 2)), issues


# ─────────────────────────────────────────────
# 6. PIPELINE
# ─────────────────────────────────────────────

def run_pipeline(
    n: int = 50,
    negative_ratio: float = 0.2,
    quality_threshold: float = 0.6,
    mode: str = "mock",
    api_key: Optional[str] = None,
    model: str = "openrouter/google/gemini-2.5-flash",
    output_dir: str = ".",
) -> dict:
    """
    Ana pipeline.

    Args:
        n: Kaç pozitif örnek üretilsin
        negative_ratio: Negatif örnek oranı (0.2 = %20)
        quality_threshold: Bu skorun altındaki örnekler atılır
        mode: "mock" | "real"
        api_key: OpenRouter veya OpenAI anahtarı (real modda; yoksa ortam)
        model: LiteLLM model stringi (örn. openrouter/google/gemini-2.5-flash)
        output_dir: JSONL dosyaları buraya yazılır

    Returns:
        Üretim istatistikleri
    """
    if mode == "real":
        if not DSPY_AVAILABLE:
            raise RuntimeError("dspy-ai kurulu değil: pip install dspy-ai")
        generator = DSPyHSEGenerator(model=model, api_key=api_key)
    else:
        generator = MockHSEGenerator()

    print(f"\n{'='*55}")
    print(f"  HSE Sentetik Veri Pipeline — {mode.upper()} mod")
    print(f"  Hedef: {n} pozitif + {int(n*negative_ratio)} negatif örnek")
    print(f"{'='*55}\n")

    positives: list[HSEIncident] = []
    negatives: list[HSEIncident] = []
    skipped = 0

    # Kombinasyon listesi oluştur
    combos = [
        (s, it, rc)
        for s in SECTORS
        for it in INCIDENT_TYPES
        for rc in ROOT_CAUSE_CATEGORIES
    ]
    random.shuffle(combos)

    # ── POZİTİF ÖRNEKLER ──
    print("Pozitif örnek üretimi:")
    for i in range(n):
        sector, incident_type, rc_cat = combos[i % len(combos)]
        inc_id = f"HSE-POS-{i+1:04d}"

        try:
            incident = generator.generate(
                sector=sector,
                incident_type=incident_type,
                root_cause_category=rc_cat,
                incident_id=inc_id,
            )
            score, issues = quality_score(incident)

            if score >= quality_threshold:
                positives.append(incident)
                print(f"  [{i+1:3d}/{n}] {inc_id} ✓  score={score:.2f}  {sector[:20]}")
            else:
                skipped += 1
                print(f"  [{i+1:3d}/{n}] {inc_id} ✗  score={score:.2f}  sorun: {issues[0] if issues else '?'}")

        except Exception as e:
            skipped += 1
            print(f"  [{i+1:3d}/{n}] {inc_id} HATA: {e}")

        if mode == "real":
            time.sleep(0.5)  # rate limit

    # ── NEGATİF ÖRNEKLER ──
    n_neg = int(n * negative_ratio)
    print(f"\nNegatif örnek üretimi ({n_neg} adet):")
    neg_sources = random.sample(positives, min(n_neg, len(positives)))

    for i, base in enumerate(neg_sources):
        neg_id = f"HSE-NEG-{i+1:04d}"
        try:
            neg = generator.generate_negative(base=base, incident_id=neg_id)
            negatives.append(neg)
            print(f"  [{i+1:3d}/{n_neg}] {neg_id} ✓  kaynak: {base.incident_id}")
        except Exception as e:
            print(f"  [{i+1:3d}/{n_neg}] {neg_id} HATA: {e}")

        if mode == "real":
            time.sleep(0.5)

    # ── KAYDET ──
    all_examples = positives + negatives
    random.shuffle(all_examples)

    # Train / dev / test bölümle (70 / 15 / 15)
    total = len(all_examples)
    t_end = int(total * 0.70)
    d_end = int(total * 0.85)

    splits = {
        "train": all_examples[:t_end],
        "dev":   all_examples[t_end:d_end],
        "test":  all_examples[d_end:],
    }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for split_name, examples in splits.items():
        filepath = output_path / f"hse_5why_{split_name}.jsonl"
        with open(filepath, "w", encoding="utf-8") as f:
            for ex in examples:
                f.write(json.dumps(ex.to_dspy_example(), ensure_ascii=False) + "\n")
        print(f"\n  → {filepath}  ({len(examples)} örnek)")

    # DSPy dspy.Example formatında da kaydet (doğrudan trainset olarak kullanılabilir)
    dspy_trainset_path = output_path / "hse_dspy_trainset.json"
    dspy_trainset = [ex.to_dspy_example() for ex in splits["train"]]
    with open(dspy_trainset_path, "w", encoding="utf-8") as f:
        json.dump(dspy_trainset, f, ensure_ascii=False, indent=2)
    print(f"  → {dspy_trainset_path}  (DSPy trainset formatı)")

    stats = {
        "toplam_uretilen": len(all_examples),
        "pozitif": len(positives),
        "negatif": len(negatives),
        "atilan": skipped,
        "train": len(splits["train"]),
        "dev": len(splits["dev"]),
        "test": len(splits["test"]),
        "sektör_dagilimi": {},
        "ciddiyet_dagilimi": {},
    }
    for ex in positives:
        stats["sektör_dagilimi"][ex.sector] = stats["sektör_dagilimi"].get(ex.sector, 0) + 1
        stats["ciddiyet_dagilimi"][ex.severity] = stats["ciddiyet_dagilimi"].get(ex.severity, 0) + 1

    print(f"\n{'='*55}")
    print("  ÖZET")
    for k, v in stats.items():
        if not isinstance(v, dict):
            print(f"  {k:25s}: {v}")
    print(f"{'='*55}\n")

    return stats


# ─────────────────────────────────────────────
# 7. DSPy ENTEGRASYON YARDIMCISI
# ─────────────────────────────────────────────

def load_dspy_examples(jsonl_path: str):
    """
    JSONL'yi yükle ve DSPy Example listesi döndür.
    Kullanım:
        trainset = load_dspy_examples("hse_5why_train.jsonl")
        optimizer = dspy.MIPROv2(metric=hse_metric, auto="medium")
        optimized = optimizer.compile(my_program, trainset=trainset)
    """
    if not DSPY_AVAILABLE:
        print("DSPy kurulu değil, raw dict listesi dönülüyor")
        examples = []
        with open(jsonl_path, encoding="utf-8") as f:
            for line in f:
                examples.append(json.loads(line))
        return examples

    examples = []
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            ex = dspy.Example(
                incident_description=data["incident_description"],
                sector=data["sector"],
                why_chain=data["why_chain"],
                root_cause=data["root_cause"],
                corrective_actions=data["corrective_actions"],
                is_negative_example=data.get("is_negative_example", False),
            ).with_inputs("incident_description", "sector")
            examples.append(ex)
    return examples


# ─────────────────────────────────────────────
# 8. CLI
# ─────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HSE 5 Why Sentetik Veri Üretici")
    parser.add_argument("--mode", choices=["mock", "real"], default="mock",
                        help="mock: API'siz test | real: gerçek LLM")
    parser.add_argument("--n", type=int, default=20,
                        help="Üretilecek pozitif örnek sayısı")
    parser.add_argument("--neg-ratio", type=float, default=0.2,
                        help="Negatif örnek oranı (varsayılan: 0.2)")
    parser.add_argument("--quality", type=float, default=0.6,
                        help="Minimum kalite skoru (varsayılan: 0.6)")
    parser.add_argument(
        "--model",
        default="openrouter/google/gemini-2.5-flash",
        help="DSPy / LiteLLM model (real modda, örn. openrouter/google/gemini-2.5-flash)",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="OpenRouter veya OpenAI API anahtarı (yoksa OPENROUTER_API_KEY / OPENAI_API_KEY)",
    )
    parser.add_argument("--output", default="/mnt/user-data/outputs",
                        help="Çıktı dizini")
    args = parser.parse_args()

    stats = run_pipeline(
        n=args.n,
        negative_ratio=args.neg_ratio,
        quality_threshold=args.quality,
        mode=args.mode,
        api_key=args.api_key,
        model=args.model,
        output_dir=args.output,
    )
