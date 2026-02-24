"""
Claude Skill-Based PDF Report Generator
Uses Claude Opus 4 with SKILL.md to generate professional PDF reports
Claude generates and executes the PDF code itself
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from openai import OpenAI


class ClaudeSkillPDFAgent:
    """
    Claude-powered PDF generator that uses SKILL.md
    Claude reads the skill file and generates PDF code dynamically
    """
    
    def __init__(self):
        """Initialize Claude Opus 4 client"""
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key
        )
        
        self.model = "anthropic/claude-sonnet-4.6"
        self.output_dir = Path("outputs/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load SKILL.md
        self.skill_path = Path("/Users/selcuk/Downloads/SKILL.md")
        if not self.skill_path.exists():
            print("⚠️  SKILL.md not found at /Users/selcuk/Downloads/SKILL.md")
            self.skill_content = None
        else:
            with open(self.skill_path, 'r', encoding='utf-8') as f:
                self.skill_content = f.read()
            print(" SKILL.md loaded successfully")
    
    def generate_report(self, rca_data: Dict, output_filename: Optional[str] = None) -> str:
        """
        Generate PDF report using Claude Opus 4 and SKILL.md
        
        Args:
            rca_data: Root cause analysis data (from agents)
            output_filename: Optional output filename
            
        Returns:
            Path to generated PDF file
        """
        
        print("\n" + "="*80)
        print(" CLAUDE OPUS 4 - SKILL-BASED PDF GENERATION")
        print("="*80)
        
        if not self.skill_content:
            raise ValueError("SKILL.md not loaded")
        
        # Transform RCA data to HSE format
        hse_data = self._transform_to_hse_format(rca_data)
        
        # Generate output filename
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"HSE_RCA_Report_{timestamp}.pdf"
        
        output_path = self.output_dir / output_filename
        
        # Prepare prompt for Claude
        prompt = self._build_claude_prompt(hse_data, str(output_path))
        
        print(" Sending request to Claude Opus 4...")
        print(f"RCA Data: {len(hse_data.get('five_whys', []))} 5-Why steps")
        print(f" Output: {output_path}")
        print(" Claude is generating and executing PDF code...")
        
        try:
            # Call Claude Opus 4
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=32000  # Maximum for complete code
            )
            
            result = response.choices[0].message.content.strip()
            
            print(" Claude Opus 4 response received")
            print("\n" + "-"*80)
            print(" CLAUDE'S RESPONSE:")
            print("-"*80)
            print(result[:500] + "..." if len(result) > 500 else result)
            print("-"*80)
            
            # Extract and execute Python code from Claude's response
            pdf_path = self._extract_and_execute_code(result, hse_data, str(output_path))
            
            if pdf_path and Path(pdf_path).exists():
                print(f"\n PDF Generated Successfully!")
                print(f" File: {pdf_path}")
                return str(pdf_path)
            else:
                print(" PDF generation failed - no file created")
                return None
                
        except Exception as e:
            print(f" Error: {e}")
            raise
    
    def _transform_to_hse_format(self, rca_data: Dict) -> Dict:
        """Transform RCA data to HSE format expected by SKILL.md"""
        
        # Extract 5-Why chains from analysis branches
        branches = rca_data.get('analysis_branches', [])
        root_causes = rca_data.get('final_root_causes', [])
        
        five_whys = []
        
        # Build 5-Why chain from first branch
        if branches:
            main_branch = branches[0]
            whys = main_branch.get('why_chain', [])
            
            for i, why in enumerate(whys[:5], 1):  # Max 5 whys
                five_whys.append({
                    "why": i,
                    "question": f"Neden {i}: {why.get('question', '')}",
                    "answer": why.get('answer', ''),
                    "evidence": why.get('evidence', 'Analiz verisi'),
                    "confidence": "HIGH" if i <= 3 else "MEDIUM"
                })
        
        # Add more whys if needed (minimum 3)
        while len(five_whys) < 3:
            five_whys.append({
                "why": len(five_whys) + 1,
                "question": f"Neden {len(five_whys) + 1}: Detaylı analiz devam ediyor",
                "answer": "İnceleme yapılmaktadır",
                "evidence": "Süreç devam ediyor",
                "confidence": "MEDIUM"
            })
        
        # Build corrective actions
        corrective_actions = []
        for i, rc in enumerate(root_causes[:5], 1):
            corrective_actions.append({
                "id": f"CA-{i:02d}",
                "description": rc.get('explanation_tr', 'Düzeltici faaliyet planlanıyor')[:100],
                "responsible": "HSE Yöneticisi",
                "due_date": datetime.now().replace(day=min(28, datetime.now().day + 30)).strftime("%Y-%m-%d"),
                "priority": "CRITICAL" if i == 1 else ("HIGH" if i <= 2 else "MEDIUM"),
                "status": "PLANNED"
            })
        
        # Build HSE report structure
        return {
            "incident_id": f"INC-{datetime.now().strftime('%Y-%m')}-{abs(hash(rca_data.get('incident_summary', ''))) % 10000:04d}",
            "incident_title": rca_data.get('incident_summary', 'Root Cause Analysis')[:100],
            "incident_date": datetime.now().strftime("%Y-%m-%d"),
            "location": "Üretim Sahası / Fabrika",
            "department": "HSE & Operations",
            "severity": "HIGH",
            "incident_type": "Root Cause Analysis",
            "reported_by": "Sistem Operatörü",
            "investigated_by": "Agentic AI RCA Sistemi",
            "investigation_date": datetime.now().strftime("%Y-%m-%d"),
            "description": rca_data.get('incident_summary', 'Detaylı kök neden analizi gerçekleştirildi.'),
            "immediate_consequences": [
                f"{len(branches)} farklı analiz dalı incelendi",
                f"{len(root_causes)} kök neden tespit edildi",
                "Hiyerarşik 5-Why metodolojisi uygulandı"
            ],
            "five_whys": five_whys,
            "root_cause": root_causes[0].get('explanation_tr', 'Analiz devam ediyor') if root_causes else "Kök neden belirleniyor",
            "contributing_factors": [rc.get('standard_title_tr', 'Faktör analizi') for rc in root_causes[1:4]],
            "corrective_actions": corrective_actions,
            "risk_assessment": {
                "likelihood_before": 4,
                "severity_before": 5,
                "risk_score_before": 20,
                "risk_level_before": "CRITICAL",
                "likelihood_after": 2,
                "severity_after": 4,
                "risk_score_after": 8,
                "risk_level_after": "MEDIUM"
            },
            "lessons_learned": "Hiyerarşik 5-Why metodolojisi ile çoklu kök neden başarıyla tespit edildi. Organizasyonel ve sistemsel faktörler öncelikli olarak ele alınmalıdır.",
            "similar_incidents": len(branches),
            "estimated_cost": 0,
            "analysis_method": rca_data.get('analysis_method', 'HSG245 5-Why Hierarchical Analysis'),
            "total_branches": len(branches),
            "total_root_causes": len(root_causes)
        }
    
    def _build_claude_prompt(self, hse_data: Dict, output_path: str) -> str:
        """Build prompt for Claude including SKILL.md and data"""
        
        data_json = json.dumps(hse_data, ensure_ascii=False, indent=2)
        
        prompt = f"""Sen bir HSE (Health, Safety, Environment) Root Cause Analysis rapor uzmanısın.

Aşağıda verilen SKILL.md dosyasını kullanarak profesyonel bir PDF raporu oluşturman gerekiyor.

# SKILL.MD İÇERİĞİ:
{self.skill_content}

# RCA VERİSİ (JSON):
```json
{data_json}
```

# GÖREV:
1. SKILL.md'deki tüm özellikleri kullanarak Python kodu yaz
2. ReportLab kütüphanesi kullan
3. Türkçe karakter desteği için UTF-8 encoding kullan
4. PDF dosyasını şu konuma kaydet: {output_path}
5. Tüm renk paletini (HSEColors) kullan
6. 5-Why zincirini görsel olarak çiz
7. Risk matrisini (5x5) oluştur
8. KPI özet kutularını ekle
9. Düzeltici faaliyetler tablosunu oluştur

# ÖNEMLİ:
- Kod bloğunu ```python ... ``` içinde ver
- Çalıştırılabilir tam kod olsun
- Türkçe karakterler için encoding='utf-8' kullan
- Tüm importları ekle
- Hata yönetimi ekle

Lütfen SKILL.md'deki yapıyı birebir uygula ve çalışır Python kodu üret."""

        return prompt
    
    def _extract_and_execute_code(self, claude_response: str, hse_data: Dict, output_path: str) -> Optional[str]:
        """Extract Python code from Claude's response and execute it"""
        
        # Find Python code blocks (multiple patterns)
        import re
        
        # Try different patterns
        patterns = [
            r'```python\s+(.*?)```',
            r'```\s*python\s+(.*?)```',
            r'```(?:python)?\s*\n(.*?)\n```',
        ]
        
        code_blocks = []
        for pattern in patterns:
            blocks = re.findall(pattern, claude_response, re.DOTALL | re.MULTILINE | re.IGNORECASE)
            if blocks:
                code_blocks.extend(blocks)
        
        if not code_blocks:
            print(" No Python code found in Claude's response")
            print("\n Full response preview:")
            print(claude_response[:2000])
            
            # Save full response for debugging
            debug_path = self.output_dir / "claude_response_debug.txt"
            with open(debug_path, 'w', encoding='utf-8') as f:
                f.write(claude_response)
            print(f"\n Full response saved to: {debug_path}")
            return None
        
        # Use the first (or longest) code block
        code = max(code_blocks, key=len) if len(code_blocks) > 1 else code_blocks[0]
        
        print(f"\n Extracted {len(code)} characters of Python code")
        print(" Executing code...")
        
        # Save code to temporary file
        temp_code_path = self.output_dir / "temp_pdf_generator.py"
        with open(temp_code_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        print(f"💾 Code saved to: {temp_code_path}")
        
        # Save data to JSON file
        temp_data_path = self.output_dir / "temp_rca_data.json"
        with open(temp_data_path, 'w', encoding='utf-8') as f:
            json.dump(hse_data, f, ensure_ascii=False, indent=2)
        
        # Execute the code using subprocess (more reliable than exec)
        import subprocess
        try:
            print(" Running code via subprocess...")
            
            # Get absolute paths
            abs_code_path = temp_code_path.resolve()
            abs_output_path = Path(output_path).resolve()
            
            result = subprocess.run(
                ["/opt/homebrew/bin/python3.10", str(abs_code_path)],
                capture_output=True,
                text=True,
                timeout=120,
                env={**os.environ}
            )
            
            if result.returncode == 0:
                print(" Subprocess execution successful")
                print(result.stdout)
                
                if Path(output_path).exists():
                    return output_path
                else:
                    print("  PDF file not found after execution")
                    return None
            else:
                print(f" Subprocess error: {result.stderr}")
                print(f"Stdout: {result.stdout}")
                return None
                
        except subprocess.TimeoutExpired:
            print(" Execution timeout (120s)")
            return None
        except Exception as e:
            print(f" Subprocess execution failed: {e}")
            return None


if __name__ == "__main__":
    """Test the Claude Skill PDF Agent"""
    import sys
    
    print("\n" + "="*80)
    print(" CLAUDE SKILL-BASED PDF AGENT TEST")
    print("="*80)
    
    # Load test RCA data
    test_data_path = Path("test_hierarchical_output.json")
    
    if not test_data_path.exists():
        print(" Test data not found: test_hierarchical_output.json")
        print(" Run test_hierarchical_rca.py first to generate test data")
        sys.exit(1)
    
    with open(test_data_path, 'r', encoding='utf-8') as f:
        rca_data = json.load(f)
    
    print(f" Loaded RCA data from {test_data_path}")
    print(f"   - {len(rca_data.get('analysis_branches', []))} analysis branches")
    print(f"   - {len(rca_data.get('final_root_causes', []))} root causes")
    
    # Initialize agent
    try:
        agent = ClaudeSkillPDFAgent()
        print(" Claude Skill PDF Agent initialized")
    except Exception as e:
        print(f" Failed to initialize agent: {e}")
        sys.exit(1)
    
    # Generate report
    print("\n Starting PDF generation with Claude Opus 4...")
    try:
        pdf_path = agent.generate_report(rca_data)
        
        if pdf_path:
            print("\n" + "="*80)
            print(" SUCCESS - PDF REPORT GENERATED")
            print("="*80)
            print(f" File: {pdf_path}")
            print(f" Size: {Path(pdf_path).stat().st_size / 1024:.1f} KB")
            print("\n Open with: open " + pdf_path)
        else:
            print("\n PDF generation failed")

    except Exception as e:
        print(f"\n Error during generation: {e}")
        import traceback
        traceback.print_exc()
