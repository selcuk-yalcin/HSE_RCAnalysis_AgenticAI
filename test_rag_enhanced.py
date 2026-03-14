#!/usr/bin/env python3
"""
Test RAG-Enhanced RootCauseAgentV2
This script tests the agent WITH vector search augmentation
"""

import json
import sys
from agents.rootcause_agent_v2 import RootCauseAgentV2

def test_rag_enhanced():
    print("=" * 80)
    print("🚀 TEST: RootCauseAgentV2 with RAG Enhancement")
    print("=" * 80)

    # Test data - realistic incident
    part1_data = {
        "IncidentType": "Kesme Yaralanması",
        "IncidentTime": "2026-03-14 14:30",
        "LocationDescription": "Rafineriler - Boru Üretim Bölümü",
        "IncidentNarrative": """
        Bir işçi (35 yaş, 8 yıl deneyim) basınçlı hava testinden sonra ventili boşaltmaya çalışmıştır.
        Valve sıkışmış durumda idi. İşçi, alet kullanmadan elle açmaya zorlamış.
        Ventil aniden açılmış, basınçlı hava ve metal parçaları işçinin sol el parmağını kesmiştir.
        Yaralanma: derin kesik, 5 dikişe ihtiyaç. İlk yardım sahasında uygulandı.
        """
    }

    part2_data = {
        "ImmediateCauseAnalysis": "İşçi prosedürü biliyordu ama stresli durumda elle açmayı tercih etti",
        "IncidentContribution": "Ventil tasarımı, işçi davranışı",
        "ControlsPresent": "Güvenlik eğitimi vardı, prosedür vardı, alet sağlanmamıştı"
    }

    print("\n📋 Test Senaryosu: Basınçlı Hava Kaynağından Kesme Yaralanması")
    print("👤 Worker: 35 yaş, 8 yıl deneyim")
    print("📍 Location: Boru Üretim Bölümü, Rafineriler")
    print("⚕️  Injury: Derin kesik, 5 dikişe ihtiyaç")

    # Initialize agent WITH RAG
    print("\n" + "-" * 80)
    print("🔧 Initializing Agent with RAG...")
    print("-" * 80)
    
    try:
        agent = RootCauseAgentV2(use_rag=True)
        print("✅ Agent ready with RAG")
        
        if agent.rag_analyzer:
            print("   📊 RAG Analyzer: ACTIVE")
            print("   🗄️  Vector Store: MongoDB Atlas")
            print("   🎯 Causes Indexed: 158")
        else:
            print("   ⚠️  RAG not available, using static knowledge base")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False

    try:
        print("\n" + "-" * 80)
        print("🚀 Running Root Cause Analysis with RAG augmentation...")
        print("-" * 80)
        
        result = agent.analyze_root_causes(part1_data, part2_data)
        
        print("\n" + "=" * 80)
        print("📊 ANALYSIS RESULTS")
        print("=" * 80)
        
        if result:
            # Pretty print (first 1500 chars)
            result_str = json.dumps(result, indent=2, ensure_ascii=False)
            print(result_str[:1500])
            print("\n... (results truncated for display)")
            
            # Summary
            print("\n" + "-" * 80)
            print("📈 Summary:")
            print("-" * 80)
            print(f"✅ Analysis completed successfully")
            print(f"✅ Result size: {len(result_str)} characters")
            
            if isinstance(result, dict):
                # Check structure
                has_immediate = False
                has_root_causes = False
                
                if 'analysis_branches' in result:
                    branches = result['analysis_branches']
                    print(f"✅ Analysis branches: {len(branches)}")
                    
                    if branches and 'immediate_cause' in branches[0]:
                        has_immediate = True
                        cause_code = branches[0]['immediate_cause'].get('code', 'N/A')
                        print(f"✅ First branch immediate cause: [{cause_code}]")
                    
                    if branches and 'root_cause' in branches[0]:
                        has_root_causes = True
                        root_code = branches[0]['root_cause'].get('code', 'N/A')
                        print(f"✅ First branch root cause: [{root_code}]")
            
            return True
        else:
            print("⚠️  No result returned")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        print("\n" + "=" * 80)
        agent.cleanup()
        print("✅ Cleanup complete")
        print("=" * 80)


if __name__ == "__main__":
    success = test_rag_enhanced()
    sys.exit(0 if success else 1)
