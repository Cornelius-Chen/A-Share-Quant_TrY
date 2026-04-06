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
class V134ORAShareOQSourceInternalManualHandoffDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134ORAShareOQSourceInternalManualHandoffDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.report_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_source_internal_manual_handoff_package_v1.csv"
        )

    def analyze(self) -> V134ORAShareOQSourceInternalManualHandoffDirectionTriageV1Report:
        handoff_rows = _read_csv(self.report_path)
        triage_rows = [
            {
                "component": "handoff_package",
                "direction": "use_handoff_package_as_the_terminal_source_internal_manual_operator_surface",
            },
            {
                "component": "primary_host_family",
                "direction": "execute_finance_sina_manual_review_first",
            },
            {
                "component": "independent_hosts",
                "direction": "review_stcn_and_yicai_only_after_primary_host_family_record_exists",
            },
            {
                "component": "sibling_host",
                "direction": "retain_stock_finance_sina_dependency_until_primary_host_family_outcome_exists",
            },
        ]
        result_summary = {
            "handoff_row_count": len(handoff_rows),
            "ready_primary_review_count": sum(
                row["dependency_state"] == "ready_primary_review" for row in handoff_rows
            ),
            "authoritative_status": "source_internal_manual_should_now_transition_from_internal_packaging_to_actual_manual_review_execution",
        }
        interpretation = [
            "The source-side manual lane has reached its internal packaging stopline.",
            "Further forward motion now requires actual manual review execution rather than additional internal modeling.",
        ]
        return V134ORAShareOQSourceInternalManualHandoffDirectionTriageV1Report(
            summary=result_summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134ORAShareOQSourceInternalManualHandoffDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ORAShareOQSourceInternalManualHandoffDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134or_a_share_oq_source_internal_manual_handoff_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
