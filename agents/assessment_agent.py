"""
Assessment Agent - Part 2 of HSG245
Initial assessment and investigation level determination
"""

from openai import OpenAI
from datetime import datetime
from typing import Dict, Optional
import json


class AssessmentAgent:
    """
    Part 2: Initial Assessment
    Determines severity, investigation level, and regulatory requirements
    
    Fields:
    - Type of event (Accident, Ill health, Near-miss, Undesired circumstance)
    - Actual/potential for harm (Fatal/major, Serious, Minor, Damage only)
    - RIDDOR reportable? Y/N
    - Entry in accident book Y/N
    - Investigation level (High, Medium, Low, Basic)
    - Further investigation required? Y/N
    - Priority (High, Medium, Low)
    """
    
    def __init__(self, openai_config: Dict):
        """Initialize Assessment Agent with OpenAI configuration"""
        self.client = OpenAI(api_key=openai_config["api_key"])
        self.model = openai_config["model"]
        self.temperature = openai_config["temperature"]
        
        print(f"✅ Assessment Agent initialized (Model: {self.model})")
    
    def assess_incident(self, part1_data: Dict, incident_details: Dict = None) -> Dict:
        """
        Perform initial assessment and determine investigation level
        
        Args:
            part1_data: Data from Part 1 (Overview)
            incident_details: Additional incident details if available
            
        Returns:
            Structured Part 2 data
        """
        print("\n" + "="*80)
        print("📋 PART 2: INITIAL ASSESSMENT - Evaluating Incident")
        print("="*80)
        
        # Prepare combined description
        description = self._prepare_description(part1_data, incident_details)
        
        # Initialize Part 2 structure
        part2_data = {
            "type_of_event": "",
            "actual_potential_harm": "",
            "riddor_reportable": "N",
            "riddor_date_reported": "",
            "accident_book_entry": "Y",
            "accident_book_date": datetime.now().strftime("%d.%m.%y"),
            "accident_book_ref": "",
            "investigation_level": "",
            "initial_assessment_by": incident_details.get("assessed_by", "H&S Officer") if incident_details else "H&S Officer",
            "assessment_date": datetime.now().strftime("%d.%m.%y"),
            "further_investigation_required": "Y",
            "priority": "",
            "investigation_team": []
        }
        
        # Classify event type
        part2_data["type_of_event"] = self._classify_event_type(description, part1_data)
        
        # Assess severity (actual/potential harm)
        part2_data["actual_potential_harm"] = self._assess_severity(description, part1_data)
        
        # Determine RIDDOR reportability
        riddor_assessment = self._assess_riddor(description, part1_data, part2_data)
        part2_data["riddor_reportable"] = riddor_assessment["reportable"]
        part2_data["riddor_date_reported"] = riddor_assessment["date_reported"]
        
        # Determine investigation level
        investigation_assessment = self._determine_investigation_level(
            part1_data, part2_data, description
        )
        part2_data["investigation_level"] = investigation_assessment["level"]
        part2_data["priority"] = investigation_assessment["priority"]
        part2_data["investigation_team"] = investigation_assessment["team"]
        
        # Generate accident book reference
        if part2_data["accident_book_entry"] == "Y":
            part2_data["accident_book_ref"] = self._generate_accident_book_ref()
        
        self._print_summary(part2_data)
        
        return part2_data
    
    def _prepare_description(self, part1_data: Dict, incident_details: Dict = None) -> str:
        """Combine all available information into a description"""
        parts = []
        
        # From Part 1
        brief = part1_data.get("brief_details", {})
        if brief.get("what"):
            parts.append(f"What: {brief['what']}")
        if brief.get("where"):
            parts.append(f"Where: {brief['where']}")
        if brief.get("who"):
            parts.append(f"Who: {brief['who']}")
        
        # Incident type from Part 1
        if part1_data.get("incident_type"):
            parts.append(f"Type: {part1_data['incident_type']}")
        
        # Additional details
        if incident_details:
            if incident_details.get("description"):
                parts.append(incident_details["description"])
        
        return ". ".join(parts)
    
    def _classify_event_type(self, description: str, part1_data: Dict) -> str:
        """
        Classify event type using AI
        Options: Accident, Ill health, Near-miss, Undesired circumstance
        """
        print("\n🤖 AI classifying event type...")
        
        prompt = f"""You are a health and safety event classifier.

INCIDENT INFORMATION:
{description}

Classify this into ONE of these event types:
1. "Accident" - An unplanned event that resulted in injury or damage
2. "Ill health" - Work-related illness or health condition
3. "Near-miss" - An event that could have resulted in injury but didn't
4. "Undesired circumstance" - Unsafe condition or situation

Return ONLY the event type name, nothing else."""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.1,
            messages=[
                {"role": "system", "content": "You are a safety event classifier. Return only the event type."},
                {"role": "user", "content": prompt}
            ]
        )
        
        event_type = response.choices[0].message.content.strip()
        print(f"✅ Event classified as: {event_type}")
        
        return event_type
    
    def _assess_severity(self, description: str, part1_data: Dict) -> str:
        """
        Assess severity level using AI
        Options: Fatal or major, Serious, Minor, Damage only
        """
        print("\n🤖 AI assessing severity level...")
        
        incident_type = part1_data.get("incident_type", "")
        
        prompt = f"""You are a health and safety severity assessor.

INCIDENT INFORMATION:
{description}

Incident Type: {incident_type}

Classify the severity into ONE of these levels:
1. "Fatal or major" - Death, major fracture, amputation, serious burns, unconsciousness
2. "Serious" - Requires medical treatment, hospitalization, significant injury
3. "Minor" - First aid treatment only, minor cuts/bruises
4. "Damage only" - No injury, only property/equipment damage

Return ONLY the severity level, nothing else."""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.1,
            messages=[
                {"role": "system", "content": "You are a severity assessor. Return only the severity level."},
                {"role": "user", "content": prompt}
            ]
        )
        
        severity = response.choices[0].message.content.strip()
        print(f"✅ Severity assessed as: {severity}")
        
        return severity
    
    def _assess_riddor(self, description: str, part1_data: Dict, part2_data: Dict) -> Dict:
        """
        Determine if incident is RIDDOR reportable using AI
        RIDDOR = Reporting of Injuries, Diseases and Dangerous Occurrences Regulations
        """
        print("\n🤖 AI assessing RIDDOR reportability...")
        
        prompt = f"""You are a UK health and safety RIDDOR expert.

INCIDENT INFORMATION:
{description}

Event Type: {part2_data.get('type_of_event', '')}
Severity: {part2_data.get('actual_potential_harm', '')}

RIDDOR (Reporting of Injuries, Diseases and Dangerous Occurrences Regulations 2013) requires reporting of:
- Deaths
- Specified injuries (fractures, amputations, crush injuries, serious burns, unconsciousness, etc.)
- Injuries causing over 7 days absence from work
- Occupational diseases
- Dangerous occurrences

Determine if this incident is RIDDOR reportable.

Return a JSON with:
- reportable: "Y" or "N"
- reason: Brief explanation why reportable or not

Return ONLY valid JSON."""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.1,
            messages=[
                {"role": "system", "content": "You are a RIDDOR expert. Return only valid JSON."},
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
            riddor = json.loads(result)
            print(f"✅ RIDDOR assessment: {riddor['reportable']} - {riddor.get('reason', '')}")
            
            return {
                "reportable": riddor.get("reportable", "N"),
                "date_reported": datetime.now().strftime("%d.%m.%y") if riddor.get("reportable") == "Y" else "",
                "reason": riddor.get("reason", "")
            }
        except json.JSONDecodeError:
            print(f"⚠️  JSON parsing error, defaulting to N")
            return {"reportable": "N", "date_reported": "", "reason": ""}
    
    def _determine_investigation_level(self, part1_data: Dict, part2_data: Dict, description: str) -> Dict:
        """
        Determine investigation level, priority, and team composition using AI
        Levels: High level, Medium level, Low level, Basic
        """
        print("\n🤖 AI determining investigation level...")
        
        prompt = f"""You are a health and safety investigation coordinator.

INCIDENT INFORMATION:
{description}

Event Type: {part2_data.get('type_of_event', '')}
Severity: {part2_data.get('actual_potential_harm', '')}
RIDDOR: {part2_data.get('riddor_reportable', '')}

Determine the investigation level based on:
- High level: Fatality, major injury, high potential severity, multiple victims
- Medium level: Serious injury, RIDDOR reportable, significant risk
- Low level: Minor injury, limited impact
- Basic: Near-miss, minor incident

Also determine:
- Priority: High, Medium, or Low
- Investigation team: List of roles needed (e.g., ["H&S Officer", "Line Manager", "Technical Expert"])

Return a JSON with:
- level: Investigation level (High level, Medium level, Low level, or Basic)
- priority: Priority (High, Medium, Low)
- team: Array of team member roles
- rationale: Brief explanation

Return ONLY valid JSON."""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": "You are an investigation coordinator. Return only valid JSON."},
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
            assessment = json.loads(result)
            print(f"✅ Investigation level: {assessment['level']}")
            print(f"   Priority: {assessment['priority']}")
            print(f"   Team: {', '.join(assessment.get('team', []))}")
            
            return assessment
        except json.JSONDecodeError:
            print(f"⚠️  JSON parsing error, using defaults")
            return {
                "level": "Medium level",
                "priority": "Medium",
                "team": ["H&S Officer", "Line Manager"]
            }
    
    def _generate_accident_book_ref(self) -> str:
        """Generate accident book reference number"""
        return f"{datetime.now().strftime('%j')}/{datetime.now().strftime('%y')}"
    
    def _print_summary(self, part2_data: Dict):
        """Print formatted summary of Part 2 data"""
        print("\n" + "-"*80)
        print("📊 PART 2 INITIAL ASSESSMENT SUMMARY")
        print("-"*80)
        print(f"Event Type:           {part2_data['type_of_event']}")
        print(f"Severity:             {part2_data['actual_potential_harm']}")
        print(f"RIDDOR Reportable:    {part2_data['riddor_reportable']}")
        if part2_data['riddor_reportable'] == 'Y':
            print(f"RIDDOR Reported:      {part2_data['riddor_date_reported']}")
        print(f"Accident Book:        {part2_data['accident_book_entry']}")
        if part2_data['accident_book_entry'] == 'Y':
            print(f"Book Reference:       {part2_data['accident_book_ref']}")
        print(f"\n🔍 Investigation:")
        print(f"Level:                {part2_data['investigation_level']}")
        print(f"Priority:             {part2_data['priority']}")
        print(f"Further Invest Req:   {part2_data['further_investigation_required']}")
        if part2_data.get('investigation_team'):
            print(f"Team Members:         {', '.join(part2_data['investigation_team'])}")
        print(f"\nAssessed by:          {part2_data['initial_assessment_by']}")
        print(f"Assessment Date:      {part2_data['assessment_date']}")
        print("-"*80)
