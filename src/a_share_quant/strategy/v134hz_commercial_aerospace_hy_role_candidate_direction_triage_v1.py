from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134hy_commercial_aerospace_event_attention_role_candidate_audit_v1 import (
    V134HYCommercialAerospaceEventAttentionRoleCandidateAuditV1Analyzer,
)


@dataclass(slots=True)
class V134HZCommercialAerospaceHYRoleCandidateDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134HZCommercialAerospaceHYRoleCandidateDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134HZCommercialAerospaceHYRoleCandidateDirectionTriageV1Report:
        audit = V134HYCommercialAerospaceEventAttentionRoleCandidateAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "candidate_group": "hard_retained_role_seed",
                "direction": "keep_000547_as_the_only_hard_anchor_decoy_case_for_now",
            },
            {
                "candidate_group": "crowded_attention_carrier_candidate",
                "direction": "retain_as_soft_candidate_not_yet_anchor_not_yet_true_selection",
            },
            {
                "candidate_group": "crowding_only_role_candidate",
                "direction": "retain_as_soft_candidate_require_event_backing_before_promotion",
            },
            {
                "candidate_group": "outlier_breakout_concentration_candidate",
                "direction": "retain_as_soft_candidate_require_stronger_attention_evidence_before_role_promotion",
            },
            {
                "candidate_group": "high_beta_attention_follow_candidate",
                "direction": "retain_as_soft_candidate_not_anchor",
            },
            {
                "candidate_group": "capital_true_selection",
                "direction": "continue_blocked_until_role_candidates_are_better_separated",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134hz_commercial_aerospace_hy_role_candidate_direction_triage_v1",
            "candidate_symbol_count": audit.summary["candidate_symbol_count"],
            "hard_retained_count": audit.summary["hard_retained_count"],
            "soft_candidate_count": audit.summary["soft_candidate_count"],
            "authoritative_status": "retain_asymmetric_role_promotion_with_one_hard_case_and_multiple_soft_candidates_capital_true_selection_still_blocked",
        }
        interpretation = [
            "V1.34HZ converts role expansion into direction.",
            "The layer should stay asymmetric: one hard role seed and several softer candidates is preferable to pretending that all named strong symbols already have the same role certainty.",
        ]
        return V134HZCommercialAerospaceHYRoleCandidateDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HZCommercialAerospaceHYRoleCandidateDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HZCommercialAerospaceHYRoleCandidateDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134hz_commercial_aerospace_hy_role_candidate_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
