from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ng_a_share_information_center_latest_status_card_v1 import (
    V134NGAShareInformationCenterLatestStatusCardV1Analyzer,
)
from a_share_quant.strategy.v134nx_a_share_execution_binding_blocker_stack_source_side_reaudit_v1 import (
    V134NXAShareExecutionBindingBlockerStackSourceSideReauditV1Analyzer,
)
from a_share_quant.strategy.v134ny_a_share_replay_promotion_latest_status_card_v1 import (
    V134NYAShareReplayPromotionLatestStatusCardV1Analyzer,
)
from a_share_quant.strategy.v134oa_a_share_index_daily_source_extension_opening_checklist_v1 import (
    V134OAAShareIndexDailySourceExtensionOpeningChecklistV1Analyzer,
)
from a_share_quant.strategy.v134pc_a_share_limit_halt_derivation_review_audit_v1 import (
    V134PCAShareLimitHaltDerivationReviewAuditV1Analyzer,
)
from a_share_quant.strategy.v134pm_a_share_replay_market_context_residual_classification_audit_v1 import (
    V134PMAShareReplayMarketContextResidualClassificationAuditV1Analyzer,
)
from a_share_quant.strategy.v134px_a_share_replay_shadow_corrected_recheck_audit_v1 import (
    V134PXAShareReplayShadowCorrectedRecheckAuditV1Analyzer,
)
from a_share_quant.strategy.v134qi_a_share_source_runtime_promotion_lane_status_audit_v1 import (
    V134QIAShareSourceRuntimePromotionLaneStatusAuditV1Analyzer,
)
from a_share_quant.strategy.v134qs_a_share_runtime_scheduler_governance_opening_review_audit_v1 import (
    V134QSAShareRuntimeSchedulerGovernanceOpeningReviewAuditV1Analyzer,
)


@dataclass(slots=True)
class V134OCAShareInformationCenterGlobalBlockerStatusCardV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134OCAShareInformationCenterGlobalBlockerStatusCardV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_information_center_global_blocker_status_card_v1.csv"

    def analyze(self) -> V134OCAShareInformationCenterGlobalBlockerStatusCardV1Report:
        latest_report = V134NGAShareInformationCenterLatestStatusCardV1Analyzer(self.repo_root).analyze()
        source_report = V134NXAShareExecutionBindingBlockerStackSourceSideReauditV1Analyzer(self.repo_root).analyze()
        replay_report = V134NYAShareReplayPromotionLatestStatusCardV1Analyzer(self.repo_root).analyze()
        replay_checklist = V134OAAShareIndexDailySourceExtensionOpeningChecklistV1Analyzer(self.repo_root).analyze()
        limit_halt_report = V134PCAShareLimitHaltDerivationReviewAuditV1Analyzer(self.repo_root).analyze()
        residual_report = V134PMAShareReplayMarketContextResidualClassificationAuditV1Analyzer(self.repo_root).analyze()
        corrected_recheck_report = V134PXAShareReplayShadowCorrectedRecheckAuditV1Analyzer(self.repo_root).analyze()
        source_runtime_report = V134QIAShareSourceRuntimePromotionLaneStatusAuditV1Analyzer(self.repo_root).analyze()
        opening_review_report = V134QSAShareRuntimeSchedulerGovernanceOpeningReviewAuditV1Analyzer(
            self.repo_root
        ).analyze()

        source_blocker_ids = [
            row["blocker_id"] for row in source_report.blocker_rows if row["blocker_layer"] == "source_activation"
        ]
        replay_status_map = {row["replay_component"]: row for row in replay_report.rows}

        rows = [
            {
                "global_component": "information_center_core",
                "global_state": "foundation_complete_enough",
                "decisive_metric": f"foundation_complete_count = {latest_report.summary['foundation_complete_count']}",
                "next_governance_mode": "freeze_framework_and_close_only_named_blockers",
            },
            {
                "global_component": "source_side_closure",
                "global_state": "single_runtime_opening_review_lane_pending_scheduler_and_governance_movement",
                "decisive_metric": (
                    f"priority_runtime_candidate_count = {source_runtime_report.summary['priority_runtime_candidate_count']}; "
                    f"scheduler_pending_count = {opening_review_report.summary['scheduler_pending_count']}; "
                    f"governance_closed_count = {opening_review_report.summary['governance_closed_count']}"
                ),
                "next_governance_mode": "continue_only_through_the_single_html-article_scheduler_governance_opening_review_lane",
            },
            {
                "global_component": "replay_promotion",
                "global_state": "promotable_subset_materialized",
                "decisive_metric": replay_status_map["daily_market_promotion"]["decisive_metric"],
                "next_governance_mode": "recheck_replay_internal_build_preconditions_from_the_controlled_promotable_subset",
            },
            {
                "global_component": "index_daily_extension_frontier",
                "global_state": "opened_for_downstream_reaudit",
                "decisive_metric": f"closed_gate_count = {replay_checklist.summary['closed_gate_count']}",
                "next_governance_mode": "keep_source-acquisition lane retired while downstream replay blockers close",
            },
            {
                "global_component": "limit_halt_derivation_frontier",
                "global_state": "semantic_materialization_complete_for_recheck",
                "decisive_metric": f"limit_halt_materialized_count = {limit_halt_report.summary['limit_halt_materialized_count']}",
                "next_governance_mode": "carry_named_semantic_residuals_into_replay_recheck_without_reopening_derivation_hunting",
            },
            {
                "global_component": "market_context_residual_frontier",
                "global_state": "external_boundary_residuals_only_under_shadow_overlay",
                "decisive_metric": (
                    f"base_missing_count = {corrected_recheck_report.summary['base_missing_count']}; "
                    f"corrected_missing_count = {corrected_recheck_report.summary['corrected_missing_count']}; "
                    f"boundary_only_residual_count = {corrected_recheck_report.summary['boundary_only_residual_count']}"
                ),
                "next_governance_mode": "retain_shadow_overlay_and_treat_market_context_work_as_boundary_handling_not_full_surface_extension",
            },
            {
                "global_component": "live_like_execution",
                "global_state": "explicitly_blocked",
                "decisive_metric": f"total_blocker_count = {source_report.summary['blocker_count']}",
                "next_governance_mode": "retain_research_shadow_only_until_source_and_replay_closure_progresses",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        summary = {
            "global_component_count": len(rows),
            "source_blocker_count": source_report.summary["source_blocker_count"],
            "replay_true_source_gap_count": replay_report.summary["true_source_gap_count"],
            "index_extension_ready_to_open_now": replay_checklist.summary["ready_to_open_now"],
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_information_center_global_blocker_status_card_materialized",
        }
        interpretation = [
            "The information center now has one global control view that merges foundation status, source-side closure, replay-side promotion status, and the reopened index-daily downstream re-audit lane.",
            "Current progress is no longer a construction problem: source-side has narrowed to a single runtime scheduler gate lane, while replay-side has moved past both source-boundary blockage and limit-halt derivation blockage into internal recheck mode with only external boundary residuals left under the shadow overlay.",
            f"Active source-side blockers are {', '.join(source_blocker_ids)}.",
        ]
        return V134OCAShareInformationCenterGlobalBlockerStatusCardV1Report(
            summary=summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134OCAShareInformationCenterGlobalBlockerStatusCardV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134OCAShareInformationCenterGlobalBlockerStatusCardV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134oc_a_share_information_center_global_blocker_status_card_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
