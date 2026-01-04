"""
Root Cause Investigation System - Configuration
HSG245 Based Multi-Agent System
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration management for Root Cause Investigation System"""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent
    AGENTS_DIR = PROJECT_ROOT / "agents"
    TEMPLATES_DIR = PROJECT_ROOT / "templates"
    DATA_DIR = PROJECT_ROOT / "data"
    OUTPUTS_DIR = PROJECT_ROOT / "outputs"
    REPORTS_DIR = OUTPUTS_DIR / "reports"
    EXAMPLES_DIR = PROJECT_ROOT / "examples"
    
    # HSG245 Configuration
    HSG245_PARTS = ["Part 1: Overview", "Part 2: Initial Assessment", 
                    "Part 3: Investigation", "Part 4: Action Plan"]
    
    INCIDENT_TYPES = ["Ill health", "Minor injury", "Serious injury", "Major injury"]
    
    EVENT_TYPES = ["Accident", "Ill health", "Near-miss", "Undesired circumstance"]
    
    SEVERITY_LEVELS = ["Fatal or major", "Serious", "Minor", "Damage only"]
    
    INVESTIGATION_LEVELS = ["High level", "Medium level", "Low level", "Basic"]
    
    # Agent Configuration
    AGENT_TIMEOUT = int(os.getenv("AGENT_TIMEOUT", "30"))  # seconds
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    
    @classmethod
    def validate(cls):
        """Validate configuration and create necessary directories"""
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "❌ OPENAI_API_KEY not found!\n"
                "Please create a .env file with:\n"
                "OPENAI_API_KEY=your-api-key-here"
            )
        
        # Create directories if they don't exist
        for directory in [cls.TEMPLATES_DIR, cls.DATA_DIR, 
                         cls.OUTPUTS_DIR, cls.REPORTS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Configuration validated")
        print(f"📁 Project root: {cls.PROJECT_ROOT}")
        print(f"🤖 OpenAI model: {cls.OPENAI_MODEL}")
        print(f"🌡️  Temperature: {cls.OPENAI_TEMPERATURE}")
        
        return True
    
    @classmethod
    def get_openai_config(cls):
        """Get OpenAI client configuration"""
        return {
            "api_key": cls.OPENAI_API_KEY,
            "model": cls.OPENAI_MODEL,
            "temperature": cls.OPENAI_TEMPERATURE
        }

# Global config instance
config = Config()
