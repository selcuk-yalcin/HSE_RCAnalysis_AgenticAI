#!/usr/bin/env python3
"""
Generate a Markdown version of knowledge_basev2_ing.txt suitable for LlamaIndex chunking.
Each code (e.g., A1.1, D4.1) becomes a level-3 heading and the following paragraph(s) are kept as the section body.
"""
import re

IN = 'agents/knowledge_basev2_ing.txt'
OUT = 'agents/knowledge_base_llamaindex.md'

def convert(in_path=IN, out_path=OUT):
    with open(in_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    out_lines = []
    out_lines.append('# HSG245 Taxonomy — LlamaIndex-ready Markdown\n')
    out_lines.append('This file was generated from `agents/knowledge_basev2_ing.txt` and formatted so each code block is a separate heading for chunking with LlamaIndex.\n\n')

    code_re = re.compile(r'^([A-D]\d+\.\d+)\s+(.+)$')
    # Also match top-level category headers like '### C. SYSTEMIC ROOT CAUSES - PERSONAL FACTORS'
    category_re = re.compile(r'^(#{1,6}\s*.+|###\s+[A-Z]\.\s+.+)$')

    for i, raw in enumerate(lines):
        line = raw.rstrip('\n')
        m = code_re.match(line.strip())
        if m:
            code = m.group(1)
            title = m.group(2).strip()
            out_lines.append(f'### {code} — {title}\n')
            continue
        # If line starts with '####' category header, convert to H2
        if line.startswith('### '):
            out_lines.append('\n## ' + line.lstrip('# ').strip() + '\n')
            continue
        # Preserve bullets and other content
        out_lines.append(line + '\n')

    with open(out_path, 'w', encoding='utf-8') as f:
        f.writelines(out_lines)

    print(f'Wrote {out_path}')

if __name__ == '__main__':
    convert()
