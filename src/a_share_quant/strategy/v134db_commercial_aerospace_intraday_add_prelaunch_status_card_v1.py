from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134DBCommercialAerospaceIntradayAddPrelaunchStatusCardV1Report:
    summary: dict[str, Any]
    status_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "status_rows": self.status_rows,
            "interpretation": self.interpretation,
        }


class V134DBCommercialAerospaceIntradayAddPrelaunchStatusCardV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.reduce_final_status_path = analysis_dir / "v134cv_commercial_aerospace_reduce_final_status_card_v1.json"
        self.opening_checklist_path = analysis_dir / "v134cz_commercial_aerospace_intraday_add_opening_checklist_v1.json"
        self.program_status_path = analysis_dir / "v134cx_program_master_status_card_v2.json"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_add_prelaunch_status_card_v1.csv"
        )

    def analyze(self) -> V134DBCommercialAerospaceIntradayAddPrelaunchStatusCardV1Report:
        reduce_final_status = json.loads(self.reduce_final_status_path.read_text(encoding="utf-8"))
        opening_checklist = json.loads(self.opening_checklist_path.read_text(encoding="utf-8"))
        program_status = json.loads(self.program_status_path.read_text(encoding="utf-8"))

        next_frontier_row = next(
            row for row in program_status["status_rows"] if row["program_line"] == "commercial_aerospace_next_frontier"
        )
        reduce_row = next(
            row for row in program_status["status_rows"] if row["program_line"] == "commercial_aerospace_reduce_branch"
        )

        status_rows = [
            {"key": "active_board", "value": "commercial_aerospace"},
            {"key": "current_frontier", "value": "reduce"},
            {"key": "current_frontier_status", "value": reduce_row["status"]},
            {"key": "next_frontier", "value": next_frontier_row["current_variant"]},
            {"key": "next_frontier_state", "value": next_frontier_row["status"]},
            {"key": "opening_gate_count", "value": opening_checklist["summary"]["checklist_gate_count"]},
            {"key": "opening_posture", "value": "prelaunch_only"},
            {"key": "silent_opening_allowed", "value": False},
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(status_rows[0].keys()))
            writer.writeheader()
            writer.writerows(status_rows)

        summary = {
            "acceptance_posture": "freeze_v134db_commercial_aerospace_intraday_add_prelaunch_status_card_v1",
            "reduce_status": next(
                row["value"] for row in reduce_final_status["status_rows"] if row["key"] == "reduce_status"
            ),
            "next_frontier": next_frontier_row["current_variant"],
            "next_frontier_state": next_frontier_row["status"],
            "opening_gate_count": opening_checklist["summary"]["checklist_gate_count"],
            "status_card_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_intraday_add_prelaunch_status_card_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34DB compresses the current board-level posture into a single prelaunch card: reduce is frozen and intraday add is named but still deferred.",
            "The card exists to reduce ambiguity later; preparation is allowed, but silent opening is not.",
        ]
        return V134DBCommercialAerospaceIntradayAddPrelaunchStatusCardV1Report(
            summary=summary,
            status_rows=status_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134DBCommercialAerospaceIntradayAddPrelaunchStatusCardV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134DBCommercialAerospaceIntradayAddPrelaunchStatusCardV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134db_commercial_aerospace_intraday_add_prelaunch_status_card_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
