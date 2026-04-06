from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134oa_a_share_index_daily_source_extension_opening_checklist_v1 import (
    V134OAAShareIndexDailySourceExtensionOpeningChecklistV1Analyzer,
)


@dataclass(slots=True)
class V134OBAShareOAIndexSourceExtensionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134OBAShareOAIndexSourceExtensionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134OBAShareOAIndexSourceExtensionDirectionTriageV1Report:
        report = V134OAAShareIndexDailySourceExtensionOpeningChecklistV1Analyzer(self.repo_root).analyze()
        if report.summary["ready_to_open_now"]:
            summary = {
                "opening_gate_count": report.summary["opening_gate_count"],
                "closed_gate_count": report.summary["closed_gate_count"],
                "authoritative_status": "index_daily_source_extension_opened_for_downstream_reaudit",
            }
            triage_rows = [
                {
                    "component": "raw_source_acquisition",
                    "direction": "retain_new_raw_index_source_as_opening_trigger_and_stop_using_true_gap_language",
                },
                {
                    "component": "materialization_review",
                    "direction": "reopen_index_daily_materialization_and_candidate_review_under_the_new_raw_horizon",
                },
                {
                    "component": "paired_surface_promotion",
                    "direction": "advance_to_downstream_paired_surface_recheck_instead_of_freezing_extension",
                },
            ]
            interpretation = [
                "Index-daily extension is no longer deferred-prelaunch because the opening gates are now materially open.",
                "The valid next move is downstream re-audit and promotion review, not another raw-source acquisition loop.",
            ]
        else:
            summary = {
                "opening_gate_count": report.summary["opening_gate_count"],
                "closed_gate_count": report.summary["closed_gate_count"],
                "authoritative_status": "index_daily_source_extension_should_remain_deferred_prelaunch",
            }
            triage_rows = [
                {
                    "component": "raw_source_acquisition",
                    "direction": "treat_new_raw_index_source_as_the_only_valid_first_move",
                },
                {
                    "component": "materialization_review",
                    "direction": "do_not_reopen_index_daily_materialization_without_new_raw_horizon",
                },
                {
                    "component": "paired_surface_promotion",
                    "direction": "keep_paired_surface_promotion_frozen_until_index_daily_opening_gates_change",
                },
            ]
            interpretation = [
                "Index-daily extension should now be treated as deferred-prelaunch work, not as an active replay research frontier.",
                "This prevents repeated drift on a line that is currently blocked by true source absence.",
            ]
        return V134OBAShareOAIndexSourceExtensionDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134OBAShareOAIndexSourceExtensionDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134OBAShareOAIndexSourceExtensionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ob_a_share_oa_index_source_extension_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
