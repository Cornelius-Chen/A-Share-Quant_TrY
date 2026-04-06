from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134qi_a_share_source_runtime_promotion_lane_status_audit_v1 import (
    V134QIAShareSourceRuntimePromotionLaneStatusAuditV1Analyzer,
)


@dataclass(slots=True)
class V134QJAShareQISourceRuntimeDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134QJAShareQISourceRuntimeDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134QJAShareQISourceRuntimeDirectionTriageV1Report:
        report = V134QIAShareSourceRuntimePromotionLaneStatusAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "priority_runtime_candidate_count": report.summary["priority_runtime_candidate_count"],
            "lane_row_count": report.summary["lane_row_count"],
            "unsatisfied_precondition_count": report.summary["unsatisfied_precondition_count"],
            "authoritative_status": "source_runtime_promotion_should_progress_through_a_single_scheduler_gate_lane",
        }
        triage_rows = [
            {
                "component": "html_article_runtime_lane",
                "direction": "treat_as_the_only_first_runtime_promotion_candidate_lane",
            },
            {
                "component": "runtime_stub_replacement_lane",
                "direction": "treat_as_stub-replacement lane foundation_ready_support_for_the_single_html_article_runtime_followthrough_lane",
            },
            {
                "component": "excluded_runtime_adapters",
                "direction": "keep_social_and_reserved_official_adapters_outside_the_first_runtime_lane",
            },
            {
                "component": "remaining_gate",
                "direction": "close_scheduler_runtime_promotion_before_any_source-side runtime opening",
            },
        ]
        interpretation = [
            "Source-side runtime work should now move through one scheduler-gated lane supported by a single materialized stub-replacement lane instead of broad activation language.",
            "This narrows the remaining source backlog to a single operational gate.",
        ]
        return V134QJAShareQISourceRuntimeDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134QJAShareQISourceRuntimeDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134QJAShareQISourceRuntimeDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134qj_a_share_qi_source_runtime_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
