"""
Root Cause Agent - Part 3 of HSG245
Performs 5 Why Analysis and identifies immediate, underlying, and root causes
"""

from openai import OpenAI
from typing import Dict, List, Optional
import json
import os


class RootCauseAgent:
    """
    Part 3: Root Cause Analysis
    Implements 5 Why methodology to identify:
    - Immediate causes (direct causes of the incident)
    - Underlying causes (contributing factors)
    - Root causes (systemic/organizational failures)
    
    Uses AI to build causal chains and analyze incidents
    """
    
    def __init__(self):
        """Initialize Root Cause Agent with OpenRouter"""
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        print(f"✅ Root Cause Agent initialized with OpenRouter")
    
    def analyze_root_causes(self, 
                          part1_data: Dict, 
                          part2_data: Dict,
                          investigation_data: Dict = None) -> Dict:
        """
        Perform comprehensive root cause analysis following HSG245 methodology
        
        CORRECT FLOW:
        1. Identify immediate causes (direct causes)
        2. For each immediate cause, perform 5 Why analysis
        3. Extract underlying causes (Why 2-4) and root causes (Why 5)
        
        Args:
            part1_data: Overview data
            part2_data: Assessment data
            investigation_data: Detailed investigation information (optional)
            
        Returns:
            Root cause analysis results with 5 Why chains
        """
        print("\n" + "="*80)
        print("📋 BÖLÜM 3: KÖK NEDEN ANALİZİ - Olay Analiz Ediliyor")
        print("📋 PART 3: ROOT CAUSE ANALYSIS - Analyzing Incident")
        print("="*80)
        
        # Prepare incident description
        incident_summary = self._prepare_incident_summary(part1_data, part2_data, investigation_data)
        
        # Initialize root cause analysis structure
        rca_data = {
            "incident_summary": incident_summary,
            "immediate_causes": [],
            "five_why_chains": [],  # One chain per immediate cause
            "underlying_causes": [],
            "root_causes": [],
            "analysis_method": "HSG245 5 Why Analysis"
        }
        
        # STEP 1: Identify immediate causes first
        print("\n🔍 ADIM 1: Doğrudan Nedenleri Belirleme...")
        print("🔍 STEP 1: Identifying Immediate Causes...")
        immediate_causes = self._identify_immediate_causes(incident_summary)
        rca_data["immediate_causes"] = immediate_causes
        
        # STEP 2: For each immediate cause, perform 5 Why analysis
        print(f"\n� ADIM 2: Her Doğrudan Neden için 5 Neden Analizi ({len(immediate_causes)} zincir)...")
        print(f"🔗 STEP 2: Performing 5 Why for Each Immediate Cause ({len(immediate_causes)} chains)...")
        
        all_chains = []
        all_underlying = []
        all_root = []
        
        for idx, immediate_cause in enumerate(immediate_causes, 1):
            print(f"\n   Zincir {idx}/{len(immediate_causes)}: {immediate_cause.get('cause_tr', immediate_cause.get('cause', ''))}...")
            print(f"   Chain {idx}/{len(immediate_causes)}: {immediate_cause.get('cause', '')}...")
            
            # Perform 5 Why for this immediate cause
            chain = self._perform_5why_for_cause(immediate_cause, incident_summary)
            all_chains.append(chain)
            
            # Extract underlying and root from this chain
            underlying = self._extract_underlying_from_chain(chain)
            root = self._extract_root_from_chain(chain)
            
            all_underlying.extend(underlying)
            all_root.append(root)
        
        rca_data["five_why_chains"] = all_chains
        rca_data["underlying_causes"] = all_underlying
        rca_data["root_causes"] = all_root
        
        print("\n✅ Kök neden analizi tamamlandı!")
        print("✅ Root cause analysis complete!")
        
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
    
    def _identify_immediate_causes(self, incident_summary: str) -> List[Dict]:
        """
        STEP 1: Identify immediate (direct) causes of the incident
        These are the unsafe acts or conditions that directly caused the incident
        """
        prompt = f"""You are a UK Health & Safety incident investigator following HSG245 methodology.

OLAY ÖZETİ / INCIDENT SUMMARY:
{incident_summary}

GÖREV: Olayın DOĞRUDAN NEDENLERİNİ belirleyin.
TASK: Identify the IMMEDIATE CAUSES (direct causes) of this incident.

IMMEDIATE CAUSES are:
- Unsafe acts or conditions that DIRECTLY caused the incident
- The "what went wrong" at the moment of the incident
- Typically 2-4 immediate causes per incident

DOĞRUDAN NEDENLER:
- Olayı DOĞRUDAN YARATIRAN güvensiz davranışlar veya koşullar
- Olay anında "neyin yanlış gittiği"
- Genellikle olay başına 2-4 doğrudan neden

Examples from HSG245:
- Person's hand was in danger area (Kişinin eli tehlike bölgesindeydi)
- Machine guard was open (Makine koruyucusu açıktı)
- Machine was still energized (Makine hala enerjiliydi)
- No safety procedure followed (Güvenlik prosedürü uygulanmadı)

Return JSON with:
- causes: Array of 2-4 immediate causes, each with:
  - cause: English description
  - cause_tr: Turkish description
  - evidence: Supporting evidence/facts
  - evidence_tr: Turkish evidence

Return ONLY valid JSON."""

        response = self.client.chat.completions.create(
            model="openai/gpt-4-turbo",
            temperature=0.2,
            messages=[
                {"role": "system", "content": "You are an HSG245 incident investigation expert. Return only valid JSON with bilingual content."},
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
            data = json.loads(result)
            causes = data.get("causes", [])
            
            print(f"✅ {len(causes)} doğrudan neden belirlendi")
            print(f"✅ Identified {len(causes)} immediate causes")
            for idx, cause in enumerate(causes, 1):
                print(f"   {idx}. {cause.get('cause_tr', cause.get('cause', 'N/A'))}")
            
            return causes
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON ayrıştırma hatası / JSON parsing error: {e}")
            return []
    
    def _perform_5why_for_cause(self, immediate_cause: Dict, incident_summary: str) -> Dict:
        """
        STEP 2: Perform 5 Why analysis for ONE immediate cause
        Returns a single causal chain from immediate → root cause
        """
        cause_en = immediate_cause.get("cause", "")
        cause_tr = immediate_cause.get("cause_tr", "")
        
        prompt = f"""You are performing 5 Why Analysis following HSG245 methodology.

OLAY ÖZETİ / INCIDENT SUMMARY:
{incident_summary}

DOĞRUDAN NEDEN / IMMEDIATE CAUSE:
EN: {cause_en}
TR: {cause_tr}

GÖREV: Bu doğrudan neden için 5 NEDEN analizi yapın.
TASK: Perform 5 WHY analysis for this immediate cause.

5 WHY METHODOLOGY:
Start with the immediate cause and ask "Why?" 5 times, going deeper each time.

Why 1: Why did this immediate cause occur?
Why 2: Why did that happen? (UNDERLYING CAUSE level starts)
Why 3: Why did that happen? (UNDERLYING CAUSE)
Why 4: Why did that happen? (UNDERLYING CAUSE)
Why 5: Why did that happen? (ROOT CAUSE - organizational/systemic)

Example from HSG245:
Why 1: Why was hand in danger area?
Because: Person was investigating a fault (İşçi bir arızayı inceliyordu)

Why 2: Why were they investigating themselves?
Because: No procedure for reporting faults (Arıza bildirme prosedürü yoktu)

Why 3: Why no procedure?
Because: Duties not clearly set out (Görevler açıkça belirtilmemişti)

Why 4: Why duties unclear?
Because: Inadequate management system (Yetersiz yönetim sistemi)

Why 5 (ROOT): Why inadequate management?
Because: No systematic risk assessment (Sistematik risk değerlendirmesi yapılmamıştı)

Return JSON with:
- immediate_cause: The starting cause (EN + TR)
- why_chain: Array of 5 why-because pairs, each with:
  - level: 1-5
  - why_question: The "why" question (EN)
  - why_question_tr: Turkish translation
  - because_answer: The "because" answer (EN)
  - because_answer_tr: Turkish translation
  - cause_type: "immediate" (level 1), "underlying" (levels 2-4), "root" (level 5)
- root_cause: Final root cause summary (EN + TR)

Return ONLY valid JSON with complete bilingual content."""

        response = self.client.chat.completions.create(
            model="openai/gpt-4-turbo",
            temperature=0.3,
            messages=[
                {"role": "system", "content": "You are a 5 Why analysis expert following HSG245. Return only valid JSON with bilingual content."},
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
            chain = json.loads(result)
            root = chain.get("root_cause", {})
            print(f"      → Kök neden / Root: {root.get('root_tr', root.get('root', 'N/A'))}")
            return chain
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON ayrıştırma hatası / JSON parsing error: {e}")
            return {
                "immediate_cause": immediate_cause,
                "why_chain": [],
                "root_cause": {}
            }
    
    def _extract_underlying_from_chain(self, chain: Dict) -> List[Dict]:
        """
        Extract underlying causes from Why levels 2-4
        """
        underlying = []
        why_chain = chain.get("why_chain", [])
        
        for why in why_chain:
            if why.get("cause_type") == "underlying":
                underlying.append({
                    "cause": why.get("because_answer", ""),
                    "cause_tr": why.get("because_answer_tr", ""),
                    "level": why.get("level", 0),
                    "from_chain": chain.get("immediate_cause", {}).get("cause", "")
                })
        
        return underlying
    
    def _extract_root_from_chain(self, chain: Dict) -> Dict:
        """
        Extract root cause from Why level 5
        """
        why_chain = chain.get("why_chain", [])
        
        # Find Why 5 (root cause level)
        for why in why_chain:
            if why.get("level") == 5 or why.get("cause_type") == "root":
                return {
                    "cause": why.get("because_answer", ""),
                    "cause_tr": why.get("because_answer_tr", ""),
                    "from_immediate": chain.get("immediate_cause", {}).get("cause", ""),
                    "from_immediate_tr": chain.get("immediate_cause", {}).get("cause_tr", "")
                }
        
        # Fallback to root_cause summary if available
        root_summary = chain.get("root_cause", {})
        return {
            "cause": root_summary.get("root", "Unknown"),
            "cause_tr": root_summary.get("root_tr", "Bilinmiyor"),
            "from_immediate": chain.get("immediate_cause", {}).get("cause", ""),
            "from_immediate_tr": chain.get("immediate_cause", {}).get("cause_tr", "")
        }
    
    def _print_summary(self, rca_data: Dict):
        """Print formatted summary of root cause analysis - PDF friendly format"""
        print("\n" + "="*80)
        print("📊 KÖK NEDEN ANALİZİ ÖZETİ / ROOT CAUSE ANALYSIS SUMMARY")
        print("="*80)
        
        print(f"\n📋 Olay Özeti / Incident Summary:")
        print(f"{rca_data['incident_summary']}")
        
        # IMMEDIATE CAUSES
        print(f"\n{'='*80}")
        print(f"⚡ DOĞRUDAN NEDENLER / IMMEDIATE CAUSES ({len(rca_data['immediate_causes'])})")
        print(f"{'='*80}")
        for idx, cause in enumerate(rca_data['immediate_causes'], 1):
            print(f"\n{idx}. {cause.get('cause_tr', cause.get('cause', 'N/A'))}")
            print(f"   {cause.get('cause', 'N/A')}")
            if cause.get('evidence_tr'):
                print(f"   Kanıt: {cause.get('evidence_tr', '')}")
            if cause.get('evidence'):
                print(f"   Evidence: {cause.get('evidence', '')}")
        
        # 5 WHY CHAINS - One per immediate cause
        print(f"\n{'='*80}")
        print(f"🔗 5 NEDEN ZİNCİRLERİ / 5 WHY CHAINS ({len(rca_data['five_why_chains'])})")
        print(f"{'='*80}")
        
        for chain_idx, chain in enumerate(rca_data['five_why_chains'], 1):
            immediate = chain.get('immediate_cause', {})
            print(f"\n{'─'*80}")
            print(f"ZİNCİR {chain_idx} / CHAIN {chain_idx}")
            print(f"Başlangıç: {immediate.get('cause_tr', immediate.get('cause', 'N/A'))}")
            print(f"Starting: {immediate.get('cause', 'N/A')}")
            print(f"{'─'*80}")
            
            why_chain = chain.get('why_chain', [])
            for why in why_chain:
                level = why.get('level', 0)
                cause_type = why.get('cause_type', 'unknown')
                
                # Show hierarchy
                indent = "   " * (level - 1)
                
                print(f"\n{indent}📍 NEDEN {level} / WHY {level} [{cause_type.upper()}]")
                print(f"{indent}❓ {why.get('why_question_tr', why.get('why_question', 'N/A'))}")
                print(f"{indent}   {why.get('why_question', 'N/A')}")
                print(f"{indent}💡 {why.get('because_answer_tr', why.get('because_answer', 'N/A'))}")
                print(f"{indent}   {why.get('because_answer', 'N/A')}")
            
            # Root cause summary
            root = chain.get('root_cause', {})
            print(f"\n   🎯 KÖK NEDEN / ROOT CAUSE:")
            print(f"      {root.get('root_tr', root.get('root', 'N/A'))}")
            print(f"      {root.get('root', 'N/A')}")
        
        # UNDERLYING CAUSES SUMMARY
        print(f"\n{'='*80}")
        print(f"🔧 ALTTA YATAN NEDENLER / UNDERLYING CAUSES ({len(rca_data['underlying_causes'])})")
        print(f"{'='*80}")
        unique_underlying = {}
        for cause in rca_data['underlying_causes']:
            key = cause.get('cause', '')
            if key not in unique_underlying:
                unique_underlying[key] = cause
        
        for idx, cause in enumerate(unique_underlying.values(), 1):
            print(f"\n{idx}. {cause.get('cause_tr', cause.get('cause', 'N/A'))}")
            print(f"   {cause.get('cause', 'N/A')}")
            print(f"   (Seviye/Level {cause.get('level', '?')})")
        
        # ROOT CAUSES SUMMARY
        print(f"\n{'='*80}")
        print(f"🎯 KÖK NEDENLER / ROOT CAUSES ({len(rca_data['root_causes'])})")
        print(f"{'='*80}")
        for idx, cause in enumerate(rca_data['root_causes'], 1):
            print(f"\n{idx}. {cause.get('cause_tr', cause.get('cause', 'N/A'))}")
            print(f"   {cause.get('cause', 'N/A')}")
            print(f"   ← Kaynağı/From: {cause.get('from_immediate_tr', cause.get('from_immediate', 'N/A'))}")
            print(f"   ← From: {cause.get('from_immediate', 'N/A')}")
        
        print(f"\n{'='*80}")
        print(f"✅ Analiz tamamlandı / Analysis complete")
        print(f"{'='*80}\n")
