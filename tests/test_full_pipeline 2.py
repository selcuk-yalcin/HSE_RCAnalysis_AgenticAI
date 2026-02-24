"""
Full RCA Pipeline Test with Claude Skill PDF Generation
1. Run hierarchical RCA analysis
2. Generate professional PDF report using Claude Skill Agent
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add agents to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.orchestrator import RootCauseOrchestrator
from agents.claude_skill_pdf_agent import ClaudeSkillPDFAgent


def print_section(title: str, char: str = "="):
    """Print formatted section header"""
    print("\n" + char * 80)
    print(f"{'  ' if char == '-' else ''}{title}")
    print(char * 80)


def run_full_pipeline(incident_description: str):
    """
    Run complete RCA pipeline with PDF generation
    
    Args:
        incident_description: The incident to analyze
        
    Returns:
        tuple: (rca_results, pdf_path)
    """
    
    print_section("🚀 FULL RCA PIPELINE WITH CLAUDE SKILL PDF")
    print(f"\n📝 Incident: {incident_description[:100]}...")
    
    # ═══════════════════════════════════════════════════════════
    # STEP 1: Run RCA Analysis
    # ═══════════════════════════════════════════════════════════
    print_section("STEP 1: ROOT CAUSE ANALYSIS", "-")
    print("🔍 Running hierarchical 5-Why analysis...")
    
    try:
        # Initialize orchestrator
        orchestrator = RootCauseOrchestrator()
        print("✅ RCA Orchestrator initialized")
        
        # Run analysis
        print("⏳ Analyzing incident...")
        
        # Prepare incident data
        incident_data = {
            "description": incident_description,
            "timestamp": datetime.now().isoformat()
        }
        
        rca_results = orchestrator.run_investigation(incident_data)
        
        # Get full investigation data
        full_data = orchestrator.get_investigation_data()
        
        # Validate results
        if not full_data:
            raise ValueError("RCA analysis returned no results")
        
        branches = full_data.get('analysis_branches', [])
        root_causes = full_data.get('final_root_causes', [])
        
        print(f"\n✅ RCA Analysis Complete!")
        print(f"   📊 Analysis branches: {len(branches)}")
        print(f"   🎯 Root causes identified: {len(root_causes)}")
        print(f"   📋 Method: {full_data.get('analysis_method', 'HSG245')}")
        
        # Show root causes
        print("\n🎯 Root Causes:")
        for i, rc in enumerate(root_causes[:3], 1):
            print(f"   {i}. {rc.get('standard_title_tr', 'N/A')}")
        
        # Save RCA results
        output_file = Path("outputs/rca_analysis_latest.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(full_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 RCA results saved: {output_file}")
        
    except Exception as e:
        print(f"\n❌ RCA Analysis Failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None
    
    # ═══════════════════════════════════════════════════════════
    # STEP 2: Generate Professional PDF Report
    # ═══════════════════════════════════════════════════════════
    print_section("STEP 2: CLAUDE SKILL PDF GENERATION", "-")
    print("🤖 Initializing Claude Skill PDF Agent...")
    
    try:
        # Initialize Claude Skill PDF Agent
        pdf_agent = ClaudeSkillPDFAgent()
        print("✅ Claude Skill PDF Agent initialized")
        
        # Generate PDF report
        print("\n📄 Generating professional PDF report...")
        print("   • Using SKILL.md specifications")
        print("   • Claude Sonnet 4.6 enhancing content")
        print("   • ReportLab creating PDF")
        
        pdf_path = pdf_agent.generate_report(full_data)
        
        if pdf_path and Path(pdf_path).exists():
            file_size = Path(pdf_path).stat().st_size / 1024
            print(f"\n✅ PDF Report Generated Successfully!")
            print(f"   📄 File: {pdf_path}")
            print(f"   📊 Size: {file_size:.1f} KB")
            return full_data, pdf_path
        else:
            print("\n⚠️  PDF generation completed but file not found")
            return full_data, None
            
    except Exception as e:
        print(f"\n❌ PDF Generation Failed: {e}")
        import traceback
        traceback.print_exc()
        return full_data, None


def main():
    """Main test function"""
    
    print_section("🎯 HSE RCA PIPELINE - FULL INTEGRATION TEST")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check environment
    if not os.getenv("OPENROUTER_API_KEY"):
        print("\n❌ OPENROUTER_API_KEY not found in environment")
        print("💡 Set it with: export OPENROUTER_API_KEY=your_key")
        sys.exit(1)
    
    print("✅ Environment configured")
    
    # ═══════════════════════════════════════════════════════════
    # Test Incident
    # ═══════════════════════════════════════════════════════════
    
    incident = """
    Fabrika üretim hattında kompresör arızası nedeniyle 4 saatlik üretim durması yaşandı.
    Ana kompresörün rulmanı aşırı ısınma sonucu seizure yaptı. Termal kamera görüntüleri
    ve bakım kayıtları incelendiğinde, otomatik yağ seviye sensörünün kalibre edilmediği
    ve son bakımda bu adımın atlandığı tespit edildi. Bakım kontrol listesinde sensör
    kalibrasyonu adımı eksikti.
    """
    
    # Run full pipeline
    rca_results, pdf_path = run_full_pipeline(incident.strip())
    
    # ═══════════════════════════════════════════════════════════
    # Final Summary
    # ═══════════════════════════════════════════════════════════
    print_section("📊 PIPELINE EXECUTION SUMMARY")
    
    if rca_results and pdf_path:
        print("✅ STATUS: SUCCESS")
        print("\n📋 Deliverables:")
        print(f"   1. RCA Analysis JSON: outputs/rca_analysis_latest.json")
        print(f"   2. Professional PDF: {pdf_path}")
        
        print("\n🎯 Next Steps:")
        print(f"   • Review PDF report: open {pdf_path}")
        print("   • Check RCA details: cat outputs/rca_analysis_latest.json | jq")
        print("   • Share report with HSE team")
        
        print("\n🌐 Open PDF:")
        print(f"   open {pdf_path}")
        
        # Optionally open PDF automatically
        if input("\n❓ Open PDF now? (y/n): ").strip().lower() == 'y':
            import subprocess
            subprocess.run(["open", pdf_path])
        
        return 0
        
    elif rca_results:
        print("⚠️  STATUS: PARTIAL SUCCESS")
        print("   • RCA analysis completed")
        print("   • PDF generation failed")
        return 1
        
    else:
        print("❌ STATUS: FAILED")
        print("   • RCA analysis failed")
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
