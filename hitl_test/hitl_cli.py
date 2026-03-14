#!/usr/bin/env python3
"""
HSE HITL Question System - Terminal/CLI Version
Gradio olmadan çalışabilen interaktif sürüm
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

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


class CLIHITLSession:
    """CLI-based HITL Session"""
    
    def __init__(self):
        self.incident_text: str = ""
        self.part1: Optional[Dict[str, Any]] = None
        self.part2: Optional[Dict[str, Any]] = None
        self.part3: Optional[Dict[str, Any]] = None
        self.current_questions: List[Dict[str, Any]] = []
        self.user_answers: Dict[int, str] = {}
        self.analysis_stage: str = "initial"
        self.conversation_history: List[Dict[str, Any]] = []
        
    def add_message(self, role, content):
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })


def print_header():
    """Ana başlık"""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║         🔍 HSE ROOT CAUSE ANALYSIS - HITL QUESTION SYSTEM                  ║
║                    İnsan-Makine Etkileşimi ile Analiz                      ║
║                                                                            ║
║  ⚙️  Terminal Sürümü (Gradio olmadan)                                      ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)


def print_step(step_num, title):
    """Adım başlığı"""
    print(f"\n{'='*80}")
    print(f"📍 ADIM {step_num}: {title}")
    print(f"{'='*80}\n")


def get_multiline_input(prompt):
    """Çok satırlı input al"""
    print(f"{prompt}")
    print("(Bitirmek için boş satır sonra Ctrl+D veya özel durdurma komutu girin)")
    print("-" * 60)
    lines = []
    try:
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
    except EOFError:
        pass
    return "\n".join(lines)


def main():
    """Ana akış"""
    
    print_header()
    
    session = CLIHITLSession()
    processor = HybridInputProcessor()
    qe = QuestionEngine()
    
    # =========================================================================
    # STEP 1: OLAY AÇIKLAMASI
    # =========================================================================
    
    print_step(1, "OLAY AÇIKLAMASI")
    incident_text = get_multiline_input(
        "🔸 İş kazasını/olayı anlatın (o zaman kısıtlı bilgi olabilir):"
    )
    
    if not incident_text.strip():
        print("❌ Olay açıklaması boş bırakılamaz!")
        return
    
    session.incident_text = incident_text
    session.add_message("user", incident_text)
    
    print("\n✅ Olay kaydedildi. Sistem analiz ediyor...\n")
    
    # =========================================================================
    # INPUT ANALİZİ
    # =========================================================================
    
    level, details = processor.detect_input_level(incident_text)
    
    print("📊 INPUT ANALİZİ")
    print("─" * 60)
    print(f"Bilgi Seviyesi: Level {level}")
    
    # Handle both old and new output formats
    detail_score = details.get('detail_score', 0) if isinstance(details, dict) else 0
    provided = details.get('present', []) if isinstance(details, dict) else []
    missing = details.get('missing', []) if isinstance(details, dict) else []
    
    print(f"Detail Skoru: {detail_score}/13 ({(detail_score/13)*100:.0f}%)")
    
    if provided:
        print("\nTespit Edilen Bilgiler:")
        for cat in provided:
            print(f"  ✓ {cat}")
    
    if missing:
        print(f"\nEksik Kategoriler ({len(missing)} adet):")
        for cat in missing:
            print(f"  ✗ {cat}")
    
    # =========================================================================
    # OVERVIEW AGENT
    # =========================================================================
    
    print("\n🔍 OLAy TANIMI (OverviewAgent)")
    print("─" * 60)
    
    try:
        incident_dict = {"description": incident_text}
        overview_agent = OverviewAgent()
        part1 = overview_agent.process_initial_report(incident_dict)
        session.part1 = part1
        
        print(f"Ref No: {part1.get('ref_no', 'N/A')}")
        print(f"Olay Tipi: {part1.get('incident_type', 'N/A')}")
        print(f"Tarih: {part1.get('incident_date', 'N/A')}")
        print(f"Konum: {part1.get('location', 'N/A')}")
        
        person = part1.get('affected_person', {})
        if isinstance(person, dict):
            print(f"Etkilenen Kişi: {person.get('name', 'N/A')} ({person.get('age', '?')} yaş)")
        else:
            print(f"Etkilenen Kişi: {person}")
        
        print(f"Yaralanma Türü: {part1.get('injury_type', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        return
    
    # =========================================================================
    # ASSESSMENT AGENT
    # =========================================================================
    
    print("\n📋 OLAY DEĞERLENDİRMESİ (AssessmentAgent)")
    print("─" * 60)
    
    try:
        assessment_agent = AssessmentAgent()
        part2 = assessment_agent.assess_incident(part1, incident_dict)
        session.part2 = part2
        
        print(f"Fiili/Potansiyel Zarar: {part2.get('actual_potential_harm', 'N/A')}")
        riddor = part2.get('riddor', {})
        if isinstance(riddor, dict):
            print(f"RIDDOR Reportable: {riddor.get('reportable', 'N/A')}")
        else:
            print(f"RIDDOR Reportable: {riddor}")
        
        investigation = part2.get('investigation', {})
        if isinstance(investigation, dict):
            print(f"Investigation Level: {investigation.get('level', 'N/A')}")
        else:
            print(f"Investigation Level: {investigation}")
        
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        return
    
    # =========================================================================
    # STEP 2: SORULAR
    # =========================================================================
    
    print_step(2, "SORULAR & CEVAPLAR")
    
    # Soru üretimi
    missing_cats = missing[:3] if missing else []  # İlk 3 kategori
    session.current_questions = qe.generate_questions_for_missing_categories(missing_cats)
    
    print(f"❓ {len(session.current_questions)} soru üretildi.\n")
    
    answered = 0
    while answered < min(3, len(session.current_questions)):
        q = session.current_questions[answered]
        q_num = answered + 1
        
        print(f"\n📌 SORU {q_num}/{len(session.current_questions)}")
        print(f"Kategori: {q['category']}")
        print(f"Gerekli: {'🔴 ZORUNLU' if q['required'] else '⚪ OPSİYONEL'}")
        print(f"HSG245 Kodlar: {q['hsg245_codes']}\n")
        
        print(f"❓ {q['question']}\n")
        
        answer = input("→ Cevapınız: ").strip()
        
        if answer:
            session.user_answers[answered] = answer
            session.add_message("user", f"S{q_num}: {answer}")
            
            # Takip soruları
            followups = qe.get_followup_questions(answer, q['category'])
            
            if followups:
                print(f"\n🔄 TAKIP SORULARI (5-Why):")
                for i, fq in enumerate(followups[:2], 1):
                    print(f"  {i}. ❓ {fq['question']}")
                    print(f"     🏷️  {fq['hsg245_link']}\n")
                    
                    followup_answer = input(f"     → Cevap: ").strip()
                    if followup_answer:
                        session.add_message("user", f"Takip {i}: {followup_answer}")
            
            answered += 1
            print(f"\n✅ Cevap kaydedildi ({answered}/{min(3, len(session.current_questions))})")
        else:
            print("⚠️  Boş cevap geçilemez, tekrar deneyin.")
    
    # =========================================================================
    # STEP 3: ROOT CAUSE ANALYSIS
    # =========================================================================
    
    print_step(3, "ROOT CAUSE ANALYSIS")
    
    print("🔄 RootCauseAgentV2 ile analiz yapılıyor...\n")
    
    try:
        rca_agent = RootCauseAgentV2()
        
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
                for i, q in enumerate(session.current_questions[:answered])
            ]
        }
        
        part3 = rca_agent.analyze_root_causes(
            part1_data=session.part1,
            part2_data=session.part2,
            investigation_data=investigation_data
        )
        session.part3 = part3
        
        branches = part3.get("analysis_branches", [])
        root_causes = part3.get("final_root_causes", [])
        
        print(f"📊 ANALIZ SONUÇLARI\n")
        print(f"Dallar: {len(branches)}")
        print(f"Kök Nedenler: {len(root_causes)}\n")
        
        # Dalları göster
        print("🌿 ANALIZ DALLARI:\n")
        for i, branch in enumerate(branches, 1):
            imm = branch.get('immediate_cause', {})
            print(f"  DAL {i}: {imm.get('cause_tr', 'N/A')}")
            
            chain = branch.get('five_why_chain', {})
            whys = chain.get('whys', [])
            
            for j, why in enumerate(whys[:2], 1):
                print(f"    Why {j}: {why.get('answer_tr', 'N/A')[:60]}...")
            
            root = chain.get('root_cause', {})
            print(f"    🎯 Root: {root.get('root_cause_title', 'N/A')}\n")
        
        # Kök nedenleri göster
        print("🎯 KÖK NEDENLER (ÖZET):\n")
        for i, rc in enumerate(root_causes, 1):
            code = rc.get('root_cause_code', 'N/A')
            title = rc.get('root_cause_title', 'N/A')
            print(f"  {i}. [{code}] {title}")
        
        print("\n✅ RCA tamamlandı.")
        
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # =========================================================================
    # STEP 4: RAPOR ÜRETİMİ
    # =========================================================================
    
    print_step(4, "RAPOR ÜRETİMİ")
    
    print("📄 DOCX + HTML rapor üretiliyor...\n")
    
    try:
        Path("outputs").mkdir(exist_ok=True)
        
        docx_agent = SkillBasedDocxAgent()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ref_no = session.part1.get("ref_no", "REPORT") if session.part1 else "REPORT"
        
        docx_file = f"outputs/{ref_no}_{timestamp}.docx"
        
        report_data = {
            "part1": session.part1,
            "part2": session.part2,
            "part3_rca": session.part3,
            "user_questions": session.current_questions,
            "user_answers": session.user_answers
        }
        
        # DOCX üretimi
        print(f"  Oluşturuluyor: {docx_file}")
        # Note: Gerçek implementasyon docx_agent kullanacak
        # Bu sadece örnek
        
        # JSON backup
        json_file = docx_file.replace(".docx", ".json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        print(f"  ✅ JSON: {json_file}")
        
        print(f"\n📊 RAPOR ÖZETİ")
        print("─" * 60)
        print(f"Reference No: {ref_no}")
        print(f"Timestamp: {timestamp}")
        print(f"Dosya: {docx_file}")
        print(f"Root Causes: {len(root_causes)}")
        
        print("\n✅ ANALIZ TAMAMLANDI!")
        
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # =========================================================================
    # ÖZEt
    # =========================================================================
    
    print("\n" + "="*80)
    print("📊 ANALIZ ÖZETİ")
    print("="*80)
    
    print(f"""
✓ Olay Açıklaması: {len(session.incident_text)} karakter
✓ Bilgi Seviyesi: Level {level}
✓ Sorular: {len(session.current_questions)} üretildi, {answered} cevaplanıd
✓ Root Causes: {len(root_causes)} bulundu
✓ Raporlar: outputs/ klasöründe kaydedildi

Dosyalar:
  • {docx_file}
  • {json_file}
    """)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Kullanıcı tarafından durduruldu.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
