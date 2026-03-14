"""
HSG245 5-Why Chatbot V2 — HITL + Agentic AI Entegrasyonu
=========================================================

FARK (v1'e göre):
  v1: Kullanıcı menüden Immediate Cause seçer → sabit 5 soru → keyword → öneri
  v2: Kullanıcı olayı anlatır → agent otomatik Immediate Cause bulur →
      agent bulgusuna göre derinleştirme soruları → agent tüm cevaplarla
      final D4.2 / D4.4 / D4.5 ... kök nedenini üretir

AKIŞ:
  "incident"         → Kullanıcı olayı yazar
  "initial_analysis" → (arka planda) OverviewAgent + AssessmentAgent çalışır,
                       RootCauseAgentV2 Immediate Cause'ları belirler
  "question_N"       → Bot agent bulgusuna göre disambiguation soruları sorar
  "final_analysis"   → Tüm cevaplarla RootCauseAgentV2 final 5-Why yapar
  "done"             → Sonuç + rapor yolu gösterilir

MİMARİ:
  • Kullanıcı Immediate Cause SEÇMEZ — agent buluyor
  • HybridInputProcessor eksik kategorileri tespit eder
  • HSG245_DISAMBIGUATION_QUESTIONS: B/A koduna göre D4.x / D3.x sorular
  • _append_hitl_answers() ile cevaplar agent prompt'una eklenir
  • Her seferinde farklı, spesifik kök nedenler üretilir
"""

import sys
import os
import threading
from typing import Any

import gradio as gr

# ── Path setup ──────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Dotenv ──────────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ── Agent imports ────────────────────────────────────────────────────────────
from agents.overview_agent import OverviewAgent
from agents.assessment_agent import AssessmentAgent
from agents.rootcause_agent_v2 import RootCauseAgentV2

try:
    from agents.skillbased_docx_agent import SkillBasedDocxAgent
    _DOCX_AVAILABLE = True
except Exception:
    _DOCX_AVAILABLE = False

# ── HITL imports ─────────────────────────────────────────────────────────────
from hitl_test.hybrid_input_processor import HybridInputProcessor
from hitl_test.question_engine import QuestionEngine

from gradio.components.chatbot import MessageDict


# ═══════════════════════════════════════════════════════════════════════════
# 1. HSG245 DISAMBİGUASYON SORU VERİTABANI
#    Her A/B kodu için → D4.x / D3.x / D1.x ayrımını sağlayan sorular
#    Bu sorular cevaplandığında agent D4.1 yerine D4.2/D4.4/D4.5 seçebilir.
# ═══════════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════════
# 2. YARDIMCI FONKSİYONLAR
# ═══════════════════════════════════════════════════════════════════════════

def _bot(content: str) -> MessageDict:
    return {"role": "assistant", "content": content}  # type: ignore[return-value]

def _user(content: str) -> MessageDict:
    return {"role": "user", "content": content}  # type: ignore[return-value]

def init_state() -> dict:
    return {
        # Akış adımı
        "step": "incident",  # incident | initial_analysis | question_N | final_analysis | done
        # Olay bilgisi
        "incident": "",
        # Ajan sonuçları
        "part1": None,
        "part2": None,
        # Immediate Causes (agent buldu)
        "immediate_causes": [],   # [{"code": "B4.4", "cause_tr": "..."}]
        # Disambiguation soruları
        "questions_list": [],  # Sorulacak soru listesi
        "current_q_idx": 0,    # Şu anki soru indeksi
        # Kullanıcı cevapları
        "qa_pairs": [],        # [{"code": "B4.4", "question": "...", "answer": "...", "hsg245": "..."}]
        # Final analiz sonuçları
        "final_rca": None,
        "report_path": None,
    }


def detect_direction(answer: str, yonler: dict) -> str:
    """Cevap metnindeki anahtar kelimelere göre yönlendirme tespit et."""
    answer_lower = answer.lower()
    for pattern, direction in yonler.items():
        for keyword in pattern.split("|"):
            if keyword.strip() in answer_lower:
                return direction
    return ""


def build_questions_for_causes(immediate_causes: list[dict]) -> list[dict]:
    """
    Agent'ın bulduğu immediate causes için disambiguation sorularını derle.
    Her cause için max 3 soru alır, toplam 6-8 soruda tutmaya çalışır.
    """
    questions = []
    seen = set()

    for cause in immediate_causes[:3]:  # Max 3 cause için soru
        code = cause.get("code", "")
        cause_desc = cause.get("cause_tr", code)
        cause_questions = get_disambiguation_questions(code)

        for q in cause_questions[:3]:  # Her cause'dan max 3 soru
            soru_text = q["soru"]
            if soru_text not in seen:
                seen.add(soru_text)
                questions.append({
                    "code": code,
                    "cause_desc": cause_desc,
                    "soru": soru_text,
                    "hsg245": q["hsg245"],
                    "yönler": q.get("yönler", {}),
                })

    # Maksimum 8 soru (chatbotun çok uzun olmaması için)
    return questions[:8]


# ═══════════════════════════════════════════════════════════════════════════
# 3. AGENT ÇAĞRI FONKSİYONLARI (BLOCKING — thread'de çalışır)
# ═══════════════════════════════════════════════════════════════════════════

def run_initial_analysis(incident_text: str) -> dict:
    """
    OverviewAgent + AssessmentAgent + RootCauseAgentV2 (sadece immediate causes)
    
    Returns:
        {"part1": ..., "part2": ..., "immediate_causes": [...], "error": str|None}
    """
    result = {"part1": None, "part2": None, "immediate_causes": [], "error": None}
    try:
        incident_data = {"description": incident_text}

        overview  = OverviewAgent()
        part1 = overview.process_initial_report(incident_data)
        result["part1"] = part1

        assessment = AssessmentAgent()
        part2 = assessment.assess_incident(part1, incident_data)
        result["part2"] = part2

        # RootCauseAgentV2'yi sadece Immediate Cause tespiti için kullan
        # (5-Why zinciri yapmadan)
        rca = RootCauseAgentV2()
        immediate_causes = rca._identify_immediate_causes_with_codes(
            rca._prepare_incident_summary(part1, part2, incident_data)
        )
        result["immediate_causes"] = immediate_causes or []

    except Exception as e:
        result["error"] = str(e)
        print(f"❌ Initial analysis error: {e}")

    return result


def run_final_analysis(state: dict) -> dict:
    """
    HITL cevaplarını kullanarak tam RootCauseAgentV2 analizi çalıştır.
    
    Returns:
        {"part3": ..., "report_path": str|None, "error": str|None}
    """
    result = {"part3": None, "report_path": None, "error": None}
    try:
        # HITL cevaplarını investigation_data formatına paketle
        investigation_data = _build_investigation_data(state)

        rca = RootCauseAgentV2()
        part3 = rca.analyze_root_causes(
            state["part1"],
            state["part2"],
            investigation_data,
        )
        result["part3"] = part3

        # DOCX raporu
        if _DOCX_AVAILABLE:
            try:
                full_data = {
                    "part1": state["part1"],
                    "part2": state["part2"],
                    "part3_rca": part3,
                    "docx_report": None,
                    "status": "investigation_complete",
                }
                docx_agent = SkillBasedDocxAgent()
                ref = (state["part1"] or {}).get("ref_no", "hitl_v2")
                out_path = f"outputs/{ref}_hitl_report.docx"
                report_path = docx_agent.generate_report(
                    investigation_data=full_data,
                    output_path=out_path,
                )
                result["report_path"] = report_path
            except Exception as de:
                print(f"⚠️ DOCX error (non-fatal): {de}")

    except Exception as e:
        result["error"] = str(e)
        print(f"❌ Final analysis error: {e}")

    return result


def _build_investigation_data(state: dict) -> dict:
    """
    Chatbot state'inden RootCauseAgentV2'ye gönderilecek veri paketini oluşturur.
    """
    qa_pairs = state.get("qa_pairs", [])
    why_answers = [
        {
            "why_level": i + 1,
            "question": qa["question"],
            "hsg245_focus": qa.get("hsg245", ""),
            "user_answer": qa["answer"],
            "suggested_direction": qa.get("direction", ""),
        }
        for i, qa in enumerate(qa_pairs)
    ]

    immediate_causes = state.get("immediate_causes", [])

    return {
        "description": state.get("incident", ""),
        "agent_immediate_causes": immediate_causes,
        # _append_hitl_answers() bu key'i okur:
        "five_why_answers": why_answers,
        "hitl_context": {
            "questions_asked": len(qa_pairs),
            "answers_collected": len(qa_pairs),
        },
    }


# ═══════════════════════════════════════════════════════════════════════════
# 4. SONUÇ FORMATLAMA
# ═══════════════════════════════════════════════════════════════════════════

def format_immediate_causes(immediate_causes: list[dict]) -> str:
    """Agent'ın bulduğu immediate causes'ları chatbot mesajı olarak formatla."""
    if not immediate_causes:
        return "⚠️ Immediate cause belirlenemedi — lütfen olayı daha ayrıntılı anlatın."

    lines = [
        "### 🔴 Tespit Edilen Doğrudan Nedenler (Agent Analizi)",
        "",
        "_HSG245 A/B kategori analizi tamamlandı:_",
        "",
    ]
    for i, cause in enumerate(immediate_causes, 1):
        code = cause.get("code", "?")
        cat  = cause.get("category_type", "")
        desc = cause.get("cause_tr", cause.get("cause_en", ""))
        cat_label = "🔵 Davranış" if cat == "A" else "🟡 Koşul" if cat == "B" else "⚪"
        lines.append(f"**{i}.** `{code}` {cat_label} — {desc}")

    return "\n".join(lines)


def format_final_result(state: dict, part3: dict) -> str:
    """Final RCA sonucunu chatbot mesajı olarak formatla."""
    branches = part3.get("analysis_branches", [])
    root_causes = part3.get("final_root_causes", [])

    lines = [
        "---",
        "## ✅ Kök Neden Analizi Tamamlandı",
        "",
    ]

    # Immediate Causes
    immediate_causes = state.get("immediate_causes", [])
    if immediate_causes:
        lines.append("### 🔴 Doğrudan Nedenler (Agent)")
        for c in immediate_causes:
            lines.append(f"- `{c.get('code','')}` — {c.get('cause_tr','')}")
        lines.append("")

    # 5-Why Dalları
    if branches:
        lines.append("### 🔗 5-Why Analiz Zincirleri")
        lines.append("")
        for branch in branches:
            imm = branch.get("immediate_cause", {})
            rc  = branch.get("root_cause", {})
            lines.append(f"#### Dal {branch.get('branch_number','')} — `{imm.get('code','')}` {imm.get('cause_tr','')}")
            lines.append("")

            whys = branch.get("why_chain", [])
            for why in whys:
                lvl = why.get("level", "?")
                q   = why.get("question", "")
                ans = why.get("answer", "")
                if q:
                    lines.append(f"**Why-{lvl}:** {q}")
                if ans:
                    lines.append(f"> _{ans}_")
                lines.append("")

            rc_code = rc.get("code", "")
            rc_desc = rc.get("cause_tr", rc.get("cause_en", ""))
            if rc_code:
                lines.append(f"🟣 **Kök Neden → `{rc_code}`** — {rc_desc}")
                lines.append("")

    # Final kök nedenler özeti
    if root_causes:
        lines.append("---")
        lines.append("### 🟣 Final Kök Nedenler (HSG245 D/C)")
        for rc in root_causes:
            code = rc.get("code", "")
            cat  = rc.get("category_type", "")
            desc = rc.get("cause_tr", rc.get("cause_en", ""))
            cat_label = "🟢 Kişisel" if cat == "C" else "🔷 Organizasyonel" if cat == "D" else ""
            lines.append(f"- `{code}` {cat_label} — {desc}")
        lines.append("")

    # Rapor yolu
    if state.get("report_path"):
        lines.append(f"📄 **Rapor:** `{state['report_path']}`")
        lines.append("")

    # HITL cevap özeti
    qa_pairs = state.get("qa_pairs", [])
    if qa_pairs:
        lines.append("---")
        lines.append("### 💬 Soruşturma Cevapları (HITL)")
        for i, qa in enumerate(qa_pairs, 1):
            lines.append(f"**S{i}:** {qa['question']}")
            lines.append(f"**C{i}:** _{qa['answer']}_")
            if qa.get("direction"):
                lines.append(f"🔀 _{qa['direction']}_")
            lines.append("")

    lines.append("---")
    lines.append("_⚠️ Bu analiz HSG245 standardına dayanır. Resmi rapor için uzman onayı gereklidir._")
    lines.append("")
    lines.append("🔄 **Yeni analiz için** `yeni` yazın veya **Temizle** butonuna basın.")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════
# 5. ANA CHATBOT FONKSİYONU
# ═══════════════════════════════════════════════════════════════════════════

def chat(user_msg: str, history: list, state: dict):
    """
    Ana Gradio chat handler.
    Her çağrıda tek bir adım ilerler, state güncellenmiş olarak döner.
    """
    user_msg = user_msg.strip()
    if not user_msg:
        return history, state, ""

    history = history + [_user(user_msg)]
    step = state["step"]

    # ── Herhangi bir aşamada sıfırla ──────────────────────────────────────
    if user_msg.lower() in ("yeni", "sıfırla", "reset", "yeniden", "baştan", "temizle"):
        state = init_state()
        history = [_bot(WELCOME_MSG)]
        return history, state, ""

    # ── ADIM 1: Olay açıklaması alındı ───────────────────────────────────
    if step == "incident":
        state["incident"] = user_msg
        state["step"] = "initial_analysis"

        history.append(_bot(
            "⏳ **Olay analiz ediliyor...**\n\n"
            "_OverviewAgent → AssessmentAgent → Immediate Cause tespiti çalışıyor..._\n\n"
            "_(Bu işlem 15–30 saniye sürebilir)_"
        ))

        # Ajan analizini çalıştır (blocking — Gradio'nun yield'siz versiyonu)
        analysis = run_initial_analysis(user_msg)

        if analysis["error"]:
            history.append(_bot(
                f"❌ **Analiz hatası:** {analysis['error']}\n\n"
                "Lütfen olayı tekrar anlatın veya `yeni` yazarak baştan başlayın."
            ))
            state["step"] = "incident"
            return history, state, ""

        state["part1"] = analysis["part1"]
        state["part2"] = analysis["part2"]
        state["immediate_causes"] = analysis["immediate_causes"]

        # Immediate causes mesajı
        ic_msg = format_immediate_causes(analysis["immediate_causes"])

        # Disambiguation sorularını oluştur
        questions = build_questions_for_causes(analysis["immediate_causes"])
        state["questions_list"] = questions
        state["current_q_idx"] = 0

        if not questions:
            # Sorumuz yoksa direkt final analiz
            history.append(_bot(ic_msg))
            history.append(_bot("⏳ Kök neden analizi başlatılıyor..."))
            final = run_final_analysis(state)
            if final["error"]:
                history.append(_bot(f"❌ Final analiz hatası: {final['error']}"))
            else:
                state["final_rca"] = final["part3"]
                state["report_path"] = final["report_path"]
                history.append(_bot(format_final_result(state, final["part3"])))
            state["step"] = "done"
            return history, state, ""

        # İlk soruyu hazırla
        q0 = questions[0]
        state["step"] = "question_0"

        intro = (
            f"{ic_msg}\n\n"
            "---\n\n"
            f"Kök nedeni daha kesin belirlemek için **{len(questions)} soruyu** "
            "cevaplamanızı isteyeceğim.\n\n"
            f"### Soru 1 / {len(questions)}\n\n"
            f"**{q0['soru']}**\n\n"
            f"_🔍 HSG245 odak: `{q0['hsg245']}`_\n\n"
            f"_💡 Kod: `{q0['code']}` — {q0['cause_desc']}_"
        )
        history.append(_bot(intro))
        return history, state, ""

    # ── ADIM 2-N: Sorular ─────────────────────────────────────────────────
    if step.startswith("question_"):
        q_idx = int(step.split("_")[1])
        questions = state["questions_list"]
        current_q = questions[q_idx]

        # Yön tespiti
        direction = detect_direction(user_msg, current_q.get("yönler", {}))

        # Cevabı kaydet
        state["qa_pairs"].append({
            "code": current_q["code"],
            "question": current_q["soru"],
            "answer": user_msg,
            "hsg245": current_q["hsg245"],
            "direction": direction,
        })

        dir_text = f"\n\n🔀 **Analiz yönü:** {direction}" if direction else ""

        next_idx = q_idx + 1
        if next_idx < len(questions):
            # Sonraki soru
            state["step"] = f"question_{next_idx}"
            nq = questions[next_idx]
            bot_msg = (
                f"{dir_text}\n\n---\n\n"
                f"### Soru {next_idx + 1} / {len(questions)}\n\n"
                f"**{nq['soru']}**\n\n"
                f"_🔍 HSG245 odak: `{nq['hsg245']}`_\n\n"
                f"_💡 Kod: `{nq['code']}` — {nq['cause_desc']}_"
            ).lstrip()
            history.append(_bot(bot_msg))
            return history, state, ""

        # Tüm sorular cevaplandı — final analiz
        state["step"] = "final_analysis"
        history.append(_bot(
            f"{dir_text}\n\n---\n\n"
            "✅ **Tüm soruşturma cevapları alındı.**\n\n"
            "⏳ **Final kök neden analizi başlatılıyor...**\n\n"
            f"_Toplanan {len(state['qa_pairs'])} cevap agent'a gönderiliyor. "
            "Bu işlem 30–60 saniye sürebilir..._"
        ))

        # Final analiz
        final = run_final_analysis(state)

        if final["error"]:
            history.append(_bot(
                f"❌ **Final analiz hatası:** {final['error']}\n\n"
                "`yeni` yazarak yeni analiz başlatabilirsiniz."
            ))
            state["step"] = "done"
            return history, state, ""

        state["final_rca"] = final["part3"]
        state["report_path"] = final["report_path"]
        state["step"] = "done"

        history.append(_bot(format_final_result(state, final["part3"])))
        return history, state, ""

    # ── DONE: Bitti ────────────────────────────────────────────────────────
    if step in ("done", "final_analysis"):
        history.append(_bot(
            "🔄 Yeni analiz başlatmak için `yeni` yazın veya **Temizle** butonuna basın."
        ))
        return history, state, ""

    # Beklenmedik durum
    return history, state, ""


def reset_chat(state):
    return [_bot(WELCOME_MSG)], init_state(), ""


# ═══════════════════════════════════════════════════════════════════════════
# 6. KARŞILAMA MESAJI
# ═══════════════════════════════════════════════════════════════════════════

WELCOME_MSG = """👋 Merhaba! Ben **HSG245 Kök Neden Analizi** asistanınım (v2 — Agentic AI).

Bu versiyon tam entegre çalışır:

1. **Siz** → Olayı anlatın _(kim, ne, nerede, nasıl)_
2. **Agent** → Immediate Cause'ları otomatik tespit eder _(siz kod seçmiyorsunuz)_
3. **Bot** → Agent bulgusuna göre derinleştirme soruları sorar _(D4.1 vs D4.2 vs D4.5...)_
4. **Agent** → Cevaplarınıza göre spesifik kök neden belirler _(jenerik D4.1 değil!)_

---

📝 **Başlamak için olayı anlatın:**
_(Kim, ne yaptı, nerede, ne sonuç oldu?)_

_Örnek: "Hasan Yıldız iskelede çalışırken 5 metreden düştü, sol bacağı kırıldı."_"""


# ═══════════════════════════════════════════════════════════════════════════
# 7. GRADIO ARAYÜZÜ
# ═══════════════════════════════════════════════════════════════════════════

with gr.Blocks(title="HSG245 — 5-Why v2 (Agentic HITL)") as demo:

    gr.HTML("""
    <div style="text-align:center; padding:20px 0 8px 0;">
      <h2 style="margin:0; color:#1e40af;">
        🔍 HSG245 — 5-Why Kök Neden Analizi
        <span style="font-size:14px; background:#dbeafe; color:#1e40af;
               padding:2px 8px; border-radius:12px; margin-left:8px;">v2 Agentic</span>
      </h2>
      <p style="color:#6b7280; margin:6px 0 0 0; font-size:13px;">
        Agent otomatik Immediate Cause bulur • HITL soruları kök nedeni hassaslaştırır
      </p>
    </div>
    """)

    state = gr.State(init_state())

    chatbot = gr.Chatbot(
        value=[_bot(WELCOME_MSG)],
        label="5-Why Analiz Asistanı",
        height=560,
        type="messages",
    )

    with gr.Row():
        msg_box = gr.Textbox(
            placeholder="Olayı anlat veya soruları cevapla...",
            label="",
            scale=8,
            container=False,
        )
        send_btn = gr.Button("Gönder ➤", variant="primary", scale=1)

    clear_btn = gr.Button("🗑 Temizle / Yeni Analiz", variant="secondary")

    gr.HTML("""
    <div style="margin-top:8px; padding:8px 16px; background:#f0f9ff;
         border-radius:6px; font-size:12px; color:#0369a1;">
      <strong>İpucu:</strong>
      Olayı detaylı anlattığınızda agent daha kesin immediate cause tespit eder.
      Soruları tam cümleyle cevaplayın — agent bu cevapları kullanarak
      D4.1 / D4.2 / D4.4 / D4.5 ayrımı yapar.
    </div>
    """)

    msg_box.submit(fn=chat, inputs=[msg_box, chatbot, state], outputs=[chatbot, state, msg_box])
    send_btn.click(fn=chat, inputs=[msg_box, chatbot, state], outputs=[chatbot, state, msg_box])
    clear_btn.click(fn=reset_chat, inputs=[state], outputs=[chatbot, state, msg_box])

    gr.HTML("""<p style="text-align:center; color:#9ca3af; font-size:11px; margin-top:8px;">
      HSG245 Knowledge Base • RootCauseAgentV2 • SkillBasedDocxAgent •
      HITL Disambiguation v2.0</p>""")


if __name__ == "__main__":
    print("🚀 HSG245 5-Why Chatbot v2 (Agentic HITL) başlatılıyor...")
    print("   Port: 7861")
    print("   V1 (gradio_chat_5why.py) → Port 7860'ta çalışmaya devam edebilir")
    demo.launch(server_name="127.0.0.1", server_port=7861, share=False, show_error=True)
