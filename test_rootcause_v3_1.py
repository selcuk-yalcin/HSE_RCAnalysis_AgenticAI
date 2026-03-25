"""
Test Script for RootCause Agent V3.1 (DSPy)
============================================

Bu script V3.1'i test etmek için kullanılır.
- Real-world case'ler ile test
- V2.5 vs V3.1 karşılaştırması
- Performance metrics

KULLANIM:
    python test_rootcause_v3_1.py
    python test_rootcause_v3_1.py --compare  (V2.5 ile karşılaştır)
    python test_rootcause_v3_1.py --verbose  (Detaylı çıktı)
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List

# Add agents to path
sys.path.insert(0, str(Path(__file__).parent))

from rootcause_agent_v3_1 import (
    RootCauseAgentV3_1,
    check_v3_1_status,
    create_v3_1_agent
)

# Optional: V2.5 comparison
try:
    from rootcause_agent_v2 import RootCauseAgentV2
    V2_AVAILABLE = True
except ImportError:
    V2_AVAILABLE = False
    print("⚠️  V2.5 not available for comparison")


# ============================================================================
# TEST CASES
# ============================================================================

TEST_CASE_1 = {
    "name": "Forklift-Kapı Kazası",
    "part1_data": {
        "brief_details": {
            "what": "Forklift operatörü geri manevrada otomatik kapıya çarptı",
            "where": "Depo (Bölüm B)",
            "when": "2026-03-22 14:30",
            "who": "Operatör (25 yaş, 3 yıl deneyim)",
            "how": "Geri giderken kapı kapanırken görüş açısı dışında kaldı"
        },
        "description": "Forklift geri manevrada otomatik açılan kapıya çarptı. "
                      "Kapı kapanma süresi 5 saniye. Operatör manevra sırasında "
                      "kapı kodu göremedi."
    },
    "incident_type": "NEAR MISS"
}

TEST_CASE_2 = {
    "name": "Asansör Acil Durma",
    "part1_data": {
        "brief_details": {
            "what": "Asansör acil durdurma düğmesine yanlışlıkla basıldı",
            "where": "Ofis binası (5. kat)",
            "when": "2026-03-21 10:15",
            "who": "Asansör kullanıcısı",
            "how": "Paket taşırken düğmeye temas etti"
        },
        "description": "Asansöre giren kişi paket taşırken acil durma düğmesine "
                      "elini kaydırdı. Asansör aniden durdu. 12 kişi sıkışma riski ile karşılaştı."
    },
    "incident_type": "NEAR MISS"
}

TEST_CASE_3 = {
    "name": "Kimyasal Sızıntı",
    "part1_data": {
        "brief_details": {
            "what": "Kimyasal depo konteyneri kırıldı, sıvı sızıntı",
            "where": "Kimyasal depo",
            "when": "2026-03-20 16:45",
            "who": "Depo operatörü",
            "how": "Forklift ile sevkiyat sırasında konteyner yere düştü"
        },
        "description": "Forklift operatörü 50L'lik kimyasal konteynerini "
                      "taşırken yere düşürdü. Konteyner kırıldı, kimyasal sıvı "
                      "depo zeminine döküldü. Operatör hemen alanı işaretledi."
    },
    "incident_type": "INCIDENT"
}


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_v3_1_basic():
    """V3.1 temel test"""
    print("\n" + "=" * 80)
    print("TEST 1: V3.1 Temel Fonksiyon Kontrolü")
    print("=" * 80)
    
    # Status check
    status = check_v3_1_status()
    print(f"\n✅ Versiyon: {status['version']}")
    print(f"✅ Durum: {status['status']}")
    print(f"✅ DSPy: {status['dspy_available']}")
    print(f"✅ RAG: {status['rag_available']}")
    
    # Create agent
    print("\n🔧 Agent oluşturuluyor...")
    agent = create_v3_1_agent(use_rag=False, enable_diversity=True)
    print("✅ Agent başarıyla oluşturuldu")
    
    return agent


def test_v3_1_single_case(agent, test_case: Dict, verbose: bool = False):
    """Tek test case'i çalıştır"""
    
    print(f"\n{'=' * 80}")
    print(f"TEST CASE: {test_case['name']}")
    print(f"{'=' * 80}")
    
    start_time = time.time()
    
    try:
        result = agent.analyze_root_causes(
            part1_data=test_case["part1_data"],
            part2_data={},
            investigation_data=None,
            synthesize_meta_root=True
        )
        
        elapsed = time.time() - start_time
        
        # Sonuçları özetle
        print(f"\n{'─' * 80}")
        print("📊 SONUÇLAR")
        print(f"{'─' * 80}")
        
        print(f"⏱️  Süre: {elapsed:.2f} saniye")
        print(f"📍 Dallar: {len(result['analysis_branches'])}")
        print(f"🎯 Root Causes: {len(result['final_root_causes'])}")
        
        if result.get('chain_quality_scores'):
            avg_quality = sum(result['chain_quality_scores']) / len(result['chain_quality_scores'])
            print(f"📈 Ortalama Zincir Kalitesi: {avg_quality:.1%}")
        
        print(f"\n🔴 ROOT CAUSES:")
        for i, rc in enumerate(result.get('final_root_causes', []), 1):
            code = rc.get('code', '???')
            cause = rc.get('cause_tr', '???')
            confidence = rc.get('confidence', 0.0)
            print(f"  {i}. [{code}] {cause} (Güven: {confidence:.1%})")
        
        if result.get('meta_root_cause'):
            meta = result['meta_root_cause']
            print(f"\n🔗 META ROOT CAUSE:")
            print(f"  [{meta.get('code')}] {meta.get('cause_tr')}")
        
        if verbose:
            print(f"\n📄 DETAYLI RAPOR:")
            print(result.get('final_report_tr', 'N/A')[:500] + "...")
        
        print(f"\n✅ Test başarıyla tamamlandı")
        
        return {
            "success": True,
            "elapsed_time": elapsed,
            "root_causes_count": len(result['final_root_causes']),
            "chain_quality": avg_quality if result.get('chain_quality_scores') else 0.0,
            "result": result
        }
        
    except Exception as e:
        print(f"\n❌ Test başarısız: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "error": str(e)
        }


def test_v3_1_all_cases(verbose: bool = False):
    """Tüm test case'lerini çalıştır"""
    print("\n" + "=" * 80)
    print("🧪 V3.1 COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    agent = test_v3_1_basic()
    
    test_cases = [TEST_CASE_1, TEST_CASE_2, TEST_CASE_3]
    results = []
    
    for test_case in test_cases:
        result = test_v3_1_single_case(agent, test_case, verbose=verbose)
        results.append(result)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SONUÇ ÖZETİ")
    print("=" * 80)
    
    successful = sum(1 for r in results if r.get('success'))
    failed = len(results) - successful
    
    print(f"\n✅ Başarılı: {successful}/{len(results)}")
    print(f"❌ Başarısız: {failed}/{len(results)}")
    
    if successful > 0:
        avg_time = sum(r['elapsed_time'] for r in results if r.get('success')) / successful
        avg_quality = sum(r.get('chain_quality', 0) for r in results if r.get('success')) / successful
        
        print(f"\n⏱️  Ortalama Zaman: {avg_time:.2f} saniye")
        print(f"📈 Ortalama Zincir Kalitesi: {avg_quality:.1%}")
    
    return results


def compare_v2_vs_v3_1():
    """V2.5 vs V3.1 karşılaştırması"""
    if not V2_AVAILABLE:
        print("⚠️  V2.5 comparison not available")
        return
    
    print("\n" + "=" * 80)
    print("🔄 V2.5 vs V3.1 KARŞILAŞTIRMASI")
    print("=" * 80)
    
    test_case = TEST_CASE_1
    
    print(f"\nTest Case: {test_case['name']}")
    
    # V2.5
    print("\n--- V2.5 (Baseline) ---")
    v25_agent = RootCauseAgentV2(use_rag=False)
    v25_start = time.time()
    v25_result = v25_agent.analyze_root_causes(
        part1_data=test_case["part1_data"],
        part2_data={},
        investigation_data=None
    )
    v25_time = time.time() - v25_start
    
    print(f"Zaman: {v25_time:.2f}s")
    print(f"Root Causes: {len(v25_result.get('final_root_causes', []))}")
    
    # V3.1
    print("\n--- V3.1 (DSPy) ---")
    v31_agent = create_v3_1_agent(use_rag=False)
    v31_start = time.time()
    v31_result = v31_agent.analyze_root_causes(
        part1_data=test_case["part1_data"],
        part2_data={},
        investigation_data=None
    )
    v31_time = time.time() - v31_start
    
    print(f"Zaman: {v31_time:.2f}s")
    print(f"Root Causes: {len(v31_result.get('final_root_causes', []))}")
    
    # Karşılaştırma
    print("\n--- KARŞILAŞTIRMA ---")
    print(f"Zaman: {v25_time:.2f}s → {v31_time:.2f}s ({(v31_time/v25_time - 1)*100:+.1f}%)")
    print(f"Zincir Kalitesi: ? → {v31_result.get('chain_quality_scores', [0.0])[0] if v31_result.get('chain_quality_scores') else '?':.1%}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="V3.1 Test Suite")
    parser.add_argument("--compare", action="store_true", help="V2.5 ile karşılaştır")
    parser.add_argument("--verbose", action="store_true", help="Detaylı çıktı")
    parser.add_argument("--single", type=int, help="Tek test case çalıştır (1-3)")
    
    args = parser.parse_args()
    
    try:
        if args.single:
            test_cases = [TEST_CASE_1, TEST_CASE_2, TEST_CASE_3]
            if args.single < 1 or args.single > len(test_cases):
                print(f"❌ Invalid case: {args.single}")
                sys.exit(1)
            
            agent = test_v3_1_basic()
            test_v3_1_single_case(agent, test_cases[args.single - 1], verbose=args.verbose)
        
        elif args.compare:
            compare_v2_vs_v3_1()
        
        else:
            test_v3_1_all_cases(verbose=args.verbose)
        
        print("\n" + "=" * 80)
        print("✅ TEST SUITE TAMAMLANDI")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
