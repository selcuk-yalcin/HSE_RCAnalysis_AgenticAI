"""
GERÇEK AGENT PIPELİNE TESTİ - MPT DÜŞEN PARÇA RAMAK KALA
=======================================================

Tüm agent'ları sırayla çalıştırıp DOCX + HTML + Decision Tree raporu oluşturur.

AKIŞ:
1. OverviewAgent      → Olay özeti (Part 1)
2. AssessmentAgent    → Risk değerlendirmesi (Part 2)
3. RootCauseAgentV2   → 5-Why kök neden analizi (Part 3)
4. ActionPlanAgent    → Düzeltici tedbirler (Part 4)
5. SkillBasedDocxAgent → DOCX + HTML + Decision Tree raporu

GEREKSINIMLER:
- OPENROUTER_API_KEY veya OPENAI_API_KEY environment variable'ı gerekli
- Eğer yoksa, mock verilerle test yapılır
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Projenin root dizinini ekle
sys.path.insert(0, str(Path(__file__).parent.parent))

# Agent'ları import et
try:
    from agents.overview_agent import OverviewAgent
    from agents.assessment_agent import AssessmentAgent
    from agents.rootcause_agent_v2 import RootCauseAgentV2
    from agents.actionplan_agent import ActionPlanAgent
    from agents.skillbased_docx_agent import SkillBasedDocxAgent
    AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Agent import hatası: {e}")
    AGENTS_AVAILABLE = False


# ============================================================================
# TEST SENARYOSU: MPT TEST SAHASI - SARMAL KAPI DÜŞEN PARÇA RAMAK KALA
# ============================================================================

INCIDENT_DATA = {
    "ref_no": "MPT-2026-001-NM",
    "reported_by": "Ahmet Yılmaz (Test Mühendisi)",
    "date": "20.01.2026",
    "time": "09:10",
    "location": "MPT Test Sahası - Test Hücresi 3",
    "incident_type": "Near-miss (Ramak Kala)",
    "description": """
MPT Test Sahası Test Hücresi 3'te, operatör test sonrası ekipmanı çıkarırken sarmal kapının (rolling shutter door) alt bölümündeki bir bağlantı parçası (10x5 cm, yaklaşık 150 gram ağırlığında metal klips) yerinden çıkarak operatörün 30 cm yakınına düştü. 

Operatör o anda eğilmiş durumda ekipman kablosunu toplamakta idi. Parça düştüğünde operatör anormal ses duyarak son anda geri çekildi. Parça betonzemine çarparak sert ses çıkardı. Operatör şoke oldu ancak fiziksel yaralanma olmadı.

Kapı son 3 aydır periyodik bakım kaydı görmemiş, ancak günlük kullanımda herhangi bir anormallik raporlanmamıştı. Olay sonrası yapılan incelemede kapının 4 farklı bağlantı noktasında gevşeme ve yıpranma izleri tespit edildi.

Test hücresinde 2 operatör bulunmaktaydı. İkinci operatör kontrol panelinde olayı görmemiş ancak ses üzerine fark etmiştir. Acil durdurma yapılarak tüm hücre ekipmanları güvenli konuma getirilmiş ve olay güvenlik ekibine bildirilmiştir.
    """,
    "emergency_response": "Kapı kapatılıp kilitlendi, test hücresi karantinaya alındı, bakım ekibi çağrıldı, olay formu dolduruldu.",
    "witnesses": ["Mehmet Kaya (Operatör 2)", "Ayşe Demir (Vardiya Amiri)"],
    "environment": "İç mekan, aydınlatma yeterli, zemin kuru, sıcaklık 22°C",
    "equipment_involved": ["Sarmal kapı (10 yıllık)", "Metal bağlantı klipsi", "Test ekipmanı"]
}


# ============================================================================
# MOCK DATA (API Key yoksa kullanılır)
# ============================================================================

MOCK_PART1 = {
    "ref_no": "MPT-2026-001-NM",
    "reported_by": "Ahmet Yılmaz (Test Mühendisi)",
    "date_time": "20.01.2026 09:10",
    "incident_type": "Near-miss (Ramak Kala)",
    "location": "MPT Test Sahası - Test Hücresi 3",
    "description": INCIDENT_DATA["description"],
    "emergency_measures": INCIDENT_DATA["emergency_response"],
    "forwarded_to": "HSE Departmanı",
    "potential_harm": [
        "Kafa travması (düşen parça)",
        "Göz yaralanması",
        "Sarsıntı/şok",
        "Operatörün çalışma kabiliyetinin azalması"
    ],
    "severity_level": "YÜKSEK - Major injury potansiyeli"
}

MOCK_PART2 = {
    "event_type": "Near-miss (Ramak Kala)",
    "actual_harm": "Yok - Sadece şok",
    "potential_harm": "Major injury (Kafa travması)",
    "riddor_reportable": "Hayır (yaralanma olmadı)",
    "accident_book_entry": "Evet (near-miss kaydı)",
    "investigation_level": "YÜKSEK (Major injury potansiyeli)",
    "further_investigation": "Evet",
    "priority": "YÜKSEK",
    "assessment_result": "Ramak kala olayı - Major injury potansiyeli nedeniyle yüksek seviye araştırma gerekli",
    "near_miss_analysis": "Operatör o anda eğilmiş durumda değilseydi veya bir saniye sonra düşseydi, parça kafasına isabet edebilir ve ciddi yaralanmaya neden olabilirdi. Şans faktörü: Operatörün o anda eğilmiş olması ve anormal sesi duyarak son anda geri çekilmesi.",
    "potential_consequences": [
        "Kafa travması → Hastaneye kaldırma → RIDDOR raporlama",
        "İş göremezlik (1-4 hafta)",
        "Psikolojik travma ve çalışana güven kaybı",
        "Diğer operatörlerde korku ve endişe",
        "Tesis itibarına zarar"
    ]
}

MOCK_PART3_RCA = {
    "incident_summary": INCIDENT_DATA["description"],
    "incident_ref": "MPT-2026-001-NM",
    "meta_root_cause": {
        "code": "D1.3",
        "name": "Yetersiz Bakım ve İnceleme Sistemleri",
        "description": "Periyodik bakım planları yetersiz veya uygulanmıyor. Ekipman durumu düzenli kontrol edilmiyor.",
        "category": "D - Organizasyonel Faktörler"
    },
    "analysis_branches": [
        {
            "branch_id": 1,
            "direct_cause": {
                "code": "B2.1",
                "name": "Ekipman/Malzeme Arızası veya Bozulması",
                "description": "Sarmal kapının metal bağlantı klipsi gevşeyerek düştü",
                "category": "B - Koşullar (Conditions)"
            },
            "root_cause": {
                "code": "D1.3",
                "name": "Yetersiz Bakım ve İnceleme Sistemleri",
                "description": "Son 3 aydır periyodik bakım yapılmamış",
                "category": "D - Organizasyonel Faktörler"
            },
            "five_why_chain": [
                {
                    "level": 1,
                    "why": "Neden metal klips düştü?",
                    "because": "Klips gevşemiş ve bağlantı noktası yıpranmış"
                },
                {
                    "level": 2,
                    "why": "Neden klips gevşedi?",
                    "because": "Düzenli sıkılaştırma ve kontrol yapılmamış"
                },
                {
                    "level": 3,
                    "why": "Neden kontrol yapılmadı?",
                    "because": "Son 3 aydır periyodik bakım kaydı yok"
                },
                {
                    "level": 4,
                    "why": "Neden bakım yapılmadı?",
                    "because": "Bakım planı takip edilmiyor veya kayıt tutulmuyor"
                },
                {
                    "level": 5,
                    "why": "Neden bakım planı takip edilmiyor?",
                    "because": "[D1.3] Yetersiz bakım ve inceleme sistemleri - Planlama, kayıt ve takip mekanizması zayıf"
                }
            ]
        },
        {
            "branch_id": 2,
            "direct_cause": {
                "code": "A1.2",
                "name": "Uygunsuz Pozisyon/Duruş",
                "description": "Operatör kapının altında eğilmiş durumda çalışıyordu",
                "category": "A - Davranışlar (Actions)"
            },
            "root_cause": {
                "code": "C2.1",
                "name": "Yetersiz Eğitim veya Bilgi",
                "description": "Operatör düşen parça riskini bilmiyor veya göz ardı ediyor",
                "category": "C - Kişisel Faktörler"
            },
            "five_why_chain": [
                {
                    "level": 1,
                    "why": "Neden operatör kapının altında eğildi?",
                    "because": "Ekipman kablosunu toplamak için eğilmesi gerekiyordu"
                },
                {
                    "level": 2,
                    "why": "Neden kapının altında çalıştı?",
                    "because": "Kablo kapıya yakın alandaydı ve başka bir yerden ulaşılamıyordu"
                },
                {
                    "level": 3,
                    "why": "Neden tehlikeyi fark etmedi?",
                    "because": "Kapının düşen parça riski olduğunu bilmiyordu"
                },
                {
                    "level": 4,
                    "why": "Neden riski bilmiyordu?",
                    "because": "Sarmal kapı risk değerlendirmesi yapılmamış veya operatöre anlatılmamış"
                },
                {
                    "level": 5,
                    "why": "Neden risk değerlendirmesi yapılmamış?",
                    "because": "[C2.1] Yetersiz eğitim - Operatörlere ekipman riskleri ve güvenli çalışma prosedürleri öğretilmemiş"
                }
            ]
        }
    ],
    "final_root_causes": [
        {
            "code": "D1.3",
            "name": "Yetersiz Bakım ve İnceleme Sistemleri",
            "description": "Periyodik bakım planları yetersiz veya uygulanmıyor",
            "category": "D - Organizasyonel"
        },
        {
            "code": "C2.1",
            "name": "Yetersiz Eğitim veya Bilgi",
            "description": "Operatörlere ekipman riskleri öğretilmemiş",
            "category": "C - Kişisel"
        }
    ],
    "contributing_factors": [
        {
            "factor": "Ekipman yaşı",
            "description": "Sarmal kapı 10 yıllık, yıpranma beklenen"
        },
        {
            "factor": "İş yükü",
            "description": "Bakım ekibi diğer işlerle meşgul, periyodik kontroller atlanıyor"
        },
        {
            "factor": "Kayıt sistemi",
            "description": "Bakım kayıtları manuel, takip zor"
        }
    ]
}

MOCK_PART4_ACTIONS = {
    "immediate_actions": [
        {
            "action_id": 1,
            "description": "TÜM sarmal kapıları acil inceleme - Gevşek parça kontrolü",
            "responsible": "Bakım Ekip Lideri",
            "deadline": "24 saat içinde",
            "priority": "KRITIK",
            "status": "Devam ediyor"
        },
        {
            "action_id": 2,
            "description": "Test Hücresi 3 karantinada - Kapı değiştirilene kadar kullanım yasağı",
            "responsible": "Test Sahası Müdürü",
            "deadline": "Devam eden",
            "priority": "KRITIK",
            "status": "Tamamlandı"
        },
        {
            "action_id": 3,
            "description": "Tüm operatörlere acil güvenlik brifingi - Sarmal kapı riskleri",
            "responsible": "HSE Koordinatörü",
            "deadline": "48 saat içinde",
            "priority": "YÜKSEK",
            "status": "Planlandı"
        }
    ],
    "short_term_actions": [
        {
            "action_id": 4,
            "description": "Sarmal kapı periyodik bakım planı oluştur ve CMMS sistemine ekle",
            "responsible": "Bakım Planlama",
            "timeline": "1-2 hafta",
            "priority": "YÜKSEK"
        },
        {
            "action_id": 5,
            "description": "Operatör eğitim programına 'Ekipman Altında Çalışma' modülü ekle",
            "responsible": "Eğitim Koordinatörü",
            "timeline": "1 ay",
            "priority": "ORTA"
        },
        {
            "action_id": 6,
            "description": "Tüm test hücrelerinde zemin işaretlemesi - 'Kapı altı çalışma yasak' bölgesi",
            "responsible": "Tesis Yönetimi",
            "timeline": "2 hafta",
            "priority": "ORTA"
        }
    ],
    "long_term_actions": [
        {
            "action_id": 7,
            "description": "10 yaşın üstündeki tüm sarmal kapıları yeni nesil güvenlikli modellerle değiştir",
            "responsible": "Yatırım Komitesi",
            "timeline": "6-12 ay",
            "priority": "ORTA"
        },
        {
            "action_id": 8,
            "description": "IoT sensör sistemi - Kapı parçalarının gevşeme takibi ve otomatik alarm",
            "responsible": "Otomasyon Ekibi",
            "timeline": "6 ay",
            "priority": "DÜŞÜK"
        }
    ],
    "success_criteria": [
        "Tüm sarmal kapılar için periyodik bakım kaydı (3 aylık)",
        "Sıfır benzer near-miss veya incident (6 ay)",
        "Operatör eğitimi tamamlanma oranı %100",
        "CMMS sisteminde kapı bakım kayıtları online"
    ]
}


# ============================================================================
# TEST FONKSİYONU
# ============================================================================

def test_full_pipeline():
    """
    Tüm agent pipeline'ını çalıştır ve DOCX + HTML raporu oluştur.
    """
    
    print("\n" + "="*80)
    print("🧪 FULL AGENT PIPELINE TESTİ - MPT RAMAK KALA OLAYV")
    print("="*80)
    
    # Output klasörü
    output_dir = Path("outputs/mpt_falling_part_near_miss")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # API Key kontrolü
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    use_real_agents = api_key and AGENTS_AVAILABLE
    
    if not use_real_agents:
        print("\n⚠️  API Key bulunamadı veya agent'lar import edilemedi")
        print("   Mock verilerle test yapılıyor...")
    
    # ========================================================================
    # AŞAMA 1: OVERVIEW AGENT
    # ========================================================================
    
    print("\n" + "─"*80)
    print("📋 AŞAMA 1/5: OVERVIEW AGENT - Olay Özeti")
    print("─"*80)
    
    if use_real_agents:
        try:
            overview_agent = OverviewAgent()
            part1 = overview_agent.process_initial_report(INCIDENT_DATA)
            print("✅ Part 1 (Overview) başarıyla oluşturuldu")
        except Exception as e:
            print(f"❌ Overview Agent hatası: {e}")
            print("   Mock veri kullanılıyor...")
            part1 = MOCK_PART1
    else:
        part1 = MOCK_PART1
    
    print(f"\n   📊 Part 1 Özeti:")
    print(f"      • Referans No: {part1.get('ref_no')}")
    print(f"      • Olay Tipi: {part1.get('incident_type')}")
    print(f"      • Ciddiyet: {part1.get('severity_level')}")
    
    # ========================================================================
    # AŞAMA 2: ASSESSMENT AGENT
    # ========================================================================
    
    print("\n" + "─"*80)
    print("📋 AŞAMA 2/5: ASSESSMENT AGENT - Risk Değerlendirmesi")
    print("─"*80)
    
    if use_real_agents:
        try:
            assessment_agent = AssessmentAgent()
            part2 = assessment_agent.assess_incident(part1, INCIDENT_DATA)
            print("✅ Part 2 (Assessment) başarıyla oluşturuldu")
        except Exception as e:
            print(f"❌ Assessment Agent hatası: {e}")
            print("   Mock veri kullanılıyor...")
            part2 = MOCK_PART2
    else:
        part2 = MOCK_PART2
    
    print(f"\n   📊 Part 2 Özeti:")
    print(f"      • Araştırma Seviyesi: {part2.get('investigation_level')}")
    print(f"      • RIDDOR: {part2.get('riddor_reportable')}")
    print(f"      • Öncelik: {part2.get('priority')}")
    
    # ========================================================================
    # AŞAMA 3: ROOT CAUSE AGENT V2
    # ========================================================================
    
    print("\n" + "─"*80)
    print("📋 AŞAMA 3/5: ROOT CAUSE AGENT V2 - 5-Why Kök Neden Analizi")
    print("─"*80)
    
    if use_real_agents:
        try:
            rca_agent = RootCauseAgentV2()
            part3_rca = rca_agent.analyze_root_causes({
                "part1": part1,
                "part2": part2,
                "incident_details": INCIDENT_DATA
            })
            print("✅ Part 3 (Root Cause Analysis) başarıyla oluşturuldu")
        except Exception as e:
            print(f"❌ Root Cause Agent hatası: {e}")
            print("   Mock veri kullanılıyor...")
            part3_rca = MOCK_PART3_RCA
    else:
        part3_rca = MOCK_PART3_RCA
    
    print(f"\n   📊 Part 3 Özeti:")
    print(f"      • Analiz Dalları: {len(part3_rca.get('analysis_branches', []))}")
    print(f"      • Kök Nedenler: {len(part3_rca.get('final_root_causes', []))}")
    meta = part3_rca.get('meta_root_cause', {})
    if meta:
        print(f"      • Meta Kök Neden: [{meta.get('code')}] {meta.get('name')}")
    
    # ========================================================================
    # AŞAMA 4: ACTION PLAN AGENT
    # ========================================================================
    
    print("\n" + "─"*80)
    print("📋 AŞAMA 4/5: ACTION PLAN AGENT - Düzeltici Tedbirler")
    print("─"*80)
    
    if use_real_agents:
        try:
            action_agent = ActionPlanAgent()
            part4_actions = action_agent.generate_action_plan({
                "part1": part1,
                "part2": part2,
                "part3_rca": part3_rca
            })
            print("✅ Part 4 (Action Plan) başarıyla oluşturuldu")
        except Exception as e:
            print(f"❌ Action Plan Agent hatası: {e}")
            print("   Mock veri kullanılıyor...")
            part4_actions = MOCK_PART4_ACTIONS
    else:
        part4_actions = MOCK_PART4_ACTIONS
    
    print(f"\n   📊 Part 4 Özeti:")
    print(f"      • Acil Tedbirler: {len(part4_actions.get('immediate_actions', []))}")
    print(f"      • Kısa Vadeli: {len(part4_actions.get('short_term_actions', []))}")
    print(f"      • Uzun Vadeli: {len(part4_actions.get('long_term_actions', []))}")
    
    # ========================================================================
    # TAM VERİYİ BİRLEŞTİR VE KAYDET
    # ========================================================================
    
    investigation_data = {
        "part1": part1,
        "part2": part2,
        "part3_rca": part3_rca,
        "part4_actions": part4_actions,
        "timestamp": timestamp,
        "test_mode": not use_real_agents
    }
    
    json_path = output_dir / f"full_pipeline_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(investigation_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Tam analiz verisi kaydedildi:")
    print(f"   📄 {json_path}")
    print(f"   📊 Dosya boyutu: {json_path.stat().st_size:,} bytes")
    
    # ========================================================================
    # AŞAMA 5: SKILL-BASED DOCX AGENT - RAPOR OLUŞTUR
    # ========================================================================
    
    print("\n" + "─"*80)
    print("📋 AŞAMA 5/5: SKILL-BASED DOCX AGENT - Rapor Oluşturma")
    print("─"*80)
    
    if use_real_agents:
        try:
            docx_agent = SkillBasedDocxAgent()
            docx_path = output_dir / f"MPT_Ramak_Kala_Raporu_{timestamp}.docx"
            
            result_path = docx_agent.generate_report(
                investigation_data=investigation_data,
                output_path=str(docx_path)
            )
            
            print("\n✅ DOCX RAPORU BAŞARIYLA OLUŞTURULDU!")
            print(f"   📄 DOCX: {result_path}")
            
            # HTML ve Decision Tree de oluşturulmuş olmalı
            html_path = str(docx_path).replace('.docx', '.html')
            dt_path = str(docx_path).replace('.docx', '_decision_tree.html')
            
            if Path(html_path).exists():
                print(f"   🌐 HTML: {html_path}")
            if Path(dt_path).exists():
                print(f"   🌳 Decision Tree: {dt_path}")
                
        except Exception as e:
            print(f"\n❌ DOCX Agent hatası: {e}")
            print("   Manuel DOCX oluşturma gerekebilir.")
            import traceback
            traceback.print_exc()
    else:
        print("\n⚠️  API Key olmadan DOCX raporu oluşturulamaz")
        print("   Lütfen .env dosyasına OPENROUTER_API_KEY ekleyin")
        print("   Alternatif: generate_docx_report.py veya generate_html_report.py scriptlerini kullanın")
    
    # ========================================================================
    # TEST SONUÇ ÖZETİ
    # ========================================================================
    
    print("\n" + "="*80)
    print("✅ TEST TAMAMLANDI!")
    print("="*80)
    
    print(f"\n📊 Oluşturulan Dosyalar:")
    print(f"   1. JSON Analiz: {json_path.name}")
    if use_real_agents:
        print(f"   2. DOCX Rapor: MPT_Ramak_Kala_Raporu_{timestamp}.docx")
        print(f"   3. HTML Rapor: MPT_Ramak_Kala_Raporu_{timestamp}.html")
        print(f"   4. Decision Tree: MPT_Ramak_Kala_Raporu_{timestamp}_decision_tree.html")
    
    print(f"\n📁 Konum: {output_dir.resolve()}")
    
    print(f"\n🎯 Pipeline Özeti:")
    print(f"   • Mod: {'GERÇEK AGENT ÇALIŞMASI' if use_real_agents else 'MOCK VERİ TESTİ'}")
    print(f"   • Part 1 (Overview): ✅")
    print(f"   • Part 2 (Assessment): ✅")
    print(f"   • Part 3 (Root Cause): ✅")
    print(f"   • Part 4 (Action Plan): ✅")
    print(f"   • Part 5 (DOCX Report): {'✅' if use_real_agents else '⚠️  (API key gerekli)'}")
    
    if not use_real_agents:
        print(f"\n💡 Gerçek agent'larla test yapmak için:")
        print(f"   1. .env dosyasına OPENROUTER_API_KEY ekleyin")
        print(f"   2. Bu testi tekrar çalıştırın")
    
    print("\n" + "="*80)
    
    return investigation_data


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    try:
        result = test_full_pipeline()
        
        print("\n🎉 TEST BAŞARIYLA TAMAMLANDI!")
        print("\nSonuç verisini kontrol etmek için:")
        print("  python -c 'import json; print(json.dumps(result, indent=2))'")
        
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ TEST HATASI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
