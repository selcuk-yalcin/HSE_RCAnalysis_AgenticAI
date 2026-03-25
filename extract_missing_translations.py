#!/usr/bin/env python3
"""
Extract all missing translation keys from IncidentForm.jsx
to help populate translations.js for all languages.
"""

import re

# Read IncidentForm.jsx
with open('/Users/selcuk/Desktop/HSE_RCAnalysis_AgenticAI-main/frontend/src/components/IncidentForm.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all t('...') calls
t_calls = re.findall(r"t\('([^']+)'\)", content)
t_calls_unique = sorted(set(t_calls))

# Read existing translations.js to see what's already defined
with open('/Users/selcuk/Desktop/HSE_RCAnalysis_AgenticAI-main/frontend/src/utils/translations.js', 'r', encoding='utf-8') as f:
    trans_content = f.read()

# Extract already defined keys for Turkish (tr)
existing_keys = set(re.findall(r"(\w+):\s*['\"]", trans_content))

missing = [k for k in t_calls_unique if k not in existing_keys]

print("=" * 60)
print(f"Found {len(t_calls_unique)} unique t() calls in IncidentForm.jsx")
print(f"Already defined keys: {len(existing_keys)}")
print(f"Missing keys: {len(missing)}")
print("=" * 60)

if missing:
    print("\nMissing translation keys:")
    for key in missing:
        print(f"  - {key}")
        # Show where it's used
        lines = [i+1 for i, line in enumerate(content.split('\n')) if f"t('{key}')" in line]
        if lines:
            print(f"    Line(s): {lines[:3]}")  # Show first 3 lines

print("\n" + "=" * 60)
