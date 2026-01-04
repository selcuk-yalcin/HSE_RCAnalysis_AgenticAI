"""
Overview Agent - Part 1 of HSG245
Collects initial incident information
"""

from openai import OpenAI
from datetime import datetime
from typing import Dict, Optional
import json


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
    
    def __init__(self, openai_config: Dict):
        """Initialize Overview Agent with OpenAI configuration"""
        self.client = OpenAI(api_key=openai_config["api_key"])
        self.model = openai_config["model"]
        self.temperature = openai_config["temperature"]
        
        print(f"✅ Overview Agent initialized (Model: {self.model})")
    
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
        
        prompt = f"""You are a health and safety incident investigator. 
Extract the following information from the incident description:

INCIDENT DESCRIPTION:
{description}

Extract and structure as JSON with these fields:
- what: What happened (brief summary)
- where: Where did it happen (location)
- when: When did it happen (date/time if mentioned)
- who: Who was involved (person/people)
- emergency_measures: What emergency measures were taken

If any information is not available, use empty string "".

Return ONLY valid JSON, no explanations."""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": "You are a health and safety incident documentation expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        
        result = response.choices[0].message.content.strip()
        
        # Clean JSON if wrapped in markdown code blocks
        if result.startswith("```json"):
            result = result.replace("```json", "").replace("```", "").strip()
        elif result.startswith("```"):
            result = result.replace("```", "").strip()
        
        try:
            details = json.loads(result)
            print("✅ Brief details extracted successfully")
            return details
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parsing error: {e}")
            print(f"Raw response: {result}")
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
        
        prompt = f"""You are a health and safety incident classifier.

INCIDENT DESCRIPTION:
{description}

Classify this incident into ONE of these categories:
1. "Ill health" - Work-related illness, disease, or health condition
2. "Minor injury" - First aid treatment, minor cuts, bruises
3. "Serious injury" - Requires medical attention, lacerations, fractures
4. "Major injury" - Severe injury, amputation, major fractures, potential fatality

Return ONLY the category name, nothing else."""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.1,  # Low temperature for consistent classification
            messages=[
                {"role": "system", "content": "You are a safety incident classifier. Return only the category name."},
                {"role": "user", "content": prompt}
            ]
        )
        
        incident_type = response.choices[0].message.content.strip()
        print(f"✅ Incident classified as: {incident_type}")
        
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
