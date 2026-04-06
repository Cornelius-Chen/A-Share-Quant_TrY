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
class V134OPAShareOOSourceInternalManualDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134OPAShareOOSourceInternalManualDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.status_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_source_internal_manual_operator_queue_v1.csv"
        )

    def analyze(self) -> V134OPAShareOOSourceInternalManualDirectionTriageV1Report:
        status_rows = _read_csv(self.status_path)
        queue_row_count = len(status_rows)
        ready_primary_review_count = sum(row["dependency_state"] == "ready_primary_review" for row in status_rows)
        triage_rows = [
            {
                "component": "primary_review_step",
                "direction": "fill_finance_sina_primary_host_family_first",
            },
            {
                "component": "secondary_review_steps",
                "direction": "prepare_stcn_and_yicai_after_primary_without_creating_new_structure",
            },
            {
                "component": "sibling_host_dependency",
                "direction": "keep_stock_finance_sina_blocked_until_primary_host_family_outcome_exists",
            },
            {
                "component": "source_internal_manual_lane",
                "direction": "treat_operator_queue_and_handoff_package_as_terminal_internal_control_surface",
            },
        ]
        result_summary = {
            "queue_row_count": queue_row_count,
            "ready_primary_review_count": ready_primary_review_count,
            "authoritative_status": "source_internal_manual_should_now_be_handled_as_manual_closure_lane_not_as_structural_build_lane",
        }
        interpretation = [
            "The remaining gain on the source-side comes from closing the first manual review step, not from additional modeling work.",
            "Once the operator queue and handoff package exist, further internal structure-building would be drift.",
        ]
        return V134OPAShareOOSourceInternalManualDirectionTriageV1Report(
            summary=result_summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134OPAShareOOSourceInternalManualDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134OPAShareOOSourceInternalManualDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134op_a_share_oo_source_internal_manual_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
