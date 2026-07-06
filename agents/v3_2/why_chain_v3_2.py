"""
V3.2 WhyChain — olay-zarar W1 + A/B cevap + W2–W5 → C/D.

Akış (her kritik faktör / dal):
  NEDEN 1 — Ortak olay sorusu (tüm dallarda aynı) → cevap: dalın A/B mekanizması
  NEDEN 2 — W1 cevabına neden (doğrudan neden alt mekanizma)
  NEDEN 3–5 — LLM zincir, branch_angle ile C/D kök nedene
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import dspy

try:
    from agents.rootcause_agent_v3_1 import (
        WHY_QUESTION_MAX_WORDS,
        WhyChain,
        WhyStepModel,
        _try_snap_to_taxonomy,
        _validate_model_dict,
        _why1_question_seed,
    )
    from agents.why_chain_quality import (
        answer_repeats_previous,
        build_direct_cause_why2_question,
        demote_solution_to_cause,
        derive_root_cause_from_why5,
        enforce_short_why_question,
        format_barsel_why_answer,
        is_solution_language,
        pick_non_forbidden_code,
        question_repeats_answer,
        resolve_why_taxonomy_code,
        score_chain_quality,
        strip_hse_codes,
    )
except ImportError:
    from ..rootcause_agent_v3_1 import (
        WHY_QUESTION_MAX_WORDS,
        WhyChain,
        WhyStepModel,
        _try_snap_to_taxonomy,
        _validate_model_dict,
        _why1_question_seed,
    )
    from ..why_chain_quality import (
        answer_repeats_previous,
        build_direct_cause_why2_question,
        demote_solution_to_cause,
        derive_root_cause_from_why5,
        enforce_short_why_question,
        format_barsel_why_answer,
        is_solution_language,
        pick_non_forbidden_code,
        question_repeats_answer,
        resolve_why_taxonomy_code,
        score_chain_quality,
        strip_hse_codes,
    )

from .why_chain_quality_v3_2 import (
    build_trainset_why1_question,
    immediate_cause_ab_answer,
)

try:
    from pydantic import ValidationError
except ImportError:
    ValidationError = Exception  # type: ignore[misc, assignment]


class IncidentWhy1Question(dspy.Signature):
    """Olay özetinden zarar/yaralanma merkezli ilk Why sorusu."""

    incident_summary = dspy.InputField(desc="Olay özeti")
    question = dspy.OutputField(
        desc=(
            "Tek Türkçe cümle, 'Neden ...?' ile bitmeli, en fazla 15 kelime. "
            "Olayın zararlı sonucunu sor (yaralanma, düşme, maruziyet). "
            "Montaj/faaliyet/operasyon cümlesi SORMA. "
            "Örnek: 'Neden Garcia 3,8 metre yükseklikten düşerek ağır yaralandı?' "
            "YANLIŞ: 'Neden segment strand halat montaj meydana geldi?'"
        )
    )


class WhyChainV32(WhyChain):
    """
    V3.2 5-Why — olay merceği + A/B → C/D.

    W1 sorusu tüm dallarda paylaşılır (shared_why1_question_cache).
    W1 cevabı dal başına immediate_cause / BARSEL A-B.
    """

    def __init__(
        self,
        enable_diversity_check: bool = True,
        *,
        use_chain_of_thought: bool = True,
    ):
        super().__init__(
            enable_diversity_check=enable_diversity_check,
            use_chain_of_thought=use_chain_of_thought,
        )
        _predict = dspy.ChainOfThought if use_chain_of_thought else dspy.Predict
        self._incident_why1 = _predict(IncidentWhy1Question)
        self.shared_why1_question_cache: Optional[str] = None

    def reset_shared_why1_cache(self) -> None:
        self.shared_why1_question_cache = None

    def get_shared_why1_question(self) -> Optional[str]:
        return self.shared_why1_question_cache

    def _resolve_why1_question(
        self,
        incident_summary: str,
        immediate_cause: Dict,
        shared_why1_question: Optional[str],
    ) -> str:
        if shared_why1_question:
            return shared_why1_question
        if self.shared_why1_question_cache:
            return self.shared_why1_question_cache
        q = build_trainset_why1_question(
            incident_summary,
            immediate_cause,
            dspy_predict=self._incident_why1,
        )
        self.shared_why1_question_cache = q
        return q

    def forward(  # noqa: PLR0912, PLR0915 — v3_1 parity
        self,
        incident_summary: str,
        immediate_cause: Dict,
        taxonomy_c: str,
        taxonomy_d: str,
        previous_why_answers: List[str] = None,
        probe_answers_by_level: Optional[Dict[int, List[Dict]]] = None,
        forbidden_root_codes: Optional[List[str]] = None,
        branch_angle: str = "",
        affirmed_root_codes: Optional[List[str]] = None,
        affirmed_probe_texts: Optional[List[str]] = None,
        shared_why1_question: Optional[str] = None,
        barsel_retriever: Any = None,
    ) -> Dict:
        if previous_why_answers is None:
            previous_why_answers = []
        forbidden_root_codes = forbidden_root_codes or []
        affirmed_root_codes = [
            str(c).strip().upper() for c in (affirmed_root_codes or []) if str(c).strip()
        ]
        affirmed_probe_texts = [t for t in (affirmed_probe_texts or []) if str(t).strip()]
        taxonomy_cd_blob = (taxonomy_c or "") + "\n" + (taxonomy_d or "")

        chain: List[Dict] = []
        current_answer_raw = immediate_cause.get("cause_tr", "")
        previous_question_raw = ""
        all_answers_in_chain: List[str] = []

        for level in range(1, 6):
            if level == 1:
                question_raw = self._resolve_why1_question(
                    incident_summary,
                    immediate_cause,
                    shared_why1_question,
                )
                answer_raw, imm_code = immediate_cause_ab_answer(
                    immediate_cause,
                    retriever=barsel_retriever,
                )
                answer_display = strip_hse_codes(demote_solution_to_cause(answer_raw))
                step_payload = {
                    "level": level,
                    "question_tr": strip_hse_codes(question_raw),
                    "answer_tr": answer_display,
                    "code": imm_code,
                }
                try:
                    step_data = _validate_model_dict(WhyStepModel, step_payload)
                except ValidationError:
                    step_data = step_payload
                chain.append(step_data)
                all_answers_in_chain.append(answer_raw)
                current_answer_raw = answer_raw
                previous_question_raw = question_raw
                continue

            if level == 2:
                # W2: A/B cevabına (W1 mekanizması) neden — V3.1 klasik adım
                imm_for_w2 = {**immediate_cause, "cause_tr": current_answer_raw}
                question_raw = build_direct_cause_why2_question(imm_for_w2)
            else:
                previous_for_question = (
                    f"Önceki soru: {previous_question_raw}\n"
                    f"Önceki cevap: {current_answer_raw}\n\n"
                    f"{_why1_question_seed(incident_summary, immediate_cause)}"
                )
                if branch_angle:
                    previous_for_question += f"\n\nDAL ODAĞI: {branch_angle}"
                level_label = f"Why-{level} — alt neden (max {WHY_QUESTION_MAX_WORDS} kelime)"
                question_result = self.why_question(
                    incident_summary=incident_summary,
                    previous_answer=previous_for_question,
                    chain_level=level_label,
                )
                question_raw = enforce_short_why_question((question_result.question or "").strip())
                if question_repeats_answer(current_answer_raw, question_raw):
                    question_result = self.why_question(
                        incident_summary=incident_summary,
                        previous_answer=previous_for_question
                        + "\n\nUYARI: Önceki cevabı TEKRARLAMA; bir alt organizasyonel/teknik nedeni sor.",
                        chain_level=level_label,
                    )
                    question_raw = enforce_short_why_question((question_result.question or "").strip())

            question_display = strip_hse_codes(question_raw)

            taxonomy = taxonomy_c if level >= 3 else ""
            if level >= 4:
                taxonomy = (taxonomy + "\n" + taxonomy_d).strip()
            if forbidden_root_codes and level >= 4:
                taxonomy += (
                    "\n\nYASAK KÖK KODLAR (bu dallarda kullanma): "
                    + ", ".join(forbidden_root_codes)
                )
            if affirmed_root_codes and level >= 4:
                allowed = [c for c in affirmed_root_codes if c not in forbidden_root_codes]
                if allowed:
                    taxonomy += (
                        "\n\nTERCİH EDİLEN KÖK KODLAR (olaya uygunluğu kullanıcı tarafından onaylandı, "
                        "uygunsa bunları seç): " + ", ".join(allowed)
                    )
            if level >= 4:
                taxonomy += (
                    "\n\nBAND SEÇİMİ: Her dalı D (organizasyonel) bandına bağlama. "
                    "Kanıt kişisel yetkinlik, beceri uygulaması, yorgunluk, muhakeme/karar verme "
                    "veya davranışsal şartlanma gösteriyorsa C bandından kod seç."
                )

            probe_level = level - 1
            incident_ctx = (
                f"Why-{level}: Bir önceki cevabın ALT nedeni. Çözüm önerisi yazma.\n\n"
                + incident_summary
            )
            probe_ctx = self._probe_context_for_level(probe_level, probe_answers_by_level)
            if branch_angle and level >= 3:
                incident_ctx += f"\n\nDAL ODAĞI: {branch_angle}"
            if probe_ctx:
                incident_ctx += "\n\n" + probe_ctx

            answer_raw = ""
            definition_code = ""
            code = ""
            for prow in (probe_answers_by_level or {}).get(probe_level) or []:
                ans_text = str(
                    (prow or {}).get("answer")
                    or (prow or {}).get("label")
                    or (prow or {}).get("value")
                    or ""
                )
                try:
                    from agents.barsel_taxonomy import (
                        build_definition_based_why_answer,
                        probe_answer_affirms_fit,
                        taxonomy_item_for_code,
                    )
                except ImportError:
                    from ..barsel_taxonomy import (
                        build_definition_based_why_answer,
                        probe_answer_affirms_fit,
                        taxonomy_item_for_code,
                    )
                if not probe_answer_affirms_fit(ans_text):
                    continue
                pcode = str(
                    (prow or {}).get("hsg_hint")
                    or (prow or {}).get("immediate_code")
                    or (prow or {}).get("code")
                    or ""
                ).strip().upper()
                item = taxonomy_item_for_code(pcode, retriever=barsel_retriever)
                if item is None:
                    continue
                def_ans = build_definition_based_why_answer(
                    item,
                    question=question_raw,
                    incident_hint=incident_summary[:400],
                )
                if def_ans:
                    answer_raw = def_ans
                    definition_code = item.code
                    break

            answer_result = None
            if not answer_raw:
                answer_result = self.why_answer(
                    question=question_raw,
                    incident_context=incident_ctx,
                    taxonomy_codes=taxonomy,
                )
                answer_raw = demote_solution_to_cause((answer_result.answer or "").strip())

            if is_solution_language(answer_raw):
                answer_raw = demote_solution_to_cause(
                    answer_raw + " (olayda bu uygulama eksikti)"
                )
            llm_code = ""
            if answer_result is not None:
                llm_code = str(getattr(answer_result, "hsg245_code", "") or "")
            code = pick_non_forbidden_code(
                definition_code or llm_code,
                answer_raw,
                taxonomy_cd_blob,
                forbidden_root_codes if level >= 5 else [],
            )
            if not code:
                code = resolve_why_taxonomy_code("", answer_raw, taxonomy_cd_blob)

            if self.enable_diversity and level >= 2:
                combined_prev = previous_why_answers + all_answers_in_chain
                prev_in_chain = chain[-1]["answer_tr"] if chain else ""
                if prev_in_chain and answer_repeats_previous(prev_in_chain, answer_raw):
                    diverse_check = self.diversity_checker(
                        question=question_raw,
                        previous_answers=combined_prev + [prev_in_chain],
                    )
                    if diverse_check:
                        answer_raw = demote_solution_to_cause(diverse_check)

            answer_display = format_barsel_why_answer(code, strip_hse_codes(answer_raw))
            step_payload = {
                "level": level,
                "question_tr": question_display,
                "answer_tr": answer_display,
                "code": code,
            }
            try:
                step_data = _validate_model_dict(WhyStepModel, step_payload)
            except ValidationError:
                step_data = step_payload

            chain.append(step_data)
            all_answers_in_chain.append(answer_raw)
            current_answer_raw = answer_raw
            previous_question_raw = question_raw

        validation = self.validator(
            cause=chain[-1]["answer_tr"],
            code=chain[-1]["code"],
        )
        from agents.rootcause_agent_v3_1 import _safe_float

        conf = _safe_float(getattr(validation, "confidence", None), default=0.8)
        affirmed_probs: List[str] = []
        root_probe_rows = list((probe_answers_by_level or {}).get(4) or []) + list(
            (probe_answers_by_level or {}).get(5) or []
        )
        for prow in root_probe_rows:
            ans_text = str(
                (prow or {}).get("answer")
                or (prow or {}).get("label")
                or (prow or {}).get("value")
                or ""
            )
            try:
                from agents.barsel_taxonomy import probe_answer_affirms_fit
            except ImportError:
                from ..barsel_taxonomy import probe_answer_affirms_fit
            if probe_answer_affirms_fit(ans_text):
                qtxt = str((prow or {}).get("question") or "").strip()
                if qtxt:
                    affirmed_probs.append(qtxt)

        for txt in affirmed_probe_texts:
            t = str(txt).strip()
            if t and t not in affirmed_probs:
                affirmed_probs.append(t)

        root_cause_data = derive_root_cause_from_why5(
            chain[-1],
            snap_fn=lambda c, a, e, **kw: _try_snap_to_taxonomy(
                c, a, e, family=kw.get("family", "cd")
            ),
            incident_hint=incident_summary[:500],
            affirmed_typical_problems=affirmed_probs or None,
        )
        root_cause_data["confidence"] = conf
        if not root_cause_data.get("category_type"):
            root_cause_data["category_type"] = getattr(validation, "category", None) or "ORGANİZASYONEL"

        final_code = root_cause_data.get("code")
        if final_code:
            chain = list(chain)
            chain[-1] = {**chain[-1], "code": final_code}

        try:
            from agents.rootcause_agent_v3_1 import RootCauseModel

            root_cause_data = _validate_model_dict(RootCauseModel, root_cause_data)
        except ValidationError:
            pass

        return {
            "whys": chain,
            "root_cause": root_cause_data,
            "chain_quality": score_chain_quality(chain),
            "shared_why1_question": self.shared_why1_question_cache,
        }
