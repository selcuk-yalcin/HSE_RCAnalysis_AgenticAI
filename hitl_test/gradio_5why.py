"""
5-Why Gradio Arayüzü — HSG245 Knowledge Base Tabanlı Adım Adım Kök Neden Analizi

AKIŞ:
  Adım 1 → Olay açıklaması + Immediate Cause seçimi
  Adım 2-6 → Why-1'den Why-5'e kadar sıralı sorular
  Her adımda: cevaba göre yönlendirme ve olası kodlar gösterilir
  Son ekran → Özet + tespit edilen kök nedenlere doğru giden yol haritası
"""

import sys
import os
import json
import gradio as gr

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hitl_test.five_why_engine import (
    get_five_why_questions,
    get_immediate_cause_list,
    detect_branch_from_answer,
    IMMEDIATE_CAUSES,
)

# ─────────────────────────────────────────────────────────────
# STATE — her session için tutulan veri
# ─────────────────────────────────────────────────────────────
def empty_state():
    return {
        "incident": "",
        "immediate_cause_code": "",
        "why_questions": [],      # 5 soru objesi
        "why_answers": [],        # kullanıcı cevapları
        "why_directions": [],     # her sorudan çıkan yönlendirme metni
        "current_why": 0,         # 0-based index (0 = Why-1)
    }

# ─────────────────────────────────────────────────────────────
# YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────────────────────────
def parse_code_from_selection(selection: str) -> str:
    """'A2.6 — açıklama' → 'A2.6'"""
    return selection.split(" — ")[0].strip() if selection else ""


def build_progress_html(state: dict) -> str:
    """Üst ilerleme çubuğunu oluştur"""
    current = state["current_why"]
    steps = ["Why-1", "Why-2", "Why-3", "Why-4", "Why-5", "Özet"]
    html = '<div style="display:flex; gap:8px; margin-bottom:12px; flex-wrap:wrap;">'
    for i, s in enumerate(steps):
        if i < current:
            color = "#22c55e"   # tamamlandı - yeşil
            text_color = "white"
        elif i == current:
            color = "#3b82f6"   # aktif - mavi
            text_color = "white"
        else:
            color = "#e5e7eb"   # bekliyor - gri
            text_color = "#6b7280"
        html += (
            f'<div style="background:{color};color:{text_color};padding:4px 12px;'
            f'border-radius:20px;font-size:13px;font-weight:600;">{s}</div>'
        )
    html += '</div>'
    return html


def build_answer_history_html(state: dict) -> str:
    """Geçmiş cevapları göster"""
    if not state["why_answers"]:
        return ""
    html = '<div style="border:1px solid #e5e7eb; border-radius:8px; padding:12px; margin-bottom:12px;">'
    html += '<p style="font-weight:700; margin:0 0 8px 0; color:#374151;">📋 Önceki Cevaplar</p>'
    for i, (ans, direction) in enumerate(zip(state["why_answers"], state["why_directions"])):
        q = state["why_questions"][i]
        html += f'<div style="margin-bottom:8px; padding:8px; background:#f9fafb; border-radius:6px;">'
        html += f'<p style="margin:0; font-size:13px; color:#6b7280;"><b>Why-{i+1}:</b> {q["soru"]}</p>'
        html += f'<p style="margin:4px 0 0 0; font-size:14px; color:#111827;">💬 {ans}</p>'
        if direction:
            html += f'<p style="margin:4px 0 0 0; font-size:13px; color:#7c3aed;">🔀 {direction}</p>'
        html += '</div>'
    html += '</div>'
    return html


def build_summary(state: dict) -> str:
    """Analiz özeti HTML"""
    code = state["immediate_cause_code"]
    desc = IMMEDIATE_CAUSES.get(code, "")

    # Tüm yönlendirmeleri topla
    all_directions = [d for d in state["why_directions"] if d]
    root_causes = []
    for d in all_directions:
        parts = d.replace("→", "").strip().split("veya")
        for p in parts:
            p = p.strip()
            if p and p not in root_causes:
                root_causes.append(p)

    html = '<div style="background:#f0fdf4; border:1px solid #86efac; border-radius:10px; padding:16px;">'
    html += '<h3 style="color:#166534; margin:0 0 12px 0;">✅ 5-Why Analizi Tamamlandı</h3>'

    html += f'<p><b>🔴 Immediate Cause:</b> <code>{code}</code> — {desc}</p>'

    html += '<p><b>🔍 Why Soruları ve Cevaplar:</b></p><ol>'
    for i, (q, a) in enumerate(zip(state["why_questions"], state["why_answers"])):
        html += f'<li style="margin-bottom:6px;"><b>Why-{i+1}:</b> {q["soru"]}<br>→ <em>{a}</em></li>'
    html += '</ol>'

    if root_causes:
        html += '<p><b>🟣 Tespit Edilen Olası Kök Nedenler (HSG245):</b></p><ul>'
        for rc in root_causes:
            html += f'<li style="color:#7c3aed;">{rc}</li>'
        html += '</ul>'
        html += '<p style="font-size:13px; color:#6b7280;">⚠️ Bu kodlar mevcut cevaplara göre önerilerdir. Tam onay için ek araştırma gerekebilir.</p>'
    else:
        html += '<p style="color:#6b7280;"><em>Cevaplardan belirgin bir kök neden yönlendirmesi çıkmadı. Cevapları gözden geçirin.</em></p>'

    # JSON export
    export_data = {
        "immediate_cause": code,
        "incident": state["incident"],
        "why_chain": [
            {
                "why": i + 1,
                "question": q["soru"],
                "answer": a,
                "hsg245_focus": q["hsg245"],
                "direction": state["why_directions"][i] if i < len(state["why_directions"]) else "",
            }
            for i, (q, a) in enumerate(zip(state["why_questions"], state["why_answers"]))
        ],
        "suggested_root_causes": root_causes,
    }
    html += '<details style="margin-top:12px;"><summary style="cursor:pointer; color:#3b82f6;">📄 JSON Çıktısını Gör</summary>'
    html += f'<pre style="background:#1e293b; color:#e2e8f0; padding:12px; border-radius:6px; overflow:auto; font-size:12px;">{json.dumps(export_data, ensure_ascii=False, indent=2)}</pre>'
    html += '</details>'
    html += '</div>'
    return html


# ─────────────────────────────────────────────────────────────
# GRADIO CALLBACK FONKSİYONLARI
# ─────────────────────────────────────────────────────────────

def start_analysis(incident_text: str, cause_selection: str, state: dict):
    """
    Adım 1: Olay açıklaması + Immediate Cause seçimi → Why-1'i göster
    """
    if not incident_text.strip():
        return (
            state,
            gr.update(visible=True),   # start panel
            gr.update(visible=False),  # why panel
            gr.update(visible=False),  # summary panel
            "⚠️ Lütfen olay açıklaması giriniz.",
            "", "", "", "", "",
        )
    if not cause_selection:
        return (
            state,
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
            "⚠️ Lütfen bir Immediate Cause seçiniz.",
            "", "", "", "", "",
        )

    code = parse_code_from_selection(cause_selection)
    questions = get_five_why_questions(code)

    new_state = empty_state()
    new_state["incident"] = incident_text
    new_state["immediate_cause_code"] = code
    new_state["why_questions"] = questions
    new_state["current_why"] = 0

    q = questions[0]
    progress = build_progress_html(new_state)
    question_text = f"**Why-1 / 5**\n\n{q['soru']}"
    hsg245_hint = f"🔍 **HSG245 Odak:** `{q['hsg245']}`"
    history_html = ""

    return (
        new_state,
        gr.update(visible=False),   # start panel
        gr.update(visible=True),    # why panel
        gr.update(visible=False),   # summary panel
        "",
        progress,
        question_text,
        hsg245_hint,
        history_html,
        "",   # cevap alanı temizle
    )


def submit_answer(answer: str, state: dict):
    """
    Why-N cevabı → yönlendirme göster → Why-N+1'e geç veya özeti aç
    """
    if not answer.strip():
        q = state["why_questions"][state["current_why"]]
        progress = build_progress_html(state)
        question_text = f"**Why-{state['current_why']+1} / 5**\n\n{q['soru']}"
        hsg245_hint = f"🔍 **HSG245 Odak:** `{q['hsg245']}`"
        history_html = build_answer_history_html(state)
        return (
            state,
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=False),
            progress,
            question_text,
            hsg245_hint,
            history_html,
            "⚠️ Lütfen bir cevap yazınız.",
            "",
        )

    current = state["current_why"]
    q = state["why_questions"][current]
    direction = detect_branch_from_answer(answer, q.get("yönler", {}))

    state["why_answers"].append(answer)
    state["why_directions"].append(direction)
    state["current_why"] += 1

    # Tüm 5 soru tamamlandı mı?
    if state["current_why"] >= len(state["why_questions"]):
        summary_html = build_summary(state)
        state["current_why"] = len(state["why_questions"])   # progress göstergesi için
        progress = build_progress_html(state)
        return (
            state,
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True, value=summary_html),
            progress,
            "",
            "",
            "",
            "",
            "",
        )

    # Sonraki soruya geç
    next_q = state["why_questions"][state["current_why"]]
    progress = build_progress_html(state)
    question_text = f"**Why-{state['current_why']+1} / 5**\n\n{next_q['soru']}"
    hsg245_hint = f"🔍 **HSG245 Odak:** `{next_q['hsg245']}`"
    history_html = build_answer_history_html(state)

    direction_html = ""
    if direction:
        direction_html = f"**🔀 Yönlendirme:** {direction}"

    return (
        state,
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(visible=False),
        progress,
        question_text,
        hsg245_hint,
        history_html,
        direction_html,
        "",   # cevap kutusunu temizle
    )


def reset_all(state: dict):
    """Sıfırla ve başa dön"""
    return (
        empty_state(),
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=False),
        "",
        "", "", "", "", "",
    )


# ─────────────────────────────────────────────────────────────
# GRADIO ARAYÜZ
# ─────────────────────────────────────────────────────────────
CAUSE_LIST = get_immediate_cause_list()

with gr.Blocks(title="HSG245 — 5-Why Kök Neden Analizi") as demo:

    state = gr.State(empty_state())

    # ── Başlık ─────────────────────────────────────────────
    gr.HTML("""
    <div style="text-align:center; padding:20px 0 10px 0;">
      <h1 style="margin:0; color:#1e40af; font-size:26px;">
        🔍 HSG245 — 5-Why Kök Neden Analizi
      </h1>
      <p style="color:#6b7280; margin:6px 0 0 0; font-size:14px;">
        Immediate Cause seçin → Adım adım derinleşen sorularla kök nedene ulaşın
      </p>
    </div>
    """)

    # ── İlerleme çubuğu (her panelde görünür) ──────────────
    progress_bar = gr.HTML("")

    # ── PANEL 1: Başlangıç ─────────────────────────────────
    with gr.Group(visible=True) as start_panel:
        gr.Markdown("### 📝 Adım 1 — Olay Açıklaması ve Immediate Cause Seçimi")
        incident_input = gr.Textbox(
            label="Olay açıklaması",
            placeholder="Örnek: İnşaat sahasında forklift yükü max kapasitesinin üzerinde taşırken devrildi, sürücü yaralandı.",
            lines=4,
        )
        cause_dropdown = gr.Dropdown(
            choices=CAUSE_LIST,
            label="Immediate Cause (İlk Görünür Neden) — hangisi en iyi tanımlıyor?",
            info="A = Davranışlar, B = Koşullar. Sahadan topladığınız bilgiye göre seçin.",
        )
        start_error = gr.Markdown("")
        start_btn = gr.Button("🚀 5-Why Analizini Başlat", variant="primary", size="lg")

    # ── PANEL 2: Why soruları ──────────────────────────────
    with gr.Group(visible=False) as why_panel:
        gr.Markdown("### 🧐 Adım 2-6 — Derinleştirici Sorular")
        history_html = gr.HTML("")
        question_md = gr.Markdown("", elem_classes=["question-box"])
        hsg245_hint_md = gr.Markdown("")
        direction_md = gr.Markdown("")
        answer_input = gr.Textbox(
            label="Cevabınız",
            placeholder="Bulgu veya gözleminizi yazın...",
            lines=3,
        )
        why_error = gr.Markdown("")
        with gr.Row():
            submit_btn = gr.Button("➡️ Cevabı Kaydet & Devam Et", variant="primary")
            reset_btn_why = gr.Button("🔄 Sıfırla", variant="secondary")

    # ── PANEL 3: Özet ─────────────────────────────────────
    with gr.Group(visible=False) as summary_panel:
        summary_html_comp = gr.HTML("")
        with gr.Row():
            reset_btn_sum = gr.Button("🔄 Yeni Analiz Başlat", variant="primary")

    # ─────────────────────────────────────────────────────
    # Ortak çıktı listesi
    # (state, start_panel, why_panel, summary_panel,
    #  start_error/direction_md/why_error,
    #  progress_bar, question_md, hsg245_hint_md,
    #  history_html, answer_input)
    # ─────────────────────────────────────────────────────
    OUTPUTS = [
        state,
        start_panel,
        why_panel,
        summary_panel,
        start_error,
        progress_bar,
        question_md,
        hsg245_hint_md,
        history_html,
        answer_input,
    ]

    start_btn.click(
        fn=start_analysis,
        inputs=[incident_input, cause_dropdown, state],
        outputs=OUTPUTS,
    )

    # submit_btn için summary_html_comp + direction_md ayrı handle
    WHY_OUTPUTS = [
        state,
        start_panel,
        why_panel,
        summary_panel,
        progress_bar,
        question_md,
        hsg245_hint_md,
        history_html,
        direction_md,
        answer_input,
    ]

    # start_btn için çıktılar biraz farklı (start_error yerine direction_md yok)
    # submit'in kendi çıktı listesi:
    submit_btn.click(
        fn=submit_answer,
        inputs=[answer_input, state],
        outputs=WHY_OUTPUTS,
    )

    # summary_panel'e geçişte summary_html_comp güncellenmesi
    # submit_answer'dan dönen why_panel update(value=...) içinde summary zaten var
    # ama summary_html_comp ayrı component — onu da güncelleyelim:
    def submit_with_summary(answer, state):
        results = submit_answer(answer, state)
        # results[3] = summary_panel update
        # Eğer summary varsa value'sunu summary_html_comp'a da ver
        summary_update = results[3]
        summary_val = summary_update.get("value", "") if hasattr(summary_update, "get") else ""
        return results + (summary_val,)

    # Bunu tekrar bağlamak yerine, summary_panel'e direkt value verdiğimiz için
    # summary_html_comp'u summary_panel içine koyduğumuz HTML componenti olarak kullanıyoruz.
    # submit_btn zaten why_panel ve summary_panel'i update ediyor.
    # summary_html_comp = summary_panel içindeki gr.HTML; tekrar bağlamaya gerek yok.

    def reset_fn(state):
        return (
            empty_state(),
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(value=""),   # start_error
            gr.update(value=""),   # progress_bar
            gr.update(value=""),   # question_md
            gr.update(value=""),   # hsg245_hint_md
            gr.update(value=""),   # history_html
            gr.update(value=""),   # answer_input
        )

    reset_btn_why.click(fn=reset_fn, inputs=[state], outputs=OUTPUTS)
    reset_btn_sum.click(fn=reset_fn, inputs=[state], outputs=OUTPUTS)

    gr.HTML("""
    <div style="text-align:center; color:#9ca3af; font-size:12px; padding:16px 0 8px 0;">
      HSG245 Knowledge Base — 5-Why Engine v1.0 | Her olayda dinamik branching
    </div>
    """)

if __name__ == "__main__":
    print("🚀 Gradio 5-Why Arayüzü başlatılıyor...")
    demo.launch(
        server_name="127.0.0.1",
        share=False,
        show_error=True,
    )
