"""
Optimize RCA WhyChain with DSPy MIPROv2.

Kullanım:
  python agents/training/optimize_rca.py --dataset-path outputs/hse_5why_train.jsonl
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _load_examples(path: str) -> List[Dict[str, Any]]:
    examples: List[Dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                examples.append(json.loads(line))
    return examples


def _split_train_val(examples: List[Dict[str, Any]], val_ratio: float = 0.15):
    n = len(examples)
    cut = max(1, int(n * (1 - val_ratio)))
    return examples[:cut], examples[cut:]


def _to_program_prediction_format(example: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "why_chain": example.get("why_chain", []),
        "root_cause": example.get("root_cause", ""),
    }


def _normalize_whychain_prediction(pred: Any) -> Dict[str, Any]:
    """Normalize WhyChain output to metric-compatible shape."""
    if isinstance(pred, dict):
        if "why_chain" in pred and "root_cause" in pred:
            return pred
        whys = pred.get("whys") or []
        chain = []
        for i, w in enumerate(whys):
            if not isinstance(w, dict):
                continue
            chain.append(
                {
                    "level": w.get("level", i + 1),
                    "question": w.get("question_tr") or w.get("question") or "",
                    "answer": w.get("answer_tr") or w.get("answer") or "",
                }
            )
        root = pred.get("root_cause")
        if isinstance(root, dict):
            root = root.get("cause_tr") or root.get("cause") or ""
        return {"why_chain": chain, "root_cause": root or ""}
    return {"why_chain": [], "root_cause": ""}


def main() -> None:
    parser = argparse.ArgumentParser(description="Optimize WhyChain with MIPROv2")
    parser.add_argument("--dataset-path", required=True, help="JSONL trainset path")
    parser.add_argument("--output-dir", default="agents/training/compiled", help="Compiled artifact output dir")
    parser.add_argument("--artifact-name", default="", help="Optional output file name")
    parser.add_argument("--num-trials", type=int, default=6, help="MIPROv2 trial count")
    parser.add_argument(
        "--allow-fallback",
        action="store_true",
        help="MIPROv2 unavailable ise baseline-only artifact üret.",
    )
    args = parser.parse_args()

    try:
        import dspy
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("dspy-ai gerekli: pip install dspy-ai") from exc
    dspy_compatible = hasattr(dspy, "MIPROv2") and hasattr(dspy, "Example")
    if not dspy_compatible and not args.allow_fallback:
        raise RuntimeError("Uyumlu DSPy sürümü bulunamadı (MIPROv2/Example eksik).")

    from agents.training.dspy_metrics import hse_5why_metric
    model = "unknown"

    examples = _load_examples(args.dataset_path)
    if len(examples) < 10:
        raise RuntimeError("MIPROv2 için en az 10 örnek önerilir.")

    train_raw, val_raw = _split_train_val(examples, val_ratio=0.15)
    trainset = train_raw
    valset = val_raw
    compiled = None
    mode = "fallback_baseline_only"

    if dspy_compatible:
        from agents.model_constants import resolve_openrouter_dspy_model
        from agents.rootcause_agent_v3_1 import WhyChain

        trainset = [
            dspy.Example(
                incident_summary=e.get("incident_description", ""),
                immediate_cause={
                    "code": "GEN.1",
                    "cause_tr": ((e.get("why_chain") or [{}])[0] or {}).get("answer", ""),
                },
                taxonomy_c="",
                taxonomy_d="",
                why_chain=e.get("why_chain", []),
                root_cause=e.get("root_cause", ""),
            ).with_inputs("incident_summary", "immediate_cause", "taxonomy_c", "taxonomy_d")
            for e in train_raw
        ]
        valset = [
            dspy.Example(
                incident_summary=e.get("incident_description", ""),
                immediate_cause={
                    "code": "GEN.1",
                    "cause_tr": ((e.get("why_chain") or [{}])[0] or {}).get("answer", ""),
                },
                taxonomy_c="",
                taxonomy_d="",
                why_chain=e.get("why_chain", []),
                root_cause=e.get("root_cause", ""),
            ).with_inputs("incident_summary", "immediate_cause", "taxonomy_c", "taxonomy_d")
            for e in val_raw
        ]

        model = resolve_openrouter_dspy_model()
        lm = dspy.LM(model=f"openrouter/{model}" if not model.startswith("openrouter/") else model)
        dspy.configure(lm=lm)

        metric_fn = lambda pred, *_args, **_kwargs: hse_5why_metric(_normalize_whychain_prediction(pred))
        optimizer = dspy.MIPROv2(metric=metric_fn, auto=None, num_candidates=6)
        program = WhyChain()
        compiled = optimizer.compile(
            program,
            trainset=trainset,
            valset=valset,
            num_trials=max(1, int(args.num_trials)),
            minibatch=True,
            minibatch_size=max(1, min(len(valset), 4)),
            minibatch_full_eval_steps=2,
        )
        mode = "mipro_v2_compile"

    # Baseline/optimized score: dataset üstünden yaklaşık hesap
    baseline_scores = [hse_5why_metric(_to_program_prediction_format(e)) for e in val_raw]
    baseline_avg = sum(baseline_scores) / max(1, len(baseline_scores))
    optimized_avg = baseline_avg  # Program-output eval burada lightweight tutuluyor

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    artifact_name = args.artifact_name or f"why_chain_compiled_{time.strftime('%Y%m%d_%H%M%S')}.json"
    artifact_path = out_dir / artifact_name

    summary = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dataset_path": args.dataset_path,
        "train_size": len(trainset),
        "val_size": len(valset),
        "model": model,
        "baseline_metric_avg": round(baseline_avg, 4),
        "optimized_metric_avg": round(optimized_avg, 4),
        "note": "optimized_metric_avg placeholder; full online eval should be run in CI pipeline.",
    }

    # Save compiled program with DSPy native save if available
    compiled_path = out_dir / artifact_name.replace(".json", ".dspy")
    if compiled is not None:
        try:
            compiled.save(str(compiled_path))
        except Exception:  # noqa: BLE001
            # Keep summary artifact even if DSPy save format fails in environment.
            pass

    summary["mode"] = mode
    summary["dspy_compatible"] = bool(dspy_compatible)
    with open(artifact_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"✅ Optimization summary: {artifact_path}")
    if compiled_path.exists():
        print(f"✅ Compiled program: {compiled_path}")


if __name__ == "__main__":
    main()

