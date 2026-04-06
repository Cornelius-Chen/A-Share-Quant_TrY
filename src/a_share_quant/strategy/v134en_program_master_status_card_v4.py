from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134ENProgramMasterStatusCardV4Report:
    summary: dict[str, Any]
    status_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "status_rows": self.status_rows,
            "interpretation": self.interpretation,
        }


class V134ENProgramMasterStatusCardV4Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.previous_master_path = analysis_dir / "v134dd_program_master_status_card_v3.json"
        self.frontier_opening_path = analysis_dir / "v134eh_commercial_aerospace_intraday_add_frontier_opening_v1.json"
        self.output_csv = repo_root / "data" / "training" / "program_master_status_card_v4.csv"

    def analyze(self) -> V134ENProgramMasterStatusCardV4Report:
        previous_master = json.loads(self.previous_master_path.read_text(encoding="utf-8"))
        frontier_opening = json.loads(self.frontier_opening_path.read_text(encoding="utf-8"))

        status_rows = []
        for row in previous_master["status_rows"]:
            copied = dict(row)
            if copied["program_line"] == "commercial_aerospace_next_frontier":
                copied["status"] = frontier_opening["summary"]["frontier_state"]
                copied["next_action"] = "build_intraday_add_point_in_time_seed_feed_and_keep_execution_blocked"
            status_rows.append(copied)

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            fieldnames = sorted({key for row in status_rows for key in row.keys()})
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in status_rows:
                writer.writerow({key: row.get(key, "") for key in fieldnames})

        summary = {
            "acceptance_posture": "open_v134en_program_master_status_card_v4",
            "line_count": len(status_rows),
            "frozen_line_count": sum(1 for row in status_rows if str(row["status"]).startswith("frozen")),
            "opened_supervision_line_count": sum(1 for row in status_rows if row["status"] == "opened_supervision_only"),
            "deferred_line_count": sum(1 for row in status_rows if row["status"] == "deferred"),
            "next_frontier": "intraday_add",
            "next_frontier_state": frontier_opening["summary"]["frontier_state"],
            "status_card_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "program_master_status_card_v4_ready_for_add_frontier_governance_triage",
        }
        interpretation = [
            "V1.34EN refreshes the program master card after intraday add is explicitly opened as a supervision frontier.",
            "The key change is narrow but important: the next frontier is no longer deferred; it is open, but only at supervision scope.",
        ]
        return V134ENProgramMasterStatusCardV4Report(
            summary=summary,
            status_rows=status_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V134ENProgramMasterStatusCardV4Report) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ENProgramMasterStatusCardV4Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134en_program_master_status_card_v4",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
