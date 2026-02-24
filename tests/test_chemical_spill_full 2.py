"""
FULL PIPELINE TEST - Kimyasal Döküntü Olayı
============================================

YENİ SENARYO:
Bir kimya fabrikasında asit tankı valf arızası nedeniyle zemine döküntü oldu.
2 işçi hafif yanıkla hastaneye kaldırıldı.

TEST AKIŞI:
1. Overview Agent      → Olayı analiz et, bağlamı oluştur
2. Assessment Agent    → Risk değerlendir, kronoloji çıkar
3. RootCause Agent V2  → 3 dal hiyerarşik analiz (5-Why)
4. SkillBasedDocxAgent → 14+ sayfa profesyonel DOCX rapor

BEKLENTİ:
✅ Tüm agentlar çalışıyor
✅ JSON yapısı doğru
✅ DOCX raporu 14+ sayfa, Türkçe karakterler doğru
✅ HSE renk paleti uygulanmış
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Agent imports
from agents.orchestrator import RootCauseOrchestrator


def main():
    print("=" * 80)
    print("🧪 FULL PIPELINE TEST - Kimyasal Döküntü Senaryosu")
    print("=" * 80)
    print()

    # ─────────────────────────────────────────────────────────────────────────
    # YENİ OLAY SENARYOSU
    # ─────────────────────────────────────────────────────────────────────────
    incident_data = {
        "incident_id": "CHEM-2026-042",
        "date": "2026-02-20T14:30:00Z",
        "location": "Kimya Fabrikası - C Blok Tank Alanı",
        "incident_type": "Kimyasal Döküntü ve İşçi Yaralanması",
        "severity": "Major",
        "reporter": "Vardiya Amiri - Mehmet Kaya",
        
        "description": """
Saat 14:30'da C Blok tank alanında 5000 litrelik sülfürik asit tankının 
alt tahliye valfinde arıza meydana geldi. Valf aniden açıldı ve yaklaşık 
200 litre %98'lik sülfürik asit zemine döküldü.

Olay sırasında tankın 3 metre yakınında kalite kontrol için numune alan 
2 işçi (Ahmet Yılmaz ve Fatma Demir) asit sıçramalarından etkilendi. 
Her iki işçi de koruyucu eldiven ve önlük giyiyordu ancak yüz siperleri 
kapalı değildi.

İşçiler acil duş istasyonuna koştular ve 15 dakika boyunca yıkandılar. 
Fabrika sağlık ekibi müdahale etti ve her iki işçi de hafif kimyasal 
yanıklarla (kol ve yüz bölgesinde 1. derece yanık) hastaneye sevk edildi.

Alan 40 dakika içinde nötralizasyon ekibi tarafından temizlendi.
Üretim 3 saat süreyle durduruldu.
        """,
        
        "immediate_actions": [
            "Acil duş istasyonu kullanıldı",
            "Yaralı işçiler hastaneye sevk edildi",
            "Tank alanı karantinaya alındı",
            "Nötralizasyon ekibi devreye girdi",
            "Bölge komple tahliye edildi",
            "Üretim durduruldu"
        ],
        
        "witnesses": [
            "Vardiya Amiri - Mehmet Kaya",
            "Bakım Teknisyeni - Ali Vural (valf bakımından sorumlu)",
            "Kalite Kontrol Uzmanı - Ayşe Çelik (olay sırasında yakında)",
            "İşçi - Ahmet Yılmaz (yaralanan)",
            "İşçi - Fatma Demir (yaralanan)"
        ],
        
        "injuries": [
            {
                "person": "Ahmet Yılmaz",
                "injury_type": "Kimyasal yanık - 1. derece",
                "affected_area": "Sol kol ve yüz sol tarafı",
                "treatment": "Hastane acil servis, gözlem altında"
            },
            {
                "person": "Fatma Demir", 
                "injury_type": "Kimyasal yanık - 1. derece",
                "affected_area": "Sağ kol ve boyun",
                "treatment": "Hastane acil servis, gözlem altında"
            }
        ],
        
        "equipment_involved": [
            "5000L Sülfürik Asit Tankı (Tank-C-07)",
            "Pnömatik Tahliye Valfi (Valf-C-07-BV01)",
            "Acil Duş İstasyonu",
            "PPE: Koruyucu eldiven, önlük, yüz siperi (kullanılmamış)"
        ],
        
        "environmental_conditions": {
            "temperature": "22°C",
            "humidity": "45%",
            "lighting": "İyi (gündüz vardiyası)",
            "ventilation": "Normal çalışır durumda"
        },
        
        "initial_observations": [
            "Valf arızası beklenmedik ve aniden gerçekleşti",
            "Son bakım: 3 ay önce (bakım kaydı mevcut)",
            "Valf üreticisi: TurkValve A.Ş., Model: PV-3000",
            "İşçilerin yüz siperleri açıktı (sıcak hava nedeniyle)",
            "Acil duş istasyonu hızla kullanıldı ve çalıştı",
            "Nötralizasyon ekibi prosedür uygun müdahale etti",
            "Tank seviye alarmı çalmadı"
        ]
    }

    print("📋 Olay Bilgileri:")
    print(f"   ID: {incident_data['incident_id']}")
    print(f"   Tip: {incident_data['incident_type']}")
    print(f"   Lokasyon: {incident_data['location']}")
    print(f"   Seviye: {incident_data['severity']}")
    print(f"   Yaralanan: {len(incident_data['injuries'])} kişi")
    print()

    # ─────────────────────────────────────────────────────────────────────────
    # ORCHESTRATOR'I BAŞLAT VE ÇALIŞTIR
    # ─────────────────────────────────────────────────────────────────────────
    print("=" * 80)
    print("🚀 ROOT CAUSE ORCHESTRATOR BAŞLATILIYOR...")
    print("=" * 80)
    print()

    orchestrator = RootCauseOrchestrator()
    
    print("\n" + "=" * 80)
    print("▶️  FULL INVESTIGATION BAŞLIYOR (4 ADIM)")
    print("=" * 80)
    
    # Tam pipeline çalıştır
    results = orchestrator.run_investigation(incident_data)
    
    # ─────────────────────────────────────────────────────────────────────────
    # SONUÇLARI KAYDET VE RAPORLA
    # ─────────────────────────────────────────────────────────────────────────
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    # JSON sonuçlarını kaydet
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_output = output_dir / f"chemical_spill_test_{timestamp}.json"
    
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print("\n" + "=" * 80)
    print("📊 TEST SONUÇLARI")
    print("=" * 80)
    print()
    
    # Part 1 sonuçları
    if results.get("part1"):
        print("✅ PART 1 - GENEL BAKIŞ")
        part1 = results["part1"]
        print(f"   Başlık: {part1.get('investigation_title', 'N/A')[:60]}...")
        print(f"   Bölüm sayısı: {len(part1.get('sections', []))}")
        print()
    
    # Part 2 sonuçları
    if results.get("part2"):
        print("✅ PART 2 - DEĞERLENDİRME")
        part2 = results["part2"]
        timeline = part2.get('timeline', [])
        print(f"   Kronoloji adımları: {len(timeline)}")
        print(f"   Risk faktörleri: {len(part2.get('risk_factors', []))}")
        print()
    
    # Part 3 sonuçları (RCA)
    if results.get("part3_rca"):
        print("✅ PART 3 - KÖK NEDEN ANALİZİ (Hiyerarşik)")
        rca = results["part3_rca"]
        
        branches = rca.get('analysis_branches', [])
        print(f"   Analiz dalları: {len(branches)}")
        
        for i, branch in enumerate(branches, 1):
            direct = branch.get('direct_cause', 'N/A')[:50]
            chain_length = len(branch.get('five_why_chain', []))
            root = branch.get('root_cause', {})
            root_desc = root.get('description', 'N/A')[:50]
            print(f"   Dal {i}: {direct}... → {chain_length} why → {root_desc}...")
        
        final_roots = rca.get('final_root_causes', [])
        print(f"   Nihai kök nedenler: {len(final_roots)}")
        print()
    
    # DOCX raporu
    if results.get("docx_report"):
        print("✅ DOCX RAPOR ÜRETİLDİ")
        docx_path = results["docx_report"]
        if os.path.exists(docx_path):
            size_kb = os.path.getsize(docx_path) / 1024
            print(f"   📄 Dosya: {docx_path}")
            print(f"   📊 Boyut: {size_kb:.1f} KB")
            print()
        else:
            print(f"   ⚠️  Dosya bulunamadı: {docx_path}")
            print()
    else:
        print("❌ DOCX raporu oluşturulmadı")
        print()
    
    # JSON dosyası
    print(f"💾 JSON Sonuçlar: {json_output}")
    json_size_kb = os.path.getsize(json_output) / 1024
    print(f"   Boyut: {json_size_kb:.1f} KB")
    print()
    
    # Durum özeti
    status = results.get("status", "unknown")
    print(f"🏁 Final Durum: {status}")
    print()
    
    # ─────────────────────────────────────────────────────────────────────────
    # BAŞARI KRİTERLERİ KONTROLÜ
    # ─────────────────────────────────────────────────────────────────────────
    print("=" * 80)
    print("🎯 BAŞARI KRİTERLERİ KONTROLÜ")
    print("=" * 80)
    print()
    
    checks = {
        "Part 1 tamamlandı": results.get("part1") is not None,
        "Part 2 tamamlandı": results.get("part2") is not None,
        "Part 3 RCA tamamlandı": results.get("part3_rca") is not None,
        "3 analiz dalı var": len(results.get("part3_rca", {}).get("analysis_branches", [])) >= 3,
        "Kök nedenler var": len(results.get("part3_rca", {}).get("final_root_causes", [])) >= 2,
        "DOCX raporu oluşturuldu": results.get("docx_report") is not None,
        "DOCX dosyası mevcut": os.path.exists(results.get("docx_report", "")),
        "JSON kaydedildi": os.path.exists(json_output),
        "Final durum 'complete'": status == "investigation_complete"
    }
    
    passed = sum(checks.values())
    total = len(checks)
    
    for check, result in checks.items():
        symbol = "✅" if result else "❌"
        print(f"{symbol} {check}")
    
    print()
    print(f"📈 Skor: {passed}/{total} ({100*passed//total}%)")
    print()
    
    if passed == total:
        print("🎉 TÜM TESTLER BAŞARILI! Pipeline tam olarak çalışıyor.")
        print()
        print("📄 DOCX raporunu açmak için:")
        print(f"   open {results['docx_report']}")
    else:
        print("⚠️  Bazı kontroller başarısız oldu. Lütfen yukarıdaki detayları inceleyin.")
    
    print()
    print("=" * 80)
    

if __name__ == "__main__":
    main()
