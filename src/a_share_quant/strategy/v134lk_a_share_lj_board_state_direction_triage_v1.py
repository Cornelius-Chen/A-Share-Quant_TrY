from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134lj_a_share_board_state_foundation_audit_v1 import (
    V134LJAShareBoardStateFoundationAuditV1Analyzer,
)


@dataclass(slots=True)
class V134LKAShareLJBoardStateDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134LKAShareLJBoardStateDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134LKAShareLJBoardStateDirectionTriageV1Report:
        audit = V134LJAShareBoardStateFoundationAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "component": "board_state_surface",
                "direction": "freeze_as_current_single_board_regime_surface",
            },
            {
                "component": "board_state_intervals",
                "direction": "retain_as_current_lockout_interval_ground_truth",
            },
            {
                "component": "residual_backlog",
                "direction": "retain_for_future_multi_board_and_full_daily_derivation_expansion",
            },
        ]
        summary = {
            "board_state_row_count": audit.summary["board_state_row_count"],
            "residual_count": audit.summary["residual_count"],
            "authoritative_status": "board_state_derivation_complete_enough_to_freeze_as_bootstrap_single_board_surface",
        }
        interpretation = [
            "Board-state derivation is no longer absent from the information center; it now exists as a central, explicit bootstrap surface.",
            "Future expansion should widen boards and timeline coverage, not replace the current commercial-aerospace regime surface.",
        ]
        return V134LKAShareLJBoardStateDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134LKAShareLJBoardStateDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134LKAShareLJBoardStateDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134lk_a_share_lj_board_state_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
