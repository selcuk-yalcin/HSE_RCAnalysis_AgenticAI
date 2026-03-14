"""
HSG245 5-Why Chatbot — Sohbet Tarzı Gradio Arayüzü

Akış:
  Bot önce olayı sorar
  Sonra Immediate Cause listesini gösterir, kullanıcı numara yazar
  Ardından Why-1'den Why-5'e kadar sırayla sorar
  Her cevaptan sonra yönlendirme gösterir
  En son özet ve kök neden kodlarını verir
"""

import sys
import os
from typing import Any
import gradio as gr

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hitl_test.five_why_engine import (
    get_five_why_questions,
    detect_branch_from_answer,
    IMMEDIATE_CAUSES,
)

# ── Sabit mesajlar ────────────────────────────────────────────────

WELCOME = """👋 Merhaba! Ben HSG245 tabanlı **5-Why Kök Neden Analizi** asistanınım.

Bir iş kazasını veya güvensiz olayı adım adım analiz ederek kök nedenine ulaşmanıza yardımcı olacağım.

📝 **Başlamak için olayı kısaca anlatın:**
_(Kim, ne yaptı, nerede, sonucu ne oldu?)_"""

def build_cause_menu() -> str:
    lines = ["**Immediate Cause'u seçin — aşağıdan numarasını yazın:**\n"]
    lines.append("_A kodları = Davranışlar &nbsp;|&nbsp; B kodları = Koşullar_\n")
    for i, (code, desc) in enumerate(IMMEDIATE_CAUSES.items(), 1):
        lines.append(f"**{i:>2}.** `{code}` — {desc}")
    return "\n".join(lines)

CAUSE_MENU = build_cause_menu()
CAUSE_KEYS = list(IMMEDIATE_CAUSES.keys())

# ── State yönetimi ────────────────────────────────────────────────
# state dict:
#   step: "incident" | "cause" | "why_N" (N=1..5) | "done"
#   incident: str
#   cause_code: str
#   questions: list
#   answers: list
#   directions: list

from gradio.components.chatbot import MessageDict

def _bot(content: str) -> MessageDict:
    return {"role": "assistant", "content": content}  # type: ignore[return-value]

def _user(content: str) -> MessageDict:
    return {"role": "user", "content": content}  # type: ignore[return-value]

def init_state():
    return {
        "step": "incident",
        "incident": "",
        "cause_code": "",
        "questions": [],
        "answers": [],
        "directions": [],
    }

def build_summary(state: dict) -> str:
    code = state["cause_code"]
    desc = IMMEDIATE_CAUSES.get(code, "")
    questions = state["questions"]
    answers = state["answers"]
    directions = state["directions"]

    lines = [
        "---",
        "## ✅ 5-Why Analizi Tamamlandı",
        "",
        f"🔴 **Immediate Cause:** `{code}` — {desc}",
        f"📋 **Olay:** {state['incident']}",
        "",
        "### Why Zinciri",
    ]
    for i, (q, a, d) in enumerate(zip(questions, answers, directions), 1):
        lines.append(f"**Why-{i}:** {q['soru']}")
        lines.append(f"→ _{a}_")
        if d:
            lines.append(f"🔀 {d}")
        lines.append("")

    all_dir = [d for d in directions if d]
    root_causes = []
    for d in all_dir:
        for part in d.replace("→", "").split("veya"):
            p = part.strip()
            if p and p not in root_causes:
                root_causes.append(p)

    if root_causes:
        lines.append("### 🟣 Tespit Edilen Olası Kök Nedenler (HSG245)")
        for rc in root_causes:
            lines.append(f"- {rc}")
        lines.append("")

    lines.append("---")
    lines.append("_⚠️ Bu kodlar cevaplara göre önerilerdir. Tam onay için ek araştırma gerekebilir._")
    lines.append("")
    lines.append("🔄 **Yeni analiz için** `yeni` yazın veya **Temizle** butonuna basın.")
    return "\n".join(lines)


# ── Ana chatbot fonksiyonu ────────────────────────────────────────

def chat(user_msg: str, history: list, state: dict):
    user_msg = user_msg.strip()
    if not user_msg:
        return history, state, ""

    # history'ye kullanıcı mesajını ekle
    history = history + [_user(user_msg)]
    step = state["step"]

    # Herhangi bir aşamada "yeni" yazılırsa sıfırla
    if user_msg.lower() in ("yeni", "sıfırla", "reset", "yeniden", "baştan"):
        state = init_state()
        history = [_bot(WELCOME)]
        return history, state, ""

    # ── ADIM 1: Olay açıklaması ───────────────────────────────
    if step == "incident":
        state["incident"] = user_msg
        state["step"] = "cause"
        history.append(_bot(CAUSE_MENU))
        return history, state, ""

    # ── ADIM 2: Immediate Cause seçimi ───────────────────────
    if step == "cause":
        try:
            idx = int(user_msg) - 1
            if not (0 <= idx < len(CAUSE_KEYS)):
                raise ValueError
        except ValueError:
            history.append(_bot(f"⚠️ Lütfen **1 ile {len(CAUSE_KEYS)}** arasında bir numara girin."))
            return history, state, ""

        code = CAUSE_KEYS[idx]
        desc = IMMEDIATE_CAUSES[code]
        state["cause_code"] = code
        state["questions"] = get_five_why_questions(code)
        state["answers"] = []
        state["directions"] = []
        state["step"] = "why_1"

        q = state["questions"][0]
        bot_msg = (
            f"✔ Seçildi: **`{code}`** — {desc}\n\n---\n\n"
            f"### Why-1 / 5\n\n**{q['soru']}**\n\n"
            f"_🔍 HSG245 odak: `{q['hsg245']}`_"
        )
        history.append(_bot(bot_msg))
        return history, state, ""

    # ── ADIM 3-7: Why soruları ────────────────────────────────
    if step.startswith("why_"):
        why_num = int(step.split("_")[1])
        idx = why_num - 1

        questions = state["questions"]
        q = questions[idx]

        direction = detect_branch_from_answer(user_msg, q.get("yönler", {}))
        state["answers"].append(user_msg)
        state["directions"].append(direction)

        dir_text = f"\n\n🔀 **Yönlendirme:** {direction}" if direction else ""

        next_why = why_num + 1
        if next_why <= len(questions):
            state["step"] = f"why_{next_why}"
            nq = questions[next_why - 1]
            bot_msg = (
                f"{dir_text}\n\n---\n\n"
                f"### Why-{next_why} / {len(questions)}\n\n"
                f"**{nq['soru']}**\n\n"
                f"_🔍 HSG245 odak: `{nq['hsg245']}`_"
            ).lstrip()
        else:
            state["step"] = "done"
            bot_msg = (dir_text + "\n\n" + build_summary(state)).lstrip()

        history.append(_bot(bot_msg))
        return history, state, ""

    # ── DONE: Bitti, yeni analiz bekle ────────────────────────
    if step == "done":
        history.append(_bot("🔄 Yeni analiz başlatmak için `yeni` yazın veya **Temizle** butonuna basın."))
        return history, state, ""

    return history, state, ""


def reset_chat(state):
    return [_bot(WELCOME)], init_state(), ""


# ── Gradio Arayüzü ────────────────────────────────────────────────

with gr.Blocks(title="HSG245 — 5-Why Chatbot") as demo:

    gr.HTML("""
    <div style="text-align:center; padding:16px 0 4px 0;">
      <h2 style="margin:0; color:#1e40af;">🔍 HSG245 — 5-Why Kök Neden Analizi</h2>
      <p style="color:#6b7280; margin:4px 0 0 0; font-size:13px;">
        Sohbet tarzı adım adım kök neden tespiti
      </p>
    </div>
    """)

    state = gr.State(init_state())

    chatbot = gr.Chatbot(
        value=[_bot(WELCOME)],
        label="5-Why Analiz Asistanı",
        height=520,
    )

    with gr.Row():
        msg_box = gr.Textbox(
            placeholder="Olayı anlat, numara seç veya cevabını yaz...",
            label="",
            scale=8,
            container=False,
        )
        send_btn = gr.Button("Gönder ➤", variant="primary", scale=1)

    clear_btn = gr.Button("🗑 Temizle / Yeni Analiz", variant="secondary")

    msg_box.submit(fn=chat, inputs=[msg_box, chatbot, state], outputs=[chatbot, state, msg_box])
    send_btn.click(fn=chat, inputs=[msg_box, chatbot, state], outputs=[chatbot, state, msg_box])
    clear_btn.click(fn=reset_chat, inputs=[state], outputs=[chatbot, state, msg_box])

    gr.HTML("""<p style="text-align:center;color:#9ca3af;font-size:11px;margin-top:8px;">
      HSG245 Knowledge Base • 5-Why Engine v1.0 • Her olayda dinamik branching</p>""")


if __name__ == "__main__":
    print("🚀 HSG245 5-Why Chatbot başlatılıyor...")
    demo.launch(server_name="127.0.0.1", share=False, show_error=True)
