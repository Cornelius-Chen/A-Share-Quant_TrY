from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ld_a_share_information_center_foundation_completion_audit_v1 import (
    V134LDAShareInformationCenterFoundationCompletionAuditV1Analyzer,
)
from a_share_quant.strategy.v134mm_a_share_network_activation_queue_surface_audit_v1 import (
    V134MMAShareNetworkActivationQueueSurfaceAuditV1Analyzer,
)
from a_share_quant.strategy.v134my_a_share_daily_market_promotion_review_audit_v1 import (
    V134MYAShareDailyMarketPromotionReviewAuditV1Analyzer,
)
from a_share_quant.strategy.v134nc_a_share_paired_surface_extension_status_audit_v1 import (
    V134NCASharePairedSurfaceExtensionStatusAuditV1Analyzer,
)
from a_share_quant.strategy.v134ne_a_share_index_daily_source_horizon_gap_audit_v1 import (
    V134NEAShareIndexDailySourceHorizonGapAuditV1Analyzer,
)
from a_share_quant.strategy.v134pc_a_share_limit_halt_derivation_review_audit_v1 import (
    V134PCAShareLimitHaltDerivationReviewAuditV1Analyzer,
)
from a_share_quant.strategy.v134mu_a_share_execution_binding_blocker_stack_reaudit_v1 import (
    V134MUAShareExecutionBindingBlockerStackReauditV1Analyzer,
)
from a_share_quant.strategy.v134pm_a_share_replay_market_context_residual_classification_audit_v1 import (
    V134PMAShareReplayMarketContextResidualClassificationAuditV1Analyzer,
)
from a_share_quant.strategy.v134px_a_share_replay_shadow_corrected_recheck_audit_v1 import (
    V134PXAShareReplayShadowCorrectedRecheckAuditV1Analyzer,
)
from a_share_quant.strategy.v134qs_a_share_runtime_scheduler_governance_opening_review_audit_v1 import (
    V134QSAShareRuntimeSchedulerGovernanceOpeningReviewAuditV1Analyzer,
)


@dataclass(slots=True)
class V134NGAShareInformationCenterLatestStatusCardV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134NGAShareInformationCenterLatestStatusCardV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_information_center_latest_status_card_v1.csv"

    def analyze(self) -> V134NGAShareInformationCenterLatestStatusCardV1Report:
        foundation_report = V134LDAShareInformationCenterFoundationCompletionAuditV1Analyzer(self.repo_root).analyze()
        queue_report = V134MMAShareNetworkActivationQueueSurfaceAuditV1Analyzer(self.repo_root).analyze()
        promotion_report = V134MYAShareDailyMarketPromotionReviewAuditV1Analyzer(self.repo_root).analyze()
        paired_report = V134NCASharePairedSurfaceExtensionStatusAuditV1Analyzer(self.repo_root).analyze()
        source_gap_report = V134NEAShareIndexDailySourceHorizonGapAuditV1Analyzer(self.repo_root).analyze()
        limit_halt_report = V134PCAShareLimitHaltDerivationReviewAuditV1Analyzer(self.repo_root).analyze()
        blocker_report = V134MUAShareExecutionBindingBlockerStackReauditV1Analyzer(self.repo_root).analyze()
        residual_report = V134PMAShareReplayMarketContextResidualClassificationAuditV1Analyzer(self.repo_root).analyze()
        corrected_recheck_report = V134PXAShareReplayShadowCorrectedRecheckAuditV1Analyzer(self.repo_root).analyze()
        opening_review_report = V134QSAShareRuntimeSchedulerGovernanceOpeningReviewAuditV1Analyzer(
            self.repo_root
        ).analyze()

        rows = [
            {
                "status_component": "information_center_foundation",
                "status_class": "foundation_complete_enough",
                "decisive_metric": (
                    f"foundation_complete_count = {foundation_report.summary['foundation_complete_count']}"
                ),
                "next_closure_mode": "keep_framework_frozen_and_close_named_backlogs_only",
            },
            {
                "status_component": "source_activation_queue_surface",
                "status_class": "single_runtime_opening_review_stopline",
                "decisive_metric": (
                    f"review_row_count = {opening_review_report.summary['review_row_count']}; "
                    f"scheduler_pending_count = {opening_review_report.summary['scheduler_pending_count']}; "
                    f"runtime_queue_count = {queue_report.summary['runtime_queue_count']}"
                ),
                "next_closure_mode": "continue_only_through_the_single_scheduler_governance_opening_review_surface",
            },
            {
                "status_component": "daily_market_promotion",
                "status_class": "promotable_subset_materialized",
                "decisive_metric": f"promotable_now_count = {promotion_report.summary['promotable_now_count']}",
                "next_closure_mode": "recheck_replay_internal_build_from_the_controlled_promotable_subset",
            },
            {
                "status_component": "paired_surface_extension",
                "status_class": "semantic_pair_layer_materialized",
                "decisive_metric": (
                    f"index_candidate_cover_count = {paired_report.summary['index_candidate_cover_count']}; "
                    f"limit_halt_materialized_count = {limit_halt_report.summary['limit_halt_materialized_count']}"
                ),
                "next_closure_mode": "use_the_semantic_pair_layer_for_replay_internal_build_recheck",
            },
            {
                "status_component": "index_daily_source_horizon",
                "status_class": "source_gap_closed",
                "decisive_metric": (
                    f"beyond_2024_source_count = {source_gap_report.summary['beyond_2024_source_count']}"
                ),
                "next_closure_mode": "retire_old_source_gap_and_keep_extension_in_downstream_reaudit_mode",
            },
            {
                "status_component": "limit_halt_derivation",
                "status_class": "semantic_surface_materialized_for_recheck",
                "decisive_metric": f"limit_halt_materialized_count = {limit_halt_report.summary['limit_halt_materialized_count']}",
                "next_closure_mode": "retire_old_derivation_blocker_and_keep_named_semantic_residuals_explicit",
            },
            {
                "status_component": "execution_live_like_gate_stack",
                "status_class": "explicitly_blocked",
                "decisive_metric": f"blocker_count = {blocker_report.summary['blocker_count']}",
                "next_closure_mode": "close_source_and_replay_blockers_before_live_like_or_execution_review",
            },
            {
                "status_component": "market_context_residuals",
                "status_class": "external_boundary_residuals_only_under_shadow_overlay",
                "decisive_metric": (
                    f"base_missing_count = {corrected_recheck_report.summary['base_missing_count']}; "
                    f"corrected_missing_count = {corrected_recheck_report.summary['corrected_missing_count']}; "
                    f"boundary_only_residual_count = {corrected_recheck_report.summary['boundary_only_residual_count']}"
                ),
                "next_closure_mode": "retain_shadow_overlay_and_treat_remaining_rows_as_boundary-handling_work_not_full_market-surface_rebuild",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        summary = {
            "foundation_complete_count": foundation_report.summary["foundation_complete_count"],
            "workstream_count": foundation_report.summary["workstream_count"],
            "queue_stopline_count": 1,
            "promotable_subset_count": 1,
            "true_source_gap_count": 0,
            "semantic_surface_materialized_count": 1,
            "explicit_blocked_stack_count": 1,
            "market_context_residual_count": 1,
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_information_center_latest_status_card_materialized",
        }
        interpretation = [
            "The information center is no longer in scaffold-building mode; the core foundation is complete enough and current work is blocker closure.",
            "Source-side has reached queue-processing stopline, replay-side has reached a controlled promotable subset, and index-daily raw-source absence has now been closed.",
            "Replay-side has now advanced again: semantic limit-halt materialization is done enough to reopen replay promotion with a controlled promotable subset.",
            "The remaining replay market-context gap is no longer broad; under the shadow-only corrected binding overlay it narrows to external boundary residuals only.",
            "Live-like and execution remain explicitly blocked by a named gate stack rather than by vague incompleteness.",
        ]
        return V134NGAShareInformationCenterLatestStatusCardV1Report(
            summary=summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134NGAShareInformationCenterLatestStatusCardV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134NGAShareInformationCenterLatestStatusCardV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ng_a_share_information_center_latest_status_card_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
