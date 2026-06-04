"""
HSG245 disambiguation soru bankası (gradio_chat_5why_v2 ile aynı veri).
Gradio bağımlılığı yok — API ve ajanlar tarafından import edilir.

HITL_USE_BARSEL=1 (varsayılan) iken BARSEL bankası önceliklidir; boş kalırsa HSG fallback.
"""
from __future__ import annotations

import os
from typing import Any

HSG245_DISAMBIGUATION: dict[str, list[dict]] = {

    # ── B4.x — YÜKSEKLİK / DÜŞME ──────────────────────────────────────────
    "B4.4": [
        {
            "soru": "Çalışma yapılan yerde bariyer, korkuluk veya güvenlik ağı mevcut muydu?",
            "hsg245": "D4.1 vs D4.2",
            "yönler": {
                "hiç yoktu|kurulmamış|yoktu|bulunmuyordu": "→ D4.1: Tehlike kontrol edilmemiş",
                "vardı ama|tamamlanmamış|eksikti|yetersiz": "→ D4.2: Kontrol belirlendi ama uygulanmadı",
                "aşıldı|geçildi|ihlal|atlandı": "→ A1.1: Bilerek ihlal",
            }
        },
        {
            "soru": "Bu çalışma için iş izni (PTW / permit-to-work) alındı mıydı? İzin koşulları sahada kontrol edildi mi?",
            "hsg245": "D4.4",
            "yönler": {
                "alınmadı|yoktu|izin yok": "→ D4.1: İş izni sistemi yok",
                "alındı ama|imzalandı ama|kontrol edilmedi|kimse bakmadı": "→ D4.4: İş izni etkisiz",
                "evet|kontrol edildi|uygulandı": "→ D4.4 değil — başka faktör aranmalı",
            }
        },
        {
            "soru": "Bu çalışma için daha önce risk değerlendirmesi yapılmış mıydı? Yapıldıysa — tehlike belirlenmişti ama önlem uygulanmadı mı?",
            "hsg245": "D4.1 vs D4.2 vs D4.3",
            "yönler": {
                "yapılmamış|hiç|yok|belirlenmemiş": "→ D4.1: Risk analizi gerçekten yok",
                "yapıldı ama|belirlendi ama|önlem alınmadı|uygulanmadı": "→ D4.2: Analiz var, kontroller sahaya yansımadı",
                "değişim|güncellenmedi|eskimiş|yeni ekipman|personel değişti": "→ D4.3: Değişim sonrası analiz güncellenmedi",
            }
        },
        {
            "soru": "Yönetim veya formen bariyer/koruyucu eksikliğinden önceden haberdardı mı? Üretim/zaman baskısı var mıydı?",
            "hsg245": "D1.4 vs D1.9",
            "yönler": {
                "biliyordu|haberdar|göz yumdu|umursamadı": "→ D1.9: Yönetim toleransı / güvensiz davranışa göz yumma",
                "üretim|baskı|yetiştir|gecikme|teslim": "→ D1.4: Üretim baskısı güvenliğin önüne geçti",
                "bilmiyordu|haber yok": "→ D1.1: Yetersiz gözetim / liderlik eksikliği",
            }
        },
        {
            "soru": "Çalışan(lar) yüksekte çalışma konusunda eğitim almış mıydı? Ne zaman aldı?",
            "hsg245": "D3.1 vs D3.6",
            "yönler": {
                "hiç almadı|verilmedi|yoktu|eğitim yok": "→ D3.1: Eğitim hiç verilmedi",
                "yıllar önce|eski|tazelenmedi|1 yıl|2 yıl": "→ D3.6: Eğitim etkinliği ölçülmüyor / tazeleme yok",
                "pratik|teorik|sınıfta": "→ D3.2: Eğitim içeriği yetersiz",
            }
        },
    ],

    "B4.1": [  # Korunmasız platform/delik
        {
            "soru": "Platformdaki açıklık/delik kapalı mıydı, yoksa açık ve işaretsiz mi bırakıldı?",
            "hsg245": "D4.1 vs D4.2",
            "yönler": {
                "açıktı|kapatılmadı|işaret yok": "→ D4.1 veya D5.1: Tehlike kontrol edilmedi",
                "örtüldü ama|geçici|yetersiz|işaret vardı ama": "→ D4.2: Kontrol var ama etkisiz",
            }
        },
        {
            "soru": "Risk değerlendirmesinde bu açıklık/tehlike belirlenmişti ama önlem alınmadı mıydı?",
            "hsg245": "D4.1 vs D4.2",
            "yönler": {
                "belirlenmemiş|analiz yok": "→ D4.1",
                "belirlendi ama|önlem alınmadı": "→ D4.2",
            }
        },
    ],

    # ── B3.x — ELEKTRİK ───────────────────────────────────────────────────
    "B3.2": [
        {
            "soru": "LOTO (Kilitleme/Etiketleme — Lockout/Tagout) prosedürü uygulandı mıydı? Ekipman enerji izole edildi mi?",
            "hsg245": "D4.5",
            "yönler": {
                "uygulanmadı|hiç|yoktu|prosedür yok|loto yok": "→ D4.5: LOTO sistemi yok/eksik",
                "uygulandı ama|kısmen|atlandı|eksik": "→ D4.5: LOTO uygulaması etkisiz",
                "bilerek|kasıtlı|biliyordu|alışkanlık": "→ A1.1 + D1.5: Bilinçli ihlal / normalleşmiş sapma",
            }
        },
        {
            "soru": "Elektrikle çalışmadan önce iş izni (PTW) alındı mıydı?",
            "hsg245": "D4.4",
            "yönler": {
                "alınmadı|yoktu|gerekmez dediler": "→ D4.1 veya D4.4: İş izni sistemi eksik",
                "alındı ama|kontrol edilmedi|kimse bakmadı": "→ D4.4: İş izni etkisiz",
            }
        },
        {
            "soru": "Çalışanın elektrik işleri için yetki belgesi (sertifika/lisans) var mıydı?",
            "hsg245": "D3.1 vs D3.4",
            "yönler": {
                "yok|belge yok|sertifika yok|ehliyetsiz": "→ D3.1 veya D3.4: Yeterliliksiz görevlendirme",
                "vardı ama|teorik|pratik değil": "→ D3.2 veya D3.3: Eğitim içeriği/pratik eksik",
            }
        },
        {
            "soru": "Bu şekilde (LOTO uygulamadan) çalışmak ekipte alışkanlık haline gelmiş miydi? Yönetim göz yumuyor muydu?",
            "hsg245": "D1.5 vs D1.9",
            "yönler": {
                "hep böyle|alışkanlık|norm|herkes yapıyor": "→ D1.5: Sapmanın normalleşmesi",
                "yönetim biliyordu|göz yumdu|umursamadı": "→ D1.9: Yönetim toleransı",
            }
        },
        {
            "soru": "Bu ekipman/sistem için risk değerlendirmesi ne zaman yapılmıştı?",
            "hsg245": "D4.1 vs D4.3",
            "yönler": {
                "yapılmamış|hiç|yok": "→ D4.1: Elektrik riski analiz edilmemiş",
                "eski|güncellenmedi|değişim|yeni ekipman": "→ D4.3: Değişim sonrası analiz güncellenmedi",
            }
        },
    ],

    # ── A3.x — KKD ─────────────────────────────────────────────────────────
    "A3.2": [
        {
            "soru": "KKD sahada mevcut muydu ve erişilebilir miydi?",
            "hsg245": "A3.4 vs A3.2",
            "yönler": {
                "yoktu|temin edilmedi|stok yok": "→ A3.4: KKD temin edilmedi (organizasyonel eksiklik → D5.1)",
                "vardı ama|ulaşamadı|uzaktaydı": "→ A3.4: KKD erişimi zor",
                "vardı ve|rahatlıkla": "→ A3.2: KKD vardı, çalışan kullanmadı",
            }
        },
        {
            "soru": "KKD kullanılmamasının nedeni neydi — rahatsızlık mı, alışkanlık mı, yönetim göz yumması mı?",
            "hsg245": "A3.6 vs D1.9",
            "yönler": {
                "rahatsız|ağır|sıcak|gözlük sisliyor|eldiven hassas": "→ A3.6: KKD rahatsızlık veriyor / D5.1: Ekipman seçimi",
                "alışkanlık|kimse kullanmıyor|norm|herkes": "→ D1.5: Sapmanın normalleşmesi",
                "yönetim|göz yumdu|gerek yok dedi": "→ D1.9: Yönetim toleransı",
            }
        },
        {
            "soru": "Çalışan KKD kullanımı için eğitim almış mıydı? Kullanım talimatı var mıydı?",
            "hsg245": "D3.1",
            "yönler": {
                "almadı|eğitim yok|hiç": "→ D3.1: KKD eğitimi verilmedi",
                "aldı ama|nasıl kullanılacağını bilmiyor": "→ D3.2: Eğitim içeriği yetersiz",
            }
        },
    ],

    # ── A1.x — PROSEDÜR İHLALİ ─────────────────────────────────────────────
    "A1.1": [
        {
            "soru": "Çalışan prosedürü biliyor muydu — yani eğitim almış mıydı ama yine de ihlal etti mi?",
            "hsg245": "D3.1 vs A1.1",
            "yönler": {
                "bilmiyordu|görmemişti|eğitim almadı": "→ D3.1: Prosedür eğitimi verilmedi — A1.1 DEĞİL",
                "biliyordu ama|eğitim almıştı|imza attı": "→ A1.1: Bilinçli ihlal",
            }
        },
        {
            "soru": "Bu ihlal daha önce de yapılıyor muydu — alışkanlık haline gelmiş miydi?",
            "hsg245": "D1.5",
            "yönler": {
                "hep böyle|alışkanlık|ilk değil|daha önce de": "→ D1.5: Sapmanın normalleşmesi",
                "ilk kez|istisnai|tek seferlik": "→ A1.1 bireysel ihlal",
            }
        },
        {
            "soru": "Yönetim bu ihlalleri biliyor muydu, göz mü yumuyordu?",
            "hsg245": "D1.9",
            "yönler": {
                "biliyordu|göz yumdu|uyarı gelmedi": "→ D1.9: Yönetim toleransı",
                "bilmiyordu|fark etmedi": "→ D1.1: Yetersiz gözetim",
            }
        },
    ],

    # ── B2.x — MEKANİK ARIZA ──────────────────────────────────────────────
    "B2.1": [
        {
            "soru": "Ekipmanın düzenli bakım planı var mıydı? Son bakım ne zaman yapılmıştı?",
            "hsg245": "D6.1",
            "yönler": {
                "plan yok|bakım yapılmıyor|hiç|kayıt yok": "→ D6.1: Bakım programı yok",
                "plan vardı ama|yapılmadı|gecikmeli": "→ D6.1: Bakım yapılmadı / kaynak eksikliği",
            }
        },
        {
            "soru": "Arıza önceden biliniyordu ama ekipman kullanılmaya devam etti mi?",
            "hsg245": "A2.3 vs D2.3",
            "yönler": {
                "biliyordu ama|raporlandı ama|devam etti|düzeltilmedi": "→ A2.3 + D2.3: Bilinen arıza rapor edilmedi/dikkate alınmadı",
                "bilmiyordu|ani arıza|görünmez": "→ D6.1: Bakım yetersizliği",
            }
        },
    ],

    # ── A4.x — DAYANIKLILIK / ERGONOMI ─────────────────────────────────────
    "A4.1": [
        {
            "soru": "Çalışan kaç saatlik vardiyadaydı? Fazla mesai var mıydı?",
            "hsg245": "D1.4 / C2.1",
            "yönler": {
                "12 saat|fazla mesai|uzun vardiya|yorgunluk": "→ C2.1: Yorgunluk + D1.4: Üretim baskısı",
                "normal|8 saat|standart": "→ A4.1 başka nedeni araştır",
            }
        },
    ],
}

# Eğer kod veritabanında yoksa, genel sorular kullan
GENEL_DISAMBIGUATION = [
    {
        "soru": "Bu olay için daha önce risk değerlendirmesi yapılmış mıydı? Tehlike belirlenmişti ama önlem alınmadı mıydı?",
        "hsg245": "D4.1 vs D4.2",
        "yönler": {
            "yapılmamış|hiç|analiz yok": "→ D4.1: Risk analizi yok",
            "yapıldı ama|önlem alınmadı|kağıtta kaldı": "→ D4.2: Kontroller uygulanmadı",
        }
    },
    {
        "soru": "Çalışan(lar) bu iş için eğitim almış mıydı? Eğitim yeterliydi ama prosedürü yine de ihlal etti mi?",
        "hsg245": "D3.1 vs A1.1",
        "yönler": {
            "eğitim almadı|yoktu|bilmiyordu": "→ D3.1: Eğitim eksikliği",
            "eğitim aldı ama|biliyordu ama|yine de ihlal": "→ A1.1 veya D1.9",
        }
    },
    {
        "soru": "Yönetim bu riski/problemi daha önce biliyor muydu? Üretim baskısı nedeniyle göz yumuldu mu?",
        "hsg245": "D1.9 vs D1.4",
        "yönler": {
            "biliyordu|göz yumdu": "→ D1.9: Yönetim toleransı",
            "üretim baskısı|zaman|teslim|yetiştir": "→ D1.4: Üretim baskısı",
        }
    },
]


def get_disambiguation_questions(cause_code: str) -> list[dict]:
    """
    Verilen immediate cause kodu için disambiguation sorularını döndür.
    Kod veritabanında yoksa genel soruları döndür.
    """
    # Önce tam kod eşleşmesi
    if cause_code in HSG245_DISAMBIGUATION:
        return HSG245_DISAMBIGUATION[cause_code]

    # Kategori prefix eşleşmesi (örn: "B4.3" → "B4.4" bulunursa, genel B4 yoksa genel kullan)
    prefix = cause_code[:2] if len(cause_code) >= 2 else ""
    for key in HSG245_DISAMBIGUATION:
        if key.startswith(prefix):
            return HSG245_DISAMBIGUATION[key]

    return GENEL_DISAMBIGUATION


def _hitl_use_barsel_disambiguation() -> bool:
    return (os.getenv("HITL_USE_BARSEL") or "1").strip().lower() not in (
        "0",
        "false",
        "no",
        "off",
    )


def _build_hsg_questions_for_causes(immediate_causes: list[dict]) -> list[dict]:
    """
    HSG245 bankası — HITL_USE_BARSEL=0 veya BARSEL boş dönerse kullanılır.
    """
    questions: list[dict[str, Any]] = []
    seen: set[str] = set()

    for cause in immediate_causes[:3]:
        code = cause.get("code", "")
        cause_desc = cause.get("cause_tr", code)
        cause_questions = get_disambiguation_questions(code)

        for q in cause_questions[:3]:
            soru_text = q["soru"]
            if soru_text not in seen:
                seen.add(soru_text)
                questions.append(
                    {
                        "code": code,
                        "cause_desc": cause_desc,
                        "soru": soru_text,
                        "hsg245": q["hsg245"],
                        "yönler": q.get("yönler", {}),
                    }
                )

    return questions[:8]


def build_questions_for_causes(
    immediate_causes: list[dict],
    incident_context: str = "",
) -> list[dict]:
    """
    Agent'ın bulduğu immediate causes için disambiguation sorularını derle.
    Her cause için max 3 soru alır, toplam 6-8 soruda tutmaya çalışır.
    """
    if _hitl_use_barsel_disambiguation():
        from agents.barsel_disambiguation_bank import build_barsel_questions_for_causes

        rows = build_barsel_questions_for_causes(
            immediate_causes,
            incident_context=incident_context,
        )
        if rows:
            return rows
    return _build_hsg_questions_for_causes(immediate_causes)


