from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass(slots=True)
class V134OWAShareIndexDailySourceIntakeChecklistAuditV1Report:
    summary: dict[str, Any]
    checklist_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "checklist_rows": self.checklist_rows,
            "interpretation": self.interpretation,
        }


class V134OWAShareIndexDailySourceIntakeChecklistAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.opening_checklist_path = (
            repo_root / "reports" / "analysis" / "v134oa_a_share_index_daily_source_extension_opening_checklist_v1.json"
        )
        self.output_csv = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "market_registry"
            / "a_share_index_daily_source_intake_checklist_v1.csv"
        )

    def analyze(self) -> V134OWAShareIndexDailySourceIntakeChecklistAuditV1Report:
        opening_report = _read_json(self.opening_checklist_path)
        checklist_rows = [
            {
                "intake_step": "new_raw_source_present",
                "required_evidence": "raw_file_or_feed_arrival",
                "success_condition": "source_extends_beyond_2024_12_31",
                "current_state": opening_report["checklist_rows"][0]["gate_state"],
            },
            {
                "intake_step": "source_horizon_matches_shadow_window",
                "required_evidence": "coverage_end_ge_shadow_horizon_end",
                "success_condition": "coverage_end_reaches_2026_03_28_or_beyond",
                "current_state": opening_report["checklist_rows"][1]["gate_state"],
            },
            {
                "intake_step": "materialization_review_reopen",
                "required_evidence": "new_source_registered_and_reviewable",
                "success_condition": "index_daily_registry_materialization_can_be_reaudited",
                "current_state": opening_report["checklist_rows"][2]["gate_state"],
            },
            {
                "intake_step": "paired_surface_promotion_recheck",
                "required_evidence": "index_daily_boundary_moves",
                "success_condition": "daily_market_promotion_can_be_reconsidered",
                "current_state": opening_report["checklist_rows"][3]["gate_state"],
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(checklist_rows[0].keys()))
            writer.writeheader()
            writer.writerows(checklist_rows)

        summary = {
            "intake_step_count": len(checklist_rows),
            "closed_step_count": sum(row["current_state"] == "closed" for row in checklist_rows),
            "artifact_path": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_index_daily_source_intake_checklist_materialized",
        }
        interpretation = [
            "Replay-side future movement now has a single intake checklist instead of requiring re-reading multiple blocker cards.",
            "No internal work can reopen this lane without new raw index source arrival, but the intake checklist now defines exactly how that reopening should be handled.",
        ]
        return V134OWAShareIndexDailySourceIntakeChecklistAuditV1Report(
            summary=summary,
            checklist_rows=checklist_rows,
            interpretation=interpretation,
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134OWAShareIndexDailySourceIntakeChecklistAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134OWAShareIndexDailySourceIntakeChecklistAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ow_a_share_index_daily_source_intake_checklist_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
