from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134oe_a_share_information_center_global_residual_backlog_audit_v1 import (
    V134OEAShareInformationCenterGlobalResidualBacklogAuditV1Analyzer,
)
from a_share_quant.strategy.v134og_a_share_batch_one_manual_review_workpack_audit_v1 import (
    V134OGAShareBatchOneManualReviewWorkpackAuditV1Analyzer,
)
from a_share_quant.strategy.v134nu_a_share_allowlist_promotion_precondition_surface_audit_v1 import (
    V134NUAShareAllowlistPromotionPreconditionSurfaceAuditV1Analyzer,
)
from a_share_quant.strategy.v134oi_a_share_shadow_execution_stub_replacement_precondition_audit_v1 import (
    V134OIAShareShadowExecutionStubReplacementPreconditionAuditV1Analyzer,
)
from a_share_quant.strategy.v134oa_a_share_index_daily_source_extension_opening_checklist_v1 import (
    V134OAAShareIndexDailySourceExtensionOpeningChecklistV1Analyzer,
)


@dataclass(slots=True)
class V134OKAShareGlobalResidualReadinessAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134OKAShareGlobalResidualReadinessAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_global_residual_readiness_status_v1.csv"

    def analyze(self) -> V134OKAShareGlobalResidualReadinessAuditV1Report:
        backlog_report = V134OEAShareInformationCenterGlobalResidualBacklogAuditV1Analyzer(self.repo_root).analyze()
        workpack_report = V134OGAShareBatchOneManualReviewWorkpackAuditV1Analyzer(self.repo_root).analyze()
        source_precondition_report = V134NUAShareAllowlistPromotionPreconditionSurfaceAuditV1Analyzer(self.repo_root).analyze()
        replay_internal_report = V134OIAShareShadowExecutionStubReplacementPreconditionAuditV1Analyzer(
            self.repo_root
        ).analyze()
        replay_external_report = V134OAAShareIndexDailySourceExtensionOpeningChecklistV1Analyzer(
            self.repo_root
        ).analyze()

        rows = [
            {
                "backlog_group": "source_internal_manual",
                "readiness_state": "workpack_ready_manual_fill_pending",
                "decisive_metric": f"workpack_row_count = {workpack_report.summary['workpack_row_count']}",
                "closure_readiness": "internally_actionable",
            },
            {
                "backlog_group": "source_promotion_preconditions",
                "readiness_state": "preconditions_explicit_but_unsatisfied",
                "decisive_metric": f"unsatisfied_count = {source_precondition_report.summary['unsatisfied_count']}",
                "closure_readiness": "internally_actionable_after_manual_fill",
            },
            {
                "backlog_group": "replay_internal_build",
                "readiness_state": "preconditions_explicit_but_blocked",
                "decisive_metric": f"unsatisfied_count = {replay_internal_report.summary['unsatisfied_count']}",
                "closure_readiness": "not_actionable_until_market_context_moves",
            },
            {
                "backlog_group": "replay_external_source",
                "readiness_state": "deferred_prelaunch_closed",
                "decisive_metric": f"closed_gate_count = {replay_external_report.summary['closed_gate_count']}",
                "closure_readiness": "externally_dependent",
            },
            {
                "backlog_group": "governance_hold",
                "readiness_state": "intentionally_closed",
                "decisive_metric": (
                    f"governance_hold_count = {sum(row['backlog_group'] == 'governance_hold' for row in backlog_report.backlog_rows)}"
                ),
                "closure_readiness": "do_not_open_early",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        summary = {
            "backlog_group_count": len(rows),
            "internally_actionable_group_count": sum(
                row["closure_readiness"] in {"internally_actionable", "internally_actionable_after_manual_fill"}
                for row in rows
            ),
            "externally_dependent_group_count": sum(
                row["closure_readiness"] == "externally_dependent" for row in rows
            ),
            "intentionally_closed_group_count": sum(
                row["closure_readiness"] == "do_not_open_early" for row in rows
            ),
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_global_residual_readiness_groups_materialized",
        }
        interpretation = [
            "Residual work is no longer just a backlog list; it is now grouped by closure readiness.",
            "Only the source-side manual lane remains internally actionable now; replay internal build is structurally specified but still blocked by market context, and replay external source remains deferred-prelaunch.",
        ]
        return V134OKAShareGlobalResidualReadinessAuditV1Report(
            summary=summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134OKAShareGlobalResidualReadinessAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134OKAShareGlobalResidualReadinessAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ok_a_share_global_residual_readiness_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
