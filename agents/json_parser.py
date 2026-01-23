"""
Robust JSON Parser for AI Responses
====================================

Extracts JSON from AI responses that may contain markdown, 
code blocks, or other formatting.
"""

import json
import re
from typing import Dict, Any, Optional


def extract_json_from_response(response_text: str, default: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Extract and parse JSON from AI response using regex.
    
    Strategy:
    1. Find first '{' and last '}' in the response
    2. Extract content between them
    3. Parse as JSON
    4. Return default dict if parsing fails
    
    Args:
        response_text: Raw text from AI response
        default: Default dict to return if parsing fails (default: {})
    
    Returns:
        Parsed JSON dict or default dict
    
    Examples:
        >>> extract_json_from_response('```json\\n{"key": "value"}\\n```')
        {'key': 'value'}
        
        >>> extract_json_from_response('Here is the data: {"a": 1, "b": 2} as requested')
        {'a': 1, 'b': 2}
        
        >>> extract_json_from_response('Invalid response', {'error': 'parse_failed'})
        {'error': 'parse_failed'}
    """
    if default is None:
        default = {}
    
    try:
        # Remove any leading/trailing whitespace
        text = response_text.strip()
        
        # Strategy 1: Find first '{' and last '}'
        # This regex finds the outermost JSON object
        match = re.search(r'\{.*\}', text, re.DOTALL)
        
        if match:
            json_str = match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON parse error on extracted string: {e}")
                print(f"📝 Extracted: {json_str[:200]}...")
        
        # Strategy 2: Try parsing the entire response (fallback)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Strategy 3: Remove common markdown artifacts and retry
        cleaned = text.replace("```json", "").replace("```", "").strip()
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        
        print(f"❌ Could not extract valid JSON from response")
        print(f"📄 Response preview: {text[:300]}...")
        return default
        
    except Exception as e:
        print(f"❌ Unexpected error in JSON extraction: {e}")
        return default


def extract_json_array_from_response(response_text: str, default: Optional[list] = None) -> list:
    """
    Extract and parse JSON array from AI response using regex.
    
    Similar to extract_json_from_response but for arrays.
    
    Args:
        response_text: Raw text from AI response
        default: Default list to return if parsing fails (default: [])
    
    Returns:
        Parsed JSON array or default list
    """
    if default is None:
        default = []
    
    try:
        text = response_text.strip()
        
        # Find first '[' and last ']'
        match = re.search(r'\[.*\]', text, re.DOTALL)
        
        if match:
            json_str = match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON array parse error: {e}")
        
        # Fallback: try entire response
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        print(f"❌ Could not extract valid JSON array from response")
        return default
        
    except Exception as e:
        print(f"❌ Unexpected error in JSON array extraction: {e}")
        return default


# Convenience function with better error messages
def safe_json_parse(response_text: str, 
                    context: str = "AI response",
                    default: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Safe JSON parsing with context-aware error messages.
    
    Args:
        response_text: Raw text to parse
        context: Context description for error messages (e.g., "Assessment Agent")
        default: Default dict to return on failure
    
    Returns:
        Parsed JSON dict or default
    """
    if default is None:
        default = {}
    
    print(f"🔍 Parsing JSON from {context}...")
    result = extract_json_from_response(response_text, default)
    
    if result == default and result == {}:
        print(f"⚠️  Warning: Using default/empty dict for {context}")
    else:
        print(f"✅ Successfully parsed JSON from {context}")
    
    return result
