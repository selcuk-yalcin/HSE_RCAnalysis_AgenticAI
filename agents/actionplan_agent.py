"""
Action Plan Agent - Part 4 of HSG245
Generates action plan based on root cause analysis results
"""

from openai import OpenAI
from typing import Dict, List
from datetime import datetime, timedelta
import json
import os
import re
from .json_parser import safe_json_parse
from .model_constants import OPENROUTER_DEFAULT_CHAT_MODEL


class ActionPlanAgent:
    """
    Part 4: The Risk Control Action Plan
    
    Generates comprehensive action plan with:
    - Immediate actions (24-48 hours)
    - Short-term actions (1-3 months)
    - Long-term actions (3-12 months)
    - Responsible persons
    - Target dates
    - Priority levels
    """
    
    def __init__(self):
        """Initialize Action Plan Agent (Basitleştirilmiş)"""
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        print(f"✅ Aksiyon Planı Ajanı başlatıldı.")
    
    def generate_action_plan(self, investigation_data: Dict) -> Dict:
        """
        Generate comprehensive action plan based on root cause analysis
        
        Args:
            investigation_data: Contains root_causes, severity, etc.
            
        Returns:
            Part 4 data with structured action plan
        """
        print("\n" + "="*80)
        print("💡 PART 4: ACTION PLAN - Generating Control Measures")
        print("="*80)
        
        # ========================================
        # GUARD CLAUSE: Validate input data
        # ========================================
        if not investigation_data or not isinstance(investigation_data, dict):
            print("\n⚠️  HATA: Araştırma verisi eksik veya geçersiz!")
            print("⚠️  Varsayılan aksiyon planı devreye giriyor...")
            return self._generate_fallback_actions()
        
        if "root_causes" not in investigation_data:
            print("\n⚠️  HATA: Kök neden verisi eksik!")
            print("⚠️  Varsayılan aksiyon planı devreye giriyor...")
            return self._generate_fallback_actions()
        
        # Extract data
        root_causes = investigation_data.get("root_causes", [])
        underlying_causes = investigation_data.get("underlying_causes", [])
        immediate_causes = investigation_data.get("immediate_causes", [])
        severity = investigation_data.get("severity", "Medium level")
        
        # Additional validation: Check if root_causes is actually populated
        if not root_causes or len(root_causes) == 0:
            print("\n⚠️  HATA: Kök neden listesi boş!")
            print("⚠️  Varsayılan aksiyon planı devreye giriyor...")
            return self._generate_fallback_actions()
        
        # Generate actions using AI
        print("\n🤖 AI generating risk control measures...")
        print(f"📊 Input: {len(root_causes)} root causes, {len(immediate_causes)} immediate causes")
        
        actions = self._generate_actions_with_ai(
            root_causes, 
            underlying_causes, 
            immediate_causes,
            severity
        )
        
        # Check if fallback was returned (already in Part 4 format)
        if isinstance(actions, dict) and "_fallback" in actions:
            print("⚠️  Using fallback action plan structure")
            return actions
        
        # Structure Part 4 data from AI-generated actions
        part4_data = {
            "control_measures": actions.get("control_measures", []),
            "immediate_actions": actions.get("immediate", []),
            "short_term_actions": actions.get("short_term", []),
            "long_term_actions": actions.get("long_term", []),
            "responsible_persons": actions.get("responsible", {}),
            "target_dates": actions.get("deadlines", {}),
            "priority_level": self._calculate_priority(severity),
            "generated_at": datetime.now().strftime("%d.%m.%y %H:%M")
        }
        
        self._print_summary(part4_data)
        
        return part4_data
    
    def _generate_actions_with_ai(self, root_causes: List, underlying_causes: List, 
                                   immediate_causes: List, severity: str) -> Dict:
        """Generate action plan using google/gemini-2.5-flash"""
        
        # Prepare causes for prompt
        root_causes_text = self._format_causes_list(root_causes)
        underlying_causes_text = self._format_causes_list(underlying_causes)
        immediate_causes_text = self._format_causes_list(immediate_causes)
        
        prompt = f"""
You are a Health & Safety expert creating a comprehensive action plan following the HSG245 framework.

INCIDENT SEVERITY: {severity}

ROOT CAUSES IDENTIFIED:
{root_causes_text}

UNDERLYING CAUSES:
{underlying_causes_text}

IMMEDIATE CAUSES:
{immediate_causes_text}

Generate a comprehensive Risk Control Action Plan with THREE time-based categories:

1. IMMEDIATE ACTIONS (24-48 hours):
   - Quick wins to prevent immediate recurrence
   - Emergency safety measures
   - Temporary controls
   - Critical communication needs

2. SHORT-TERM ACTIONS (1-3 months):
   - Process improvements
   - Equipment modifications
   - Procedure updates
   - Training programs
   - Documentation updates

3. LONG-TERM ACTIONS (3-12 months):
   - System redesign
   - Culture change initiatives
   - Major equipment upgrades
   - Strategic safety improvements
   - Policy changes

For EACH action, provide:
- Clear, specific, actionable measure
- Suggested responsible role (e.g., "Safety Manager", "Operations Director")
- Realistic target date (use format: DD/MM/YYYY)

Ensure actions follow the hierarchy of controls:
1. Elimination
2. Substitution
3. Engineering controls
4. Administrative controls
5. PPE (last resort)

Return as JSON with this exact structure:
{{
    "control_measures": [
        {{
            "measure": "Specific action description",
            "responsible": "Role/Position",
            "target_date": "DD/MM/YYYY",
            "category": "immediate|short_term|long_term",
            "control_type": "elimination|substitution|engineering|administrative|ppe"
        }}
    ],
    "immediate": ["Action 1", "Action 2", ...],
    "short_term": ["Action 1", "Action 2", ...],
    "long_term": ["Action 1", "Action 2", ...],
    "responsible": {{"action_name": "role"}},
    "deadlines": {{"action_name": "DD/MM/YYYY"}}
}}

Generate at least 2-3 actions per category. Be specific and practical.

Return ONLY valid JSON.
"""

        schema_feedback = ""
        parse_attempts = 0
        try:
            for attempt in range(1, 4):
                parse_attempts = attempt
                final_prompt = prompt
                if schema_feedback:
                    final_prompt += (
                        "\n\nPrevious output was invalid.\n"
                        f"Validation feedback: {schema_feedback}\n"
                        "Regenerate as strict JSON object only, no markdown/code fences."
                    )

                response = self.client.chat.completions.create(
                    model=OPENROUTER_DEFAULT_CHAT_MODEL,  # actual model
                    messages=[{"role": "user", "content": final_prompt}],
                    temperature=0.0,
                    max_tokens=2000,
                    extra_headers={
                        "anthropic-version": "2023-06-01"  # Prompt caching desteği
                    }
                )
                try:
                    from shared.usage_context import try_record_openai_completion

                    try_record_openai_completion(
                        response,
                        reason="actionplan",
                        model=OPENROUTER_DEFAULT_CHAT_MODEL,
                        operation_label="Aksiyon planı üretimi",
                    )
                except Exception:  # noqa: BLE001
                    pass

                result_text = (response.choices[0].message.content or "").strip()
                result, parse_info = self._parse_action_plan_response(result_text)
                if result and self._validate_action_plan_schema(result):
                    print(
                        f"✅ Action plan generated successfully "
                        f"(parse_attempts={attempt}, sanitized={parse_info.get('sanitized')})"
                    )
                    return result

                schema_feedback = parse_info.get("error") or "Schema validation failed."
                print(
                    f"⚠️  Action plan parse/schema failed "
                    f"(attempt={attempt}, sanitized={parse_info.get('sanitized')}): {schema_feedback}"
                )

            print(
                "⚠️  Using fallback action plan "
                f"(parse_attempts={parse_attempts}, fallback_reason=invalid_json_or_schema)"
            )
            return self._generate_fallback_actions()

        except Exception as e:
            print(f"⚠️  Error generating actions with AI: {e}")
            # Fallback to default actions
            return self._generate_fallback_actions()

    def _parse_action_plan_response(self, text: str):
        info = {"sanitized": False, "error": ""}
        if not text:
            info["error"] = "Empty response"
            return None, info

        # 1) First, try existing parser directly.
        parsed = safe_json_parse(text, context="Action Plan Generation", default=None)
        if isinstance(parsed, dict) and parsed:
            return parsed, info

        # 2) Try sanitized candidates.
        for candidate in self._json_candidates(text):
            info["sanitized"] = True
            parsed = safe_json_parse(candidate, context="Action Plan Generation (sanitized)", default=None)
            if isinstance(parsed, dict) and parsed:
                return parsed, info

        info["error"] = "Could not extract valid JSON object."
        return None, info

    def _json_candidates(self, text: str) -> List[str]:
        candidates: List[str] = []
        raw = (text or "").strip()
        if not raw:
            return candidates

        # Remove markdown fences if present.
        if raw.startswith("```"):
            raw = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            raw = raw.strip()

        candidates.append(raw)

        # Extract first JSON object range.
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidates.append(raw[start:end + 1].strip())

        # Remove trailing commas before object/array close.
        for c in list(candidates):
            candidates.append(re.sub(r",\s*([}\]])", r"\1", c))

        # Unique order-preserving
        uniq: List[str] = []
        for c in candidates:
            if c and c not in uniq:
                uniq.append(c)
        return uniq

    def _validate_action_plan_schema(self, payload: Dict) -> bool:
        required_keys = ["control_measures", "immediate", "short_term", "long_term", "responsible", "deadlines"]
        for key in required_keys:
            if key not in payload:
                return False

        if not isinstance(payload.get("control_measures"), list):
            return False
        if not all(isinstance(payload.get(k), list) for k in ("immediate", "short_term", "long_term")):
            return False
        if not isinstance(payload.get("responsible"), dict) or not isinstance(payload.get("deadlines"), dict):
            return False

        allowed_category = {"immediate", "short_term", "long_term"}
        allowed_control_type = {"elimination", "substitution", "engineering", "administrative", "ppe"}
        for item in payload.get("control_measures", []):
            if not isinstance(item, dict):
                return False
            for field in ("measure", "responsible", "target_date", "category", "control_type"):
                if not item.get(field):
                    return False
            if item.get("category") not in allowed_category:
                return False
            if item.get("control_type") not in allowed_control_type:
                return False
        return True
    
    def _format_causes_list(self, causes: List) -> str:
        """Format causes list for prompt"""
        if not causes:
            return "None identified"
        
        formatted = []
        for i, cause in enumerate(causes, 1):
            if isinstance(cause, dict):
                cause_text = cause.get('cause', str(cause))
                description = cause.get('description', '')
                formatted.append(f"{i}. {cause_text}")
                if description:
                    formatted.append(f"   → {description}")
            else:
                formatted.append(f"{i}. {cause}")
        
        return "\n".join(formatted)
    
    def _generate_fallback_actions(self) -> Dict:
        """
        Generate basic fallback actions if AI fails or data is missing
        Returns Part 4 compatible structure
        """
        print("\n🛡️  Generating fallback action plan...")
        
        today = datetime.now()
        
        # Raw actions structure (for backward compatibility)
        raw_actions = {
            "control_measures": [
                {
                    "measure": "Review incident with management team and identify immediate hazards",
                    "responsible": "H&S Manager",
                    "target_date": (today + timedelta(days=1)).strftime("%d/%m/%Y"),
                    "category": "immediate",
                    "control_type": "administrative"
                },
                {
                    "measure": "Implement temporary safety measures at incident location",
                    "responsible": "Site Supervisor",
                    "target_date": (today + timedelta(days=2)).strftime("%d/%m/%Y"),
                    "category": "immediate",
                    "control_type": "engineering"
                },
                {
                    "measure": "Update risk assessments based on findings",
                    "responsible": "H&S Officer",
                    "target_date": (today + timedelta(days=30)).strftime("%d/%m/%Y"),
                    "category": "short_term",
                    "control_type": "administrative"
                },
                {
                    "measure": "Conduct refresher training for all affected staff",
                    "responsible": "Training Manager",
                    "target_date": (today + timedelta(days=60)).strftime("%d/%m/%Y"),
                    "category": "short_term",
                    "control_type": "administrative"
                },
                {
                    "measure": "Review and update safety management system",
                    "responsible": "Operations Director",
                    "target_date": (today + timedelta(days=180)).strftime("%d/%m/%Y"),
                    "category": "long_term",
                    "control_type": "administrative"
                }
            ],
            "immediate": [
                "Review incident with management team",
                "Implement temporary safety measures"
            ],
            "short_term": [
                "Update risk assessments",
                "Conduct refresher training"
            ],
            "long_term": [
                "Review safety management system"
            ],
            "responsible": {
                "Review incident": "H&S Manager",
                "Implement measures": "Site Supervisor",
                "Update assessments": "H&S Officer",
                "Conduct training": "Training Manager",
                "Review system": "Operations Director"
            },
            "deadlines": {
                "Review incident": (today + timedelta(days=1)).strftime("%d/%m/%Y"),
                "Implement measures": (today + timedelta(days=2)).strftime("%d/%m/%Y"),
                "Update assessments": (today + timedelta(days=30)).strftime("%d/%m/%Y"),
                "Conduct training": (today + timedelta(days=60)).strftime("%d/%m/%Y"),
                "Review system": (today + timedelta(days=180)).strftime("%d/%m/%Y")
            }
        }
        
        # Return Part 4 compatible structure
        part4_fallback = {
            "control_measures": raw_actions["control_measures"],
            "immediate_actions": raw_actions["immediate"],
            "short_term_actions": raw_actions["short_term"],
            "long_term_actions": raw_actions["long_term"],
            "responsible_persons": raw_actions["responsible"],
            "target_dates": raw_actions["deadlines"],
            "priority_level": "Medium",  # Default priority
            "generated_at": datetime.now().strftime("%d.%m.%y %H:%M"),
            "_fallback": True  # Flag to indicate this is fallback data
        }
        
        print("✅ Fallback plan generated successfully")
        return part4_fallback
    
    def _calculate_priority(self, severity: str) -> str:
        """Calculate priority based on severity"""
        severity_lower = severity.lower()
        
        if any(word in severity_lower for word in ['high', 'major', 'fatal', 'serious']):
            return "High"
        elif any(word in severity_lower for word in ['medium', 'moderate']):
            return "Medium"
        else:
            return "Low"
    
    def _print_summary(self, data: Dict):
        """Print action plan summary"""
        print("\n" + "-"*80)
        print("📊 ACTION PLAN SUMMARY")
        print("-"*80)
        
        print(f"\n🎯 Priority Level: {data['priority_level']}")
        print(f"📅 Generated: {data['generated_at']}")
        
        # Print control measures table
        print("\n📋 CONTROL MEASURES:")
        print("\n⚡ IMMEDIATE ACTIONS (24-48 hours):")
        immediate_count = sum(1 for m in data['control_measures'] if m['category'] == 'immediate')
        print(f"   Total: {immediate_count} actions")
        for measure in data['control_measures']:
            if measure['category'] == 'immediate':
                print(f"   • {measure['measure']}")
                print(f"     └─ Responsible: {measure['responsible']} | Due: {measure['target_date']}")
        
        print("\n📅 SHORT-TERM ACTIONS (1-3 months):")
        short_count = sum(1 for m in data['control_measures'] if m['category'] == 'short_term')
        print(f"   Total: {short_count} actions")
        for measure in data['control_measures']:
            if measure['category'] == 'short_term':
                print(f"   • {measure['measure']}")
                print(f"     └─ Responsible: {measure['responsible']} | Due: {measure['target_date']}")
        
        print("\n🎯 LONG-TERM ACTIONS (3-12 months):")
        long_count = sum(1 for m in data['control_measures'] if m['category'] == 'long_term')
        print(f"   Total: {long_count} actions")
        for measure in data['control_measures']:
            if measure['category'] == 'long_term':
                print(f"   • {measure['measure']}")
                print(f"     └─ Responsible: {measure['responsible']} | Due: {measure['target_date']}")
        
        print("\n" + "="*80)
