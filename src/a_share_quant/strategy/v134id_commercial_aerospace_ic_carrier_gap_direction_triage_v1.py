from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ic_commercial_aerospace_carrier_grade_evidence_gap_audit_v1 import (
    V134ICCommercialAerospaceCarrierGradeEvidenceGapAuditV1Analyzer,
)


@dataclass(slots=True)
class V134IDCommercialAerospaceICCarrierGapDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134IDCommercialAerospaceICCarrierGapDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134IDCommercialAerospaceICCarrierGapDirectionTriageV1Report:
        audit = V134ICCommercialAerospaceCarrierGradeEvidenceGapAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "next_target": "second_event_backed_carrier_case",
                "direction": "promote_as_next_high_value_search_target",
            },
            {
                "next_target": "anchor_decoy_counterpanel",
                "direction": "promote_as_next_high_value_role_supervision_target",
            },
            {
                "next_target": "followthrough_surface",
                "direction": "defer_until_role_counterpanel_is_thicker_but_keep_as_named future need",
            },
            {
                "next_target": "capital_true_selection",
                "direction": "keep_blocked_until_the_named_gaps_are_partially_closed",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134id_commercial_aerospace_ic_carrier_gap_direction_triage_v1",
            "active_gap_count": audit.summary["active_gap_count"],
            "authoritative_status": "retain_named_gap_blocking_and_use_gap_closure_not_intuition_as_the_next_promotion_rule",
        }
        interpretation = [
            "V1.34ID converts carrier-grade evidence gaps into direction.",
            "The value is procedural: true selection stays blocked until explicit gaps shrink, not until the analyst merely feels more comfortable.",
        ]
        return V134IDCommercialAerospaceICCarrierGapDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134IDCommercialAerospaceICCarrierGapDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134IDCommercialAerospaceICCarrierGapDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134id_commercial_aerospace_ic_carrier_gap_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
