from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V134OVAShareOUSourceInternalManualChecklistDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134OVAShareOUSourceInternalManualChecklistDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.checklist_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_source_internal_manual_operator_checklist_v1.csv"
        )

    def analyze(self) -> V134OVAShareOUSourceInternalManualChecklistDirectionTriageV1Report:
        rows = _read_csv(self.checklist_path)
        summary = {
            "checklist_row_count": len(rows),
            "stage_1_count": sum(row["checklist_stage"] == "stage_1_primary_host_family_review" for row in rows),
            "authoritative_status": "source_internal_manual_should_now_be_worked_from_checklist_stage_order",
        }
        triage_rows = [
            {"component": "stage_1", "direction": "execute_primary_host_family_checklist_first"},
            {"component": "stage_2", "direction": "hold_independent_hosts_until_stage_1_record_exists"},
            {"component": "stage_3", "direction": "retain_sibling_host_blocked_until_primary_outcome_exists"},
            {"component": "lane_mode", "direction": "treat_source_side_as_manual_checklist_execution_not_structural_build"},
        ]
        interpretation = [
            "The remaining internally actionable lane now has an explicit staged checklist order.",
            "The next gain comes from executing stage 1, not from further modeling or registry expansion.",
        ]
        return V134OVAShareOUSourceInternalManualChecklistDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134OVAShareOUSourceInternalManualChecklistDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134OVAShareOUSourceInternalManualChecklistDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ov_a_share_ou_source_internal_manual_checklist_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
