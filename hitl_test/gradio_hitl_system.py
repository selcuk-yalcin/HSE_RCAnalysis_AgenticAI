"""
HITL Question System with Gradio - Interactive Root Cause Analysis
Kullanıcı olay açıklaması girer → Sistem sorular sorar → Detaylı analiz → Rapor üretir

Akış:
1. User Input: İlk olay açıklaması
2. System Analysis: OverviewAgent + AssessmentAgent
3. Question Generation: Knowledge Base ile entegre sorular
4. User Q&A: 5-Why zincirine göre detay toplama
5. Root Cause Analysis: RootCauseAgentV2
6. Report Generation: SkillBasedDocxAgent
1. KULLANICI OLAY AÇIKLAMASI GİRER
   └─ (İlk başta kısıtlı bilgi: "Elektrik çarpması oldu")
   
2. SISTEM ANALIZ EDER (Overview + Assessment)
   ├─ Olay tipini tanımla
   ├─ Şiddeti belirle
   └─ Investigation level set et
   
3. SORU SORMA YAPISI DEVREYE GİRER (Knowledge Base'le entegre)
   ├─ Eksik kategorileri tespit et
   ├─ HSG245 kodlarına bağlı sorular üret
   └─ GRADIO arayüzü ile kullanıcıya sor
   
4. KULLANICI CEVAPLAR
   └─ Her cevap ile daha detaylı bilgi
   
5. ROOT CAUSE ANALYSIS (RootCauseAgentV2)
   ├─ Immediate Cause'tan başla
   ├─ 5-Why zinciri ile inerken sorular sor
   └─ Dallar halinde root causes belirle
   
6. RAPOR ÜRETİMİ (SkillBasedDocxAgent)
   └─ Toplanan tüm bilgilerle DOCX + HTML rapor
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Gradio import - optional fallback
try:
    import gradio as gr
except ImportError:
    gr = None
    print("⚠️  Gradio not installed. Run: pip install gradio")

# Path setup
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from agents.overview_agent import OverviewAgent
from agents.assessment_agent import AssessmentAgent
from agents.rootcause_agent_v2 import RootCauseAgentV2
from agents.skillbased_docx_agent import SkillBasedDocxAgent
from hitl_test.question_engine import QuestionEngine
from hitl_test.hybrid_input_processor import HybridInputProcessor


# ============================================================================
# GLOBAL STATE MANAGEMENT
# ============================================================================

class HITLSession:
    """HITL Analysis Session State Management"""
    
    def __init__(self):
        self.incident_text: str = ""
        self.part1: Optional[Dict[str, Any]] = None  # OverviewAgent sonucu
        self.part2: Optional[Dict[str, Any]] = None  # AssessmentAgent sonucu
        self.part3: Optional[Dict[str, Any]] = None  # RootCauseAgent sonucu
        self.current_questions: List[Dict[str, Any]] = []
        self.user_answers: Dict[int, str] = {}
        self.analysis_stage: str = "initial"  # initial → questions → rca → report
        self.conversation_history: List[Dict[str, Any]] = []
        
    def reset(self):
        """Yeni analiz başlat"""
        self.__init__()
    
    def add_message(self, role, content):
        """Sohbet geçmişine ekle"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_summary(self):
        """Analiz özeti"""
        return {
            "stage": self.analysis_stage,
            "incident": self.incident_text[:100] + "...",
            "questions_asked": len(self.current_questions),
            "answers_collected": len(self.user_answers),
            "conversation_turns": len(self.conversation_history)
        }


# Global session
session = HITLSession()
processor = HybridInputProcessor()
qe = QuestionEngine()

# API kontrolü
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    print("⚠️  OPENROUTER_API_KEY bulunamadı. API'ye ihtiyaç duyulan fonksiyonlar çalışmayacaktır.")

# ============================================================================
# STEP 1: INITIAL INCIDENT SUBMISSION
# ============================================================================

def submit_incident(incident_description: str) -> tuple:
    """
    Adım 1: Kullanıcı olay açıklamasını girer
    
    İşlem:
    1. Input analizi (HybridInputProcessor)
    2. OverviewAgent ile tanımlama
    3. AssessmentAgent ile değerlendirme
    4. Soru üretimi
    """
    
    if not incident_description.strip():
        return (
            "❌ Lütfen olay açıklaması girin",
            "",
            ""
        )
    
    session.reset()
    session.incident_text = incident_description
    session.add_message("user", incident_description)
    
    try:
        # Step 1: Input Analysis
        level, details = processor.detect_input_level(incident_description)
        
        analysis_text = f"""
📊 INPUT ANALİZİ
────────────────────────────────────────────────────────
Bilgi Seviyesi: Level {level}
Detail Skoru: {details['detail_score']}/13 ({(details['detail_score']/13)*100:.0f}%)

Tespit Edilen Bilgiler:
{chr(10).join([f"  • {cat}" for cat in details['present']]) if details['present'] else "  (Henüz bilgi yok)"}

Eksik Kategoriler ({len(details['missing'])} adet):
{chr(10).join([f"  • {cat}" for cat in details['missing']]) if details['missing'] else "  (Tüm kategoriler mevcut)"}
"""
        
        # Step 2: OverviewAgent
        incident_dict = {"description": incident_description}
        overview_agent = OverviewAgent()
        part1 = overview_agent.process_initial_report(incident_dict)
        session.part1 = part1
        
        overview_text = f"""
🔍 OLAy TANIMI (OverviewAgent)
────────────────────────────────────────────────────────
Ref No: {part1.get('ref_no', 'N/A')}
Olay Tipi: {part1.get('incident_type', 'N/A')}
Tarih: {part1.get('incident_date', 'N/A')}
Konum: {part1.get('location', 'N/A')}
Etkilenen Kişi: {part1.get('affected_person', {}).get('name', 'N/A')}
Yaralanma Türü: {part1.get('injury_type', 'N/A')}
"""
        
        # Step 3: AssessmentAgent
        assessment_agent = AssessmentAgent()
        part2 = assessment_agent.assess_incident(part1, incident_dict)
        session.part2 = part2
        
        assessment_text = f"""
📋 OLAY DEĞERLENDİRMESİ (AssessmentAgent)
────────────────────────────────────────────────────────
Fiili/Potansiyel Zarar: {part2.get('actual_potential_harm', 'N/A')}
RIDDOR: {part2.get('riddor', {}).get('reportable', 'N/A')}
Investigation Level: {part2.get('investigation', {}).get('level', 'N/A')}
"""
        
        # Step 4: Question Generation
        session.current_questions = qe.generate_questions_for_missing_categories(
            details['missing'][:3]  # İlk 3 kategori
        )
        
        session.analysis_stage = "questions"
        session.add_message("assistant", analysis_text + overview_text + assessment_text)
        
        result_text = analysis_text + overview_text + assessment_text
        
        # Questions display
        questions_display = "❓ SORULACAK SORULAR\n" + "─" * 50 + "\n"
        for i, q in enumerate(session.current_questions[:5], 1):
            required = "🔴 ZORUNLU" if q['required'] else "⚪ OPSİYONEL"
            questions_display += f"\n{i}. [{required}] {q['question']}\n"
            questions_display += f"   📁 Kategori: {q['category']}\n"
            questions_display += f"   🏷️  HSG245: {q['hsg245_codes']}\n"
        
        return (
            result_text,
            questions_display,
            f"✅ Olay analizi tamamlandı. Şimdi sorular sorulacak.\n\nToplam {len(session.current_questions)} soru hazır."
        )
    
    except Exception as e:
        error_msg = f"❌ Hata: {str(e)}"
        session.add_message("assistant", error_msg)
        return error_msg, "", error_msg


# ============================================================================
# STEP 2: QUESTION & ANSWER PHASE
# ============================================================================

def answer_question(question_idx: int, answer: str) -> tuple:
    """
    Adım 2: Kullanıcı soruları cevaplar
    
    İşlem:
    1. Cevabı kaydet
    2. Takip soruları (5-Why) üret
    3. Sonraki soru öner
    """
    
    if not session.current_questions:
        return "❌ Henüz soru yüklenmedi", "", ""
    
    if question_idx >= len(session.current_questions):
        return "❌ Geçersiz soru numarası", "", ""
    
    if not answer.strip():
        return "❌ Lütfen cevap girin", "", ""
    
    try:
        question = session.current_questions[question_idx]
        session.user_answers[question_idx] = answer
        session.add_message("user", f"S: {question['question']}\nC: {answer}")
        
        # Takip soruları üret (5-Why)
        followups = qe.get_followup_questions(answer, question['category'])
        
        followup_text = f"""
🔄 TAKIP SORULARI (5-Why)
────────────────────────────────────────────────────────
Orijinal Cevap: "{answer}"

Takip Soruları:
"""
        
        for i, fq in enumerate(followups, 1):
            followup_text += f"\n{i}. ❓ {fq['question']}\n"
            followup_text += f"   🏷️  {fq['hsg245_link']}\n"
            followup_text += f"   📊 Why Level: {fq['why_level']}\n"
        
        # Sonraki soru
        next_q_idx = question_idx + 1
        
        if next_q_idx < len(session.current_questions):
            next_question = session.current_questions[next_q_idx]
            next_text = f"""
📌 SONRAKI SORU
────────────────────────────────────────────────────────
{next_question['question']}

Kategori: {next_question['category']}
HSG245: {next_question['hsg245_codes']}
Gerekli: {'Evet' if next_question['required'] else 'Hayır'}
"""
            progress = f"İlerleme: {question_idx + 1}/{len(session.current_questions)}"
        else:
            next_text = """
✅ TÜM SORULAR CEVAPLANMIŞTUR
────────────────────────────────────────────────────────
Devam etmek için "RCA Analizi Başlat" butonuna tıklayın.
"""
            progress = f"İlerleme: TAMAMLANDI ({len(session.current_questions)}/{len(session.current_questions)})"
        
        session.add_message("assistant", followup_text)
        
        summary_text = f"""
✅ Cevap Kaydedildi
────────────────────────────────────────────────────────
Soru #{question_idx + 1}: {question['question'][:50]}...
Cevap: {answer[:80]}...

{followup_text}
"""
        
        return summary_text, next_text, progress
    
    except Exception as e:
        error_msg = f"❌ Hata: {str(e)}"
        return error_msg, "", error_msg


# ============================================================================
# STEP 3: ROOT CAUSE ANALYSIS
# ============================================================================

def start_rca() -> tuple:
    """
    Adım 3: Root Cause Analysis (RootCauseAgentV2)
    
    İşlem:
    1. Toplanan tüm bilgileri bir araya getir
    2. RootCauseAgentV2 ile analiz
    3. Dalları ve kök nedenleri belirle
    """
    
    if not session.part1 or not session.part2:
        return "❌ Önce olay açıklaması ve sorular işlemi yapmanız gerekir", "", ""
    
    try:
        rca_agent = RootCauseAgentV2()
        
        # Cevapları metadata'ya ekle
        investigation_data = {
            "description": session.incident_text,
            "user_answers": session.user_answers,
            "questions_asked": [
                {
                    "idx": i,
                    "question": q['question'],
                    "category": q['category'],
                    "answer": session.user_answers.get(i, "")
                }
                for i, q in enumerate(session.current_questions)
            ]
        }
        
        # Root cause analysis
        part3 = rca_agent.analyze_root_causes(
            part1_data=session.part1,
            part2_data=session.part2,
            investigation_data=investigation_data
        )
        session.part3 = part3
        session.analysis_stage = "rca"
        
        # Format results
        branches = part3.get("analysis_branches", [])
        root_causes = part3.get("final_root_causes", [])
        
        rca_text = f"""
🌳 ROOT CAUSE ANALYSIS SONUÇLARI
════════════════════════════════════════════════════════

📊 ÖZET:
  • Analiz Dalları: {len(branches)}
  • Kök Nedenler: {len(root_causes)}
  • Immediate Causes: {len([b.get('immediate_cause') for b in branches])}

🌿 DALLAR:
"""
        
        for i, branch in enumerate(branches, 1):
            imm = branch.get('immediate_cause', {})
            rca_text += f"\n  DAL {i}:"
            rca_text += f"\n    Immediate: [{imm.get('code')}] {imm.get('cause_tr', 'N/A')}"
            
            chain = branch.get('five_why_chain', {})
            whys = chain.get('whys', [])
            rca_text += f"\n    5-Why Chain ({len(whys)} level):"
            for why in whys[:3]:
                rca_text += f"\n      Why {why.get('level')}: {why.get('answer_tr', 'N/A')[:60]}..."
            
            root = chain.get('root_cause', {})
            rca_text += f"\n    🎯 Root Cause: [{root.get('code')}] {root.get('root_cause_title', 'N/A')}"
        
        rca_text += f"\n\n🎯 KÖK NEDENLER (ÖZET):\n"
        for i, rc in enumerate(root_causes, 1):
            rca_text += f"\n  {i}. [{rc.get('root_cause_code')}] {rc.get('root_cause_title')}"
            rca_text += f"\n     → {rc.get('description', 'N/A')[:80]}..."
        
        session.analysis_stage = "report"
        session.add_message("assistant", rca_text)
        
        return (
            rca_text,
            f"✅ Root cause analysis tamamlandı.\n\n{len(branches)} dal analiz edildi.",
            f"✅ Hazırlanıyor... {len(root_causes)} kök neden belirlendi."
        )
    
    except Exception as e:
        error_msg = f"❌ Hata: {str(e)}\n\nDetay: {str(e)}"
        return error_msg, "", error_msg


# ============================================================================
# STEP 4: REPORT GENERATION
# ============================================================================

def generate_report() -> tuple:
    """
    Adım 4: Report Generation (SkillBasedDocxAgent)
    
    İşlem:
    1. Tüm bilgileri birleştir
    2. DOCX + HTML rapor üret
    3. Dosyaları kaydet
    """
    
    if not session.part3:
        return "❌ Önce RCA analizi yapmanız gerekir", "", ""
    
    try:
        Path("outputs").mkdir(exist_ok=True)
        
        docx_agent = SkillBasedDocxAgent()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ref_no = session.part1.get("ref_no", "REPORT") if session.part1 else "REPORT"
        
        docx_file = f"outputs/{ref_no}_{timestamp}.docx"
        
        # Veri paketini hazırla
        report_data = {
            "part1": session.part1,
            "part2": session.part2,
            "part3_rca": session.part3,
            "user_questions": session.current_questions,
            "user_answers": session.user_answers,
            "conversation_history": session.conversation_history,
        }
        
        # Rapor üret
        result = docx_agent.generate_report(report_data, docx_file)
        html_file = result.replace(".docx", ".html")
        
        # Dosya kontrolü
        files_created = []
        
        if Path(result).exists():
            size_kb = Path(result).stat().st_size / 1024
            files_created.append(f"✅ DOCX Rapor: {result} ({size_kb:.1f} KB)")
        
        if Path(html_file).exists():
            size_kb = Path(html_file).stat().st_size / 1024
            files_created.append(f"✅ HTML Rapor: {html_file} ({size_kb:.1f} KB)")
        
        # JSON Backup
        json_file = f"outputs/{ref_no}_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(session.part3, f, ensure_ascii=False, indent=2)
        files_created.append(f"✅ JSON Backup: {json_file}")
        
        report_text = f"""
✅ RAPOR ÜRETİMİ BAŞARILI
════════════════════════════════════════════════════════

📄 Oluşturulan Dosyalar:
{chr(10).join(files_created)}

📊 Rapor İçeriği:
  • Olay Özeti
  • Yaralanma Detayları
  • Root Cause Analysis (Dallar)
  • Kök Nedenler
  • Önerilen Aksiyonlar
  • HSG245 Kod Eşleştirmesi

🔍 Detaylar:
  • Reference No: {session.part1.get('ref_no') if session.part1 else 'N/A'}
  • Olay Tipi: {session.part1.get('incident_type') if session.part1 else 'N/A'}
  • RIDDOR: {session.part2.get('riddor', {}).get('reportable') if session.part2 else 'N/A'}
  • Investigasyon Seviyesi: {session.part2.get('investigation', {}).get('level') if session.part2 else 'N/A'}
  
  • Toplanan Sorular: {len(session.current_questions)}
  • Cevaplanan Sorular: {len(session.user_answers)}
  • Analiz Dalları: {len(session.part3.get('analysis_branches', []))}
  • Kök Nedenler: {len(session.part3.get('final_root_causes', []))}
"""
        
        session.analysis_stage = "complete"
        session.add_message("assistant", report_text)
        
        return (
            report_text,
            "🎉 HITL Analiz Tamamlandı!",
            f"📁 Dosyalar outputs/ klasöründe kaydedildi."
        )
    
    except Exception as e:
        import traceback
        error_msg = f"❌ Hata: {str(e)}\n\n{traceback.format_exc()}"
        return error_msg, "", error_msg


# ============================================================================
# GRADIO INTERFACE
# ============================================================================

def create_interface():
    """Gradio arayüzü oluştur"""
    
    if gr is None:
        raise ImportError("Gradio is not installed. Run: pip install gradio")
    
    with gr.Blocks(title="HSE HITL Question System") as app:
        
        gr.Markdown("""
# 🔍 HSE Root Cause Analysis - HITL Question System
## İnsan-Makine Etkileşimi ile Detaylı İş Kazası Analizi
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                
                # STEP 1: Incident Submission
                gr.Markdown("## 📝 Adım 1: Olay Açıklaması")
                incident_input = gr.Textbox(
                    label="Olay Açıklaması",
                    placeholder="Kazanın ne olduğunu anlatın...",
                    lines=6,
                    max_lines=15
                )
                
                submit_btn = gr.Button("✅ Olay Analizini Başlat", variant="primary")
                
                incident_output = gr.Textbox(
                    label="Olay Tahlili",
                    lines=8,
                    interactive=False
                )
                
                # STEP 2: Questions
                gr.Markdown("## ❓ Adım 2: Sorular & Cevaplar")
                
                questions_display = gr.Textbox(
                    label="Sorular",
                    lines=6,
                    interactive=False
                )
                
                with gr.Row():
                    q_idx = gr.Slider(
                        minimum=0,
                        maximum=10,
                        step=1,
                        label="Soru Numarası",
                        value=0,
                        info="0-10 arası soru seç"
                    )
                    answer_input = gr.Textbox(
                        label="Cevap",
                        placeholder="Soruya cevap verin..."
                    )
                
                answer_btn = gr.Button("✅ Cevap Gönder", variant="secondary")
                
                with gr.Row():
                    followup_output = gr.Textbox(
                        label="Takip Soruları",
                        lines=6,
                        interactive=False
                    )
                    next_q_output = gr.Textbox(
                        label="Sonraki Soru",
                        lines=4,
                        interactive=False
                    )
                
                progress_output = gr.Label(
                    value="Bekleniyor...",
                    label="İlerleme"
                )
                
                # STEP 3: RCA
                gr.Markdown("## 🌳 Adım 3: Root Cause Analysis")
                
                rca_btn = gr.Button("▶️ RCA Analizi Başlat", variant="primary")
                
                rca_output = gr.Textbox(
                    label="RCA Sonuçları",
                    lines=10,
                    interactive=False
                )
                
                rca_status = gr.Textbox(
                    label="Durum",
                    interactive=False
                )
                
                # STEP 4: Report
                gr.Markdown("## 📄 Adım 4: Rapor Üretimi")
                
                report_btn = gr.Button("📊 Rapor Üret", variant="primary")
                
                report_output = gr.Textbox(
                    label="Rapor Sonucu",
                    lines=8,
                    interactive=False
                )
                
                report_status = gr.Textbox(
                    label="Durum",
                    interactive=False
                )
                
            with gr.Column(scale=1):
                gr.Markdown("## 📊 Analiz Özeti")
                
                summary_btn = gr.Button("📋 Özeti Göster")
                summary_output = gr.Textbox(
                    label="Analiz Özeti",
                    lines=15,
                    interactive=False
                )
                
                reset_btn = gr.Button("🔄 Yeniden Başla", variant="stop")
        
        # Event Bindings
        submit_btn.click(
            fn=submit_incident,
            inputs=[incident_input],
            outputs=[incident_output, questions_display, progress_output]
        )
        
        answer_btn.click(
            fn=answer_question,
            inputs=[q_idx, answer_input],
            outputs=[followup_output, next_q_output, progress_output]
        )
        
        rca_btn.click(
            fn=start_rca,
            inputs=[],
            outputs=[rca_output, rca_status, progress_output]
        )
        
        report_btn.click(
            fn=generate_report,
            inputs=[],
            outputs=[report_output, report_status, progress_output]
        )
        
        summary_btn.click(
            fn=lambda: json.dumps(session.get_summary(), ensure_ascii=False, indent=2),
            inputs=[],
            outputs=[summary_output]
        )
        
        def reset_session():
            session.reset()
            return "", "", ""
        
        reset_btn.click(
            fn=reset_session,
            inputs=[],
            outputs=[incident_input, incident_output, questions_display]
        )
        
        return app


if __name__ == "__main__":
    if gr is None:
        print("""
❌ HATA: Gradio yüklenmedi!

Çözüm:
    pip install gradio

Ardından tekrar deneyin:
    python hitl_test/gradio_hitl_system.py
        """)
        sys.exit(1)
    
    app = create_interface()
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║           🔍 HSE HITL QUESTION SYSTEM - GRADIO ARAYÜZÜ                       ║
║                                                                              ║
║           Açılıyor: http://127.0.0.1:7860                                    ║
║                                                                              ║
║  Akış:                                                                       ║
║    1. Olay açıklaması girin                                                  ║
║    2. Sistem sorular sorar (Knowledge Base entegre)                           ║
║    3. Her cevaba göre 5-Why takip soruları                                    ║
║    4. Root Cause Analysis (RootCauseAgentV2)                                  ║
║    5. DOCX + HTML Rapor üretimi (SkillBasedDocxAgent)                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    app.launch(share=True, server_name="0.0.0.0", server_port=7860)
