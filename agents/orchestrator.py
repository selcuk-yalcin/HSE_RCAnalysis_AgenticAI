"""
Root Cause Orchestrator - Coordinates all agents in HSG245 workflow
"""

from typing import Dict, Optional
from .overview_agent import OverviewAgent
from .assessment_agent import AssessmentAgent
from .rootcause_agent import RootCauseAgent


class RootCauseOrchestrator:
    """
    Master coordinator for HSG245 investigation workflow
    
    Workflow:
    1. Overview Agent → Part 1 data
    2. Assessment Agent → Part 2 data
    3. Root Cause Agent → Part 3 analysis
    4. Generate final report
    """
    
    def __init__(self, openai_config: Dict):
        """Initialize all agents"""
        print("\n" + "="*80)
        print("🚀 INITIALIZING ROOT CAUSE INVESTIGATION SYSTEM")
        print("="*80)
        
        self.overview_agent = OverviewAgent(openai_config)
        self.assessment_agent = AssessmentAgent(openai_config)
        self.rootcause_agent = RootCauseAgent(openai_config)
        
        self.investigation_data = {
            "part1": None,
            "part2": None,
            "part3_rca": None,
            "status": "initialized"
        }
        
        print("\n✅ All agents initialized successfully")
        print("="*80)
    
    def run_investigation(self, incident_data: Dict) -> Dict:
        """
        Run complete investigation workflow
        
        Args:
            incident_data: Initial incident information
            
        Returns:
            Complete investigation results
        """
        print("\n" + "="*80)
        print("🔬 STARTING INVESTIGATION WORKFLOW")
        print("="*80)
        
        try:
            # Step 1: Part 1 - Overview
            print("\n📌 STEP 1/3: Processing Overview (Part 1)")
            print("-"*80)
            self.investigation_data["part1"] = self.overview_agent.process_initial_report(
                incident_data
            )
            self.investigation_data["status"] = "part1_complete"
            
            # Step 2: Part 2 - Assessment
            print("\n📌 STEP 2/3: Conducting Assessment (Part 2)")
            print("-"*80)
            self.investigation_data["part2"] = self.assessment_agent.assess_incident(
                self.investigation_data["part1"],
                incident_data
            )
            self.investigation_data["status"] = "part2_complete"
            
            # Step 3: Part 3 - Root Cause Analysis
            print("\n📌 STEP 3/3: Performing Root Cause Analysis (Part 3)")
            print("-"*80)
            self.investigation_data["part3_rca"] = self.rootcause_agent.analyze_root_causes(
                self.investigation_data["part1"],
                self.investigation_data["part2"],
                incident_data.get("investigation_details")
            )
            self.investigation_data["status"] = "investigation_complete"
            
            # Success summary
            self._print_final_summary()
            
            return self.investigation_data
            
        except Exception as e:
            print(f"\n❌ Error during investigation: {e}")
            self.investigation_data["status"] = "error"
            self.investigation_data["error"] = str(e)
            raise
    
    def _print_final_summary(self):
        """Print final investigation summary"""
        print("\n" + "="*80)
        print("✅ INVESTIGATION COMPLETE")
        print("="*80)
        
        part1 = self.investigation_data.get("part1", {})
        part2 = self.investigation_data.get("part2", {})
        part3 = self.investigation_data.get("part3_rca", {})
        
        print(f"\n📋 Investigation Reference: {part1.get('ref_no', 'N/A')}")
        print(f"📊 Incident Type: {part1.get('incident_type', 'N/A')}")
        print(f"⚠️  Severity: {part2.get('actual_potential_harm', 'N/A')}")
        print(f"🔍 Investigation Level: {part2.get('investigation_level', 'N/A')}")
        print(f"📝 RIDDOR Reportable: {part2.get('riddor_reportable', 'N/A')}")
        
        print(f"\n🎯 Root Cause Analysis:")
        print(f"   - Causal Chains: {len(part3.get('five_why_chains', []))}")
        print(f"   - Immediate Causes: {len(part3.get('immediate_causes', []))}")
        print(f"   - Underlying Causes: {len(part3.get('underlying_causes', []))}")
        print(f"   - Root Causes: {len(part3.get('root_causes', []))}")
        
        print(f"\n✅ Status: {self.investigation_data.get('status', 'Unknown')}")
        print("="*80)
    
    def get_investigation_data(self) -> Dict:
        """Get current investigation data"""
        return self.investigation_data
    
    def export_to_json(self, filepath: str):
        """Export investigation to JSON file"""
        import json
        from pathlib import Path
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.investigation_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Investigation exported to: {filepath}")
