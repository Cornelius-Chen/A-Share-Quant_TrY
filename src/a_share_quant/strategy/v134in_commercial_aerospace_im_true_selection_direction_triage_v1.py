from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134im_commercial_aerospace_capital_true_selection_readiness_audit_v1 import (
    V134IMCommercialAerospaceCapitalTrueSelectionReadinessAuditV1Analyzer,
)


@dataclass(slots=True)
class V134INCommercialAerospaceIMTrueSelectionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134INCommercialAerospaceIMTrueSelectionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134INCommercialAerospaceIMTrueSelectionDirectionTriageV1Report:
        audit = V134IMCommercialAerospaceCapitalTrueSelectionReadinessAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "component": "second_event_backed_carrier_case",
                "direction": "retain_as_hard_missing_case_and_do_not_synthesize_a_second_carrier_from non-carrier concentration names",
            },
            {
                "component": "anchor_decoy_counterpanel",
                "direction": "retain_as_hard_thin_panel_and_do_not_inflate_soft_decoy_only names into hard counterpanel status",
            },
            {
                "component": "symbol_followthrough_surface",
                "direction": "retain_as_supporting evidence only and do not read symbol persistence as true selection authority",
            },
            {
                "component": "board_event_alignment",
                "direction": "retain_as supporting supervision only and do not read alignment alone as capital permission",
            },
            {
                "component": "capital_true_selection",
                "direction": "continue_blocked_until_the_two_remaining_hard_gaps_stop_being_single-case bottlenecks",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134in_commercial_aerospace_im_true_selection_direction_triage_v1",
            "remaining_hard_gap_count": audit.summary["remaining_hard_gap_count"],
            "authoritative_status": "retain_partial_gap_closure_but_keep_capital_true_selection_blocked",
        }
        interpretation = [
            "V1.34IN converts the readiness audit into direction.",
            "The route now has cleaner support layers, but promotion still fails for structural reasons rather than for lack of analyst confidence.",
        ]
        return V134INCommercialAerospaceIMTrueSelectionDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134INCommercialAerospaceIMTrueSelectionDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134INCommercialAerospaceIMTrueSelectionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134in_commercial_aerospace_im_true_selection_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
