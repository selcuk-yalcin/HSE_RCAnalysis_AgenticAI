"""
Overview Agent - Part 1 of HSG245
Collects initial incident information
"""

from openai import OpenAI
from datetime import datetime
from typing import Dict, Optional
import json
import os
from .json_parser import extract_json_from_response, safe_json_parse


class OverviewAgent:
    """
    Part 1: Overview
    Collects initial incident report information
    
    Fields:
    - Ref no
    - Reported by
    - Date/time of adverse event
    - Incident type (Ill health, Minor injury, Serious injury, Major injury)
    - Brief details (What, where, when, who, emergency measures)
    - Forwarded to / Date/Time
    """
    
    def __init__(self):
        """Initialize Overview Agent with OpenRouter"""
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        print("✅ Overview Agent initialized with OpenRouter")
    
    def process_initial_report(self, incident_data: Dict) -> Dict:
        """
        Process initial incident report and structure Part 1 data
        
        Args:
            incident_data: Raw incident information
            
        Returns:
            Structured Part 1 data
        """
        print("\n" + "="*80)
        print("📋 PART 1: OVERVIEW - Processing Initial Report")
        print("="*80)
        
        # Extract basic information
        part1_data = {
            "ref_no": incident_data.get("ref_no", self._generate_ref_no()),
            "reported_by": incident_data.get("reported_by", ""),
            "date_time": incident_data.get("date_time", datetime.now().strftime("%d.%m.%y %I:%M%p")),
            "incident_type": "",
            "brief_details": {
                "what": "",
                "where": "",
                "when": "",
                "who": "",
                "emergency_measures": ""
            },
            "forwarded_to": incident_data.get("forwarded_to", ""),
            "forwarded_date_time": incident_data.get("forwarded_date_time", "")
        }
        
        # Use AI to structure the brief details if raw description provided
        if "description" in incident_data:
            structured_details = self._extract_brief_details(incident_data["description"])
            part1_data["brief_details"] = structured_details
        
        # Determine incident type using AI
        if "description" in incident_data or "injury_description" in incident_data:
            description = incident_data.get("description", "") + " " + incident_data.get("injury_description", "")
            part1_data["incident_type"] = self._classify_incident_type(description)
        
        self._print_summary(part1_data)
        
        return part1_data
    
    def _generate_ref_no(self) -> str:
        """Generate unique reference number"""
        return f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    def _extract_brief_details(self, description: str) -> Dict:
        """
        Use AI to extract What, Where, When, Who, Emergency measures from description
        """
        print("\n🤖 AI extracting brief details...")
        
        prompt = f"""Extract incident information as JSON.

INCIDENT: {description}

JSON format:
{{
  "what": "brief summary",
  "where": "location",
  "when": "date/time",
  "who": "people involved",
  "emergency_measures": "actions taken"
}}

Return ONLY the JSON object. No explanations, no markdown, just pure JSON."""

        try:
            response = self.client.chat.completions.create(
                model="anthropic/claude-sonnet-4.5", # Yasal Durumu (RIDDOR) Değerlendir
                #model="openai/gpt-4o-mini",  #test model  # Veriyi Hızlıca Topla
                temperature=0.0,
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                extra_headers={
                    "anthropic-version": "2023-06-01"  # Prompt caching desteği
                }
            )
            
            result = response.choices[0].message.content.strip()
            
            # Use robust JSON parser
            details = safe_json_parse(
                result,
                context="Brief Details Extraction",
                default={
                    "what": description[:200],
                    "where": "",
                    "when": "",
                    "who": "",
                    "emergency_measures": ""
                }
            )
            
            print("✅ Brief details extracted successfully")
            return details
        except Exception as e:
            print(f"⚠️  Extraction error: {e}")
            print(f"Raw response: {result if 'result' in locals() else 'No response'}")
            return {
                "what": description[:200],
                "where": "",
                "when": "",
                "who": "",
                "emergency_measures": ""
            }
    
    def _classify_incident_type(self, description: str) -> str:
        """
        Classify incident type using AI
        Options: Ill health, Minor injury, Serious injury, Major injury
        """
        print("\n🤖 AI classifying incident type...")
        
        prompt = f"""Classify this incident into ONE category:
1. "Ill health" - disease or health condition
2. "Minor injury" - first aid only
3. "Serious injury" - medical attention needed
4. "Major injury" - severe injury

INCIDENT: {description}

Return ONLY the category name (e.g., "Minor injury"), nothing else."""

        try:
            response = self.client.chat.completions.create(
                model="anthropic/claude-sonnet-4.5", # Yasal Durumu (RIDDOR) Değerlendir
                #model="openai/gpt-4o-mini",  #test model,   # Veriyi Hızlıca Topla
                temperature=0.0,
                max_tokens=50,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                extra_headers={
                    "anthropic-version": "2023-06-01"  # Prompt caching desteği
                }
            )
            
            incident_type = response.choices[0].message.content.strip()
            # Clean any quotes or extra text
            incident_type = incident_type.replace('"', '').replace("'", "").strip()
            print(f"✅ Incident classified as: {incident_type}")
            
            return incident_type
        except Exception as e:
            print(f"⚠️  Classification error: {e}")
            return "Minor injury"
        
        return incident_type
    
    def _print_summary(self, part1_data: Dict):
        """Print formatted summary of Part 1 data"""
        print("\n" + "-"*80)
        print("📊 PART 1 OVERVIEW SUMMARY")
        print("-"*80)
        print(f"Ref No:          {part1_data['ref_no']}")
        print(f"Reported by:     {part1_data['reported_by']}")
        print(f"Date/Time:       {part1_data['date_time']}")
        print(f"Incident Type:   {part1_data['incident_type']}")
        print(f"\n📝 Brief Details:")
        print(f"  What:          {part1_data['brief_details']['what']}")
        print(f"  Where:         {part1_data['brief_details']['where']}")
        print(f"  When:          {part1_data['brief_details']['when']}")
        print(f"  Who:           {part1_data['brief_details']['who']}")
        print(f"  Emergency:     {part1_data['brief_details']['emergency_measures']}")
        print(f"\nForwarded to:    {part1_data['forwarded_to']}")
        print(f"Forwarded at:    {part1_data['forwarded_date_time']}")
        print("-"*80)
