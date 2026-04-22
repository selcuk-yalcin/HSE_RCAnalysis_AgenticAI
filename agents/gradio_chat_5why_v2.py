"""
HSG245 5-Why Chatbot V2 — HITL + Agentic AI Entegrasyonu
=========================================================
Konum: agents/ (hitl_test/gradio_chat_5why_v2.py geriye dönük başlatıcı kullanır)

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
  • Disambiguation soruları: agents.hitl_disambiguation_bank
  • _append_hitl_answers() ile cevaplar agent prompt'una eklenir
  • Her seferinde farklı, spesifik kök nedenler üretilir
"""

import sys
import os
import threading
from typing import Any

import gradio as gr

# ── Path setup ──────────────────────────────────────────────────────────────
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)

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
from agents.hitl_disambiguation_bank import build_questions_for_causes

try:
    from agents.skillbased_docx_agent import SkillBasedDocxAgent
    _DOCX_AVAILABLE = True
except Exception:
    _DOCX_AVAILABLE = False

from gradio.components.chatbot import MessageDict



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
