from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134mo_a_share_replay_cost_model_foundation_audit_v1 import (
    V134MOAShareReplayCostModelFoundationAuditV1Analyzer,
)
from a_share_quant.strategy.v134ms_a_share_replay_market_coverage_gap_audit_v1 import (
    V134MSAShareReplayMarketCoverageGapAuditV1Analyzer,
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
from a_share_quant.strategy.v134pm_a_share_replay_market_context_residual_classification_audit_v1 import (
    V134PMAShareReplayMarketContextResidualClassificationAuditV1Analyzer,
)
from a_share_quant.strategy.v134px_a_share_replay_shadow_corrected_recheck_audit_v1 import (
    V134PXAShareReplayShadowCorrectedRecheckAuditV1Analyzer,
)


@dataclass(slots=True)
class V134NYAShareReplayPromotionLatestStatusCardV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134NYAShareReplayPromotionLatestStatusCardV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_replay_promotion_latest_status_card_v1.csv"

    def analyze(self) -> V134NYAShareReplayPromotionLatestStatusCardV1Report:
        cost_report = V134MOAShareReplayCostModelFoundationAuditV1Analyzer(self.repo_root).analyze()
        coverage_report = V134MSAShareReplayMarketCoverageGapAuditV1Analyzer(self.repo_root).analyze()
        promotion_report = V134MYAShareDailyMarketPromotionReviewAuditV1Analyzer(self.repo_root).analyze()
        paired_report = V134NCASharePairedSurfaceExtensionStatusAuditV1Analyzer(self.repo_root).analyze()
        source_gap_report = V134NEAShareIndexDailySourceHorizonGapAuditV1Analyzer(self.repo_root).analyze()
        limit_halt_report = V134PCAShareLimitHaltDerivationReviewAuditV1Analyzer(self.repo_root).analyze()
        residual_report = V134PMAShareReplayMarketContextResidualClassificationAuditV1Analyzer(self.repo_root).analyze()
        corrected_recheck_report = V134PXAShareReplayShadowCorrectedRecheckAuditV1Analyzer(self.repo_root).analyze()

        execution_journal_stub_count = 0
        for row in cost_report.rows:
            if row["component"] == "shadow_execution_journal":
                execution_journal_stub_count = int(row["coverage_note"].split("=")[1].strip())
                break

        index_gap_closed = source_gap_report.summary["beyond_2024_source_count"] > 0
        paired_candidate_ready = (
            paired_report.summary["index_candidate_cover_count"] > 0
            and paired_report.summary["limit_halt_candidate_cover_count"] > 0
        )

        rows = [
            {
                "replay_component": "shadow_execution_journal",
                "status_class": "stub_only",
                "decisive_metric": f"execution_journal_stub_count = {execution_journal_stub_count}",
                "next_closure_mode": "replace_stub_only_after_market_context_closes",
            },
            {
                "replay_component": "market_coverage",
                "status_class": "external_boundary_residuals_only_under_shadow_overlay",
                "decisive_metric": (
                    f"base_missing_count = {corrected_recheck_report.summary['base_missing_count']}; "
                    f"corrected_missing_count = {corrected_recheck_report.summary['corrected_missing_count']}; "
                    f"boundary_only_residual_count = {corrected_recheck_report.summary['boundary_only_residual_count']}"
                ),
                "next_closure_mode": "retain_shadow_overlay_for_internal_rechecks_and_treat_remaining_rows_as_external_boundary_residuals",
            },
            {
                "replay_component": "daily_market_promotion",
                "status_class": "promotable_subset_materialized",
                "decisive_metric": f"promotable_now_count = {promotion_report.summary['promotable_now_count']}",
                "next_closure_mode": "recheck_replay_internal_build_preconditions_from_the_controlled_promotable_subset",
            },
            {
                "replay_component": "paired_surfaces",
                "status_class": "semantic_pair_layer_materialized" if paired_candidate_ready else "index_daily_primary_blocker",
                "decisive_metric": (
                    f"index_candidate_cover_count = {paired_report.summary['index_candidate_cover_count']}; "
                    f"limit_halt_materialized_count = {limit_halt_report.summary['limit_halt_materialized_count']}"
                ),
                "next_closure_mode": (
                    "use_semantic_pair_layer_for_replay_internal_build_recheck"
                    if paired_candidate_ready
                    else "treat_index_daily_as_primary_replay_promotion_blocker"
                ),
            },
            {
                "replay_component": "index_daily_source_horizon",
                "status_class": "source_gap_closed" if index_gap_closed else "true_source_gap",
                "decisive_metric": f"beyond_2024_source_count = {source_gap_report.summary['beyond_2024_source_count']}",
                "next_closure_mode": (
                    "retire_source_gap_and_reopen_downstream_reaudit"
                    if index_gap_closed
                    else "require_new_raw_index_source_before_any_index_extension_review"
                ),
            },
            {
                "replay_component": "shadow_corrected_recheck",
                "status_class": "shadow_overlay_materialized",
                "decisive_metric": (
                    f"corrected_via_effective_trade_date_count = {corrected_recheck_report.summary['corrected_via_effective_trade_date_count']}"
                ),
                "next_closure_mode": "retain_as_shadow_only_overlay_without_replacing_base_binding",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        summary = {
            "replay_component_count": len(rows),
            "stub_only_count": 1,
            "promotable_subset_count": 1,
            "true_source_gap_count": 0 if index_gap_closed else 1,
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_replay_promotion_latest_status_card_materialized",
        }
        interpretation = [
            "Replay promotion is no longer blocked by vague incompleteness; its current blockers are explicit and layered.",
            (
                "Index-daily raw-source absence has been closed, and semantic pair-layer materialization has reopened replay promotion with a controlled promotable subset."
                if index_gap_closed
                else "Daily market and limit-halt now have meaningful candidate progress, but index-daily remains the primary blocker because it has hit a true raw-source horizon gap."
            ),
            "Replay should now be steered as boundary-residual handling plus internal-build precondition recheck, not as open-ended replay design.",
            "The only internally fixable calendar residual has already been removed inside a shadow-only corrected binding overlay.",
        ]
        return V134NYAShareReplayPromotionLatestStatusCardV1Report(
            summary=summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134NYAShareReplayPromotionLatestStatusCardV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134NYAShareReplayPromotionLatestStatusCardV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ny_a_share_replay_promotion_latest_status_card_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
