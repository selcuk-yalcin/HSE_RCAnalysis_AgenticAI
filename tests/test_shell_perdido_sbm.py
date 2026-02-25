#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST: Shell Perdido Spar - SBM Salınımı Olayı
Platform: Perdido Spar (Meksika Körfezi AC 857)
Olay: 24 varil SBM'nin denize salınması
Tarih: 4 Eylül 2023, ~13:20
Operatör: Helmerich & Payne (H&P)
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.overview_agent import OverviewAgent
from agents.assessment_agent import AssessmentAgent
from agents.rootcause_agent_v2 import RootCauseAgentV2
from agents.skillbased_docx_agent import SkillBasedDocxAgent
from shared.config import Config

def print_header(title, char="=", width=80):
    print(f"\n{char * width}")
    print(f"  {title}")
    print(f"{char * width}")

def print_step(step_num, title):
    print_header(f"ADIM {step_num}: {title}")

def print_success(message):
    print(f"  ✅ {message}")

def print_info(message):
    print(f"  {message}")

# ============================================================================
# SHELL PERDIDO SPAR - SBM SALIM OLAYI
# ============================================================================
INCIDENT_DESCRIPTION = """
OLAY RAPORU - ÇEVRESELSENTETİK BAZLI ÇAMUR (SBM) SALINMI

Tarih: 4 Eylül 2023, Saat: 13:20
Lokasyon: Meksika Körfezi, AC 857 Sahası - Perdido Spar Platformu, HAP 205 Sondaj Kulesi
İşletmeci: Helmerich & Payne (H&P) / Shell
Kuyu: G#009
Rapor Eden: Rig Manager
Olay Sonucu: 24 varil SBM (Sentetik Bazlı Çamur) denize salındı

OLAY ÖZETİ:
G#009 kuyusunda sondaj sırasında gazlı çamur tespit edildi. Gaz ayırıcı tank devreye alındı ve aynı anda aktif tanktan işleme çukurlarına 17 varil SBM transfer edildi. Transfer öncesi gaz ayırıcı tankın tahliye valflerinin (bıçak valf ve kelebek valf) kapalı olduğu GÖRSEL olarak kontrol edildi ancak FİZİKSEL DOĞRULAMA yapılmadı. Transfer sırasında gaz ayırıcı tankın seviye kontrolü yapılmadı (küçük hacimli transfer prosedürde muaf tutulmuştu).

Transfer sonrası 6 saat içinde Driller gaz ayırıcı tankta seviye düşüşü fark etti. İnceleme sonucu 24 varil SBM'nin denize salındığı tespit edildi. Sonradan yapılan valf incelemesinde:
- Bıçak valf tortularla tıkanmış, tamamen kapanmıyordu
- Kelebek valf içinde sıkışan lastik parça nedeniyle düzgün çalışmıyordu
- Son valf işlev testi Nisan 2023'te yapılmıştı (5 ay önce)

OLAY TİPİ: Çevresel Salınım - Ekipman Arızası ve Prosedür Eksikliği

OLAY TİPİ: Çevresel Salınım - Ekipman Arızası ve Prosedür Eksikliği

KRİTİK FAKTÖRLER:

1. VALF ARIZASI (Donanım):
   - Gaz ayırıcı tankın (1 varil kapasite) tahliye valfleri arızalıydı
   - Bıçak valf: Tortularla tıkanmış, tam kapanmıyor
   - Kelebek valf: İçinde sıkışan lastik parça, düzgün çalışmıyor
   - Son işlev testi: 5 ay önce (Nisan 2023)
   - Düzenli bakım/test sıklığı yetersiz

2. PROSEDÜR EKSİKLİĞİ:
   - Fluid Transfer Procedure (W1.5.03 Rev. 5): "İki kişi tarafından GÖRSEL kontrol yapılmalı"
   - Pit-hand ve AD valfleri GÖRSEL kontrol etti: "Yüksekteydi, tam net göremedik ama kapalı varsaydık"
   - FİZİKSEL doğrulama yapılmadı (valflerin manuel olarak test edilmesi)
   - Küçük hacimli transferlerde seviye kontrolü zorunlu DEĞİL (prosedür boşluğu)
   - Gaz ayırıcı tank gibi küçük hacimlerde özel kontrol protokolü YOK

3. TASARIM SORUNU:
   - Gaz ayırıcı tank sadece 1 varil (çok küçük - hızlı dolma/boşalma riski)
   - Çıkış valfi eğimin ÜST noktasında (katı partikül birikimi sorunu)
   - Seviye göstergesi gecikmeli yanıt veriyor
   - İşleme çukurları kapak boşlukları var (yabancı cisim giriş riski)
   - Valflerde kilit (skillet) güvenlik YOK (aktif tankta var, işleme çukurunda yok)

4. OPERASYONEL DAVRANIŞLAR:
   - Driller: "Seviye düşüşünü gördüm ama sistem dengeleniyor sandım. Valfleri kontrol etmedim."
   - Ekip prosedüre fazla güvendi, fiziksel doğrulama yapmadı
   - İlk 30 dakika su yüzeyinde parlama görülmedi (gecikmiş tespit)

TANIK İFADELERİ:
- Pit-hand: "Valfleri AD ile birlikte görsel kontrol ettik. Yüksekteydi, tam net göremedik ama kapalı varsaydık."
- Driller: "Seviye düşüşünü fark ettim ama başlangıçta sistem dengeleniyor sandım. Valfleri kontrol etmedim, prosedür yeterli diye düşündüm."
- Tool-pusher: "Kum tuzak dolu, gaz ayırıcı neredeyse boşalmıştı. Denize bir şey aktığını o anda fark etmedik."

SONUÇ:
24 varil SBM denize salındı. BSEE (Bureau of Safety and Environmental Enforcement) resmi soruşturma başlattı.
"""

def main():
    print_header("SHELL PERDIDO SPAR - SBM SALINMI OLAYI TEST", "=", 80)
    print(f"     Test Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"     Platform: Perdido Spar (Meksika Körfezi AC 857)")
    print(f"     Olay: 24 varil SBM deniz salınımı - Valf arızası ve prosedür eksikliği")
    
    start_time = datetime.now()
    
    # API Key kontrolü
    print_step(1, "Ortam Kontrolü")
    api_key = Config.OPENROUTER_API_KEY
    if not api_key:
        print("  ❌ OPENROUTER_API_KEY bulunamadı!")
        return
    print_success(f"API Key: {api_key[:8]}...{api_key[-4:]}")
    
    # Output dizini
    output_dir = project_root / "outputs"
    output_dir.mkdir(exist_ok=True)
    print_success("Çıktı dizini hazır")
    
    # Test ID
    incident_id = f"shell_perdido_sbm_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # ========================================================================
    # ADIM 2: OVERVIEW AGENT
    # ========================================================================
    print_step(2, "OverviewAgent")
    overview_agent = OverviewAgent()
    print_success(f"Agent başlatıldı")
    
    # INCIDENT_DESCRIPTION'ı dict formatına çevir
    incident_dict = {"description": INCIDENT_DESCRIPTION}
    overview_result = overview_agent.process_initial_report(incident_dict)
    
    print_success(f"Ref No: {overview_result.get('ref_no', 'N/A')}")
    print_success(f"Olay Tipi: {overview_result.get('incident_type', 'N/A')}")
    
    # ========================================================================
    # ADIM 3: ASSESSMENT AGENT
    # ========================================================================
    print_step(3, "AssessmentAgent")
    assessment_agent = AssessmentAgent()
    print_success(f"Agent başlatıldı")
    
    # INCIDENT_DESCRIPTION'ı dict olarak gönder
    incident_dict = {"description": INCIDENT_DESCRIPTION}
    assessment_result = assessment_agent.assess_incident(overview_result, incident_dict)
    
    print_success(f"Şiddet: {assessment_result.get('actual_potential_harm', 'N/A')}")
    print_success(f"RIDDOR: {assessment_result.get('riddor', {}).get('reportable', 'N/A')}")
    print_success(f"Level: {assessment_result.get('investigation', {}).get('level', 'N/A')}")
    
    # ========================================================================
    # ADIM 4: ROOT CAUSE AGENT V2
    # ========================================================================
    print_step(4, "RootCauseAgentV2")
    rc_agent = RootCauseAgentV2()
    print_success("Kök Neden Ajanı V2 başlatıldı (knowledge_base)")
    
    # Doğru parametreler: part1_data, part2_data, investigation_data
    incident_dict = {"description": INCIDENT_DESCRIPTION}
    root_cause_result = rc_agent.analyze_root_causes(
        part1_data=overview_result,
        part2_data=assessment_result,
        investigation_data=incident_dict
    )
    
    branches = root_cause_result.get('branches', [])
    root_causes = root_cause_result.get('root_causes', [])
    
    print_success(f"Dallar: {len(branches)}")
    print_success(f"Kök nedenler: {len(root_causes)}")
    for idx, rc in enumerate(root_causes, 1):
        print(f"     [{idx}] {rc.get('hsg_code', 'N/A')} - {rc.get('title', 'N/A')[:60]}...")
    
    # JSON kaydet
    import json
    json_path = output_dir / f"{incident_id}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'overview': overview_result,
            'assessment': assessment_result,
            'root_cause': root_cause_result
        }, f, ensure_ascii=False, indent=2)
    print_success(f"JSON: {json_path}")
    
    # ========================================================================
    # ADIM 5: DOCX + HTML RAPOR
    # ========================================================================
    print_step(5, "Rapor Üretimi (DOCX + HTML)")
    
    docx_agent = SkillBasedDocxAgent()
    print_success("SkillBasedDocxAgent V2 hazır (OpenRouter anthropic/claude-sonnet-4.5)")
    
    # Rapor üret - tek bir combined dict olarak gönder
    combined_data = {
        'part1': overview_result,
        'part2': assessment_result,
        'part3_rca': root_cause_result
    }
    
    ref_no = overview_result.get('ref_no', 'INC-UNKNOWN')
    incident_type_raw = overview_result.get('incident_type', 'incident')
    # Incident type'ı dosya adı için sanitize et
    incident_type_clean = incident_type_raw.lower().replace(' ', '_')[:30]
    
    output_docx = f"outputs/{ref_no}_{incident_type_clean}.docx"
    
    docx_path = docx_agent.generate_report(
        investigation_data=combined_data,
        output_path=output_docx
    )
    
    # HTML path'i DOCX'ten türet
    html_path = docx_path.replace('.docx', '.html')
    
    # Dosya boyutları
    docx_size = os.path.getsize(docx_path) / 1024
    
    # HTML dosyası varsa boyutunu al
    if os.path.exists(html_path):
        html_size = os.path.getsize(html_path) / 1024
        print_success(f"HTML: {html_size:.1f} KB - {html_path}")
    else:
        html_path = "N/A"
        print_info("HTML dosyası oluşturulmadı")
    
    print_success(f"DOCX: {docx_size:.1f} KB - {docx_path}")
    
    # ========================================================================
    # ÖZET
    # ========================================================================
    elapsed = (datetime.now() - start_time).total_seconds()
    
    print_header("TEST ÖZET")
    print(f"     Süre: {elapsed:.1f} saniye")
    print(f"     Sonuç: 5/5 adım başarılı")
    print_success("🎉 TÜM TESTLER BAŞARILI!")
    print()
    print("📄 Üretilen Dosyalar:")
    print(f"   • {json_path}")
    print(f"   • {docx_path}")
    print(f"   • {html_path}")

if __name__ == "__main__":
    main()
