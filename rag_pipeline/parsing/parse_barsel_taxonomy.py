"""
BARSEL Taksonomi Parser — DOCX → taxonomy_multilingual-compatible JSON
========================================================================

Kaynak: rag_pipeline/data/processed/BARSEL_Taksonomi.docx

Çıktı alanları (cause):
  - content.tr: title, definition, selection_criteria, typical_problems
  - keywords.tr: anahtar kelimeler (1. eleme için)
  - section_ids / section_titles: bölüm hiyerarşisi

Kullanım:
    python rag_pipeline/parsing/parse_barsel_taxonomy.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from docx import Document

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from rag_pipeline.schemas.cause_models import (  # noqa: E402
    Cause,
    LocalizedContent,
    Taxonomy,
    TaxonomyMeta,
    TaxonomySection,
)

CODE_RE = re.compile(r"^([A-Z]\d+\.\d+)\s+(.+)$")
TOP_SECTION_RE = re.compile(r"^([A-D])\.\s+(.+)$")
SUB_SECTION_RE = re.compile(r"^([A-D]\d+)\.\s+(.+)$")
TOP_SECTION_NO_DOT_RE = re.compile(r"^([A-D])\s+(.+)$")
KEYWORDS_RE = re.compile(r"^Anahtar kelimeler:\s*(.*)$", re.IGNORECASE)
TYPICAL_PROBLEMS_HEADER = "Tipik Problemler / Yaygın Eksiklikler"

SELECTION_HINTS = (
    "mevcutsa",
    "durumda",
    "doğrulanabiliyorsa",
    "doğrulanması",
    "saptandığı",
    "teyit edildiği",
    "teyit edildiğ",
    "uygulanabiliyorsa",
    "seçilir",
    "seçilmelidir",
)


def _normalize(text: str) -> str:
    return text.replace("\xa0", " ").replace("\n", " ").strip()


def _parse_keywords(line: str) -> List[str]:
    raw = KEYWORDS_RE.match(line)
    if not raw:
        return []
    body = raw.group(1).strip()
    if not body:
        return []
    parts = re.findall(r'["\'""'']([^"\']+)["\'""'']', body)
    if parts:
        return [p.strip() for p in parts if p.strip()]
    # fallback: split on common delimiters
    chunks = re.split(r'[;,|/]+', body)
    return [c.strip().strip('"\'') for c in chunks if c.strip()]


def _is_selection_line(line: str) -> bool:
    lower = line.lower()
    return any(h in lower for h in SELECTION_HINTS)


def _determine_cause_type(code: str) -> str:
    return "immediate_cause" if code.startswith("A") else "root_cause"


def _section_key(title: str) -> Optional[Tuple[str, str, int, str]]:
    """Return (id, title, level, band) or None."""
    m = TOP_SECTION_RE.match(title)
    if m:
        return m.group(1), title, 1, m.group(1)
    m = TOP_SECTION_NO_DOT_RE.match(title)
    if m and not re.match(r"^[A-D]\d", title):
        return m.group(1), title, 1, m.group(1)
    m = SUB_SECTION_RE.match(title)
    if m:
        sid = m.group(1)
        return sid, title, 2, sid[0]
    return None


class BarselTaxonomyParser:
    def __init__(self, docx_path: Path):
        self.docx_path = docx_path
        self.sections: Dict[str, TaxonomySection] = {}
        self.current_band: Optional[str] = None
        self.current_sub: Optional[str] = None

    def _register_section(self, parsed: Tuple[str, str, int, str]) -> None:
        sid, title, level, band = parsed
        parent_id = band if level == 2 else None
        if sid in self.sections:
            return
        self.sections[sid] = TaxonomySection(
            id=sid,
            title=title,
            parent_id=parent_id,
            level=level,
            band=band,
        )
        if level == 1:
            self.current_band = sid
            self.current_sub = None
        else:
            self.current_sub = sid

    def _section_path(self) -> Tuple[List[str], List[str]]:
        ids: List[str] = []
        titles: List[str] = []
        if self.current_band and self.current_band in self.sections:
            ids.append(self.current_band)
            titles.append(self.sections[self.current_band].title)
        if self.current_sub and self.current_sub in self.sections:
            ids.append(self.current_sub)
            titles.append(self.sections[self.current_sub].title)
        return ids, titles

    def parse(self) -> Taxonomy:
        document = Document(str(self.docx_path))
        paras = [_normalize(p.text) for p in document.paragraphs]
        paras = [p for p in paras if p]

        pending_keywords: List[str] = []
        causes_raw: List[dict] = []
        i = 0
        while i < len(paras):
            line = paras[i]

            sec = _section_key(line)
            if sec and not CODE_RE.match(line):
                self._register_section(sec)
                i += 1
                continue

            kw = _parse_keywords(line)
            if kw:
                pending_keywords = kw
                i += 1
                continue

            code_match = CODE_RE.match(line)
            if not code_match:
                i += 1
                continue

            code = code_match.group(1)
            title = code_match.group(2).strip()
            section_ids, section_titles = self._section_path()
            keywords = list(pending_keywords)
            pending_keywords = []

            i += 1
            definition = ""
            if i < len(paras) and not CODE_RE.match(paras[i]) and TYPICAL_PROBLEMS_HEADER not in paras[i]:
                definition = paras[i]
                i += 1

            typical_problems: List[str] = []
            selection_lines: List[str] = []
            if i < len(paras) and paras[i].strip() == TYPICAL_PROBLEMS_HEADER:
                i += 1
                while i < len(paras):
                    nxt = paras[i]
                    if CODE_RE.match(nxt) or KEYWORDS_RE.match(nxt) or _section_key(nxt):
                        break
                    if _is_selection_line(nxt):
                        selection_lines.append(nxt)
                    else:
                        typical_problems.append(nxt)
                    i += 1

            selection_criteria = " ".join(selection_lines).strip() or None
            causes_raw.append(
                {
                    "code": code,
                    "title": title,
                    "definition": definition,
                    "selection_criteria": selection_criteria,
                    "typical_problems": typical_problems,
                    "keywords": keywords,
                    "section_ids": section_ids,
                    "section_titles": section_titles,
                }
            )

        # Trailing keywords belong to last cause if block ended without next code
        if pending_keywords and causes_raw:
            last = causes_raw[-1]
            seen = set(last["keywords"])
            for k in pending_keywords:
                if k not in seen:
                    last["keywords"].append(k)

        cause_objects: List[Cause] = []
        for raw in causes_raw:
            cause_objects.append(
                Cause(
                    code=raw["code"],
                    cause_type=_determine_cause_type(raw["code"]),
                    content={
                        "tr": LocalizedContent(
                            title=raw["title"],
                            definition=raw["definition"],
                            selection_criteria=raw["selection_criteria"],
                            typical_examples=[],
                            typical_problems=raw["typical_problems"],
                        )
                    },
                    exclusion_conditions=[],
                    related_codes=[],
                    keywords={"tr": raw["keywords"]},
                    severity_indicators=[],
                    industry_contexts=[],
                    section_ids=raw["section_ids"],
                    section_titles=raw["section_titles"],
                    taxonomy_source="barsel",
                )
            )

        meta = TaxonomyMeta(
            taxonomy_id="barsel",
            source_file=self.docx_path.name,
            version="1.0",
            primary_language="tr",
            cause_count=len(cause_objects),
        )
        sections_sorted = sorted(
            self.sections.values(),
            key=lambda s: (s.level, s.id),
        )
        return Taxonomy(meta=meta, sections=sections_sorted, causes=cause_objects)


def main() -> None:
    docx_path = project_root / "rag_pipeline" / "data" / "processed" / "BARSEL_Taksonomi.docx"
    output_path = project_root / "rag_pipeline" / "data" / "processed" / "barsel_taxonomy_multilingual.json"

    if not docx_path.exists():
        raise FileNotFoundError(f"BARSEL docx not found: {docx_path}")

    print("=" * 70)
    print("BARSEL Taxonomy Parser")
    print("=" * 70)
    parser = BarselTaxonomyParser(docx_path)
    taxonomy = parser.parse()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(taxonomy.model_dump(), f, ensure_ascii=False, indent=2)

    with_kw = sum(1 for c in taxonomy.causes if c.keywords.get("tr"))
    with_prob = sum(
        1 for c in taxonomy.causes if c.content.get("tr") and c.content["tr"].typical_problems
    )
    print(f"✓ Sections: {len(taxonomy.sections)}")
    print(f"✓ Causes: {len(taxonomy.causes)}")
    print(f"✓ With keywords: {with_kw}")
    print(f"✓ With typical_problems: {with_prob}")
    print(f"✅ Written: {output_path}")


if __name__ == "__main__":
    main()
