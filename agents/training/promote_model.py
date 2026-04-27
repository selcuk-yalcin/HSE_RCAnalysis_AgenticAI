"""
Promote/rollback-safe model version controls for RCA artifacts.

Kullanım:
  python agents/training/promote_model.py --new-version why_chain_v7 --reason "validated on devset"
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


def _load_registry(path: Path) -> dict:
    if not path.exists():
        return {"active_version": "", "history": []}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save_registry(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Promote RCA model version with rollback metadata")
    parser.add_argument("--new-version", required=True, help="Yeni aktif model/artifact versiyonu")
    parser.add_argument("--reason", default="", help="Promosyon nedeni")
    parser.add_argument("--registry-path", default="agents/training/compiled/promotion_registry.json")
    args = parser.parse_args()

    registry_path = Path(args.registry_path)
    registry = _load_registry(registry_path)
    previous = registry.get("active_version", "")
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    record = {
        "timestamp": now,
        "new_version": args.new_version,
        "previous_version": previous,
        "reason": args.reason,
        "rollback_target": previous,
    }
    registry["active_version"] = args.new_version
    registry.setdefault("history", []).append(record)
    _save_registry(registry_path, registry)

    print(f"✅ Active version: {args.new_version}")
    print(f"↩️ Rollback target: {previous or '(none)'}")


if __name__ == "__main__":
    main()

