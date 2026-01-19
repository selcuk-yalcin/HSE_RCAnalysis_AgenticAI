"""
Root Cause Agent - Part 3 of HSG245
Performs 5 Why Analysis and identifies immediate, underlying, and root causes
Updated Strategy: DeepSeek V3 (Logic) + Claude 3.5 Sonnet (Reporting)
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
        
        # STEP 1: Identify immediate causes first (DeepSeek)
        print("\n🔍 ADIM 1: Doğrudan Nedenleri Belirleme (DeepSeek)...")
        immediate_causes = self._identify_immediate_causes(incident_summary)
        rca_data["immediate_causes"] = immediate_causes
        
        # STEP 2: For each immediate cause, perform 5 Why analysis (DeepSeek)
        print(f"\n🔗 ADIM 2: Her Doğrudan Neden için 5 Neden Analizi ({len(immediate_causes)} zincir)...")
        
        all_chains = []
        all_underlying = []
        all_root = []
        
        for idx, immediate_cause in enumerate(immediate_causes, 1):
            print(f"\n   Zincir {idx}/{len(immediate_causes)}: {immediate_cause.get('cause_tr', immediate_cause.get('cause', ''))}...")
            
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
        
        # --- ESKİ YÖNTEMİ DEVRE DIŞI BIRAKTIK ---
        # self._print_summary(rca_data)
        
        # --- YENİ YÖNTEM: CLAUDE İLE PROFESYONEL RAPOR ---
        self._generate_final_report(rca_data)
        
        return rca_data
    
    def _prepare_incident_summary(self, part1_data: Dict, part2_data: Dict, 
                                 investigation_data: Dict = None) -> str:
        """Combine all available information into incident summary"""
        summary_parts = []
        brief = part1_data.get("brief_details", {})
        if brief.get("what"): summary_parts.append(f"What happened: {brief['what']}")
        if brief.get("who"): summary_parts.append(f"Who: {brief['who']}")
        if brief.get("where"): summary_parts.append(f"Where: {brief['where']}")
        summary_parts.append(f"Event type: {part2_data.get('type_of_event', 'Unknown')}")
        summary_parts.append(f"Severity: {part2_data.get('actual_potential_harm', 'Unknown')}")
        if investigation_data:
            if investigation_data.get("equipment"): summary_parts.append(f"Equipment: {investigation_data['equipment']}")
            if investigation_data.get("additional_details"): summary_parts.append(investigation_data["additional_details"])
        return ". ".join(summary_parts)
    
    def _identify_immediate_causes(self, incident_summary: str) -> List[Dict]:
        """
        STEP 1: Identify immediate causes using DeepSeek V3 (Cost Effective Logic)
        """
        prompt = f"""You are a UK Health & Safety incident investigator following HSG245 methodology.

OLAY ÖZETİ / INCIDENT SUMMARY:
{incident_summary}

GÖREV: Olayın DOĞRUDAN NEDENLERİNİ belirleyin.
TASK: Identify the IMMEDIATE CAUSES (direct causes) of this incident.

IMMEDIATE CAUSES are:
- Unsafe acts or conditions that DIRECTLY caused the incident
- Typically 2-4 immediate causes per incident

Return JSON with:
- causes: Array of 2-4 immediate causes (cause, cause_tr, evidence, evidence_tr)

Return ONLY valid JSON."""

        response = self.client.chat.completions.create(
            # MODEL GÜNCELLEMESİ: DeepSeek V3
            model="deepseek/deepseek-chat",
            temperature=0.0,
            messages=[
                {"role": "system", "content": "You are an HSG245 incident investigation expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        
        result = response.choices[0].message.content.strip()
        if result.startswith("```json"): result = result.replace("```json", "").replace("```", "").strip()
        elif result.startswith("```"): result = result.replace("```", "").strip()
        
        try:
            data = json.loads(result)
            causes = data.get("causes", [])
            print(f"✅ {len(causes)} doğrudan neden belirlendi")
            return causes
        except json.JSONDecodeError:
            return []
    
    def _perform_5why_for_cause(self, immediate_cause: Dict, incident_summary: str) -> Dict:
        """
        STEP 2: Perform 5 Why analysis using DeepSeek V3 (Deep Logic)
        """
        cause_en = immediate_cause.get("cause", "")
        cause_tr = immediate_cause.get("cause_tr", "")
        
        prompt = f"""You are performing 5 Why Analysis following HSG245 methodology.

OLAY: {incident_summary}
NEDEN: {cause_en} ({cause_tr})

TASK: Perform 5 WHY analysis.
Why 1 -> Why 2 -> Why 3 -> Why 4 -> Why 5 (Root Cause)

Return JSON with:
- immediate_cause: ...
- why_chain: Array of 5 items (why_question, because_answer, etc.)
- root_cause: Final summary

Return ONLY valid JSON."""

        response = self.client.chat.completions.create(
            # MODEL GÜNCELLEMESİ: DeepSeek V3
            model="deepseek/deepseek-chat",
            temperature=0.0,
            messages=[
                {"role": "system", "content": "You are a 5 Why analysis expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        
        result = response.choices[0].message.content.strip()
        if result.startswith("```json"): result = result.replace("```json", "").replace("```", "").strip()
        elif result.startswith("```"): result = result.replace("```", "").strip()
        
        try:
            chain = json.loads(result)
            root = chain.get("root_cause", {})
            print(f"      → Kök: {root.get('root_tr', root.get('root', 'N/A'))}")
            return chain
        except json.JSONDecodeError:
            return {"immediate_cause": immediate_cause, "why_chain": [], "root_cause": {}}
    
    def _generate_final_report(self, rca_data: Dict):
        """
        FINAL EDITOR: Claude 3.5 Sonnet
        DeepSeek'in ürettiği ham veriyi (JSON) alır ve mükemmel bir Türkçe rapora çevirir.
        """
        print("\n✍️ Claude 3.5 Sonnet Final Raporu Yazıyor (Professional Report Generation)...")
        
        # DeepSeek'in bulduğu tüm veriyi metne döküyoruz
        raw_data_str = json.dumps(rca_data, indent=2, ensure_ascii=False)
        
        prompt = f"""You are a professional Report Editor using Claude 3.5 Sonnet.
        
        INPUT DATA (Analysis performed by DeepSeek AI):
        {raw_data_str}
        
        TASK:
        Write a professional, formal 'Root Cause Analysis Report' in TURKISH based on this data.
        
        REQUIREMENTS:
        1. Tone: Official, objective, senior safety engineer style.
        2. Structure:
           - YÖNETİCİ ÖZETİ (Executive Summary)
           - OLAY DETAYLARI (Incident Details)
           - DOĞRUDAN NEDENLER (Immediate Causes)
           - KÖK NEDEN ANALİZİ (Detailed 5 Why Chains)
           - SİSTEMİK BULGULAR (Systemic Failures - The Root Causes)
           - SONUÇ (Conclusion)
        3. Do NOT output JSON. Output clean, formatted text.
        4. Fix any logical gaps or bad translations from the input data.
        """

        # Raporlama için PAHALI ama KALİTELİ modeli kullanıyoruz
        response = self.client.chat.completions.create(
            model="anthropic/claude-3.5-sonnet", 
            temperature=0.3,
            messages=[
                {"role": "system", "content": "Sen kıdemli bir İş Güvenliği rapor editörüsün."},
                {"role": "user", "content": prompt}
            ]
        )
        
        print("\n" + "="*80)
        print(response.choices[0].message.content)
        print("="*80)

    # Helper methods (extract_underlying, extract_root) stay the same...
    def _extract_underlying_from_chain(self, chain: Dict) -> List[Dict]:
        underlying = []
        for why in chain.get("why_chain", []):
            if why.get("cause_type") == "underlying":
                underlying.append({
                    "cause": why.get("because_answer", ""),
                    "cause_tr": why.get("because_answer_tr", ""),
                    "level": why.get("level", 0)
                })
        return underlying
    
    def _extract_root_from_chain(self, chain: Dict) -> Dict:
        for why in chain.get("why_chain", []):
            if why.get("level") == 5 or why.get("cause_type") == "root":
                return {
                    "cause": why.get("because_answer", ""),
                    "cause_tr": why.get("because_answer_tr", "")
                }
        return chain.get("root_cause", {})

    def _print_summary(self, rca_data: Dict):
        # Bu fonksiyon artık kullanılmıyor ama eski loglar için tutulabilir.
        pass