from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ok_a_share_global_residual_readiness_audit_v1 import (
    V134OKAShareGlobalResidualReadinessAuditV1Analyzer,
)


@dataclass(slots=True)
class V134OLAShareOKResidualReadinessDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134OLAShareOKResidualReadinessDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134OLAShareOKResidualReadinessDirectionTriageV1Report:
        report = V134OKAShareGlobalResidualReadinessAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "backlog_group_count": report.summary["backlog_group_count"],
            "internally_actionable_group_count": report.summary["internally_actionable_group_count"],
            "externally_dependent_group_count": report.summary["externally_dependent_group_count"],
            "authoritative_status": "residual_backlog_should_now_be_steered_by_group_readiness",
        }
        triage_rows = [
            {
                "component": "source_internal_manual",
                "direction": "treat_source_manual_fill_as_the_only_immediate_actionable_closure_lane",
            },
            {
                "component": "source_promotion_preconditions",
                "direction": "do_not_separate_preconditions_from_manual_fill_they_close_together",
            },
            {
                "component": "replay_internal_build",
                "direction": "retain_replay_internal_build_as_blocked_even_though_its_preconditions_are_explicit",
            },
            {
                "component": "replay_external_source",
                "direction": "treat_replay_external_source_as_future_frontier_not_current_build_lane",
            },
            {
                "component": "governance_hold",
                "direction": "retain_governance_holds_closed_until_other_groups_change_state",
            },
        ]
        interpretation = [
            "The next meaningful internal work should stay concentrated on source-side manual closure rather than being diffused across every residual group.",
            "This keeps the project from drifting into replay and governance lines that are already structurally specified but not currently actionable.",
        ]
        return V134OLAShareOKResidualReadinessDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134OLAShareOKResidualReadinessDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134OLAShareOKResidualReadinessDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ol_a_share_ok_residual_readiness_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
