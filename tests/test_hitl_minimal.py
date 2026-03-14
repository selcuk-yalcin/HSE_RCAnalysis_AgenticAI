"""
Test: Minimal giriş (serbest metin)
Beklenen: 8-10 soru, adım adım tamamlama
"""

from hitl_test.hybrid_input_processor import HybridInputProcessor
from hitl_test.question_engine import QuestionEngine

def test_minimal_input():
    incident_text = "Forklift geri manevra yaparken çalışana çarptı."
    
    processor = HybridInputProcessor()
    level, details = processor.detect_input_level(incident_text)
    
    assert level == 3, f"Minimal girdi Level 3 olmalı, {level} çıktı"
    assert len(details["missing"]) >= 5, "Eksik bilgi tespit edilmeli"
    
    # Soru üretimi
    engine = QuestionEngine()
    questions = engine.generate_missing_questions(details["missing"], "forklift")
    
    assert len(questions) >= 5, f"En az 5 soru üretilmeli, {len(questions)} üretildi"
    print(f"✅ {len(questions)} soru üretildi (Minimal giriş testi başarılı)")

if __name__ == "__main__":
    test_minimal_input()
