"""
Root Cause Agent - Part 3 of HSG245
Performs 5 Why Analysis and identifies immediate, underlying, and root causes
Updated Strategy: DeepSeek V3 (Logic) + Claude 3.5 Sonnet (Reporting) (During inference, we planned to test many different model in order to improve results) 
"""

from openai import OpenAI
from typing import Dict, List, Optional
import json
import os


class RootCauseAgent:
    """
    Part 3: Root Cause Analysis
    Implements 5 Why methodology to identify:
    - Immediate causes (direct causes of the incident) #We will take that causes from our vector databases!!!)
    - Underlying causes (contributing factors)
    - Root causes (systemic/organizational failures) (We take list in to account when we will fill out the part!!)
    
    Uses AI to build causal chains and analyze incidents
    """
    
    def __init__(self):
        """Initialize Root Cause Agent with OpenRouter"""
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        # --- DEĞİŞİKLİK 1: İngilizce log -> Türkçe log ---
        print(f"✅ Kök Neden Ajanı (Root Cause Agent) başlatıldı")
    
    def analyze_root_causes(self, 
                          part1_data: Dict, 
                          part2_data: Dict,
                          investigation_data: Dict = None) -> Dict:
        """
        Perform comprehensive root cause analysis following HSG245 methodology
        """
        print("\n" + "="*80)
        print("📋 BÖLÜM 3: KÖK NEDEN ANALİZİ - Olay Analiz Ediliyor")
        print("="*80)
        
        # Prepare incident description (with fallback)
        try:
            incident_summary = self._prepare_incident_summary(part1_data, part2_data, investigation_data)
        except Exception as e:
            # --- DEĞİŞİKLİK 2: Log Türkçeleştirme ---
            print(f"⚠️ Uyarı: Tam özet hazırlanamadı ({e}). Sadece soruşturma verisi kullanılıyor.")
            # Fallback: Use only investigation data
            incident_summary = f"{investigation_data.get('how_happened', 'Olay detayı mevcut değil')}"
        
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
        print("\n🔍 ADIM 1: Doğrudan Nedenleri Belirleme ...")
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
        
        # --- DEĞİŞİKLİK 4 (YENİ KOD): Raporu yakala ve veriye ekle ---
        try:
            # Raporu fonksiyondan alıyoruz
            final_report_text = self._generate_final_report(rca_data)
            
            # Admin panelinin okuması için sözlüğe ekliyoruz
            rca_data["final_report_tr"] = final_report_text
            
        except Exception as e:
            print(f"❌ Rapor oluşturulurken hata: {e}")
            rca_data["final_report_tr"] = "Rapor oluşturulamadı."
        
        # Veriyi döndür (Artık içinde final_report_tr var!)
        return rca_data
    
    def _prepare_incident_summary(self, part1_data: Dict, part2_data: Dict, 
                                 investigation_data: Dict = None) -> str:
        """Combine all available information into incident summary"""
        # DEBUG: Check types
        print(f"🐛 DEBUG - part1_data type: {type(part1_data)}, value: {part1_data}")
        print(f"🐛 DEBUG - part2_data type: {type(part2_data)}, value: {part2_data}")
        
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
        STEP 1: Identify immediate causes using AI with Turkish output
        """
        prompt = f"""You are a UK Health & Safety incident investigator following HSG245 methodology.

INCIDENT SUMMARY:
{incident_summary}

TASK: Identify the IMMEDIATE CAUSES (direct causes) of this incident.

IMMEDIATE CAUSES are:
- Unsafe acts or conditions that DIRECTLY caused the incident
- Typically 2-4 immediate causes per incident

Return JSON with:
- causes: Array of 2-4 immediate causes (cause, cause_tr, evidence, evidence_tr)

CRITICAL: All text fields (cause, cause_tr, evidence, evidence_tr) must be 100% in TURKISH language. No English words allowed.

Return ONLY valid JSON."""

        response = self.client.chat.completions.create(
            model="google/gemma-3-27b-it:free",
            temperature=0.1,
            messages=[
                {"role": "system", "content": "You are an HSG245 incident investigation expert. Return only valid JSON with ALL content in TURKISH language."},
                {"role": "user", "content": prompt}
            ]
        )
        
        result = response.choices[0].message.content.strip()
        if result.startswith("```json"): result = result.replace("```json", "").replace("```", "").strip()
        elif result.startswith("```"): result = result.replace("```", "").strip()
        
        try:
            data = json.loads(result)
            causes = data.get("causes", [])
            
            # --- YENİ EKLENEN KISIM: İngilizce alanları Türkçe ile değiştir ---
            for item in causes:
                # Eğer Türkçe veri varsa, ana 'cause' alanına onu yaz
                if item.get("cause_tr"):
                    item["cause"] = item["cause_tr"] 
                
                # Eğer Türkçe kanıt varsa, ana 'evidence' alanına onu yaz
                if item.get("evidence_tr"):
                    item["evidence"] = item["evidence_tr"]
            # ------------------------------------------------------------------
            
            print(f"{len(causes)} dogrudan neden belirlendi (Turkcelesstirildi)")
            return causes
        except json.JSONDecodeError:
            return []
    
    def _perform_5why_for_cause(self, immediate_cause: Dict, incident_summary: str) -> Dict:
        """
        STEP 2: Perform 5 Why analysis with Turkish output
        """
        cause_en = immediate_cause.get("cause", "")
        cause_tr = immediate_cause.get("cause_tr", "")
        
        prompt = f"""You are performing 5 Why Analysis following HSG245 methodology.

INCIDENT: {incident_summary}
IMMEDIATE CAUSE: {cause_en} ({cause_tr})

TASK: Perform 5 WHY analysis.
Why 1 -> Why 2 (underlying) -> Why 3 (underlying) -> Why 4 (underlying) -> Why 5 (ROOT CAUSE)

Return JSON with:
{{
  "immediate_cause": {{...}},
  "why_chain": [
    {{"level": 1, "cause_type": "immediate", "why_question": "...", "why_question_tr": "...", "because_answer": "...", "because_answer_tr": "..."}},
    {{"level": 2, "cause_type": "underlying", "why_question": "...", "why_question_tr": "...", "because_answer": "...", "because_answer_tr": "..."}},
    {{"level": 3, "cause_type": "underlying", "why_question": "...", "why_question_tr": "...", "because_answer": "...", "because_answer_tr": "..."}},
    {{"level": 4, "cause_type": "underlying", "why_question": "...", "why_question_tr": "...", "because_answer": "...", "because_answer_tr": "..."}},
    {{"level": 5, "cause_type": "root", "why_question": "...", "why_question_tr": "...", "because_answer": "...", "because_answer_tr": "..."}}
  ],
  "root_cause": {{"root": "...", "root_tr": "..."}}
}}

IMPORTANT: 
- Level 1: immediate cause (already known)
- Levels 2-4: UNDERLYING CAUSES (cause_type: "underlying")
- Level 5: ROOT CAUSE (cause_type: "root")
- All why_question_tr, because_answer_tr fields must be in TURKISH language

CRITICAL: All _tr fields must be 100% TURKISH. No English words allowed.

Return ONLY valid JSON."""

        response = self.client.chat.completions.create(
            model="google/gemma-3-27b-it:free",
            temperature=0.0,
            messages=[
                {"role": "system", "content": "You are a 5 Why analysis expert. Return only valid JSON with all _tr fields in TURKISH language."},
                {"role": "user", "content": prompt}
            ]
        )
        
        result = response.choices[0].message.content.strip()
        if result.startswith("```json"): result = result.replace("```json", "").replace("```", "").strip()
        elif result.startswith("```"): result = result.replace("```", "").strip()
        
        try:
            chain = json.loads(result)
            
            # --- YENİ EKLENEN KISIM: Zinciri Türkçeleştir ---
            # 1. Zincirdeki (Why 1, Why 2...) soruları ve cevapları değiştir
            for step in chain.get("why_chain", []):
                if step.get("why_question_tr"):
                    step["why_question"] = step["why_question_tr"]
                
                if step.get("because_answer_tr"):
                    step["because_answer"] = step["because_answer_tr"]
            
            # 2. Kök Nedeni (Root Cause) değiştir
            root = chain.get("root_cause", {})
            if isinstance(root, dict):
                if root.get("root_tr"):
                    root["root"] = root["root_tr"]
                print(f"      Kok: {root.get('root', 'N/A')}")
            else:
                # Bazen string gelebilir, onu da handle edelim
                pass 
            # ------------------------------------------------
            
            return chain
        except json.JSONDecodeError:
            return {"immediate_cause": immediate_cause, "why_chain": [], "root_cause": {}}
    
    def _generate_final_report(self, rca_data: Dict) -> str:
        """
        FINAL EDITOR: Generate professional Turkish report
        """
        print("\nFinal Rapor Hazirlanyor (Profesyonel Rapor Modu)...")
        
        raw_data_str = json.dumps(rca_data, indent=2, ensure_ascii=False)
        
        prompt = f"""You are a professional Occupational Health and Safety Report Editor.

INPUT DATA (AI-generated analysis):
{raw_data_str}

TASK:
Based on this data, write a professional, formal 'Root Cause Analysis Report'.

MANDATORY REQUIREMENTS:
1. Language: ONLY TURKISH (no English words!)
2. Tone: Formal, objective, senior safety expert style
3. Structure:
   - YONETICI OZETI (Executive Summary)
   - OLAY DETAYLARI (Incident Details)
   - DOGRUDAN NEDENLER (Immediate Causes - list all immediate causes from input)
   - KOK NEDEN ANALIZI (For each immediate cause, explain the 5 Why chain in detail)
   - TEMEL NEDENLER (Underlying Causes - all level 2-4 causes)
   - SISTEMIK BULGULAR (Root Causes - level 5 causes)
   - SONUC VE ONERILER (Conclusion and Recommendations)
4. Format: Clean, organized text (not JSON)
5. Fix any poor translations in input data, fill logic gaps

CRITICAL: Report must be 100% in TURKISH language. Absolutely NO English words allowed in the output."""

        response = self.client.chat.completions.create(
            model="google/gemma-3-27b-it:free", 
            temperature=0.3,
            messages=[
                {"role": "system", "content": "You are a senior Occupational Health and Safety Expert working in Turkey. You write ALL reports in TURKISH language. You never use English."},
                {"role": "user", "content": prompt}
            ]
        )
        
        report_content = response.choices[0].message.content
        
        print("\n" + "="*80)
        print(report_content)
        print("="*80)
        
        return report_content

    # Helper methods (extract_underlying, extract_root) stay the same...
    def _extract_underlying_from_chain(self, chain: Dict) -> List[Dict]:
        underlying = []
        for why in chain.get("why_chain", []):
            if why.get("cause_type") == "underlying":
                # Önceliği Türkçeye veriyoruz
                cause_text = why.get("because_answer_tr") or why.get("because_answer", "")
                
                underlying.append({
                    "cause": cause_text,     # Artık burası kesin Türkçe
                    "cause_tr": cause_text,  # Yedek olarak kalsın
                    "level": why.get("level", 0)
                })
        return underlying
    
    def _extract_root_from_chain(self, chain: Dict) -> Dict:
        for why in chain.get("why_chain", []):
            if why.get("level") == 5 or why.get("cause_type") == "root":
                # Önceliği Türkçeye veriyoruz
                cause_text = why.get("because_answer_tr") or why.get("because_answer", "")
                
                return {
                    "cause": cause_text,    # Artık burası kesin Türkçe
                    "cause_tr": cause_text
                }
        
        # Eğer zincirden bulunamazsa root_cause objesine bak
        root_obj = chain.get("root_cause", {})
        if isinstance(root_obj, dict):
             root_text = root_obj.get("root_tr") or root_obj.get("root", "")
             return {"cause": root_text, "cause_tr": root_text}
             
        return chain.get("root_cause", {})

    def _print_summary(self, rca_data: Dict):
        # Bu fonksiyon artık kullanılmıyor ama eski loglar için tutulabilir.
        pass
