"""
Gradio Test Arayüzü - HITL Sistemi
Test versiyonu - Ana sistemi değiştirmez
"""

import gradio as gr
import sys
import os

# Ana proje klasörünü path'e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hybrid_input_processor import HybridInputProcessor
from question_engine import QuestionEngine


# Global state
state = {
    "incident_text": "",
    "input_level": None,
    "missing_info": [],
    "current_question": 0,
    "answers": {},
    "generated_questions": [],
}

processor = HybridInputProcessor()
question_engine = QuestionEngine()


def analyze_incident(incident_text):
    """Olay girişini analiz eder ve HSG245'e göre sorular üretir"""
    if not incident_text.strip():
        return "❌ Lütfen olay açıklaması girin!"
    
    level, details = processor.detect_input_level(incident_text)
    
    state["incident_text"] = incident_text
    state["input_level"] = level
    state["missing_info"] = details["missing"]
    
    # HSG245 entegreli sorular üret
    questions = question_engine.generate_questions_for_missing_categories(details["missing"])
    state["generated_questions"] = questions
    
    # Sonuç raporu
    result = f"""
## 📊 Analiz Sonucu

**Girdi Seviyesi:** Level {level} {'(Detaylı ✅)' if level == 1 else '(Orta 🟡)' if level == 2 else '(Minimal ⚠️)'}

**Detay Puanı:** {details['detail_score']}/13

**Mevcut Bilgiler:**
{', '.join(details['present']) if details['present'] else 'Yok'}

**Eksik Bilgiler:**
{', '.join(details['missing']) if details['missing'] else 'Yok - Tüm bilgiler mevcut!'}

---

"""
    
    if level == 1:
        result += """
### ✅ Yeterli Detay Mevcut!

Direkt kök neden analizine geçebiliriz.

**Sonraki Adım:** TAB 3'e geçin (Kök Neden Analizi)
"""
    elif level == 2:
        result += f"""
### 🔍 Eksik Bilgi Tespiti

{len(details['missing'])} kategori için sorgulama yapılacak:
{chr(10).join(['- ' + cat for cat in details['missing']])}

**HSG245 Bağlantılı Sorular:** {len(questions)} soru hazır

**Sonraki Adım:** TAB 2'ye geçin (Sorgulama)
"""
    else:
        result += f"""
### ❓ Detaylı Sorgulama Gerekli

{len(details['missing'])} kategori için detaylı sorular soracağım.

**HSG245 Bağlantılı Sorular:** {len(questions)} soru hazır

**Öneri:** Daha fazla bilgi ekleyebilir veya TAB 2'de soruları yanıtlayabilirsiniz.
"""
    
    # Soruları da ekle
    if questions:
        result += "\n\n### 📝 Üretilen Sorular (HSG245 Entegreli):\n\n"
        for i, q in enumerate(questions[:5], 1):  # İlk 5 soruyu göster
            required_mark = "🔴" if q["required"] else "⚪"
            result += f"{i}. {required_mark} **[{q['category'].upper()}]** {q['question']}\n"
            result += f"   *HSG245 Kodları: {q['hsg245_codes']}*\n\n"
        
        if len(questions) > 5:
            result += f"\n*... ve {len(questions) - 5} soru daha (TAB 2'de tümünü görebilirsiniz)*\n"
    
    return result


def generate_sample_data(incident_type):
    """Örnek olay verisi üretir"""
    samples = {
        "Minimal (Forklift)": "Forklift geri manevra yaparken yaya yolundaki çalışana çarptı. Çalışan ayağından yaralandı.",
        
        "Orta (Elektrik)": """Bakım teknisyeni elektrik panosunda çalışırken 380V akımına kapıldı.
        
ETKİLENEN: Kemal Arslan, 29 yaş, 4 yıl deneyim
YARALANMA: Elektrik çarpması, 2. derece yanık
İHLALLER: LOTO uygulanmadı, elektrik enerjisi kesilmedi
""",
        
        "Detaylı (Düşme)": """OLAY RAPORU - YÜKSEKTEN DÜŞME

Tarih: 18 Şubat 2026, Saat: 10:35
Lokasyon: İnşaat Şantiyesi - 4. Kat İskele

OLAY KRONOLOJİSİ:
- 10:20 - İskele montajına başlandı
- 10:35 - İşçi 6 metre yükseklikten düştü
- 10:42 - İlk yardım uygulandı
- 10:55 - Ambulans geldi

GÜVENLİK İHLALLERİ:
✗ Emniyet kemeri kullanılmadı
✗ Korkuluk montajı tamamlanmamış
✗ Güvenlik ağı yoktu

TANIK BEYANI:
Ali Demir: "Herkes kemersiz çalışıyordu, amir hızlı bitirin dedi"

YÖNETİM FAKTÖRÜ:
Proje 3 hafta gecikmiş, müşteri baskısı var
"""
    }
    
    return samples.get(incident_type, "")


# Gradio Arayüzü
with gr.Blocks(title="HITL Test - HSE Analiz", theme=gr.themes.Soft()) as app:
    
    gr.Markdown("""
    # 🔍 Human-in-the-Loop Test Arayüzü
    
    **HSE Kök Neden Analizi - Hibrit Girdi Sistemi**
    
    ⚠️ Bu bir **TEST** arayüzüdür. Ana sistem dosyalarını değiştirmez.
    """)
    
    with gr.Tab("1️⃣ Olay Girişi"):
        gr.Markdown("## Olayı Açıklayın")
        
        with gr.Row():
            sample_dropdown = gr.Dropdown(
                choices=["Minimal (Forklift)", "Orta (Elektrik)", "Detaylı (Düşme)"],
                label="Örnek Veri Yükle",
                value=None
            )
        
        incident_input = gr.Textbox(
            label="Olay Açıklaması",
            placeholder="Olayı buraya yazın veya yukarıdan örnek seçin...",
            lines=15
        )
        
        with gr.Row():
            clear_btn = gr.Button("🗑️ Temizle", variant="secondary")
            analyze_btn = gr.Button("🔍 Analiz Et", variant="primary", scale=2)
        
        analysis_output = gr.Markdown()
        
        # Event handlers
        sample_dropdown.change(
            generate_sample_data,
            inputs=sample_dropdown,
            outputs=incident_input
        )
        
        clear_btn.click(
            lambda: "",
            outputs=incident_input
        )
        
        analyze_btn.click(
            analyze_incident,
            inputs=incident_input,
            outputs=analysis_output
        )
    
    with gr.Tab("2️⃣ Sorgulama"):
        gr.Markdown("## 📋 HSG245 Entegreli Sorular")
        gr.Markdown("*Knowledge Base'den üretilen, kök neden kodlarına bağlı sorular*")
        
        with gr.Row():
            gr.Markdown(f"""
            **Mevcut Durum:**
            - Olay girişi: {'✅ Tamamlandı' if state['incident_text'] else '❌ Henüz yapılmadı'}
            - Girdi Seviyesi: {f"Level {state['input_level']}" if state['input_level'] else 'Belirlenmedi'}
            - Eksik Kategori: {len(state['missing_info'])}
            - Üretilen Soru: {len(state['generated_questions'])}
            """)
        
        questions_display = gr.Markdown()
        
        with gr.Row():
            current_q_index = gr.Number(value=0, label="Soru #", visible=False)
            current_question = gr.Textbox(
                label="📝 Soru",
                placeholder="Önce TAB 1'de olay analizi yapın...",
                lines=3,
                interactive=False
            )
        
        with gr.Row():
            hsg245_info = gr.Textbox(
                label="🔗 HSG245 Bağlantısı",
                placeholder="İlgili HSG245 kodları burada görünecek...",
                lines=2,
                interactive=False
            )
        
        answer_input = gr.Textbox(
            label="✍️ Cevabınız",
            placeholder="Cevabınızı buraya yazın...",
            lines=4
        )
        
        with gr.Row():
            prev_btn = gr.Button("⬅️ Önceki", variant="secondary")
            skip_btn = gr.Button("⏭️ Atla", variant="secondary")
            next_btn = gr.Button("➡️ Sonraki & Kaydet", variant="primary", scale=2)
        
        progress_info = gr.Markdown()
        
        def load_questions():
            """Soruları yükle ve görüntüle"""
            if not state["generated_questions"]:
                return "⚠️ Önce TAB 1'de olay analizi yapın!"
            
            output = f"### 📊 Toplam {len(state['generated_questions'])} Soru Hazır\n\n"
            
            for i, q in enumerate(state["generated_questions"], 1):
                required = "🔴 ZORUNLU" if q["required"] else "⚪ OPSİYONEL"
                output += f"**{i}. [{required}] [{q['category'].upper()}]**\n"
                output += f"{q['question']}\n"
                output += f"*HSG245: {q['hsg245_codes']} | {q['hsg245_link']}*\n\n"
            
            return output
        
        def show_question(index):
            """Belirli bir soruyu göster"""
            if not state["generated_questions"]:
                return "Önce analiz yapın...", "", 0
            
            index = int(index) % len(state["generated_questions"])
            q = state["generated_questions"][index]
            
            question_text = f"[{q['category'].upper()}] {q['question']}"
            hsg245_text = f"📊 Kodlar: {q['hsg245_codes']}\n🔗 {q['hsg245_link']}"
            
            return question_text, hsg245_text, index
        
        def next_question(current_idx, answer):
            """Sonraki soruya geç ve cevabı kaydet"""
            if answer.strip():
                state["answers"][int(current_idx)] = answer
            
            new_idx = (int(current_idx) + 1) % len(state["generated_questions"])
            
            answered = len(state["answers"])
            total = len(state["generated_questions"])
            progress = f"✅ {answered}/{total} soru yanıtlandı ({answered*100//total}% tamamlandı)"
            
            q_text, hsg_text, _ = show_question(new_idx)
            
            return q_text, hsg_text, new_idx, "", progress
        
        def prev_question(current_idx):
            """Önceki soruya dön"""
            new_idx = (int(current_idx) - 1) % len(state["generated_questions"])
            q_text, hsg_text, _ = show_question(new_idx)
            
            # Eğer daha önce cevaplandıysa göster
            prev_answer = state["answers"].get(new_idx, "")
            
            return q_text, hsg_text, new_idx, prev_answer
        
        # Event handlers
        gr.Button("🔄 Soruları Yükle", variant="secondary").click(
            load_questions,
            outputs=questions_display
        )
        
        next_btn.click(
            next_question,
            inputs=[current_q_index, answer_input],
            outputs=[current_question, hsg245_info, current_q_index, answer_input, progress_info]
        )
        
        prev_btn.click(
            prev_question,
            inputs=[current_q_index],
            outputs=[current_question, hsg245_info, current_q_index, answer_input]
        )
        
        skip_btn.click(
            lambda idx: next_question(idx, ""),
            inputs=[current_q_index],
            outputs=[current_question, hsg245_info, current_q_index, answer_input, progress_info]
        )
        
        question_display = gr.Markdown("Soru burada görünecek...")
        answer_radio = gr.Radio(
            label="Seçiminiz",
            choices=["Evet", "Hayır", "Kısmen"],
        )
        submit_btn = gr.Button("İlerle →")
    
    with gr.Tab("3️⃣ Kök Neden Analizi (WIP)"):
        gr.Markdown("## Kök Neden Kodları")
        gr.Markdown("⚠️ Bu bölüm henüz geliştirilme aşamasında...")
        
        gr.Markdown("""
        Burada AI'nın önerdiği kök neden kodları gösterilecek:
        - Dal 1: [B1.5] Uyarı sistemi arızası
        - Dal 2: [D4.2] LOTO prosedürü uygulanmıyor
        - Dal 3: [D1.4] Üretim baskısı
        """)
    
    with gr.Tab("4️⃣ Rapor (WIP)"):
        gr.Markdown("## Nihai Rapor")
        gr.Markdown("⚠️ Bu bölüm henüz geliştirilme aşamasında...")
        
        report_preview = gr.HTML("<p>Rapor burada görünecek...</p>")
    
    with gr.Tab("ℹ️ Bilgi"):
        gr.Markdown("""
        ## Test Ortamı Hakkında
        
        Bu arayüz, HITL sisteminin **girdi seviyesi tespit** modülünü test eder.
        
        ### Nasıl Çalışır?
        
        1. **TAB 1**: Olay açıklaması girin (minimal/orta/detaylı)
        2. Sistem girdinizi analiz eder ve seviye tespit eder
        3. Eksik bilgiler varsa, TAB 2'de sorular sorar
        4. Tamamlanan veriyle TAB 3'te kök neden analizi yapılır
        
        ### Girdi Seviyeleri
        
        - **Level 1 (Detaylı)**: 8+ puan - Test formatı gibi
        - **Level 2 (Orta)**: 4-7 puan - Form girişi gibi  
        - **Level 3 (Minimal)**: 0-3 puan - Serbest metin
        
        ### Puanlama Kriterleri
        
        - Kronoloji var mı? (+2)
        - Tanık beyanı var mı? (+2)
        - Prosedür bilgisi var mı? (+2)
        - Kök neden ön bulgusu var mı? (+3)
        - Yönetim faktörü var mı? (+2)
        - 500+ kelime mi? (+2)
        
        ---
        
        **Geliştirici:** HSE AI Team  
        **Versiyon:** 0.1.0 (Test)
        """)


if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False,
        show_error=True
    )
