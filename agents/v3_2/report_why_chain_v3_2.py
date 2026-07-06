"""
V3.2 rapor 5-Why pin — trainset W1 + agent why_chain (W2–W5).

skillbased_docx_agent LLM merge sonrası agent part3_rca verisine sabitler.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Tuple

try:
    from agents.report_text_sanitize import strip_hse_codes
    from agents.why_chain_quality import strip_barsel_answer_prefix
except ImportError:
    from ..report_text_sanitize import strip_hse_codes
    from ..why_chain_quality import strip_barsel_answer_prefix

try:
    from agents.v3_2.why_chain_quality_v3_2 import (
        build_trainset_why1_question_heuristic,
        immediate_cause_ab_answer,
    )
except ImportError:
    from .why_chain_quality_v3_2 import (
        build_trainset_why1_question_heuristic,
        immediate_cause_ab_answer,
    )


def build_shared_trainset_why1_question(
    incident_text: str,
    *,
    cached: str | None = None,
) -> str:
    """Tüm dallarda ortak NEDEN 1 (trainset tarzı)."""
    if cached:
        return cached
    return build_trainset_why1_question_heuristic(incident_text)


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


def immediate_cause_report_answer_v32(immediate: Dict[str, Any]) -> str:
    ans, _ = immediate_cause_ab_answer(immediate)
    return strip_hse_codes(ans)


def build_pinned_why_chain_v32(
    raw_branch: Dict[str, Any],
    shared_why1_question: str,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Agent dalından rapor why_chain (5 satır): trainset W1 pin + W2–W5 agent."""
    immediate = raw_branch.get("immediate_cause") or {}
    agent_steps = _collect_agent_why_steps(raw_branch)
    by_level: Dict[int, Dict[str, Any]] = {}
    for step in agent_steps:
        lvl = int(step.get("level") or 0)
        if 1 <= lvl <= 5:
            by_level[lvl] = step

    warnings: List[str] = []
    branch_no = raw_branch.get("branch_number", "?")
    w1_answer = immediate_cause_report_answer_v32(immediate)

    chain: List[Dict[str, Any]] = [
        {
            "number": 1,
            "question": strip_hse_codes(shared_why1_question),
            "answer": w1_answer,
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
    if not w1_answer.strip():
        warnings.append(f"dal {branch_no}: NEDEN 1 cevabı (A/B) boş")

    return chain, warnings


def validate_report_why_chains_v32(branches: List[Dict[str, Any]]) -> List[str]:
    issues: List[str] = []
    for br in branches or []:
        bn = br.get("branch_number", "?")
        wc = br.get("why_chain") or []
        if len(wc) != 5:
            issues.append(f"dal {bn}: {len(wc)} NEDEN satırı (5 olmalı)")
            continue
        if not str(wc[0].get("answer") or "").strip():
            issues.append(f"dal {bn}: NEDEN 1 cevabı (A/B) boş")
        for w in wc:
            n = int(w.get("number") or 0)
            if n >= 2 and not str(w.get("question") or "").strip():
                issues.append(f"dal {bn}: NEDEN {n} sorusu boş")
    if len(branches) > 1:
        first_q = []
        for br in branches:
            wc = br.get("why_chain") or []
            if wc:
                first_q.append(str(wc[0].get("question") or "").strip())
        if first_q and len(set(first_q)) > 1:
            issues.append("NEDEN 1 trainset sorusu tüm dallarda aynı değil")
    return issues


def pin_agent_why_chains_to_report_v32(
    content: Dict[str, Any],
    raw_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Merge sonrası branches[].why_chain → V3.2 agent verisi."""
    if not isinstance(content, dict):
        return content
    raw_branches = _raw_analysis_branches(raw_data)
    if not raw_branches:
        return content

    incident_summary = _incident_summary_from_raw(raw_data)
    shared_q = build_shared_trainset_why1_question(incident_summary)
    out = copy.deepcopy(content)
    report_branches: List[Dict[str, Any]] = list(out.get("branches") or [])
    all_warnings: List[str] = []
    pinned: List[Dict[str, Any]] = []

    for i, raw_br in enumerate(raw_branches[:8]):
        chain, warns = build_pinned_why_chain_v32(raw_br, shared_q)
        all_warnings.extend(warns)

        if i < len(report_branches):
            rb = copy.deepcopy(report_branches[i])
        else:
            rb = {"branch_number": raw_br.get("branch_number", i + 1)}

        rb["why_chain"] = chain
        imm = raw_br.get("immediate_cause") or {}
        if imm:
            rb["direct_cause"] = immediate_cause_report_answer_v32(imm)

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

    all_warnings.extend(validate_report_why_chains_v32(out.get("branches") or []))
    for msg in all_warnings:
        print(f"  ⚠️  [why_chain pin v3.2] {msg}")

    return out
