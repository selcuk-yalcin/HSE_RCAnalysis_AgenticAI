"""
P1.26 — Rapor 5-Why zincirini agent (part3_rca) verisine sabitle.

LLM rapor katmanı why_chain'i yeniden yazamaz; NEDEN 1 ortak olay sorusu +
cevap A/B taksonomiden (immediate_cause) gelir.
"""

from __future__ import annotations

import copy
import re
from typing import Any, Dict, List, Tuple

try:
    from agents.report_text_sanitize import strip_hse_codes
    from agents.why_chain_quality import (
        build_event_why1_question,
        immediate_cause_sentence,
        strip_barsel_answer_prefix,
    )
except ImportError:
    from .report_text_sanitize import strip_hse_codes
    from .why_chain_quality import (
        build_event_why1_question,
        immediate_cause_sentence,
        strip_barsel_answer_prefix,
    )


def build_shared_event_question(incident_text: str) -> str:
    """Tüm dallarda ortak NEDEN 1 olay sorusu."""
    return build_event_why1_question(incident_text)


def _incident_summary_from_raw(raw_data: Dict[str, Any]) -> str:
    part3 = raw_data.get("part3_rca") or {}
    part1 = raw_data.get("part1") or {}
    overview = part1.get("overview") if isinstance(part1.get("overview"), dict) else {}
    return str(
        part3.get("incident_summary")
        or overview.get("what_happened")
        or part1.get("description")
        or ""
    ).strip()


def _raw_analysis_branches(raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    part3 = raw_data.get("part3_rca") or {}
    rows = part3.get("analysis_branches") or part3.get("branches") or []
    return [b for b in rows if isinstance(b, dict)]


def immediate_cause_report_answer(immediate: Dict[str, Any]) -> str:
    """
    NEDEN 1 cevabı: A/B bandından immediate_cause (BARSEL cause_tr / resmi başlık).
    Kodlar rapor metnine gömülmez.
    """
    imm = immediate if isinstance(immediate, dict) else {}
    code = str(imm.get("code") or "").strip().upper()
    cause_tr = str(imm.get("cause_tr") or imm.get("cause") or "").strip()
    if not cause_tr:
        try:
            from agents.barsel_taxonomy import official_title_tr_for_code
        except ImportError:
            from .barsel_taxonomy import official_title_tr_for_code
        if code:
            cause_tr = str(official_title_tr_for_code(code) or imm.get("standard_title_tr") or "").strip()
    cause_tr = str(imm.get("standard_title_tr") or cause_tr).strip()
    body = immediate_cause_sentence(strip_barsel_answer_prefix(cause_tr))
    return strip_hse_codes(body)


def _collect_agent_why_steps(raw_branch: Dict[str, Any]) -> List[Dict[str, Any]]:
    whys = (
        raw_branch.get("why_chain")
        or raw_branch.get("whys")
        or raw_branch.get("questions_and_answers")
        or []
    )
    if not isinstance(whys, list):
        return []
    out: List[Dict[str, Any]] = []
    for i, w in enumerate(whys):
        if not isinstance(w, dict):
            continue
        level = w.get("level", w.get("number", i + 1))
        try:
            level = int(level)
        except (TypeError, ValueError):
            level = i + 1
        out.append({**w, "level": level})
    out.sort(key=lambda x: int(x.get("level") or 0))
    return out


def build_pinned_why_chain(
    raw_branch: Dict[str, Any],
    shared_event_question: str,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Agent dalından rapor why_chain (5 satır): W1 pin + W2–W5 agent.
    """
    immediate = raw_branch.get("immediate_cause") or {}
    agent_steps = _collect_agent_why_steps(raw_branch)
    by_level: Dict[int, Dict[str, Any]] = {}
    for step in agent_steps:
        lvl = int(step.get("level") or 0)
        if 1 <= lvl <= 5:
            by_level[lvl] = step

    warnings: List[str] = []
    branch_no = raw_branch.get("branch_number", "?")

    chain: List[Dict[str, Any]] = [
        {
            "number": 1,
            "question": strip_hse_codes(shared_event_question),
            "answer": immediate_cause_report_answer(immediate),
        }
    ]

    for level in range(2, 6):
        step = by_level.get(level)
        if step:
            q = strip_hse_codes(str(step.get("question_tr") or step.get("question") or ""))
            a = strip_hse_codes(
                strip_barsel_answer_prefix(str(step.get("answer_tr") or step.get("answer") or ""))
            )
        else:
            q, a = "", ""
            warnings.append(f"dal {branch_no}: NEDEN {level} agent zincirinde eksik")
        chain.append({"number": level, "question": q, "answer": a})

    if len(chain) != 5:
        warnings.append(f"dal {branch_no}: why_chain uzunluğu {len(chain)} (beklenen 5)")

    return chain, warnings


def validate_report_why_chains(branches: List[Dict[str, Any]]) -> List[str]:
    """Render öncesi doğrulama — eksik zincir uyarıları."""
    issues: List[str] = []
    for br in branches or []:
        bn = br.get("branch_number", "?")
        wc = br.get("why_chain") or []
        if len(wc) != 5:
            issues.append(f"dal {bn}: {len(wc)} NEDEN satırı (5 olmalı)")
            continue
        w1_qs = {str(w.get("question") or "").strip() for w in wc if int(w.get("number") or 0) == 1}
        if len(branches) > 1 and len(w1_qs) > 1:
            issues.append(f"dal {bn}: NEDEN 1 sorusu diğer dallardan farklı olabilir")
        if not str(wc[0].get("answer") or "").strip():
            issues.append(f"dal {bn}: NEDEN 1 cevabı (A/B doğrudan neden) boş")
        for w in wc:
            n = int(w.get("number") or 0)
            if n >= 2 and not str(w.get("question") or "").strip():
                issues.append(f"dal {bn}: NEDEN {n} sorusu boş")
    if len(branches) > 1:
        first_questions = []
        for br in branches:
            wc = br.get("why_chain") or []
            if wc:
                first_questions.append(str(wc[0].get("question") or "").strip())
        if first_questions and len(set(first_questions)) > 1:
            issues.append("NEDEN 1 olay sorusu tüm dallarda aynı değil")
    return issues


def pin_agent_why_chains_to_report(content: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge sonrası: branches[].why_chain ve kök neden alanlarını agent verisine sabitle.
    """
    if not isinstance(content, dict):
        return content
    raw_branches = _raw_analysis_branches(raw_data)
    if not raw_branches:
        return content

    incident_summary = _incident_summary_from_raw(raw_data)
    shared_q = build_shared_event_question(incident_summary)
    out = copy.deepcopy(content)
    report_branches: List[Dict[str, Any]] = list(out.get("branches") or [])

    all_warnings: List[str] = []
    pinned: List[Dict[str, Any]] = []

    for i, raw_br in enumerate(raw_branches[:8]):
        chain, warns = build_pinned_why_chain(raw_br, shared_q)
        all_warnings.extend(warns)

        if i < len(report_branches):
            rb = copy.deepcopy(report_branches[i])
        else:
            rb = {"branch_number": raw_br.get("branch_number", i + 1)}

        rb["why_chain"] = chain

        imm = raw_br.get("immediate_cause") or {}
        if imm:
            rb["direct_cause"] = immediate_cause_report_answer(imm)

        root = raw_br.get("root_cause") or {}
        if isinstance(root, dict) and root:
            rc_title = strip_hse_codes(
                str(root.get("cause_tr") or root.get("standard_title_tr") or "")
            )
            rc_detail = strip_hse_codes(
                str(root.get("explanation_tr") or root.get("explanation") or rc_title)
            )
            if rc_title:
                rb["root_cause_title"] = rc_title
            if rc_detail:
                rb["root_cause_detail"] = rc_detail

        pinned.append(rb)

    if pinned:
        out["branches"] = pinned

    validation = validate_report_why_chains(out.get("branches") or [])
    all_warnings.extend(validation)
    for msg in all_warnings:
        print(f"  ⚠️  [why_chain pin] {msg}")

    return out
