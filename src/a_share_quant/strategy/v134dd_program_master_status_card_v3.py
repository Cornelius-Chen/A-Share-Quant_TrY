from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134DDProgramMasterStatusCardV3Report:
    summary: dict[str, Any]
    status_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "status_rows": self.status_rows,
            "interpretation": self.interpretation,
        }


class V134DDProgramMasterStatusCardV3Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.previous_master_path = analysis_dir / "v134cx_program_master_status_card_v2.json"
        self.prelaunch_status_path = analysis_dir / "v134db_commercial_aerospace_intraday_add_prelaunch_status_card_v1.json"
        self.output_csv = repo_root / "data" / "training" / "program_master_status_card_v3.csv"

    def analyze(self) -> V134DDProgramMasterStatusCardV3Report:
        previous_master = json.loads(self.previous_master_path.read_text(encoding="utf-8"))
        prelaunch_status = json.loads(self.prelaunch_status_path.read_text(encoding="utf-8"))

        status_rows = []
        for row in previous_master["status_rows"]:
            copied = dict(row)
            if copied["program_line"] == "commercial_aerospace_next_frontier":
                copied["opening_gate_count"] = prelaunch_status["summary"]["opening_gate_count"]
                copied["opening_posture"] = next(
                    item["value"] for item in prelaunch_status["status_rows"] if item["key"] == "opening_posture"
                )
                copied["silent_opening_allowed"] = next(
                    item["value"] for item in prelaunch_status["status_rows"] if item["key"] == "silent_opening_allowed"
                )
            status_rows.append(copied)

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            fieldnames = [
                "program_line",
                "status",
                "current_variant",
                "next_action",
                "opening_gate_count",
                "opening_posture",
                "silent_opening_allowed",
            ]
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in status_rows:
                writer.writerow({key: row.get(key, "") for key in fieldnames})

        summary = {
            "acceptance_posture": "freeze_v134dd_program_master_status_card_v3",
            "line_count": len(status_rows),
            "frozen_line_count": sum(1 for row in status_rows if str(row["status"]).startswith("frozen")),
            "deferred_line_count": sum(1 for row in status_rows if row["status"] == "deferred"),
            "next_frontier": "intraday_add",
            "opening_gate_count": prelaunch_status["summary"]["opening_gate_count"],
            "silent_opening_allowed": False,
            "authoritative_output": "program_master_status_card_v3_ready_for_prelaunch_governance_triage",
            "status_card_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34DD refreshes the program master card after the intraday-add prelaunch package exists.",
            "The new card does not open add; it merely makes the deferred frontier legible at program level, including its gate count and silent-opening ban.",
        ]
        return V134DDProgramMasterStatusCardV3Report(
            summary=summary,
            status_rows=status_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V134DDProgramMasterStatusCardV3Report) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134DDProgramMasterStatusCardV3Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134dd_program_master_status_card_v3",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
