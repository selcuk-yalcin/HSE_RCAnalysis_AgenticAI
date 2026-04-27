"""
Build ABS Guidance Vector Store
===============================

ABS Root Cause Map guidance PDF dosyasını chunk'lara ayırır, embedding üretir ve
MongoDB'ye yükler.

Kullanım:
  python rag_pipeline/indexing/build_abs_guidance_vector_store.py
  python rag_pipeline/indexing/build_abs_guidance_vector_store.py --chunk-size 1200 --chunk-overlap 160
"""

from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import hashlib


load_dotenv()


@dataclass
class GuidanceChunk:
    chunk_id: str
    source: str
    section_hint: str
    page_start: int
    page_end: int
    text: str
    block_type: str = "general"


def _extract_pdf_text(pdf_path: Path) -> List[str]:
    try:
        from pypdf import PdfReader
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("PDF parse için pypdf gerekli (pip install pypdf).") from exc

    reader = PdfReader(str(pdf_path))
    pages: List[str] = []
    for page in reader.pages:
        text = (page.extract_text() or "").strip()
        pages.append(text)
    return pages


def _clean_page_text(text: str) -> str:
    # Normalize common PDF ligatures and dash variants for robust heading detection.
    t = (
        text.replace("ﬁ", "fi")
        .replace("ﬂ", "fl")
        .replace("’", "'")
        .replace("–", "-")
        .replace("—", "-")
    )
    t = re.sub(r"\r", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    t = re.sub(r"[ \t]+", " ", t)
    return t.strip()


def _detect_section_hint(text: str, fallback: str = "general") -> str:
    # Prefer real ABS page titles (e.g., "Personnel Records Issue") over page_* fallback.
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    ignored = (
        "copyright",
        "definitions/typical issues",
        "typical recommendations",
        "examples",
        "note",
        "notes",
    )
    for ln in lines[:40]:
        m_issue = re.search(r"(?:\d+\s*-\s*)?([A-Za-z][A-Za-z0-9/&,\-()'. ]+?Issue(?:\s*\(cont\.\))?)", ln)
        if m_issue:
            title = re.sub(r"\s+", " ", m_issue.group(1)).strip(" -")
            title = re.sub(r"\s*\(cont\.\)\s*$", "", title, flags=re.IGNORECASE)
            if len(title) >= 8:
                return title[:120]

    for ln in lines[:40]:
        low = ln.lower()
        if any(tok in low for tok in ignored):
            continue
        # Matches:
        # - "Personnel Records Issue - 71"
        # - "70 - Out-of-date Documents Used"
        # - "Personnel Records Issue"
        m = re.match(r"^(?:\d+\s*-\s*)?([A-Za-z][A-Za-z0-9/&,\-()'. ]{3,}?)(?:\s*-\s*\d+)?$", ln)
        if m:
            title = re.sub(r"\s+", " ", m.group(1)).strip(" -")
            if len(title) >= 8:
                return title[:120]

    for ln in lines[:24]:
        if ln.isupper() and len(ln) > 6:
            return ln[:120]
    return fallback


def _split_text_naturally(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """Split text near sentence/line boundaries to avoid mid-content cuts."""
    s = text.strip()
    if not s:
        return []
    chunks: List[str] = []
    start = 0
    n = len(s)
    while start < n:
        tentative_end = min(n, start + chunk_size)
        if tentative_end < n:
            window = s[start:tentative_end]
            candidates = [window.rfind("\n\n"), window.rfind("\n"), window.rfind(". "), window.rfind("; "), window.rfind(": ")]
            best = max(candidates)
            # keep boundary search meaningful; avoid tiny chunk fragments
            if best >= int(chunk_size * 0.55):
                end = start + best + 1
            else:
                end = tentative_end
        else:
            end = tentative_end
        piece = s[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= n:
            break
        start = max(start + 1, end - chunk_overlap)
    return chunks


def _chunk_pages(pages: List[str], chunk_size: int, chunk_overlap: int) -> List[GuidanceChunk]:
    chunks: List[GuidanceChunk] = []
    source = "ABSG_Consulting_Inc_Root_Cause_Map_Guidance_Document_1703.pdf"

    for page_idx, raw in enumerate(pages, start=1):
        cleaned = _clean_page_text(raw)
        if not cleaned:
            continue
        section_hint = _detect_section_hint(cleaned, fallback=f"page_{page_idx}")
        start = 0
        part_idx = 1
        while start < len(cleaned):
            end = min(len(cleaned), start + chunk_size)
            chunk_text = cleaned[start:end].strip()
            if len(chunk_text) >= 80:
                chunks.append(
                    GuidanceChunk(
                        chunk_id=f"abs_p{page_idx:03d}_c{part_idx:03d}",
                        source=source,
                        section_hint=section_hint,
                        page_start=page_idx,
                        page_end=page_idx,
                        text=chunk_text,
                    )
                )
                part_idx += 1
            if end >= len(cleaned):
                break
            start = max(0, end - chunk_overlap)
    return chunks


_STRUCTURED_HEADINGS = [
    (
        "definitions_typical_issues",
        r"De\S*nitions\s*/\s*Typical\s*Issues",
    ),
    ("notes", r"\bNotes?\b"),
    ("examples", r"\bExamples?\b"),
    ("typical_recommendations", r"Typical\s+Recommendations"),
]


def _structured_blocks_from_text(text: str) -> List[tuple[str, str]]:
    """Split page text into known ABS sections."""
    spans = []
    for key, pattern in _STRUCTURED_HEADINGS:
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            spans.append((m.start(), m.end(), key))
    if not spans:
        return [("general", text.strip())] if text.strip() else []

    spans.sort(key=lambda x: x[0])
    blocks: List[tuple[str, str]] = []
    for i, (start, end, key) in enumerate(spans):
        next_start = spans[i + 1][0] if i + 1 < len(spans) else len(text)
        body = text[end:next_start].strip()
        if body:
            blocks.append((key, body))
    return blocks


def _chunk_pages_structured(pages: List[str], chunk_size: int, chunk_overlap: int) -> List[GuidanceChunk]:
    """
    Chunk with ABS section-aware blocks:
    Definitions/Typical Issues, Notes, Examples, Typical Recommendations.
    """
    chunks: List[GuidanceChunk] = []
    source = "ABSG_Consulting_Inc_Root_Cause_Map_Guidance_Document_1703.pdf"

    for page_idx, raw in enumerate(pages, start=1):
        cleaned = _clean_page_text(raw)
        if not cleaned:
            continue
        section_hint = _detect_section_hint(cleaned, fallback=f"page_{page_idx}")
        blocks = _structured_blocks_from_text(cleaned)
        block_counter = 1
        for block_type, block_text in blocks:
            part_idx = 1
            for chunk_text in _split_text_naturally(block_text, chunk_size=chunk_size, chunk_overlap=chunk_overlap):
                if len(chunk_text) >= 80:
                    chunks.append(
                        GuidanceChunk(
                            chunk_id=f"abs_p{page_idx:03d}_b{block_counter:02d}_c{part_idx:03d}",
                            source=source,
                            section_hint=section_hint,
                            page_start=page_idx,
                            page_end=page_idx,
                            text=chunk_text,
                            block_type=block_type,
                        )
                    )
                    part_idx += 1
            block_counter += 1
    return chunks


class ABSGuidanceVectorBuilder:
    def __init__(
        self,
        mongo_db: str = "rca",
        mongo_collection: str = "abs_guidance_chunks",
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
    ):
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection
        self.model_name = model_name
        self.client: Optional[MongoClient] = None
        self.collection = None
        self.model = None
        self._use_fallback_embedding = False
        try:
            from sentence_transformers import SentenceTransformer

            print(f"🤖 Embedding model yükleniyor: {model_name}")
            self.model = SentenceTransformer(model_name)
        except Exception as exc:  # noqa: BLE001
            print(f"⚠️ SentenceTransformer yüklenemedi ({exc}). Fallback embedding kullanılacak.")
            self._use_fallback_embedding = True

    @staticmethod
    def _fallback_embed(text: str, dim: int = 384) -> list[float]:
        """Dependency-free deterministic embedding fallback (for indexing continuity)."""
        vec = [0.0] * dim
        tokens = text.lower().split()
        if not tokens:
            return vec
        for tok in tokens:
            h = int(hashlib.sha256(tok.encode("utf-8")).hexdigest(), 16)
            idx = h % dim
            sign = -1.0 if (h % 2) else 1.0
            vec[idx] += sign
        norm = sum(v * v for v in vec) ** 0.5
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def connect(self) -> None:
        uri = os.getenv("MONGODB_URI", "").strip()
        if not uri:
            raise RuntimeError("MONGODB_URI bulunamadı.")
        self.client = MongoClient(uri, server_api=ServerApi("1"))
        self.client.admin.command("ping")
        self.collection = self.client[self.mongo_db][self.mongo_collection]
        print(f"✓ Mongo bağlantısı: {self.mongo_db}.{self.mongo_collection}")

    def upload(self, chunks: List[GuidanceChunk]) -> None:
        if self.collection is None:
            raise RuntimeError("Mongo bağlantısı hazır değil.")
        if not chunks:
            raise RuntimeError("Yüklenecek chunk bulunamadı.")

        texts = [c.text for c in chunks]
        if self._use_fallback_embedding:
            vectors = [self._fallback_embed(t) for t in texts]
        else:
            vectors = self.model.encode(texts, convert_to_tensor=False, show_progress_bar=True)

        docs = []
        for c, emb in zip(chunks, vectors):
            docs.append(
                {
                    "chunk_id": c.chunk_id,
                    "source": c.source,
                    "section_hint": c.section_hint,
                    "block_type": c.block_type,
                    "page_start": c.page_start,
                    "page_end": c.page_end,
                    "text": c.text,
                    "embedding": emb.tolist() if hasattr(emb, "tolist") else emb,
                }
            )

        print("🗑️ Eski ABS guidance chunk'ları temizleniyor...")
        self.collection.delete_many({"source": "ABSG_Consulting_Inc_Root_Cause_Map_Guidance_Document_1703.pdf"})
        print(f"⬆️ {len(docs)} chunk MongoDB'ye yükleniyor...")
        self.collection.insert_many(docs)
        self.collection.create_index("chunk_id", unique=True)
        self.collection.create_index([("source", 1), ("page_start", 1)])
        print("✅ ABS guidance vector store güncellendi.")

    def close(self) -> None:
        if self.client is not None:
            self.client.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="ABS guidance PDF -> Mongo vector store")
    parser.add_argument(
        "--pdf-path",
        default="knowlodge_base/ABSG_Consulting_Inc_Root_Cause_Map_Guidance_Document_1703.pdf",
        help="ABS guidance PDF dosya yolu",
    )
    parser.add_argument("--chunk-size", type=int, default=1200, help="Her chunk için karakter limiti")
    parser.add_argument("--chunk-overlap", type=int, default=160, help="Chunk overlap karakter sayısı")
    parser.add_argument("--mongo-db", default="rca", help="Mongo database adı")
    parser.add_argument("--mongo-collection", default="abs_guidance_chunks", help="Mongo collection adı")
    parser.add_argument("--embedding-model", default="paraphrase-multilingual-MiniLM-L12-v2", help="SentenceTransformer model adı")
    args = parser.parse_args()

    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF bulunamadı: {pdf_path}")

    print("📄 ABS guidance PDF okunuyor...")
    pages = _extract_pdf_text(pdf_path)
    chunks = _chunk_pages_structured(pages, chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)
    print(f"✓ {len(chunks)} chunk üretildi.")

    builder = ABSGuidanceVectorBuilder(
        mongo_db=args.mongo_db,
        mongo_collection=args.mongo_collection,
        model_name=args.embedding_model,
    )
    try:
        builder.connect()
        builder.upload(chunks)
    finally:
        builder.close()


if __name__ == "__main__":
    main()

