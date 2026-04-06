from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134qk_a_share_runtime_scheduler_activation_precondition_audit_v1 import (
    V134QKAShareRuntimeSchedulerActivationPreconditionAuditV1Analyzer,
)


@dataclass(slots=True)
class V134QLAShareQKRuntimeSchedulerDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134QLAShareQKRuntimeSchedulerDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134QLAShareQKRuntimeSchedulerDirectionTriageV1Report:
        report = V134QKAShareRuntimeSchedulerActivationPreconditionAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "precondition_count": report.summary["precondition_count"],
            "unsatisfied_count": report.summary["unsatisfied_count"],
            "authoritative_status": "runtime_scheduler_followthrough_should_focus_on_a_single_stub_activation_gate",
        }
        triage_rows = [
            {
                "component": "candidate_selection",
                "direction": "keep_only_network_html_article_fetch_inside_the_first_runtime_followthrough_lane",
            },
            {
                "component": "scheduler_gate",
                "direction": "treat_scheduler_stub_not_activated_as_the_only_remaining_source-side runtime blocker",
            },
            {
                "component": "excluded_adapters",
                "direction": "keep_social_and_reserved_official_adapters_outside_this_followthrough_lane",
            },
        ]
        interpretation = [
            "Source-side runtime followthrough now has a single remaining operational blocker: scheduler activation for html-article fetch.",
            "This should stay a controlled lane rather than a broad runtime opening.",
        ]
        return V134QLAShareQKRuntimeSchedulerDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134QLAShareQKRuntimeSchedulerDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134QLAShareQKRuntimeSchedulerDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ql_a_share_qk_runtime_scheduler_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
