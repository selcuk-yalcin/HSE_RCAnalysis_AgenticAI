"""
OpenAI API Helper
Centralized OpenAI API client and utility functions
"""

import os
from typing import List, Dict, Optional, Any
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()


class OpenAIClient:
    """
    Centralized OpenAI API client
    Provides easy-to-use methods for common operations
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 4000
    ):
        """
        Initialize OpenAI client
        
        Args:
            api_key: OpenAI API key (defaults to env variable)
            model: Model to use (gpt-4, gpt-4o-mini, etc.)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        print(f"✅ OpenAI Client initialized")
        print(f"🤖 Model: {self.model}")
        print(f"🌡️  Temperature: {self.temperature}")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False
    ) -> str:
        """
        Generate chat completion
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system message to prepend
            temperature: Override default temperature
            max_tokens: Override default max tokens
            json_mode: Force JSON response format
            
        Returns:
            Response content as string
        """
        # Prepend system message if provided
        if system_prompt:
            messages = [
                {"role": "system", "content": system_prompt}
            ] + messages
        
        # Build request params
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens
        }
        
        # Enable JSON mode if requested
        if json_mode:
            params["response_format"] = {"type": "json_object"}
        
        # Make API call
        response = self.client.chat.completions.create(**params)
        
        return response.choices[0].message.content
    
    def chat_completion_json(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate chat completion and parse as JSON
        
        Args:
            messages: List of message dicts
            system_prompt: Optional system message
            temperature: Override default temperature
            
        Returns:
            Parsed JSON response as dict
        """
        # Ensure system prompt requests JSON
        if system_prompt and "JSON" not in system_prompt:
            system_prompt += "\n\nReturn response as valid JSON."
        elif not system_prompt:
            system_prompt = "You are a helpful assistant. Return response as valid JSON."
        
        response_text = self.chat_completion(
            messages=messages,
            system_prompt=system_prompt,
            temperature=temperature,
            json_mode=True
        )
        
        # Parse JSON
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parsing error: {e}")
            print(f"Raw response: {response_text}")
            return {"error": "Failed to parse JSON", "raw_response": response_text}
    
    def simple_prompt(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Simple prompt-response interface
        
        Args:
            prompt: User prompt
            system_prompt: Optional system instructions
            temperature: Override default temperature
            
        Returns:
            Response content
        """
        messages = [{"role": "user", "content": prompt}]
        
        return self.chat_completion(
            messages=messages,
            system_prompt=system_prompt,
            temperature=temperature
        )
    
    def extract_structured_data(
        self,
        text: str,
        fields: List[str],
        instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract structured data from text
        
        Args:
            text: Source text to extract from
            fields: List of field names to extract
            instructions: Additional extraction instructions
            
        Returns:
            Dictionary with extracted fields
        """
        system_prompt = "You are a data extraction expert. Extract information and return as JSON."
        
        if instructions:
            system_prompt += f"\n{instructions}"
        
        fields_str = ", ".join(fields)
        prompt = f"""Extract the following fields from the text:
Fields: {fields_str}

Text:
{text}

Return as JSON with field names as keys. Use empty string "" if field not found."""
        
        messages = [{"role": "user", "content": prompt}]
        
        return self.chat_completion_json(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.1  # Low temperature for accuracy
        )
    
    def classify_text(
        self,
        text: str,
        categories: List[str],
        instructions: Optional[str] = None
    ) -> str:
        """
        Classify text into one of given categories
        
        Args:
            text: Text to classify
            categories: List of possible categories
            instructions: Additional classification instructions
            
        Returns:
            Selected category
        """
        system_prompt = "You are a classification expert. Return ONLY the category name."
        
        if instructions:
            system_prompt += f"\n{instructions}"
        
        categories_str = "\n".join([f"- {cat}" for cat in categories])
        prompt = f"""Classify the following text into ONE of these categories:

{categories_str}

Text to classify:
{text}

Return ONLY the category name, nothing else."""
        
        response = self.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=system_prompt,
            temperature=0.1
        )
        
        return response.strip()
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis result
        """
        system_prompt = "Analyze sentiment and return as JSON with fields: sentiment (positive/negative/neutral), confidence (0-1), explanation"
        
        messages = [{"role": "user", "content": f"Analyze sentiment:\n{text}"}]
        
        return self.chat_completion_json(
            messages=messages,
            system_prompt=system_prompt
        )


# Singleton instance
_client: Optional[OpenAIClient] = None


def get_openai_client(
    api_key: Optional[str] = None,
    model: str = "gpt-4o-mini",
    temperature: float = 0.7
) -> OpenAIClient:
    """
    Get or create OpenAI client singleton
    
    Args:
        api_key: OpenAI API key
        model: Model to use
        temperature: Default temperature
        
    Returns:
        OpenAIClient instance
    """
    global _client
    
    if _client is None:
        _client = OpenAIClient(
            api_key=api_key,
            model=model,
            temperature=temperature
        )
    
    return _client


# Convenience functions
def chat(prompt: str, system_prompt: Optional[str] = None) -> str:
    """Quick chat completion"""
    client = get_openai_client()
    return client.simple_prompt(prompt, system_prompt)


def chat_json(prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
    """Quick chat completion with JSON response"""
    client = get_openai_client()
    messages = [{"role": "user", "content": prompt}]
    return client.chat_completion_json(messages, system_prompt)


def classify(text: str, categories: List[str]) -> str:
    """Quick text classification"""
    client = get_openai_client()
    return client.classify_text(text, categories)


def extract(text: str, fields: List[str]) -> Dict[str, Any]:
    """Quick data extraction"""
    client = get_openai_client()
    return client.extract_structured_data(text, fields)


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = OpenAIClient()
    
    # Simple prompt
    response = client.simple_prompt("What is health and safety?")
    print("Simple prompt:", response)
    
    # Classification
    incident_text = "Worker fell from ladder and broke arm"
    category = client.classify_text(
        incident_text,
        categories=["Ill health", "Minor injury", "Serious injury", "Major injury"]
    )
    print(f"Classification: {category}")
    
    # Extraction
    data = client.extract_structured_data(
        "Incident reported by John Doe on 05/01/2025 at warehouse",
        fields=["reported_by", "date", "location"]
    )
    print(f"Extracted: {data}")
    
    # JSON response
    analysis = client.chat_completion_json(
        messages=[{"role": "user", "content": "Analyze: Worker slipped on wet floor"}],
        system_prompt="Analyze incident and return JSON with: type, severity, root_cause"
    )
    print(f"Analysis: {analysis}")
