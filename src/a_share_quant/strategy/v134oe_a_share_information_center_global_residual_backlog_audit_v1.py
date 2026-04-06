from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134nx_a_share_execution_binding_blocker_stack_source_side_reaudit_v1 import (
    V134NXAShareExecutionBindingBlockerStackSourceSideReauditV1Analyzer,
)
from a_share_quant.strategy.v134nu_a_share_allowlist_promotion_precondition_surface_audit_v1 import (
    V134NUAShareAllowlistPromotionPreconditionSurfaceAuditV1Analyzer,
)
from a_share_quant.strategy.v134oa_a_share_index_daily_source_extension_opening_checklist_v1 import (
    V134OAAShareIndexDailySourceExtensionOpeningChecklistV1Analyzer,
)
from a_share_quant.strategy.v134oc_a_share_information_center_global_blocker_status_card_v1 import (
    V134OCAShareInformationCenterGlobalBlockerStatusCardV1Analyzer,
)
from a_share_quant.strategy.v134qa_a_share_shadow_execution_eligible_subset_audit_v1 import (
    V134QAAShareShadowExecutionEligibleSubsetAuditV1Analyzer,
)
from a_share_quant.strategy.v134qk_a_share_runtime_scheduler_activation_precondition_audit_v1 import (
    V134QKAShareRuntimeSchedulerActivationPreconditionAuditV1Analyzer,
)
from a_share_quant.strategy.v134qs_a_share_runtime_scheduler_governance_opening_review_audit_v1 import (
    V134QSAShareRuntimeSchedulerGovernanceOpeningReviewAuditV1Analyzer,
)


@dataclass(slots=True)
class V134OEAShareInformationCenterGlobalResidualBacklogAuditV1Report:
    summary: dict[str, Any]
    backlog_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "backlog_rows": self.backlog_rows, "interpretation": self.interpretation}


class V134OEAShareInformationCenterGlobalResidualBacklogAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_information_center_global_residual_backlog_v1.csv"

    def analyze(self) -> V134OEAShareInformationCenterGlobalResidualBacklogAuditV1Report:
        blocker_report = V134NXAShareExecutionBindingBlockerStackSourceSideReauditV1Analyzer(self.repo_root).analyze()
        precondition_report = V134NUAShareAllowlistPromotionPreconditionSurfaceAuditV1Analyzer(self.repo_root).analyze()
        checklist_report = V134OAAShareIndexDailySourceExtensionOpeningChecklistV1Analyzer(self.repo_root).analyze()
        global_report = V134OCAShareInformationCenterGlobalBlockerStatusCardV1Analyzer(self.repo_root).analyze()
        eligible_subset_report = V134QAAShareShadowExecutionEligibleSubsetAuditV1Analyzer(self.repo_root).analyze()
        scheduler_report = V134QKAShareRuntimeSchedulerActivationPreconditionAuditV1Analyzer(self.repo_root).analyze()
        opening_review_report = V134QSAShareRuntimeSchedulerGovernanceOpeningReviewAuditV1Analyzer(
            self.repo_root
        ).analyze()

        blocker_map = {row["blocker_id"]: row for row in blocker_report.blocker_rows}
        precondition_map = {row["precondition"]: row for row in precondition_report.rows}

        backlog_rows = [
            {
                "backlog_id": "bg_001",
                "backlog_group": "source_runtime_followthrough",
                "backlog_item": "runtime_scheduler_governance_opening_followthrough_for_html_article_fetch",
                "current_state": "single_opening_review_lane_pending_scheduler_and_governance_movement",
                "blocking_reason": opening_review_report.review_rows[0]["blocking_reason"],
                "closure_mode": "activate_scheduler_runtime_binding_first_then_reaudit_live_like_and_execution_governance_without_reopening_excluded_adapters",
            },
            {
                "backlog_id": "bg_002",
                "backlog_group": "replay_internal_build",
                "backlog_item": "shadow_execution_journal_replace_stub_from_eligible_subset",
                "current_state": "narrowed_to_shadow_eligible_subset_lane",
                "blocking_reason": (
                    f"{blocker_map['replay_execution_journal_stub_only']['blocking_reason']}; "
                    f"eligible_subset_count = {eligible_subset_report.summary['eligible_subset_count']}; "
                    f"excluded_boundary_count = {eligible_subset_report.summary['excluded_boundary_count']}"
                ),
                "closure_mode": "replace_stub_from_the_15_row_shadow_eligible_subset_without_forcing_boundary_rows_inside",
            },
            {
                "backlog_id": "bg_003",
                "backlog_group": "replay_external_source",
                "backlog_item": "index_daily_raw_source_extension",
                "current_state": "deferred_prelaunch",
                "blocking_reason": checklist_report.checklist_rows[0]["gate_reason"],
                "closure_mode": "acquire_new_raw_index_source_then_reopen_extension",
            },
            {
                "backlog_id": "bg_004",
                "backlog_group": "replay_external_source",
                "backlog_item": "index_daily_source_horizon_match_shadow_window",
                "current_state": "deferred_prelaunch",
                "blocking_reason": checklist_report.checklist_rows[1]["gate_reason"],
                "closure_mode": "extend_raw_index_horizon_to_cover_shadow_window",
            },
            {
                "backlog_id": "bg_005",
                "backlog_group": "governance_hold",
                "backlog_item": "live_like_opening_gate",
                "current_state": "closed",
                "blocking_reason": blocker_map["live_like_opening_gate_closed"]["blocking_reason"],
                "closure_mode": "keep_closed_until_source_and_replay_backlogs_shrink",
            },
            {
                "backlog_id": "bg_006",
                "backlog_group": "governance_hold",
                "backlog_item": "execution_authority_gate",
                "current_state": "closed",
                "blocking_reason": blocker_map["execution_authority_gate_closed"]["blocking_reason"],
                "closure_mode": "retain_research_shadow_only",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(backlog_rows[0].keys()))
            writer.writeheader()
            writer.writerows(backlog_rows)

        summary = {
            "backlog_count": len(backlog_rows),
            "source_runtime_count": sum(row["backlog_group"] == "source_runtime_followthrough" for row in backlog_rows),
            "internal_build_count": sum(row["backlog_group"] == "replay_internal_build" for row in backlog_rows),
            "external_source_count": sum(row["backlog_group"] == "replay_external_source" for row in backlog_rows),
            "governance_hold_count": sum(row["backlog_group"] == "governance_hold" for row in backlog_rows),
            "global_state_count": len(global_report.rows),
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_information_center_global_residual_backlog_materialized",
        }
        interpretation = [
            "The remaining work is now consolidated into one global backlog instead of being dispersed across source, replay, and governance registries.",
            "What remains is not a generic buildout: it is a mixed queue of source runtime followthrough, replay build closure from a 15-row shadow-eligible subset, external source acquisition, and explicit governance holds.",
        ]
        return V134OEAShareInformationCenterGlobalResidualBacklogAuditV1Report(
            summary=summary, backlog_rows=backlog_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134OEAShareInformationCenterGlobalResidualBacklogAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134OEAShareInformationCenterGlobalResidualBacklogAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134oe_a_share_information_center_global_residual_backlog_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
