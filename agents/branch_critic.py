"""
Branch Critic Agent - 5-Why Dalları Arası Tekrar Önleme
========================================================
Amaç:
  V3.1 RootCauseAgent tarafından üretilen N adet dal (her biri 5-Why zinciri +
  bir kök neden) arasında tekrarları tespit edip, gerektiğinde dalları
  yeniden üretmek için bir critic katmanı sağlar.

Çalışma Mantığı:
  1. Deterministik dedup:
     - Aynı root_cause kodu farklı dallarda kullanılıyorsa çakışma
     - Why cevapları arası Jaccard benzerliği > eşik ise çakışma
     - Tüm dalın "fingerprint"i (kod + cevaplar) Jaccard ile karşılaştırılır
  2. LLM critic (DSPy):
     - Çakışan dallar için "neden tekrar?" gerekçesi
     - Hangi açıdan yeniden ele alınmalı önerisi
  3. Regenerate (DSPy):
     - Çakışan dalın kök nedenini yeni bir taksonomi açısından
       (insan/sistem/donanım/yönetim) yeniden ele alır
     - Why zincirinin son halkasını ve root_cause'u günceller

Çıktı:
  {
    "critique_report": [...],      # her çift için karar
    "fixed_branches": [...],        # düzeltilmiş final dallar
    "diversity_score": 0..1,        # genel çeşitlilik skoru
    "regenerated_count": int
  }
"""

from typing import Dict, List, Tuple, Optional
import dspy

try:
    from .json_parser import (
        extract_json_from_response,
        extract_json_array_from_response,
    )
except ImportError:
    try:
        from json_parser import (
            extract_json_from_response,
            extract_json_array_from_response,
        )
    except ImportError:
        from agents.json_parser import (
            extract_json_from_response,
            extract_json_array_from_response,
        )


def _strip_code_fence(text: str) -> str:
    """LLM çıktısındaki ```json ... ``` çitini soyar."""
    if not isinstance(text, str):
        return text
    s = text.strip()
    if s.startswith("```"):
        first_nl = s.find("\n")
        if first_nl != -1:
            s = s[first_nl + 1:]
        if s.rstrip().endswith("```"):
            s = s.rstrip()[: -3].rstrip()
    return s.strip()


# ============================================================================
# DSPy SIGNATURES
# ============================================================================

class BranchDuplicationCritic(dspy.Signature):
    """İki kök nedenin gerçekten tekrar olup olmadığını değerlendir.

    Sadece kelime benzerliği değil; aynı sistemik zaafa mı işaret ediyor
    kararını ver. Farklı seviyelerde (kişisel vs örgütsel) olabilirler.
    """
    incident_summary = dspy.InputField(desc="Olay özeti")
    branch_a_summary = dspy.InputField(
        desc="A dalı özeti: doğrudan neden + 5 Why cevapları + kök neden"
    )
    branch_b_summary = dspy.InputField(
        desc="B dalı özeti: doğrudan neden + 5 Why cevapları + kök neden"
    )

    is_duplicate = dspy.OutputField(
        desc="'true' veya 'false'. Aynı sistemik kök nedene mi işaret ediyorlar?"
    )
    rationale_tr = dspy.OutputField(
        desc="Kararın kısa gerekçesi (Türkçe, 1-2 cümle)"
    )
    suggested_angle = dspy.OutputField(
        desc="Eğer tekrar ise B dalı hangi farklı açıdan ele alınmalı? "
             "(ör: 'denetim eksikliği', 'tasarım hatası', 'eğitim sistemi'). "
             "Tekrar değilse 'NONE'."
    )


class BranchRegenerator(dspy.Signature):
    """Tekrar eden bir dalı yeni bir açıdan yeniden ele al.

    Aynı doğrudan nedeni koru, ancak 5-Why zincirini ve kök nedeni
    `new_angle` perspektifinden yeniden üret. Diğer dallarda
    geçen kök nedenleri (forbidden_codes / forbidden_summaries)
    tekrarlama.
    """
    incident_summary = dspy.InputField(desc="Olay özeti")
    immediate_cause_tr = dspy.InputField(desc="Doğrudan neden (değişmeyecek)")
    forbidden_codes = dspy.InputField(
        desc="Diğer dallarda kullanılan HSG245 kodları (kullanma)"
    )
    forbidden_summaries = dspy.InputField(
        desc="Diğer dallarda çıkan kök neden cümleleri (tekrarlama)"
    )
    new_angle = dspy.InputField(
        desc="Bu dalı ele alacağın yeni açı (ör: 'denetim ve gözetim sistemi')"
    )
    taxonomy_cd = dspy.InputField(
        desc="HSG245 C ve D kategorileri (geçerli kodlar)"
    )

    new_why_chain = dspy.OutputField(
        desc="JSON: 5 elemanlı liste, her biri "
             "{level:int, question_tr, answer_tr, code}"
    )
    new_root_cause = dspy.OutputField(
        desc="JSON: {code, cause_tr, category_type, explanation_tr, confidence}"
    )


# ============================================================================
# CORE CRITIC AGENT
# ============================================================================

class BranchCriticAgent:
    """Dallar arası tekrar tespiti + opsiyonel LLM critic + regenerate.

    Kullanım:
        critic = BranchCriticAgent(taxonomy_cd_text="...")
        report = critic.review(branches, incident_summary)
        # branches yerinde güncellenir; report ek meta veridir.
    """

    def __init__(
        self,
        taxonomy_cd_text: str = "",
        jaccard_threshold: float = 0.55,
        use_llm_critic: bool = True,
        max_regenerations: int = 3,
    ):
        self.taxonomy_cd_text = taxonomy_cd_text
        self.jaccard_threshold = jaccard_threshold
        self.use_llm_critic = use_llm_critic
        self.max_regenerations = max_regenerations

        if use_llm_critic:
            self.critic = dspy.ChainOfThought(BranchDuplicationCritic)
            self.regenerator = dspy.ChainOfThought(BranchRegenerator)
        else:
            self.critic = None
            self.regenerator = None

    # ---------------------------------------------------------------- helpers

    @staticmethod
    def _tokens(text: str) -> set:
        if not text:
            return set()
        cleaned = "".join(
            ch.lower() if ch.isalnum() or ch.isspace() else " "
            for ch in text
        )
        return {t for t in cleaned.split() if len(t) >= 4}

    @classmethod
    def _jaccard(cls, a: str, b: str) -> float:
        ta, tb = cls._tokens(a), cls._tokens(b)
        if not ta or not tb:
            return 0.0
        inter = len(ta & tb)
        union = len(ta | tb)
        return inter / union if union else 0.0

    @staticmethod
    def _branch_summary(branch: Dict) -> str:
        immediate = branch.get("immediate_cause", {})
        whys = branch.get("why_chain", [])
        root = branch.get("root_cause", {})
        lines = [
            f"Doğrudan neden [{immediate.get('code','?')}]: "
            f"{immediate.get('cause_tr','')}",
        ]
        for w in whys:
            lines.append(
                f"Why-{w.get('level','?')} [{w.get('code','?')}]: "
                f"{w.get('answer_tr','')}"
            )
        lines.append(
            f"Kök neden [{root.get('code','?')}]: {root.get('cause_tr','')}"
        )
        return "\n".join(lines)

    @staticmethod
    def _branch_fingerprint(branch: Dict) -> str:
        whys = branch.get("why_chain", [])
        root = branch.get("root_cause", {})
        parts = [w.get("answer_tr", "") for w in whys]
        parts.append(root.get("cause_tr", ""))
        return " ".join(parts)

    # --------------------------------------------------------- duplicate find

    def _find_conflicts(self, branches: List[Dict]) -> List[Tuple[int, int, Dict]]:
        """Çakışan dal çiftlerini döner: [(i, j, info), ...].

        Önce deterministik (kod eşitliği veya yüksek Jaccard), sonra
        LLM critic ile teyit.
        """
        conflicts: List[Tuple[int, int, Dict]] = []
        n = len(branches)
        for i in range(n):
            for j in range(i + 1, n):
                bi, bj = branches[i], branches[j]
                root_i = bi.get("root_cause", {}) or {}
                root_j = bj.get("root_cause", {}) or {}

                same_code = (
                    root_i.get("code")
                    and root_j.get("code")
                    and root_i.get("code") == root_j.get("code")
                )
                fp_i = self._branch_fingerprint(bi)
                fp_j = self._branch_fingerprint(bj)
                root_sim = self._jaccard(
                    root_i.get("cause_tr", ""), root_j.get("cause_tr", "")
                )
                fp_sim = self._jaccard(fp_i, fp_j)

                deterministic_dup = (
                    same_code
                    or root_sim >= self.jaccard_threshold
                    or fp_sim >= self.jaccard_threshold
                )

                info = {
                    "same_code": bool(same_code),
                    "root_jaccard": round(root_sim, 3),
                    "fingerprint_jaccard": round(fp_sim, 3),
                    "deterministic_duplicate": bool(deterministic_dup),
                }
                if deterministic_dup:
                    conflicts.append((i, j, info))

        return conflicts

    # -------------------------------------------------------------- llm step

    def _llm_judge(
        self,
        incident_summary: str,
        branch_a: Dict,
        branch_b: Dict,
    ) -> Dict:
        """LLM critic'i çağır. Hata durumunda güvenli default döner."""
        result = {
            "is_duplicate": True,
            "rationale_tr": "Deterministik benzerlik eşiği aşıldı.",
            "suggested_angle": "denetim ve gözetim sistemi",
        }
        if not self.use_llm_critic or self.critic is None:
            return result
        try:
            out = self.critic(
                incident_summary=incident_summary,
                branch_a_summary=self._branch_summary(branch_a),
                branch_b_summary=self._branch_summary(branch_b),
            )
            is_dup_raw = str(getattr(out, "is_duplicate", "true")).strip().lower()
            result["is_duplicate"] = is_dup_raw.startswith("t") or is_dup_raw == "1"
            result["rationale_tr"] = (
                getattr(out, "rationale_tr", "") or result["rationale_tr"]
            )
            angle = (getattr(out, "suggested_angle", "") or "").strip()
            if angle and angle.upper() != "NONE":
                result["suggested_angle"] = angle
        except Exception as e:  # noqa: BLE001
            print(f"⚠️  BranchCritic LLM hata: {type(e).__name__}: {e}")
        return result

    # ----------------------------------------------------------- regenerate

    def _regenerate(
        self,
        incident_summary: str,
        branch: Dict,
        forbidden_codes: List[str],
        forbidden_summaries: List[str],
        new_angle: str,
    ) -> Optional[Dict]:
        """Bir dalı yeni açıdan üret. Başarısızsa None döner."""
        if not self.use_llm_critic or self.regenerator is None:
            return None
        try:
            out = self.regenerator(
                incident_summary=incident_summary,
                immediate_cause_tr=branch.get("immediate_cause", {}).get(
                    "cause_tr", ""
                ),
                forbidden_codes=", ".join([c for c in forbidden_codes if c]),
                forbidden_summaries="\n".join(
                    [s for s in forbidden_summaries if s]
                ),
                new_angle=new_angle,
                taxonomy_cd=self.taxonomy_cd_text or "C ve D kategorileri",
            )
            new_chain_raw = _strip_code_fence(
                getattr(out, "new_why_chain", "") or ""
            )
            new_root_raw = _strip_code_fence(
                getattr(out, "new_root_cause", "") or ""
            )

            new_chain = extract_json_array_from_response(
                new_chain_raw, default=[]
            )
            if not isinstance(new_chain, list) or not new_chain:
                print(
                    "⚠️  BranchCritic regenerate: new_why_chain parse boş, "
                    f"önizleme: {new_chain_raw[:200]}"
                )
                return None

            new_root = extract_json_from_response(new_root_raw, default={})
            if not isinstance(new_root, dict) or not new_root:
                print(
                    "⚠️  BranchCritic regenerate: new_root_cause parse boş, "
                    f"önizleme: {new_root_raw[:200]}"
                )
                return None

            return {"why_chain": new_chain, "root_cause": new_root}
        except Exception as e:  # noqa: BLE001
            print(f"⚠️  BranchCritic regenerate hata: {type(e).__name__}: {e}")
            return None

    # --------------------------------------------------------------- public

    def review(
        self,
        branches: List[Dict],
        incident_summary: str,
    ) -> Dict:
        """Tekrarları bul, gerekirse dalları yeniden üret.

        `branches` listesi yerinde güncellenir.
        """
        report: Dict = {
            "checked_pairs": 0,
            "conflicts": [],
            "regenerated_branches": [],
            "diversity_score": 1.0,
            "regenerated_count": 0,
        }

        if not branches or len(branches) < 2:
            return report

        n = len(branches)
        pair_count = n * (n - 1) // 2
        report["checked_pairs"] = pair_count

        conflicts = self._find_conflicts(branches)
        regenerated_indices: set = set()
        regenerations = 0

        for i, j, info in conflicts:
            judge = self._llm_judge(incident_summary, branches[i], branches[j])
            entry = {
                "pair": (i + 1, j + 1),
                "metrics": info,
                "llm_is_duplicate": judge["is_duplicate"],
                "rationale_tr": judge["rationale_tr"],
                "suggested_angle": judge["suggested_angle"],
                "action": "kept",
            }

            if judge["is_duplicate"] and regenerations < self.max_regenerations:
                target = j if j not in regenerated_indices else i
                if target in regenerated_indices:
                    entry["action"] = "skipped (already_regenerated)"
                    report["conflicts"].append(entry)
                    continue

                # Yasaklı kod ve cümleleri topla (diğer tüm dallar)
                forbidden_codes = [
                    (b.get("root_cause", {}) or {}).get("code", "")
                    for k, b in enumerate(branches)
                    if k != target
                ]
                forbidden_summaries = [
                    (b.get("root_cause", {}) or {}).get("cause_tr", "")
                    for k, b in enumerate(branches)
                    if k != target
                ]

                new_payload = self._regenerate(
                    incident_summary=incident_summary,
                    branch=branches[target],
                    forbidden_codes=forbidden_codes,
                    forbidden_summaries=forbidden_summaries,
                    new_angle=judge["suggested_angle"],
                )
                if new_payload:
                    branches[target]["why_chain"] = new_payload["why_chain"]
                    branches[target]["root_cause"] = new_payload["root_cause"]
                    branches[target]["regenerated_by_critic"] = True
                    branches[target]["regeneration_angle"] = judge[
                        "suggested_angle"
                    ]
                    regenerated_indices.add(target)
                    regenerations += 1
                    entry["action"] = f"regenerated branch #{target + 1}"
                    report["regenerated_branches"].append(target + 1)
                else:
                    entry["action"] = "regeneration_failed"

            report["conflicts"].append(entry)

        report["regenerated_count"] = regenerations

        # Diversity score: tekrar oranına göre 1 - (conflicts/pairs)
        if pair_count:
            confirmed = sum(
                1 for c in report["conflicts"] if c["llm_is_duplicate"]
            )
            report["diversity_score"] = round(
                max(0.0, 1.0 - confirmed / pair_count), 3
            )

        return report


__all__ = [
    "BranchCriticAgent",
    "BranchDuplicationCritic",
    "BranchRegenerator",
]
