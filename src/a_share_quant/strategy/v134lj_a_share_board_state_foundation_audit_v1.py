from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.market.board_state.materialize_a_share_board_state_foundation_v1 import (
    MaterializeAShareBoardStateFoundationV1,
)


@dataclass(slots=True)
class V134LJAShareBoardStateFoundationAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134LJAShareBoardStateFoundationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_board_state_foundation_status_v1.csv"

    def analyze(self) -> V134LJAShareBoardStateFoundationAuditV1Report:
        materialized = MaterializeAShareBoardStateFoundationV1(self.repo_root).materialize()
        summary = materialized.summary
        rows = [
            {
                "component": "board_state_surface",
                "component_state": "materialized_bootstrap_single_board",
                "artifact_path": summary["surface_path"],
                "coverage_note": f"board_state_row_count = {summary['board_state_row_count']}",
            },
            {
                "component": "board_state_intervals",
                "component_state": "materialized_bootstrap_single_board",
                "artifact_path": summary["interval_path"],
                "coverage_note": f"lockout_interval_count = {summary['lockout_interval_count']}",
            },
            {
                "component": "board_state_residual_backlog",
                "component_state": "materialized_named_residuals",
                "artifact_path": summary["residual_path"],
                "coverage_note": f"residual_count = {summary['residual_count']}",
            },
        ]
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        report_summary = {
            "acceptance_posture": "build_v134lj_a_share_board_state_foundation_audit_v1",
            "board_state_row_count": summary["board_state_row_count"],
            "unlock_worthy_count": summary["unlock_worthy_count"],
            "lockout_worthy_count": summary["lockout_worthy_count"],
            "false_bounce_count": summary["false_bounce_count"],
            "residual_count": summary["residual_count"],
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_board_state_foundation_ready_for_direction_triage",
        }
        interpretation = [
            "This closes the first board-state derivation backlog by centralizing the already-stabilized commercial-aerospace board regime states into the information center.",
            "The surface is intentionally single-board and seed-driven, which is better than pretending a multi-board daily regime surface already exists.",
        ]
        return V134LJAShareBoardStateFoundationAuditV1Report(
            summary=report_summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134LJAShareBoardStateFoundationAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134LJAShareBoardStateFoundationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134lj_a_share_board_state_foundation_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
