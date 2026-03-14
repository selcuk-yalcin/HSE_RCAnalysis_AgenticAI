"""
Pydantic Models for the HSE Taxonomy Knowledge Base.

This module defines the structured representation of the root cause analysis taxonomy.
These models are used to parse the raw text data from knowledge_base.py into a
structured, validated, and queryable format.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class LocalizedContent(BaseModel):
    """
    Represents content in a specific language.
    """
    title: str = Field(..., description="The title in this language.")
    definition: str = Field(..., description="The definition in this language.")
    selection_criteria: Optional[str] = Field(None, description="Selection criteria in this language.")
    typical_examples: List[str] = Field(default_factory=list, description="Examples in this language.")

class ExclusionCondition(BaseModel):
    """
    Represents a single exclusion condition ('✗ Not this if').
    
    This model captures the logic for when a specific cause should NOT be chosen,
    and which other cause should be considered instead.
    """
    condition: str = Field(..., description="The condition under which the parent cause should be excluded.")
    redirect_code: str = Field(..., description="The code of the cause to consider instead.")
    reason: Optional[str] = Field(None, description="An optional explanation for the redirection.")
    language: str = Field(default="tr", description="Language code (tr, en, etc.)")

class Cause(BaseModel):
    """
    Represents a single cause (Immediate or Root) in the taxonomy.
    
    This is the core data model for each entry in the knowledge base.
    Supports multiple languages through the 'content' field.
    """
    code: str = Field(..., description="The unique code for the cause, e.g., 'A1.1' or 'D9.5'.")
    
    cause_type: str = Field(
        ..., 
        description="The type of the cause, derived from its code prefix. E.g., 'immediate_action', 'root_organizational'."
    )
    
    # Multi-language content
    content: Dict[str, LocalizedContent] = Field(
        default_factory=dict,
        description="Content in different languages. Keys are language codes (tr, en, etc.)"
    )
    
    exclusion_conditions: List[ExclusionCondition] = Field(
        default_factory=list,
        description="A list of conditions under which this cause should be excluded."
    )
    
    related_codes: List[str] = Field(
        default_factory=list,
        description="A list of related cause codes."
    )
    
    keywords: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Keywords by language for better retrieval."
    )
    
    severity_indicators: List[str] = Field(
        default_factory=list,
        description="Indicators of severity or impact level."
    )
    
    industry_contexts: List[str] = Field(
        default_factory=list,
        description="Specific industries or contexts where this cause is common."
    )

    def to_embedding_text(self) -> str:
        """
        Generates a single, coherent string of text for vector embedding.
        
        This text combines the most important fields into a narrative format,
        which is ideal for creating high-quality semantic vectors for RAG.
        """
        text_parts = [
            f"Code: {self.code}",
            f"Type: {self.cause_type.replace('_', ' ')}",
        ]
        
        # Add content in Turkish if available
        if 'tr' in self.content:
            tr_content = self.content['tr']
            text_parts.append(f"Title: {tr_content.title}")
            text_parts.append(f"Definition: {tr_content.definition}")
            if tr_content.selection_criteria:
                text_parts.append(f"When to select: {tr_content.selection_criteria}")
            if tr_content.typical_examples:
                text_parts.append(f"Typical examples include: {'; '.join(tr_content.typical_examples)}.")
        else:
            # Fallback to any available language (e.g., English)
            fallback_lang = next(iter(self.content))
            fallback_content = self.content[fallback_lang]
            text_parts.append(f"Title: {fallback_content.title}")
            text_parts.append(f"Definition: {fallback_content.definition}")
            if fallback_content.selection_criteria:
                text_parts.append(f"When to select: {fallback_content.selection_criteria}")
            if fallback_content.typical_examples:
                text_parts.append(f"Typical examples include: {'; '.join(fallback_content.typical_examples)}.")
        
        if self.exclusion_conditions:
            exclusions = [f"do not select if {ex.condition} (consider {ex.redirect_code} instead)" for ex in self.exclusion_conditions]
            text_parts.append("Exclusion criteria: " + ", ".join(exclusions) + ".")
            
        return ". ".join(text_parts)

class Taxonomy(BaseModel):
    """
    Represents the entire collection of causes, forming the complete knowledge base.
    
    This is the root model that will be used to store the entire parsed taxonomy
    in a single, structured JSON file.
    """
    causes: List[Cause] = Field(..., description="A list of all causes in the taxonomy.")

