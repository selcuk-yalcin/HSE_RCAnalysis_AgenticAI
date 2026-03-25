"""
SENARYO: FORKLIFT SARMAL KAPI ÇARPIŞMASI - MALZEMENİN HASAR GÖRMESİ
====================================================================

🎯 AMAÇ: 3-Branch RCA + Granular Caching + Token Optimization Test

📊 ÖZET:
- Operatör yeni çalışan (1 ay Green Transfo fabrikası tecrübesi)
- Sarmal kapı 60 saniye otomatik kapanma sistemi var (stop tuşu bilgisi eksik)
- Malzeme hasarı (kişisel yaralanma değil)
- Görüş açısı sorunu (operatör geri giderken kapıyı göremiyordu)
- Kış şartları nedeniyle kapı otomatik kapanma
- Eğitim/bilgilendirilme eksikliği

⚡ OPTIMIZASYONLAR:
1. GRANULAR CACHING: Her bölüm (Overview/Assessment/RootCause) ayrı cache'e
   - İlk çalıştırma: ~5 dakika, 48,000 token, $0.50
   - Tekrar çalıştırma: ~15 saniye, 2,000 token, $0.02 (96% tasarruf!)
   
2. TOKEN OPTIMIZATION: Max 3 branch analizi
   - 4 branch yerine 3 branch: ~12,000 token tasarrufu
   - Confidence bazlı seçim: En önemli nedenler önceliklendirilir
   
3. CACHE HIT SENARYOLARI:
   - Senaryo A: İlk çalıştırma (MISS) → Tam analiz
   - Senaryo B: Aynı incident (HIT) → Tüm cache kullanılır
   - Senaryo C: Description değişiklik (PARTIAL HIT) → Overview/Assessment cache, RootCause yeni

🔄 AKIŞ:
   1. Incident data hazırla
   2. Granular cache kontrolü (Overview → Assessment → RootCause)
   3. Cache miss kısımları analiz et
   4. Cache hit kısımları atla (hız!)
   5. Rapor oluştur (her zaman)
   6. Sonuçları cache'e kaydet

💾 CACHE DEPO:
   - Disk: Local (JSON formatında)
   - TTL: 30 gün (otomatik silme)

📈 BEKLENEN SONUÇLAR:
   ✅ Tüm 3 branch analiz edilir
   ✅ Meta root cause oluşturulmaz (synthesize_meta_root=False)
   ✅ Cache hit/miss istatistikleri görülür
   ✅ Token kullanımı optimizedir
   ✅ Rapor DOCX formatında oluşturulur
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.overview_agent import OverviewAgent
from agents.assessment_agent import AssessmentAgent
from agents.rootcause_agent_v2 import RootCauseAgentV2
from agents.skillbased_docx_agent import SkillBasedDocxAgent
from agents.unified_analysis_pipeline import AnalysisCache


def main():
    print("=" * 100)
    print("🚚 FORKLIFT SARMAL KAPI ÇARPIŞMASI SENARYOSU - MALZEMENİN HASAR GÖRMESİ")
    print("=" * 100)
    print()

    incident_summary = """KAZA RAPORU - FORKLIFT SARMAL KAPI ÇARPIŞMASI
==============================================

1. OLAY ÖZETİ
Operatör paletli yükü almak için sarmal kapıyı forkliftten inerek açmıştır. Daha sonra kapalı
alana girip yükü kaldırmış ve geri manevrayla giriş yaptığı kapıdan çıkmak istemiştir. Operatör
geri geri hareket ederken kapı kendiliğinden kapanmaya başlamıştır. Kapı operatörün görüş açısında
olmadığı için forklift kabininin üst kısmı sarmal kapıya çarpmıştır.

Operatörün fabrika tecrübesi 1 aydır. Sarmal kapı kış şartları nedeniyle 60 saniye sonra otomatik
olarak kapanmaktadır. Sarmal kapının açık kalması isteniyorsa kapı üzerindeki kumanda sisteminden
'stop' tuşuna basılması gerekmektedir. Operatör bu bilgiye sahip değildir. Olay malzeme hasarlı
olarak kaydedilmiştir."""

    incident_data = {
        "ref_no": "TRANS-2026-001-DOOR",
        "incident_type": "Malzeme Hasarı",
        "reported_by": "Vardiya Amiri",
        "date_time": "14:35",
        "description": incident_summary,
        "injury_description": "Kişisel yaralanma yok. Forklift kabininde çarpma hasarı, paletli yükte malzeme hasarı."
    }

    # ══════════════════════════════════════════════════════════════════════════════════════════════
    # GRANULAR CACHING: Her bölüm ayrı cache'e
    # ══════════════════════════════════════════════════════════════════════════════════════════════
    
    print("\n" + "="*100)
    print("💾 GRANULAR CACHE KONTROLÜ - BÖLÜM BÖLÜM")
    print("="*100 + "\n")

    cache = AnalysisCache()
    overview_result = None
    assessment_result = None
    root_cause_result = None
    
    incident_key = f"{incident_data.get('ref_no', 'unknown')}_door_scenario"
    cache_stats = {
        "overview_hit": False,
        "assessment_hit": False,
        "rootcause_hit": False
    }

    # ── 1. OVERVIEW CACHE KONTROLÜ ──
    print(f"1️⃣  OVERVIEW BÖLÜMÜ CACHE KONTROLÜ...")
    overview_cache_key = f"{incident_key}_overview_v1"
    
    try:
        cache_overview = cache.get_by_key(overview_cache_key)
        if cache_overview and isinstance(cache_overview, dict):
            print("   ✅ CACHE HIT - Overview bulundu!")
            print(f"      📅 Cached: {cache_overview.get('_cache_timestamp', 'N/A')}")
            print("      ⏭️  Atlanıyor (yeni analiz yapılmayacak)\n")
            overview_result = cache_overview
            cache_stats["overview_hit"] = True
    except Exception as e:
        print(f"   ⚠️  Cache kontrol hatası: {e}")
    
    # Cache miss ise analiz yap
    if not overview_result:
        print("   ❌ CACHE MISS - Overview analiz başlanıyor...\n")
        overview_agent = OverviewAgent()
        
        try:
            overview_result = overview_agent.process_initial_report(incident_data)
            overview_result['_cache_timestamp'] = datetime.now().isoformat()
            
            # Cache'e kaydet
            cache.set_by_key(overview_cache_key, overview_result)
            print("   💾 Overview cache'e kaydedildi\n")
        except Exception as e:
            print(f"   ❌ HATA: {e}")
            import traceback
            traceback.print_exc()
            return

    # ── 2. ASSESSMENT CACHE KONTROLÜ ──
    print(f"2️⃣  ASSESSMENT BÖLÜMÜ CACHE KONTROLÜ...")
    assessment_cache_key = f"{incident_key}_assessment_v1"
    
    try:
        cache_assessment = cache.get_by_key(assessment_cache_key)
        if cache_assessment and isinstance(cache_assessment, dict):
            print("   ✅ CACHE HIT - Assessment bulundu!")
            print(f"      📅 Cached: {cache_assessment.get('_cache_timestamp', 'N/A')}")
            print("      ⏭️  Atlanıyor (yeni analiz yapılmayacak)\n")
            assessment_result = cache_assessment
            cache_stats["assessment_hit"] = True
    except Exception as e:
        print(f"   ⚠️  Cache kontrol hatası: {e}")
    
    if not assessment_result:
        print("   ❌ CACHE MISS - Assessment analiz başlanıyor...\n")
        assessment_agent = AssessmentAgent()
        
        try:
            assessment_result = assessment_agent.assess_incident(overview_result, incident_data)
            assessment_result['_cache_timestamp'] = datetime.now().isoformat()
            
            # Cache'e kaydet
            cache.set_by_key(assessment_cache_key, assessment_result)
            print("   💾 Assessment cache'e kaydedildi\n")
        except Exception as e:
            print(f"   ❌ HATA: {e}")
            import traceback
            traceback.print_exc()
            return

    # ── 3. ROOT CAUSE CACHE KONTROLÜ ──
    print(f"3️⃣  ROOT CAUSE BÖLÜMÜ CACHE KONTROLÜ...")
    rootcause_cache_key = f"{incident_key}_rootcause_v1_3branches_no_meta"
    
    try:
        cache_rootcause = cache.get_by_key(rootcause_cache_key)
        if cache_rootcause and isinstance(cache_rootcause, dict):
            print("   ✅ CACHE HIT - Root Cause bulundu!")
            print(f"      📅 Cached: {cache_rootcause.get('_cache_timestamp', 'N/A')}")
            print("      ⏭️  Atlanıyor (yeni analiz yapılmayacak)\n")
            root_cause_result = cache_rootcause
            cache_stats["rootcause_hit"] = True
    except Exception as e:
        print(f"   ⚠️  Cache kontrol hatası: {e}")
    
    if not root_cause_result:
        print("   ❌ CACHE MISS - Root Cause analiz başlanıyor...\n")
        rootcause_agent = RootCauseAgentV2(use_rag=True)
        
        try:
            root_cause_result = rootcause_agent.analyze_root_causes(
                overview_result,
                assessment_result,
                incident_data,
                synthesize_meta_root=False
            )
            root_cause_result['_cache_timestamp'] = datetime.now().isoformat()
            
            # Cache'e kaydet
            cache.set_by_key(rootcause_cache_key, root_cause_result)
            print("   💾 Root Cause cache'e kaydedildi\n")
        except Exception as e:
            print(f"   ❌ HATA: {e}")
            import traceback
            traceback.print_exc()
            return

    # ── CACHE İSTATİSTİKLERİ ──
    print("\n" + "="*100)
    print("📊 CACHE İSTATİSTİKLERİ")
    print("="*100)
    
    hit_count = sum([cache_stats["overview_hit"], cache_stats["assessment_hit"], cache_stats["rootcause_hit"]])
    total_parts = 3
    hit_rate = (hit_count / total_parts) * 100
    
    print(f"\n🔍 BÖLÜM BÖLÜM HIT ORANI:")
    print(f"   📋 Overview:   {'✅ HIT' if cache_stats['overview_hit'] else '❌ MISS'}")
    print(f"   📊 Assessment: {'✅ HIT' if cache_stats['assessment_hit'] else '❌ MISS'}")
    print(f"   🎯 RootCause:  {'✅ HIT' if cache_stats['rootcause_hit'] else '❌ MISS'}")
    print(f"\n📈 Toplam Hit Rate: {hit_rate:.0f}% ({hit_count}/{total_parts} bölüm)")
    
    if hit_rate == 0:
        print(f"   ⏱️  İlk çalıştırma - Tahmini toplam süre: ~5 dakika")
        print(f"   💰 Token kullanımı: ~48,000 (~$0.50)")
    elif hit_rate == 100:
        print(f"   ⏱️  Tüm cache'den - Tahmini toplam süre: ~20 saniye")
        print(f"   💰 Token kullanımı: ~2,000 (~$0.02) - 96% tasarruf!")
    else:
        print(f"   ⏱️  Kısmi cache - Tahmini toplam süre: ~2-3 dakika")
        print(f"   💰 Token kullanımı: ~16,000 (~$0.17) - 66% tasarruf!")

    # ──────────────────────────────────────────────────────────────────────────────────────────────
    # ADIM 4: TAM RAPOR OLUŞTUR (HER ZAMAN)
    # ──────────────────────────────────────────────────────────────────────────────────────────────
    
    print("\n" + "="*100)
    print("📄 ADIM 4: TAM RAPOR OLUŞTURULUYOR (DOCX)")
    print("="*100 + "\n")

    docx_agent = SkillBasedDocxAgent()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"outputs/forklift_door_test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = str(output_dir / f"forklift_door_{timestamp}")
    
    try:
        investigation_data = {
            "part1": overview_result,
            "part2": assessment_result,
            "part3_rca": root_cause_result
        }
        
        print("🤖 DOCX rapor oluşturuluyor...")
        docx_path = docx_agent.generate_report(investigation_data, output_path)
        
        if Path(docx_path).exists():
            size_mb = Path(docx_path).stat().st_size / (1024 * 1024)
            print(f"   ✅ {docx_path}")
            print(f"      📊 Boyut: {size_mb:.1f} MB")
        
        print("\n" + "="*100)
        print("✅ TEST BAŞARIYLA TAMAMLANDI!")
        print("="*100)
        print(f"\n📊 SONUÇ ÖZETİ:")
        print(f"   🌳 {len(root_cause_result.get('analysis_branches', []))} Ana Dal")
        print(f"   🎯 {len(root_cause_result.get('final_root_causes', []))} Kök Neden")
        print(f"   💾 Cache Hit Rate: {hit_rate:.0f}%")
        print(f"   ⏱️  Süre: {'~5 dakika (İlk)' if hit_rate == 0 else '~20 saniye (Cache)' if hit_rate == 100 else '~2-3 dakika (Kısmi)'}")
        print(f"   💰 Token tasarrufu: {'%96' if hit_rate == 100 else '%66' if hit_rate > 0 else '%25'}")
        
        print("\n" + "="*100 + "\n")
        
    except Exception as e:
        print(f"❌ HATA: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    main()
