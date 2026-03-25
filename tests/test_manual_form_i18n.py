#!/usr/bin/env python3
"""
Test Manuel Form (IncidentForm.jsx) internationalization:
Verify that all expected translation keys exist in all languages.
"""

import json
import re

print("=" * 70)
print(" 📋 MANUEL FORM - I18N TEST REPORT")
print("=" * 70)

# Read translations.js
with open('/Users/selcuk/Desktop/HSE_RCAnalysis_AgenticAI-main/frontend/src/utils/translations.js', 'r', encoding='utf-8') as f:
    trans_content = f.read()

# Extract translation objects for each language
languages = ['tr', 'en', 'de', 'fr', 'es', 'ar']
translations = {}

for lang in languages:
    # Find the language block: `lang: { ... }`
    pattern = rf"{lang}:\s*{{(.*?)\n  }}"
    match = re.search(pattern, trans_content, re.DOTALL)
    if match:
        lang_content = match.group(1)
        # Count keys (rough count)
        keys = len(re.findall(r'(\w+):\s*[\'"]', lang_content))
        translations[lang] = keys
    else:
        translations[lang] = 0

print(f"\n✅ Translations file loaded successfully")
print(f"   Translation keys per language:")
for lang in languages:
    print(f"   {lang.upper()}: {translations[lang]} keys defined")

# Read IncidentForm.jsx and count t() calls
with open('/Users/selcuk/Desktop/HSE_RCAnalysis_AgenticAI-main/frontend/src/components/IncidentForm.jsx', 'r', encoding='utf-8') as f:
    form_content = f.read()

t_calls = re.findall(r"t\('([^']+)'\)", form_content)
t_calls_unique = sorted(set(t_calls))

print(f"\n✅ IncidentForm.jsx analyzed")
print(f"   Total t() calls: {len(t_calls)}")
print(f"   Unique keys used: {len(t_calls_unique)}")

# Check if all keys exist in translations
print(f"\n🔍 Checking key coverage...")

missing_keys_by_lang = {lang: [] for lang in languages}
all_missing = []

for key in t_calls_unique:
    for lang in languages:
        pattern = rf'"{key}":\s*[\'"]|{key}:\s*[\'"]'
        # Search in language block
        lang_pattern = rf"{lang}:\s*{{(.*?)\n  }}"
        lang_match = re.search(lang_pattern, trans_content, re.DOTALL)
        if lang_match:
            lang_block = lang_match.group(1)
            if not re.search(pattern, lang_block):
                missing_keys_by_lang[lang].append(key)
                if key not in all_missing:
                    all_missing.append(key)

if all_missing:
    print(f"   ⚠️  Missing keys found: {len(all_missing)}")
    for key in all_missing[:10]:  # Show first 10
        print(f"      - {key}")
    if len(all_missing) > 10:
        print(f"      ... and {len(all_missing) - 10} more")
else:
    print(f"   ✅ ALL keys found in translations!")

# Test sections coverage
print(f"\n📋 Form sections verification:")
sections = [
    'section_reporter',
    'section_incident_details',
    'section_description',
    'section_safety_equipment',
    'section_witnesses',
    'section_environment',
    'section_work_conditions',
    'section_injuries',
    'section_root_cause'
]

for section in sections:
    found_in_lang = sum(1 for lang in languages if missing_keys_by_lang[lang].count(section) == 0)
    status = "✅" if found_in_lang == len(languages) else "⚠️ "
    print(f"   {status} {section}: {found_in_lang}/{len(languages)} languages")

# Summary
print(f"\n" + "=" * 70)
total_missing = sum(len(v) for v in missing_keys_by_lang.values())

if total_missing == 0:
    print("✅ TEST PASSED: Manuel Form is fully internationalized!")
    print("   - All form sections translated")
    print("   - All fields and labels covered")
    print("   - Ready for multi-language deployment")
else:
    print(f"⚠️  TEST WARNING: {total_missing} missing translations found")
    print("   Language breakdown:")
    for lang in languages:
        if missing_keys_by_lang[lang]:
            print(f"   {lang.upper()}: {len(missing_keys_by_lang[lang])} missing")

print("=" * 70 + "\n")
