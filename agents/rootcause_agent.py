"""
Root Cause Agent - Part 3 of HSG245
Performs 5 Why Analysis and identifies immediate, underlying, and root causes
"""

from openai import OpenAI
from typing import Dict, List, Optional
import json


class RootCauseAgent:
    """
    Part 3: Root Cause Analysis
    Implements 5 Why methodology to identify:
    - Immediate causes (direct causes of the incident)
    - Underlying causes (contributing factors)
    - Root causes (systemic/organizational failures)
    
    Uses AI to build causal chains and analyze incidents
    """
    
    def __init__(self, openai_config: Dict):
        """Initialize Root Cause Agent with OpenAI configuration"""
        self.client = OpenAI(api_key=openai_config["api_key"])
        self.model = openai_config["model"]
        self.temperature = openai_config["temperature"]
        
        print(f"✅ Root Cause Agent initialized (Model: {self.model})")
    
    def analyze_root_causes(self, 
                          part1_data: Dict, 
                          part2_data: Dict,
                          investigation_data: Dict = None) -> Dict:
        """
        Perform comprehensive root cause analysis
        
        Args:
            part1_data: Overview data
            part2_data: Assessment data
            investigation_data: Detailed investigation information (optional)
            
        Returns:
            Root cause analysis results with 5 Why chains
        """
        print("\n" + "="*80)
        print("📋 PART 3: ROOT CAUSE ANALYSIS - Analyzing Incident")
        print("="*80)
        
        # Prepare incident description
        incident_summary = self._prepare_incident_summary(part1_data, part2_data, investigation_data)
        
        # Initialize root cause analysis structure
        rca_data = {
            "incident_summary": incident_summary,
            "five_why_chains": [],
            "immediate_causes": [],
            "underlying_causes": [],
            "root_causes": [],
            "causal_relationships": [],
            "analysis_method": "5 Why Analysis + Causal Chain"
        }
        
        # Perform 5 Why Analysis
        print("\n🔍 Performing 5 Why Analysis...")
        five_why_results = self._perform_five_why_analysis(incident_summary)
        rca_data["five_why_chains"] = five_why_results
        
        # Extract and categorize causes
        print("\n📊 Categorizing causes...")
        categorized_causes = self._categorize_causes(five_why_results, incident_summary)
        rca_data["immediate_causes"] = categorized_causes["immediate"]
        rca_data["underlying_causes"] = categorized_causes["underlying"]
        rca_data["root_causes"] = categorized_causes["root"]
        
        # Build causal relationships
        print("\n🔗 Building causal relationships...")
        rca_data["causal_relationships"] = self._build_causal_relationships(
            categorized_causes, five_why_results
        )
        
        self._print_summary(rca_data)
        
        return rca_data
    
    def _prepare_incident_summary(self, part1_data: Dict, part2_data: Dict, 
                                 investigation_data: Dict = None) -> str:
        """Combine all available information into incident summary"""
        summary_parts = []
        
        # Part 1 info
        brief = part1_data.get("brief_details", {})
        if brief.get("what"):
            summary_parts.append(f"What happened: {brief['what']}")
        if brief.get("who"):
            summary_parts.append(f"Who: {brief['who']}")
        if brief.get("where"):
            summary_parts.append(f"Where: {brief['where']}")
        
        # Part 2 info
        summary_parts.append(f"Event type: {part2_data.get('type_of_event', 'Unknown')}")
        summary_parts.append(f"Severity: {part2_data.get('actual_potential_harm', 'Unknown')}")
        
        # Additional investigation data
        if investigation_data:
            if investigation_data.get("equipment"):
                summary_parts.append(f"Equipment: {investigation_data['equipment']}")
            if investigation_data.get("additional_details"):
                summary_parts.append(investigation_data["additional_details"])
        
        return ". ".join(summary_parts)
    
    def _perform_five_why_analysis(self, incident_summary: str) -> List[Dict]:
        """
        Perform 5 Why Analysis using AI to identify multiple causal chains
        """
        prompt = f"""You are a root cause analysis expert using the 5 Why methodology.

INCIDENT SUMMARY:
{incident_summary}

Perform a comprehensive 5 Why Analysis. The incident may have MULTIPLE causal chains (e.g., Chain A, B, C).

For EACH causal chain:
1. Start with "Why did the incident occur?" (Why 1)
2. Ask "Why?" 4 more times, going deeper each time
3. Each "Why" should identify a cause, and "Because" should explain it
4. Final answer should be a root cause (organizational/systemic issue)

Example format from HSG245:
Chain A:
- Why 1: Person was injured
- Because: They were working on machine
- Why 2: Why were they working on machine?
- Because: They were investigating a fault
- Why 3: Why were they investigating?
- Because: No procedures for reporting faults
- Why 4: Why no procedures?
- Because: Duties/responsibilities not clearly set out
- Why 5 (ROOT): Why weren't duties clear?
- Because: Management system inadequate

Return a JSON with:
- chains: Array of chain objects, each with:
  - chain_id: "A", "B", "C", etc.
  - description: Brief description of this chain
  - whys: Array of 5 objects with "question" and "answer"
  - root_cause: The final root cause identified

Return ONLY valid JSON with 2-4 causal chains."""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.3,
            messages=[
                {"role": "system", "content": "You are a 5 Why analysis expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        
        result = response.choices[0].message.content.strip()
        
        # Clean JSON
        if result.startswith("```json"):
            result = result.replace("```json", "").replace("```", "").strip()
        elif result.startswith("```"):
            result = result.replace("```", "").strip()
        
        try:
            analysis = json.loads(result)
            chains = analysis.get("chains", [])
            
            print(f"✅ Identified {len(chains)} causal chains")
            for chain in chains:
                print(f"   Chain {chain.get('chain_id', '?')}: {chain.get('description', 'N/A')}")
            
            return chains
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parsing error: {e}")
            return []
    
    def _categorize_causes(self, five_why_chains: List[Dict], incident_summary: str) -> Dict:
        """
        Categorize causes into Immediate, Underlying, and Root causes using AI
        """
        chains_text = json.dumps(five_why_chains, indent=2)
        
        prompt = f"""You are a root cause analysis expert. Categorize causes from the 5 Why analysis.

INCIDENT SUMMARY:
{incident_summary}

5 WHY CHAINS:
{chains_text}

Categorize the identified causes into three levels:

1. IMMEDIATE CAUSES (Direct causes):
   - Unsafe acts or conditions that directly caused the incident
   - Examples: Guard was open, machine was live, hand in danger area

2. UNDERLYING CAUSES (Contributing factors):
   - Equipment issues, procedural gaps, competence issues
   - Examples: Interlock easily defeated, no isolation procedures, inadequate training

3. ROOT CAUSES (Systemic/organizational):
   - Management system failures, organizational culture issues
   - Examples: Inadequate safety management, poor risk assessment, unclear responsibilities

Return a JSON with:
- immediate: Array of immediate causes (each with "cause" and "description")
- underlying: Array of underlying causes (each with "cause" and "description")
- root: Array of root causes (each with "cause" and "description")

Provide 3-5 causes for each category.

Return ONLY valid JSON."""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.3,
            messages=[
                {"role": "system", "content": "You are a cause categorization expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        
        result = response.choices[0].message.content.strip()
        
        # Clean JSON
        if result.startswith("```json"):
            result = result.replace("```json", "").replace("```", "").strip()
        elif result.startswith("```"):
            result = result.replace("```", "").strip()
        
        try:
            categorized = json.loads(result)
            
            print(f"✅ Categorized causes:")
            print(f"   Immediate: {len(categorized.get('immediate', []))} causes")
            print(f"   Underlying: {len(categorized.get('underlying', []))} causes")
            print(f"   Root: {len(categorized.get('root', []))} causes")
            
            return categorized
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parsing error: {e}")
            return {"immediate": [], "underlying": [], "root": []}
    
    def _build_causal_relationships(self, categorized_causes: Dict, 
                                   five_why_chains: List[Dict]) -> List[Dict]:
        """
        Build relationships showing how causes connect (similar to HSG245 diagram)
        """
        print("🔗 Mapping causal relationships...")
        
        relationships = []
        
        # For each root cause, trace back to immediate causes
        for root in categorized_causes.get("root", []):
            for underlying in categorized_causes.get("underlying", []):
                for immediate in categorized_causes.get("immediate", []):
                    relationships.append({
                        "from": immediate.get("cause", ""),
                        "through": underlying.get("cause", ""),
                        "to": root.get("cause", ""),
                        "relationship_type": "causal_chain"
                    })
        
        print(f"✅ Identified {len(relationships)} causal relationships")
        
        return relationships[:10]  # Limit to prevent overwhelming output
    
    def _print_summary(self, rca_data: Dict):
        """Print formatted summary of root cause analysis"""
        print("\n" + "-"*80)
        print("📊 ROOT CAUSE ANALYSIS SUMMARY")
        print("-"*80)
        
        print(f"\n📋 Incident Summary:")
        print(f"{rca_data['incident_summary']}")
        
        print(f"\n🔍 5 Why Analysis - Identified {len(rca_data['five_why_chains'])} Causal Chains:")
        for chain in rca_data['five_why_chains']:
            chain_id = chain.get('chain_id', '?')
            desc = chain.get('description', 'N/A')
            root = chain.get('root_cause', 'N/A')
            print(f"\n   Chain {chain_id}: {desc}")
            print(f"   → Root Cause: {root}")
        
        print(f"\n⚡ IMMEDIATE CAUSES ({len(rca_data['immediate_causes'])}):")
        for idx, cause in enumerate(rca_data['immediate_causes'], 1):
            print(f"   {idx}. {cause.get('cause', 'N/A')}")
            if cause.get('description'):
                print(f"      └─ {cause['description']}")
        
        print(f"\n🔧 UNDERLYING CAUSES ({len(rca_data['underlying_causes'])}):")
        for idx, cause in enumerate(rca_data['underlying_causes'], 1):
            print(f"   {idx}. {cause.get('cause', 'N/A')}")
            if cause.get('description'):
                print(f"      └─ {cause['description']}")
        
        print(f"\n🎯 ROOT CAUSES ({len(rca_data['root_causes'])}):")
        for idx, cause in enumerate(rca_data['root_causes'], 1):
            print(f"   {idx}. {cause.get('cause', 'N/A')}")
            if cause.get('description'):
                print(f"      └─ {cause['description']}")
        
        print("-"*80)
