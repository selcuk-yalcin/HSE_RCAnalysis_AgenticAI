#!/usr/bin/env python3
"""
HTML Özelliklerini Test Et

Bu script, yeni eklenen HTML özelliklerini test eder:
- Navigation menu
- Düzenleme toolbar
- Scroll to top button
- Keyboard shortcuts
- Sayfa numaralandırma (yazdırma için)
"""

import os
import sys
from agents.overview_agent import OverviewAgent
from agents.assessment_agent import AssessmentAgent
from agents.rootcause_agent_v2 import RootCauseAgentV2
from agents.skillbased_docx_agent import SkillBasedDocxAgent

# Basit bir test senaryosu
SIMPLE_INCIDENT = """
On 15 January 2026, at approximately 14:30, a maintenance technician 
experienced an electric shock while working on a control panel. 
The incident occurred when the technician touched exposed live wires 
during maintenance activities.

The technician was working alone without proper isolation procedures. 
The control panel's main circuit breaker was not locked out as required 
by LOTO procedures. Warning signs were not posted.

The technician received immediate first aid and was transported to hospital. 
Fortunately, injuries were minor, but this was a serious near-miss incident.
"""

def main():
    """HTML özellikleri test et."""
    print("\n" + "="*70)
    print("HTML ÖZELLİKLERİ TEST")
    print("="*70)
    
    # API key kontrolü
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY bulunamadı!")
        return 1
    
    print(f"✅ API Key: {api_key[:10]}...{api_key[-10:]}")
    
    try:
        # 1. Overview
        print("\n" + "="*70)
        print("ADIM 1: OverviewAgent")
        print("="*70)
        
        agent1 = OverviewAgent()
        incident_dict = {"description": SIMPLE_INCIDENT}
        part1 = agent1.process_initial_report(incident_dict)
        
        if not part1:
            print("❌ Overview başarısız!")
            return 1
        
        ref_no = part1.get("ref_no", "UNKNOWN")
        print(f"✅ Ref No: {ref_no}")
        
        # 2. Assessment
        print("\n" + "="*70)
        print("ADIM 2: AssessmentAgent")
        print("="*70)
        
        agent2 = AssessmentAgent()
        part2 = agent2.assess_incident(incident_dict, part1)
        
        if not part2:
            print("❌ Assessment başarısız!")
            return 1
        
        print(f"✅ Severity: {part2.get('severity_level', 'N/A')}")
        
        # 3. Root Cause Analysis
        print("\n" + "="*70)
        print("ADIM 3: RootCauseAgentV2")
        print("="*70)
        
        agent3 = RootCauseAgentV2()
        part3 = agent3.analyze_root_causes(part1, part2, incident_dict)
        
        if not part3:
            print("❌ RCA başarısız!")
            return 1
        
        branches = part3.get("branches", [])
        root_causes = part3.get("final_root_causes", [])
        print(f"✅ Dallar: {len(branches)}")
        print(f"✅ Kök Nedenler: {len(root_causes)}")
        
        # 4. HTML Report Generation
        print("\n" + "="*70)
        print("ADIM 4: HTML RAPOR OLUŞTURMA")
        print("="*70)
        
        agent4 = SkillBasedDocxAgent()
        
        combined_data = {
            "part1": part1,
            "part2": part2,
            "part3_rca": part3
        }
        
        output_path = f"outputs/INC-{ref_no}_html_test.docx"
        docx_file = agent4.generate_report(
            combined_data,
            output_path=output_path
        )
        
        if not docx_file or not os.path.exists(docx_file):
            print("❌ DOCX oluşturulamadı!")
            return 1
        
        # HTML dosyası kontrol et
        html_file = docx_file.replace(".docx", ".html")
        if not os.path.exists(html_file):
            print("❌ HTML dosyası bulunamadı!")
            return 1
        
        # Dosya boyutları
        docx_size = os.path.getsize(docx_file) / 1024
        html_size = os.path.getsize(html_file) / 1024
        
        print(f"✅ DOCX: {docx_file} ({docx_size:.1f} KB)")
        print(f"✅ HTML: {html_file} ({html_size:.1f} KB)")
        
        # HTML içeriğini kontrol et
        print("\n" + "="*70)
        print("HTML İÇERİK ANALİZİ")
        print("="*70)
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        features = {
            "Navigation Menu": 'class="nav-menu"' in html_content,
            "Navigation Toggle": 'class="nav-toggle"' in html_content,
            "Edit Toolbar": 'class="edit-toolbar"' in html_content,
            "Scroll to Top": 'class="scroll-top"' in html_content,
            "contenteditable": 'contenteditable="true"' in html_content,
            "Section IDs": 'id="executive-summary"' in html_content,
            "JavaScript Functions": 'function toggleNav()' in html_content,
            "Keyboard Shortcuts": 'keydown' in html_content,
            "Print Styles": '@media print' in html_content,
            "localStorage": 'localStorage' in html_content,
        }
        
        print("\nYeni Özellikler:")
        for feature, exists in features.items():
            status = "✅" if exists else "❌"
            print(f"  {status} {feature}")
        
        all_present = all(features.values())
        
        if all_present:
            print("\n" + "="*70)
            print("🎉 TÜM ÖZELLİKLER BAŞARILI!")
            print("="*70)
            print(f"\n📄 HTML Raporu: {html_file}")
            print("\n💡 HTML dosyasını tarayıcınızda açın ve şu özellikleri test edin:")
            print("   • 📋 Sağ üstteki 'İçindekiler' butonuna tıklayın")
            print("   • 🔓 'Düzenleme Modu' butonuyla düzenlemeyi açın")
            print("   • ✏️ Herhangi bir metne tıklayarak düzenleyin")
            print("   • 💾 Ctrl+S ile kaydedin")
            print("   • 🖨️ Ctrl+P ile yazdırma önizlemesi açın")
            print("   • ↑ Scroll to top butonu ile yukarı çıkın")
            print("   • 📥 'HTML İndir' ile raporu indirin")
            print("\n" + "="*70)
            return 0
        else:
            print("\n❌ Bazı özellikler eksik!")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Kullanıcı tarafından iptal edildi")
        return 130
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
