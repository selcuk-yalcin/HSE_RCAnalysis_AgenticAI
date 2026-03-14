"""
Quick 5-Why Test - Sadece bir senaryo, hızlı test
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.rootcause_agent_v2 import RootCauseAgentV2
from hitl_test.question_engine import QuestionEngine
from hitl_test.hybrid_input_processor import HybridInputProcessor


def quick_test():
    """Hızlı test - LOTO senaryosu"""
    
    print("\n" + "=" * 80)
    print("🔬 HIZLI 5-WHY TESTİ - LOTO İHLALİ")
    print("=" * 80)
    
    # Olay
    incident_text = """
    Bakım teknisyeni elektrik panosunda çalışırken 380V akımına kapıldı.
    LOTO prosedürü uygulanmadı. Elektrik enerjisi kesilmedi.
    Çalışan 2. derece yanık ile hastaneye kaldırıldı.
    """
    
    print("\n📝 OLAY:")
    print(incident_text)
    
    # 1. Input analizi
    print("\n" + "─" * 80)
    print("ADIM 1: INPUT ANALİZİ")
    print("─" * 80)
    
    processor = HybridInputProcessor()
    level, details = processor.detect_input_level(incident_text)
    
    print(f"Seviye: Level {level} ({details['detail_score']}/13)")
    print(f"Eksik: {', '.join(details['missing']) if details['missing'] else 'YOK'}")
    
    # 2. Soru üretimi
    print("\n" + "─" * 80)
    print("ADIM 2: SORU ÜRETİMİ")
    print("─" * 80)
    
    qe = QuestionEngine()
    questions = qe.generate_questions_for_missing_categories(details['missing'][:2])  # İlk 2 kategori
    
    print(f"Üretilen soru: {len(questions)}")
    for i, q in enumerate(questions[:3], 1):
        print(f"{i}. [{q['hsg245_codes']}] {q['question']}")
    
    # 3. RootCause analizi
    print("\n" + "─" * 80)
    print("ADIM 3: 5-WHY ANALİZİ")
    print("─" * 80)
    
    agent = RootCauseAgentV2()
    
    part1 = {"description": incident_text}
    part2 = {"severity": "Major"}
    
    print("\n⏳ AI analiz yapıyor (30-60 saniye sürebilir)...\n")
    
    result = agent.analyze_root_causes(part1, part2)
    
    # 4. Sonuçlar
    print("\n" + "=" * 80)
    print("📊 SONUÇLAR")
    print("=" * 80)
    
    for i, branch in enumerate(result['analysis_branches'], 1):
        print(f"\n🌿 DAL {i}:")
        
        imm = branch['immediate_cause']
        print(f"\n   🔴 Immediate: [{imm['code']}] {imm['cause_tr']}")
        
        chain = branch['five_why_chain']
        print(f"\n   🔗 5-Why Chain:")
        for why in chain['whys'][:3]:  # İlk 3 why
            print(f"      Why {why['level']}: {why['answer_tr'][:80]}...")
        
        root = chain['root_cause']
        print(f"\n   🎯 Root Cause: [{root['code']}] {root['custom_description_tr']}")
    
    print("\n" + "=" * 80)
    print("✅ TEST TAMAMLANDI")
    print("=" * 80)
    
    return result


if __name__ == "__main__":
    try:
        result = quick_test()
        print(f"\n💾 {len(result['analysis_branches'])} dal analiz edildi")
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()
