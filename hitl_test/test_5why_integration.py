"""
5-Why Integration Test
Test RootCauseAgentV2 ile QuestionEngine entegrasyonu
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.rootcause_agent_v2 import RootCauseAgentV2
from question_engine import QuestionEngine
from hybrid_input_processor import HybridInputProcessor
import json
from datetime import datetime


def test_scenario_1_minimal():
    """Test 1: Minimal input ile tam analiz"""
    
    print("\n" + "=" * 80)
    print("TEST 1: MİNİMAL INPUT - FORKLIFT ÇARPMA")
    print("=" * 80)
    
    # Minimal olay girişi
    incident_text = """
    Forklift geri manevra yaparken yaya yolundaki çalışana çarptı. 
    Çalışan ayağından yaralandı.
    """
    
    print("\n📝 OLAY GİRİŞİ:")
    print(incident_text)
    
    # Step 1: Input processor
    processor = HybridInputProcessor()
    level, details = processor.detect_input_level(incident_text)
    
    print(f"\n📊 GİRDİ SEVİYESİ: Level {level}")
    print(f"Detay puanı: {details['detail_score']}/13")
    print(f"Eksik kategoriler: {', '.join(details['missing'])}")
    
    # Step 2: Question Engine
    question_engine = QuestionEngine()
    questions = question_engine.generate_questions_for_missing_categories(details['missing'])
    
    print(f"\n❓ ÜRETİLEN SORULAR: {len(questions)} adet")
    for i, q in enumerate(questions[:3], 1):
        print(f"{i}. [{q['category']}] {q['question']}")
        print(f"   HSG245: {q['hsg245_codes']}")
    
    # Step 3: RootCauseAgentV2 (otomatik mod)
    print("\n🔍 KÖK NEDEN ANALİZİ BAŞLIYOR...")
    print("(AI otomatik olarak immediate causes ve 5-Why üretecek)\n")
    
    agent = RootCauseAgentV2()
    
    # Basit part1, part2 verisi
    part1_data = {
        "description": incident_text,
        "incident_type": "Forklift collision",
        "affected_persons": ["Worker"],
        "consequences": ["Foot injury"]
    }
    
    part2_data = {
        "severity": "Minor",
        "riddor_status": "Non-RIDDOR",
        "investigation_level": "Basic"
    }
    
    # Analiz
    rca_result = agent.analyze_root_causes(part1_data, part2_data)
    
    # Sonuçları göster
    print("\n" + "=" * 80)
    print("SONUÇLAR")
    print("=" * 80)
    
    print(f"\n📋 Analiz Metodu: {rca_result['analysis_method']}")
    print(f"🌿 Toplam Dal Sayısı: {len(rca_result['analysis_branches'])}")
    
    for i, branch in enumerate(rca_result['analysis_branches'], 1):
        print(f"\n{'─' * 80}")
        print(f"DAL {i}:")
        print(f"{'─' * 80}")
        
        immediate = branch['immediate_cause']
        print(f"\n🔴 IMMEDIATE CAUSE [{immediate['code']}]:")
        print(f"   {immediate.get('standard_title_tr', '')}")
        print(f"   {immediate['cause_tr']}")
        
        five_why = branch['five_why_chain']
        print(f"\n🔗 5-WHY ZİNCİRİ:")
        
        for why in five_why['whys']:
            print(f"\n   Why {why['level']}: {why['question_tr']}")
            print(f"   → {why['answer_tr']}")
        
        root = five_why['root_cause']
        print(f"\n🎯 ROOT CAUSE [{root['code']}]:")
        print(f"   {root.get('standard_title_tr', '')}")
        print(f"   {root['custom_description_tr']}")
    
    print("\n" + "=" * 80)
    print("✅ TEST 1 TAMAMLANDI")
    print("=" * 80)
    
    return rca_result


def test_scenario_2_detailed():
    """Test 2: Detaylı input ile analiz"""
    
    print("\n" + "=" * 80)
    print("TEST 2: DETAYLI INPUT - ELEKTRİK ÇARPMASI")
    print("=" * 80)
    
    # Detaylı olay girişi
    incident_text = """
    OLAY RAPORU - ELEKTRİK ÇARPMA KAZASI
    
    TARİH: 15 Şubat 2026, Saat: 14:30
    YER: Bakım atölyesi, elektrik panosu #3
    ETKİLENEN: Kemal Arslan, 29 yaş, Bakım Teknisyeni, 4 yıl deneyim
    
    OLAY:
    Bakım teknisyeni elektrik panosunda rutin bakım yaparken 380V akımına kapıldı.
    Eller ve kolda 2. derece yanık oluştu. Ambulans ile hastaneye kaldırıldı.
    
    TESPİTLER:
    - LOTO prosedürü uygulanmadı
    - Elektrik enerjisi kesilmedi
    - İzole eldiven kullanılmadı
    - Pano kapağında "ENERJİLİ" etiketi mevcut değildi
    - Çalışan daha önce LOTO eğitimi almış ancak tazeleme eğitimi yapılmamış
    - Benzer bir olay 6 ay önce yaşanmış, aksiyon kapatılmamış
    
    TANIKLAR:
    - Ali Yılmaz (Formen): "Kemal'in panoya dokunduğunu gördüm, sonra elektrik çarptı"
    - Mehmet Demir (İş arkadaşı): "LOTO yapmıyoruz genelde, zaman kaybı diyorlar"
    
    PROSEDÜR DURUMU:
    - LOTO prosedürü mevcut (rev. 2023)
    - Elektrikli ekipman bakım talimatı mevcut
    - Risk değerlendirmesi 2024'te yapılmış, LOTO vurgulanmış
    """
    
    print("\n📝 OLAY GİRİŞİ:")
    print(incident_text[:300] + "...\n")
    
    # Step 1: Input processor
    processor = HybridInputProcessor()
    level, details = processor.detect_input_level(incident_text)
    
    print(f"\n📊 GİRDİ SEVİYESİ: Level {level}")
    print(f"Detay puanı: {details['detail_score']}/13")
    print(f"Mevcut kategoriler: {', '.join(details['present'])}")
    
    if details['missing']:
        print(f"Eksik kategoriler: {', '.join(details['missing'])}")
    else:
        print("✅ Tüm kategoriler mevcut!")
    
    # Step 2: Question Engine (kod-spesifik sorular)
    question_engine = QuestionEngine()
    
    # Olaydan çıkarılabilecek muhtemel kodlar
    suspected_codes = ['A1.1', 'A3.2', 'D3.1', 'D1.9']
    code_questions = question_engine.get_code_specific_questions(suspected_codes)
    
    print(f"\n❓ KOD-SPESİFİK SORULAR: {len(code_questions)} adet")
    for i, q in enumerate(code_questions[:4], 1):
        print(f"{i}. [Kod {q['hsg245_code']}] {q['question']}")
    
    # Step 3: RootCauseAgentV2
    print("\n🔍 KÖK NEDEN ANALİZİ BAŞLIYOR...")
    print("(Detaylı input, daha zengin analiz bekleniyor)\n")
    
    agent = RootCauseAgentV2()
    
    part1_data = {
        "description": incident_text,
        "incident_type": "Electrical shock",
        "affected_persons": ["Kemal Arslan, 29, Bakım Teknisyeni"],
        "consequences": ["2nd degree burns", "Hospitalization"]
    }
    
    part2_data = {
        "severity": "Major",
        "riddor_status": "RIDDOR - Electrical injury",
        "investigation_level": "Detailed"
    }
    
    # Analiz
    rca_result = agent.analyze_root_causes(part1_data, part2_data)
    
    # Sonuçları göster
    print("\n" + "=" * 80)
    print("SONUÇLAR")
    print("=" * 80)
    
    print(f"\n🌿 Toplam Dal Sayısı: {len(rca_result['analysis_branches'])}")
    
    for i, branch in enumerate(rca_result['analysis_branches'], 1):
        print(f"\n{'─' * 80}")
        print(f"DAL {i}:")
        print(f"{'─' * 80}")
        
        immediate = branch['immediate_cause']
        print(f"\n🔴 [{immediate['code']}] {immediate['cause_tr']}")
        
        five_why = branch['five_why_chain']
        
        # Sadece kritik why'ları göster
        print(f"\n   Why 1: {five_why['whys'][0]['answer_tr']}")
        print(f"   Why 2: {five_why['whys'][1]['answer_tr']}")
        print(f"   ...")
        print(f"   Why 5: {five_why['whys'][4]['answer_tr']}")
        
        root = five_why['root_cause']
        print(f"\n🎯 [{root['code']}] {root['custom_description_tr']}")
    
    print("\n" + "=" * 80)
    print("✅ TEST 2 TAMAMLANDI")
    print("=" * 80)
    
    return rca_result


def test_scenario_3_user_context():
    """Test 3: Kullanıcı cevaplarıyla zenginleştirilmiş analiz (simüle)"""
    
    print("\n" + "=" * 80)
    print("TEST 3: KULLANICI CONTEXT İLE ANALİZ (Simüle)")
    print("=" * 80)
    
    incident_text = """
    Çalışan 3 metre yükseklikten düştü. Bacakta kırık oluştu.
    """
    
    print("\n📝 OLAY GİRİŞİ (Minimal):")
    print(incident_text)
    
    # Simüle edilmiş kullanıcı cevapları
    user_answers = {
        "prosedür": "İskele kurulum prosedürü vardı ama çalışan bilmiyordu",
        "ekipman": "İskele malzemesi eksikti, improvize yapıldı",
        "eğitim": "Çalışan yüksekte çalışma eğitimi almamış",
        "ppe": "Emniyet kemeri vardı ama kullanılmadı",
        "yönetim": "Denetim yapılmadı, yönetim göz yumuyor"
    }
    
    print("\n💬 KULLANICI CEVAPLARI:")
    for category, answer in user_answers.items():
        print(f"   [{category}] {answer}")
    
    # Question Engine - context hazırlama (simüle)
    print("\n🔧 CONTEXT HAZIRLANIYOR...")
    
    context = {
        "immediate_cause_hints": ["A1.1", "A3.2", "D3.1"],
        "context_for_why": {
            "prosedür_durumu": user_answers["prosedür"],
            "ekipman_durumu": user_answers["ekipman"],
            "eğitim_durumu": user_answers["eğitim"],
            "ppe_durumu": user_answers["ppe"],
            "yönetim_durumu": user_answers["yönetim"]
        }
    }
    
    print("✅ Context hazır:")
    print(f"   Kod ipuçları: {', '.join(context['immediate_cause_hints'])}")
    print(f"   Context alanları: {len(context['context_for_why'])} kategori")
    
    # Not: Şu anda RootCauseAgentV2'de _perform_5why_chain_hybrid() yok
    # Bu test sadece veri yapısını gösteriyor
    
    print("\n⚠️  NOT: _perform_5why_chain_hybrid() henüz implement edilmedi")
    print("Bu test, gelecekteki entegrasyon için veri yapısını gösteriyor.")
    
    # Standart analiz (user context olmadan)
    print("\n🔍 Standart analiz yapılıyor (user context inject edilmeyecek - henüz)...")
    
    agent = RootCauseAgentV2()
    
    # Context'i incident_summary'ye manuel ekleyerek simüle edelim
    enriched_text = incident_text + "\n\nEK BİLGİLER (Kullanıcı girişi):\n"
    for category, answer in user_answers.items():
        enriched_text += f"- {category.capitalize()}: {answer}\n"
    
    print("\n📋 Zenginleştirilmiş metin:")
    print(enriched_text)
    
    part1_data = {
        "description": enriched_text,
        "incident_type": "Fall from height",
        "affected_persons": ["Worker"],
        "consequences": ["Broken leg"]
    }
    
    part2_data = {
        "severity": "Major",
        "riddor_status": "RIDDOR",
        "investigation_level": "Detailed"
    }
    
    rca_result = agent.analyze_root_causes(part1_data, part2_data)
    
    # Sonuçları göster
    print("\n" + "=" * 80)
    print("SONUÇLAR (User context manuel eklendi)")
    print("=" * 80)
    
    for i, branch in enumerate(rca_result['analysis_branches'], 1):
        immediate = branch['immediate_cause']
        root = branch['five_why_chain']['root_cause']
        
        print(f"\n{i}. [{immediate['code']}] → [{root['code']}]")
        print(f"   Immediate: {immediate['cause_tr'][:60]}...")
        print(f"   Root: {root['custom_description_tr'][:60]}...")
    
    print("\n" + "=" * 80)
    print("✅ TEST 3 TAMAMLANDI")
    print("=" * 80)
    
    return rca_result


def save_test_results(results: dict, test_name: str):
    """Test sonuçlarını JSON olarak kaydet"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_5why_{test_name}_{timestamp}.json"
    filepath = os.path.join(os.path.dirname(__file__), "..", "outputs", filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Test sonuçları kaydedildi: {filename}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🧪 5-WHY INTEGRATION TEST SUITE")
    print("RootCauseAgentV2 + QuestionEngine Entegrasyon Testi")
    print("=" * 80)
    
    try:
        # Test 1: Minimal input
        result1 = test_scenario_1_minimal()
        save_test_results(result1, "minimal_forklift")
        
        print("\n\n" + "⏸" * 40)
        input("Enter tuşuna basarak Test 2'ye geçin...")
        
        # Test 2: Detaylı input
        result2 = test_scenario_2_detailed()
        save_test_results(result2, "detailed_electrical")
        
        print("\n\n" + "⏸" * 40)
        input("Enter tuşuna basarak Test 3'e geçin...")
        
        # Test 3: User context (simüle)
        result3 = test_scenario_3_user_context()
        save_test_results(result3, "usercontext_fall")
        
        print("\n\n" + "=" * 80)
        print("🎉 TÜM TESTLER TAMAMLANDI!")
        print("=" * 80)
        print("\n📊 Özet:")
        print(f"   Test 1 (Minimal): {len(result1['analysis_branches'])} dal")
        print(f"   Test 2 (Detaylı): {len(result2['analysis_branches'])} dal")
        print(f"   Test 3 (Context): {len(result3['analysis_branches'])} dal")
        print("\n✅ Tüm sonuçlar outputs/ klasörüne kaydedildi")
        
    except Exception as e:
        print(f"\n❌ HATA: {str(e)}")
        import traceback
        traceback.print_exc()
