"""
BARSEL taksonomi — RAG / MongoDB belge modeli ve normalizasyon.

Kaynak dosyalar:
  - barsel_taxonomy_vectordb.jsonl  (ham export)
  - barsel_taxonomy_multilingual.json (yapılandırılmış, opsiyonel birleştirme)

Çıktı:
  - barsel_taxonomy_rag.jsonl  (temiz, RAG + Mongo import için tek satır = bir kod)
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from pydantic import BaseModel, Field

SELECTION_HINTS = (
    "mevcutsa",
    "durumda",
    "doğrulanabiliyorsa",
    "doğrulanması",
    "saptandığı",
    "teyit edildiği",
    "uygulanabiliyorsa",
    "seçilir",
    "seçilmelidir",
)

JUNK_PATTERNS = (
    r"^ler\s*/\s*yaygın eksiklikler$",
    r"^tipik problemler",
    r"^#+\s*[A-D]",
    r"^genel çerçeve",
)


class BarselSection(BaseModel):
    band: str = Field(..., description="A, B, C veya D")
    band_title: str = ""
    band_title_en: str = ""
    group_id: str = ""
    group_title: str = ""


class BarselContentTr(BaseModel):
    title: str
    definition: str
    selection_criteria: Optional[str] = None
    typical_problems: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)


class BarselRetrievalTexts(BaseModel):
    """İki aşamalı eleme metinleri."""
    keyword_text: str = Field(
        ...,
        description="1. eleme: anahtar kelime overlap (düşük maliyet).",
    )
    semantic_text: str = Field(
        ...,
        description="2. eleme: tanım + tipik problemler embedding metni.",
    )
    full_text: str = Field(..., description="Debug / prompt inject için okunabilir özet.")


class BarselRagDocument(BaseModel):
    doc_type: str = "barsel_taxonomy_item"
    taxonomy_id: str = "barsel"
    source: str = ""
    code: str
    code_slug: str = ""
    cause_type: str = Field(..., description="immediate_cause | root_cause")
    cause_level: str = Field(default="", description="immediate | contributing | systemic")
    section: BarselSection
    content: Dict[str, BarselContentTr]
    retrieval: BarselRetrievalTexts

    def to_mongo_document(
        self,
        embedding: Optional[List[float]] = None,
        embedding_meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """MongoDB `rca.taxonomy_barsel` şeması — mevcut retriever ile uyumlu content alanı."""
        tr = self.content.get("tr")
        if not tr:
            raise ValueError(f"{self.code}: tr content missing")

        section_ids: List[str] = [self.section.band]
        section_titles: List[str] = [self.section.band_title] if self.section.band_title else []
        if self.section.group_id:
            section_ids.append(self.section.group_id)
            if self.section.group_title:
                section_titles.append(self.section.group_title)

        doc: Dict[str, Any] = {
            "taxonomy_source": self.taxonomy_id,
            "source": self.source,
            "code": self.code,
            "code_slug": self.code_slug or self.code.replace(".", "_"),
            "cause_type": self.cause_type,
            "cause_level": self.cause_level,
            "section_ids": section_ids,
            "section_titles": section_titles,
            "section": self.section.model_dump(),
            "content": {
                "tr": {
                    "title": tr.title,
                    "definition": tr.definition,
                    "selection_criteria": tr.selection_criteria,
                    "typical_examples": [],
                    "typical_problems": tr.typical_problems,
                }
            },
            "keywords": {"tr": tr.keywords},
            "retrieval": self.retrieval.model_dump(),
            "exclusion_conditions": [],
            "related_codes": [],
        }
        if embedding is not None:
            doc["embedding"] = embedding
        if embedding_meta is not None:
            doc["embedding_meta"] = embedding_meta
        return doc

    def embedding_text(self) -> str:
        return self.retrieval.semantic_text


def _is_junk_line(line: str) -> bool:
    s = (line or "").strip()
    if not s or len(s) < 4:
        return True
    lower = s.lower()
    for pat in JUNK_PATTERNS:
        if re.search(pat, lower):
            return True
    if re.match(r"^[A-D]\d*\.?\s+[A-ZÇĞİÖŞÜ]", s) and not re.match(r"^[A-Z]\d+\.\d+", s):
        return True
    return False


def _is_selection_line(line: str) -> bool:
    lower = line.lower()
    return any(h in lower for h in SELECTION_HINTS)


def parse_keywords(raw: Any) -> List[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        out: List[str] = []
        for item in raw:
            out.extend(parse_keywords(item))
        return _dedupe(out)
    text = str(raw).strip()
    if not text:
        return []
    # Unicode + ASCII tırnak içi ifadeler
    parts = re.findall(r'[""\'\u201c\u201d\u2018\u2019]([^""\'\u201c\u201d\u2018\u2019]+)[""\'\u201c\u201d\u2018\u2019]', text)
    if not parts:
        parts = re.findall(r'["\']([^"\']+)["\']', text)
    if parts:
        return _dedupe(p.strip() for p in parts if p.strip())
    chunks = re.split(r'[;,|]+', text)
    cleaned = []
    for c in chunks:
        c = c.strip().strip('"\'""''\u201c\u201d')
        c = re.sub(r"^anahtar kelimeler:\s*", "", c, flags=re.I)
        if c and len(c) > 2:
            cleaned.append(c)
    return _dedupe(cleaned)


def _dedupe(items: Iterable[str]) -> List[str]:
    seen: set[str] = set()
    out: List[str] = []
    for item in items:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out


def split_problems_and_selection(lines: List[str]) -> tuple[List[str], Optional[str]]:
    problems: List[str] = []
    selection: List[str] = []
    for line in lines:
        line = line.strip()
        if not line or _is_junk_line(line):
            continue
        if _is_selection_line(line):
            selection.append(line)
        else:
            problems.append(line)
    criteria = " ".join(selection).strip() or None
    return problems, criteria


def _cause_type_from_record(raw: Dict[str, Any]) -> str:
    level = (raw.get("cause_level") or "").lower()
    if level == "immediate":
        return "immediate_cause"
    letter = (raw.get("category_letter") or raw.get("hsg_layer") or raw.get("code") or "A")[0]
    return "immediate_cause" if letter == "A" else "root_cause"


def build_retrieval_texts(
    *,
    code: str,
    title: str,
    definition: str,
    typical_problems: List[str],
    selection_criteria: Optional[str],
    keywords: List[str],
    section: BarselSection,
) -> BarselRetrievalTexts:
    kw_text = " ".join(keywords)
    semantic_parts = [
        f"Code: {code}",
        f"Title: {title}",
        f"Definition: {definition}",
    ]
    if typical_problems:
        semantic_parts.append(
            "Typical problems and common gaps: " + "; ".join(typical_problems)
        )
    if selection_criteria:
        semantic_parts.append(f"When to select: {selection_criteria}")

    full_lines = [
        f"[{code}] {title}",
        f"Band {section.band}: {section.band_title}",
    ]
    if section.group_title:
        full_lines.append(f"Group {section.group_id}: {section.group_title}")
    full_lines.append("")
    full_lines.append(definition)
    if typical_problems:
        full_lines.append("")
        full_lines.append("Tipik Problemler / Yaygın Eksiklikler:")
        for p in typical_problems:
            full_lines.append(f"- {p}")
    if selection_criteria:
        full_lines.append("")
        full_lines.append(f"Seçim kriterleri: {selection_criteria}")
    if keywords:
        full_lines.append("")
        full_lines.append("Anahtar kelimeler: " + ", ".join(keywords))

    return BarselRetrievalTexts(
        keyword_text=kw_text,
        semantic_text=". ".join(semantic_parts),
        full_text="\n".join(full_lines),
    )


def normalize_vectordb_record(raw: Dict[str, Any]) -> BarselRagDocument:
    """Ham barsel_taxonomy_vectordb.jsonl satırını temiz RAG belgesine çevirir."""
    code = str(raw.get("code") or "").strip()
    if not code:
        raise ValueError("code missing")

    raw_problems = raw.get("typical_problems") or []
    if not isinstance(raw_problems, list):
        raw_problems = [str(raw_problems)]
    problems, selection = split_problems_and_selection([str(x) for x in raw_problems])

    keywords = parse_keywords(raw.get("keywords"))
    definition = str(raw.get("definition") or "").strip()
    title = str(raw.get("title") or "").strip()

    section = BarselSection(
        band=str(raw.get("category_letter") or raw.get("hsg_layer") or code[0]),
        band_title=str(raw.get("category_name") or ""),
        band_title_en=str(raw.get("category_name_en") or ""),
        group_id=_group_id_from_parent(str(raw.get("parent_group") or "")),
        group_title=str(raw.get("parent_group") or "").strip(),
    )

    retrieval = build_retrieval_texts(
        code=code,
        title=title,
        definition=definition,
        typical_problems=problems,
        selection_criteria=selection,
        keywords=keywords,
        section=section,
    )

    tr = BarselContentTr(
        title=title,
        definition=definition,
        selection_criteria=selection,
        typical_problems=problems,
        keywords=keywords,
    )

    return BarselRagDocument(
        source=str(raw.get("source") or "BARSEL_Taksonomi"),
        code=code,
        code_slug=str(raw.get("code_slug") or code.replace(".", "_")),
        cause_type=_cause_type_from_record(raw),
        cause_level=str(raw.get("cause_level") or ""),
        section=section,
        content={"tr": tr},
        retrieval=retrieval,
    )


def _group_id_from_parent(parent_group: str) -> str:
    m = re.match(r"^([A-D]\d+)", parent_group.strip())
    return m.group(1) if m else ""


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(docs: List[BarselRagDocument], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for doc in docs:
            f.write(json.dumps(doc.model_dump(), ensure_ascii=False) + "\n")
