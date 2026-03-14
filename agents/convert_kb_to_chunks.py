#!/usr/bin/env python3
"""
Convert knowledge_basev2_ing.txt to MongoDB-ready JSON chunks
Each code becomes a separate chunk for vector embedding and search
"""

import json
import re
from datetime import datetime

def parse_knowledge_base(filepath):
    """Parse knowledge_basev2_ing.txt and extract structured chunks"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    chunks = []
    
    # Split by code patterns (e.g., A1.1, B2.3, C1.2, D9.5)
    code_pattern = r'([ABCD]\d+\.\d+)\s+([^\n]+)'
    
    # Find all code sections
    matches = list(re.finditer(code_pattern, content))
    
    for i, match in enumerate(matches):
        code = match.group(1)
        title = match.group(2).strip()
        
        # Remove warning emoji if present
        title = re.sub(r'⚠️.*$', '', title).strip()
        
        # Get content between this code and next code
        start_pos = match.end()
        end_pos = matches[i+1].start() if i+1 < len(matches) else len(content)
        code_content = content[start_pos:end_pos].strip()
        
        # Parse structured fields
        chunk = {
            "chunk_id": code,
            "category": code[0],
            "subcategory": code[:2],
            "code": code,
            "title": title,
            "description": "",
            "selection_criteria": [],
            "typical_examples": [],
            "not_this_if": [],
            "root_cause_likely": [],
            "embeddings_keywords": []
        }
        
        # Extract description (first line after code)
        lines = code_content.split('\n')
        if lines:
            chunk["description"] = lines[0].strip()
        
        # Extract "→ Choose if:" lines
        choose_if = re.findall(r'→ Choose if:\s*(.+)', code_content)
        if choose_if:
            chunk["selection_criteria"] = choose_if
        
        # Extract "→ Typical:" examples
        typical = re.findall(r'→ Typical:\s*(.+)', code_content)
        if typical:
            chunk["typical_examples"] = typical
        
        # Extract "✗ Not this if:" redirections
        not_this_pattern = r'✗ Not this if:\s*(.+?)→\s*([A-D]\d+\.\d+)'
        not_this_matches = re.findall(not_this_pattern, code_content)
        for condition, redirect_code in not_this_matches:
            chunk["not_this_if"].append({
                "condition": condition.strip(),
                "redirect_to": redirect_code.strip()
            })
        
        # Extract "→ Root cause likely:" codes
        root_cause = re.findall(r'→ Root cause likely:\s*(.+)', code_content)
        if root_cause:
            # Extract code references like D6.3, D9.1
            codes = re.findall(r'([A-D]\d+\.\d+)', root_cause[0])
            chunk["root_cause_likely"] = codes
        
        # Special handling for critical codes
        if code == "D1.5":
            chunk["critical_warning"] = "USE VERY CAREFULLY - ALL 5 CRITERIA MUST BE TRUE"
            chunk["mandatory_criteria"] = [
                "Same violation repeated MANY times (not once/twice)",
                "MULTIPLE people doing it (not individual)",
                "Extended time period (weeks/months, not days)",
                "No incident happened YET",
                "Gradual cultural acceptance (not sudden decision)"
            ]
            chunk["strong_redirects"] = [
                "If delayed maintenance: USE D6.6, NOT D1.5",
                "If LOTO skipped: USE D9.5 or D1.9, NOT D1.5",
                "If manager knew: USE D1.9, NOT D1.5"
            ]
        
        elif code == "D6.6":
            chunk["critical_warning"] = "SPECIFIC to maintenance delays - NOT general normalization"
            chunk["difference_from_d15"] = [
                "D6.6 = SPECIFIC to maintenance delays/backlogs",
                "D1.5 = GENERAL cultural normalization (rare, multi-criteria)"
            ]
            chunk["use_for"] = ["Delayed maintenance", "Deferred PM", "Backlog accepted"]
        
        elif code == "D9.5":
            chunk["critical_warning"] = "SPECIFIC lack of monitoring system - NOT cultural issue"
            chunk["difference_from_others"] = [
                "D9.5 = SPECIFIC lack of monitoring/audit system",
                "D1.5 = GENERAL cultural normalization (rare)",
                "D1.9 = Manager KNEW but tolerated"
            ]
            chunk["use_for"] = ["LOTO skipped", "Permit not followed", "No audits"]
        
        # Generate embedding keywords from title, description, examples
        keywords = []
        keywords.append(title.lower())
        if chunk["description"]:
            keywords.extend([w.lower() for w in chunk["description"].split() if len(w) > 4])
        keywords.extend([ex.lower() for ex in chunk["typical_examples"]])
        
        # Add specific keywords for better semantic search
        code_keywords = {
            "A1.1": ["rule violation", "deliberate bypass", "LOTO skip", "intentional"],
            "D1.5": ["normalization", "cultural acceptance", "widespread", "everyone does it"],
            "D6.6": ["delayed maintenance", "deferred PM", "backlog", "overdue inspection"],
            "D9.5": ["no monitoring", "no audit", "LOTO skipped", "compliance not verified"],
            "D1.9": ["manager knew", "supervisor tolerated", "leadership ignored"],
        }
        
        if code in code_keywords:
            keywords.extend(code_keywords[code])
        
        # Remove duplicates and clean
        chunk["embeddings_keywords"] = list(set([k.strip() for k in keywords if k.strip()]))[:20]
        
        chunks.append(chunk)
    
    return chunks


def create_mongodb_document(chunks):
    """Create final MongoDB-ready JSON document"""
    
    return {
        "metadata": {
            "version": "2.0",
            "language": "english",
            "total_chunks": len(chunks),
            "categories": ["A", "B", "C", "D"],
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "purpose": "MongoDB vector search chunks for HSG245 taxonomy",
            "source_file": "knowledge_basev2_ing.txt"
        },
        "chunks": chunks
    }


def main():
    input_file = "knowledge_basev2_ing.txt"
    output_file = "knowledge_base_chunks_full.json"
    
    print(f"📖 Reading {input_file}...")
    chunks = parse_knowledge_base(input_file)
    
    print(f"✅ Parsed {len(chunks)} code chunks")
    
    # Create MongoDB document
    mongo_doc = create_mongodb_document(chunks)
    
    # Save to JSON
    print(f"💾 Saving to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mongo_doc, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 SUCCESS!")
    print(f"   Total chunks: {len(chunks)}")
    print(f"   Output: {output_file}")
    
    # Show sample
    print(f"\n📊 Sample chunks:")
    for code in ["A1.1", "D1.5", "D6.6", "D9.5"]:
        matching = [c for c in chunks if c["code"] == code]
        if matching:
            c = matching[0]
            print(f"\n{code}: {c['title']}")
            print(f"  - Keywords: {', '.join(c['embeddings_keywords'][:5])}")
            print(f"  - Examples: {len(c['typical_examples'])}")
            print(f"  - Redirects: {len(c['not_this_if'])}")


if __name__ == "__main__":
    main()
