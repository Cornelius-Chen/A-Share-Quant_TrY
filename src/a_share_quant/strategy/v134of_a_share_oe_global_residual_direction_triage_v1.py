from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134oe_a_share_information_center_global_residual_backlog_audit_v1 import (
    V134OEAShareInformationCenterGlobalResidualBacklogAuditV1Analyzer,
)


@dataclass(slots=True)
class V134OFAShareOEGlobalResidualDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134OFAShareOEGlobalResidualDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134OFAShareOEGlobalResidualDirectionTriageV1Report:
        report = V134OEAShareInformationCenterGlobalResidualBacklogAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "backlog_count": report.summary["backlog_count"],
            "internal_manual_count": report.summary["internal_manual_count"],
            "external_source_count": report.summary["external_source_count"],
            "authoritative_status": "global_residual_backlog_should_be_worked_by_group_not_as_flat_list",
        }
        triage_rows = [
            {
                "component": "source_internal_manual",
                "direction": "treat_source_manual_closure_as_first_internal_backlog_lane",
            },
            {
                "component": "replay_internal_build",
                "direction": "keep_replay_internal_build_backlog_frozen_until_market_context_boundary_moves",
            },
            {
                "component": "replay_external_source",
                "direction": "treat_external_index_source_acquisition_as_separate_future_frontier",
            },
            {
                "component": "governance_hold",
                "direction": "retain_governance_holds_closed_while_other_backlog_groups_remain_open",
            },
        ]
        interpretation = [
            "The remaining work should now be steered by backlog groups instead of by a flat undifferentiated to-do list.",
            "This separates what can be closed internally now from what is truly waiting on future raw source acquisition.",
        ]
        return V134OFAShareOEGlobalResidualDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134OFAShareOEGlobalResidualDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134OFAShareOEGlobalResidualDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134of_a_share_oe_global_residual_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
