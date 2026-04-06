from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ia_commercial_aerospace_event_attention_role_separation_audit_v1 import (
    V134IACommercialAerospaceEventAttentionRoleSeparationAuditV1Analyzer,
)


@dataclass(slots=True)
class V134IBCommercialAerospaceIARoleSeparationDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134IBCommercialAerospaceIARoleSeparationDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134IBCommercialAerospaceIARoleSeparationDirectionTriageV1Report:
        audit = V134IACommercialAerospaceEventAttentionRoleSeparationAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "separated_role": "event_backed_attention_carrier_candidate",
                "direction": "retain_as_best_soft_role_candidate_and_test_against_future_anchor_decoy cases",
            },
            {
                "separated_role": "non_anchor_crowded_concentration_candidate",
                "direction": "retain_as_non_anchor concentration not capital_true_selection",
            },
            {
                "separated_role": "non_anchor_outlier_breakout_candidate",
                "direction": "retain_as_non_anchor concentration not attention_anchor",
            },
            {
                "separated_role": "event_backed_high_beta_follow_candidate",
                "direction": "retain_as_follow_candidate not anchor not true_selection",
            },
            {
                "separated_role": "capital_true_selection",
                "direction": "continue_blocked_until_more_than_one_event_backed carrier case exists",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134ib_commercial_aerospace_ia_role_separation_direction_triage_v1",
            "soft_candidate_count": audit.summary["soft_candidate_count"],
            "authoritative_status": "retain_role_separation_without_true_selection_promotion",
        }
        interpretation = [
            "V1.34IB converts role separation into direction.",
            "The main benefit is negative: capital_true_selection stays blocked until the role layer contains more than one event-backed carrier-grade case.",
        ]
        return V134IBCommercialAerospaceIARoleSeparationDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134IBCommercialAerospaceIARoleSeparationDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134IBCommercialAerospaceIARoleSeparationDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ib_commercial_aerospace_ia_role_separation_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
