"""
HGS taxonomy parser/utilities for HITL and Mongo export.
"""

from __future__ import annotations

import re
import runpy
from pathlib import Path
from typing import Iterable, Optional

from pydantic import BaseModel, Field


CODE_RE = re.compile(r"^([ABCD]\d+\.\d+)\s+(.+)$")
TOKEN_RE = re.compile(r"[a-z0-9çğıöşü]+", re.IGNORECASE)


class HGSTaxonomyItem(BaseModel):
    code: str
    title: str
    category: str
    section_key: str
    description: str = ""
    choose_if: list[str] = Field(default_factory=list)
    typical_examples: list[str] = Field(default_factory=list)
    not_this_if: list[str] = Field(default_factory=list)

    def to_search_text(self) -> str:
        fields = [
            self.code,
            self.title,
            self.description,
            " ".join(self.choose_if),
            " ".join(self.typical_examples),
            " ".join(self.not_this_if),
        ]
        return " ".join(fields).lower()


def _tokenize(text: str) -> set[str]:
    return {t.lower() for t in TOKEN_RE.findall(text or "") if len(t) >= 3}


def load_hsg_taxonomy_source(
    source_path: str = "agents/knowledge.json",
) -> dict[str, str]:
    payload = runpy.run_path(str(Path(source_path)))
    raw = payload.get("HSG245_TAXONOMY")
    if not isinstance(raw, dict):
        raise RuntimeError("HSG245_TAXONOMY not found in agents/knowledge.json")
    return {str(k): str(v) for k, v in raw.items()}


def parse_hsg_taxonomy_items(source_path: str = "agents/knowledge.json") -> list[HGSTaxonomyItem]:
    taxonomy_sections = load_hsg_taxonomy_source(source_path)
    items: list[HGSTaxonomyItem] = []

    for section_key, section_text in taxonomy_sections.items():
        lines = [ln.strip() for ln in str(section_text).splitlines() if ln.strip()]
        current_code: Optional[str] = None
        current_title = ""
        buf: list[str] = []

        def flush() -> None:
            if not current_code:
                return
            description_parts: list[str] = []
            choose_if: list[str] = []
            typical_examples: list[str] = []
            not_this_if: list[str] = []
            for ln in buf:
                if ln.startswith("→ Choose if:"):
                    choose_if.append(ln.replace("→ Choose if:", "", 1).strip())
                elif ln.startswith("→ Typical:"):
                    typical_examples.append(ln.replace("→ Typical:", "", 1).strip())
                elif "✗ Not this if:" in ln:
                    not_this_if.append(ln.split("✗ Not this if:", 1)[-1].strip())
                elif not ln.startswith(("→", "✗")):
                    description_parts.append(ln)

            items.append(
                HGSTaxonomyItem(
                    code=current_code,
                    title=current_title,
                    category=current_code[0],
                    section_key=section_key,
                    description=" ".join(description_parts).strip(),
                    choose_if=[s for s in choose_if if s],
                    typical_examples=[s for s in typical_examples if s],
                    not_this_if=[s for s in not_this_if if s],
                )
            )

        for ln in lines:
            m = CODE_RE.match(ln)
            if m:
                flush()
                current_code = m.group(1).upper()
                current_title = m.group(2).strip()
                buf = []
                continue
            if current_code:
                buf.append(ln)
        flush()
    return items


def infer_codes_from_text(text: str, items: Iterable[HGSTaxonomyItem], top_k: int = 3) -> list[str]:
    qtokens = _tokenize(text)
    if not qtokens:
        return []
    scored: list[tuple[float, str]] = []
    for item in items:
        stokens = _tokenize(item.to_search_text())
        if not stokens:
            continue
        common = qtokens.intersection(stokens)
        if not common:
            continue
        score = len(common) / max(1.0, len(qtokens))
        scored.append((score, item.code))
    scored.sort(key=lambda x: x[0], reverse=True)
    out: list[str] = []
    for _, code in scored:
        if code not in out:
            out.append(code)
        if len(out) >= top_k:
            break
    return out

