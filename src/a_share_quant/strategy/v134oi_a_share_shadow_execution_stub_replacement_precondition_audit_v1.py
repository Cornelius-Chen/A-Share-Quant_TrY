from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ms_a_share_replay_market_coverage_gap_audit_v1 import (
    V134MSAShareReplayMarketCoverageGapAuditV1Analyzer,
)
from a_share_quant.strategy.v134my_a_share_daily_market_promotion_review_audit_v1 import (
    V134MYAShareDailyMarketPromotionReviewAuditV1Analyzer,
)
from a_share_quant.strategy.v134nc_a_share_paired_surface_extension_status_audit_v1 import (
    V134NCASharePairedSurfaceExtensionStatusAuditV1Analyzer,
)
from a_share_quant.strategy.v134mo_a_share_replay_cost_model_foundation_audit_v1 import (
    V134MOAShareReplayCostModelFoundationAuditV1Analyzer,
)
from a_share_quant.strategy.v134px_a_share_replay_shadow_corrected_recheck_audit_v1 import (
    V134PXAShareReplayShadowCorrectedRecheckAuditV1Analyzer,
)
from a_share_quant.strategy.v134qe_a_share_shadow_execution_stub_replacement_lane_audit_v1 import (
    V134QEAShareShadowExecutionStubReplacementLaneAuditV1Analyzer,
)


@dataclass(slots=True)
class V134OIAShareShadowExecutionStubReplacementPreconditionAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134OIAShareShadowExecutionStubReplacementPreconditionAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root / "data" / "training" / "a_share_shadow_execution_stub_replacement_precondition_status_v1.csv"
        )

    def analyze(self) -> V134OIAShareShadowExecutionStubReplacementPreconditionAuditV1Report:
        coverage_report = V134MSAShareReplayMarketCoverageGapAuditV1Analyzer(self.repo_root).analyze()
        promotion_report = V134MYAShareDailyMarketPromotionReviewAuditV1Analyzer(self.repo_root).analyze()
        paired_report = V134NCASharePairedSurfaceExtensionStatusAuditV1Analyzer(self.repo_root).analyze()
        cost_report = V134MOAShareReplayCostModelFoundationAuditV1Analyzer(self.repo_root).analyze()
        corrected_recheck_report = V134PXAShareReplayShadowCorrectedRecheckAuditV1Analyzer(self.repo_root).analyze()
        lane_report = V134QEAShareShadowExecutionStubReplacementLaneAuditV1Analyzer(self.repo_root).analyze()

        cost_ready_count = 0
        for row in cost_report.rows:
            if row["component"] == "shadow_cost_models":
                cost_ready_count = int(row["coverage_note"].split("=")[1].strip())
                break

        rows = [
            {
                "precondition": "market_context_coverage_closed",
                "precondition_state": "unsatisfied",
                "supporting_count": corrected_recheck_report.summary["corrected_missing_count"],
                "blocking_reason": (
                    f"base_missing_count = {corrected_recheck_report.summary['base_missing_count']}; "
                    f"corrected_missing_count = {corrected_recheck_report.summary['corrected_missing_count']}; "
                    f"boundary_only_residual_count = {corrected_recheck_report.summary['boundary_only_residual_count']}"
                ),
            },
            {
                "precondition": "daily_market_promotion_nonblocked",
                "precondition_state": "satisfied_foundation_only",
                "supporting_count": promotion_report.summary["promotable_now_count"],
                "blocking_reason": f"promotable_now_count = {promotion_report.summary['promotable_now_count']}",
            },
            {
                "precondition": "paired_surfaces_promotive",
                "precondition_state": "satisfied_foundation_only",
                "supporting_count": paired_report.summary["index_candidate_cover_count"],
                "blocking_reason": (
                    f"index_candidate_cover_count = {paired_report.summary['index_candidate_cover_count']}; "
                    f"limit_halt_candidate_cover_count = {paired_report.summary['limit_halt_candidate_cover_count']}"
                ),
            },
            {
                "precondition": "cost_model_foundation_ready",
                "precondition_state": "satisfied_foundation_only",
                "supporting_count": cost_ready_count,
                "blocking_reason": "cost models exist but cannot promote execution journaling while only external boundary residuals still remain unresolved",
            },
            {
                "precondition": "shadow_stub_replacement_lane_materialized",
                "precondition_state": "satisfied_foundation_only",
                "supporting_count": lane_report.summary["lane_overlay_row_count"],
                "blocking_reason": (
                    f"lane_overlay_row_count = {lane_report.summary['lane_overlay_row_count']}; "
                    f"excluded_boundary_count = {lane_report.summary['excluded_boundary_count']}"
                ),
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        summary = {
            "precondition_count": len(rows),
            "unsatisfied_count": sum(row["precondition_state"] == "unsatisfied" for row in rows),
            "foundation_only_count": sum(row["precondition_state"] == "satisfied_foundation_only" for row in rows),
            "promotable_now_count": promotion_report.summary["promotable_now_count"],
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_shadow_execution_stub_replacement_preconditions_explicit",
        }
        interpretation = [
            "Shadow execution journal replacement is no longer a vague replay backlog; it now has an explicit precondition surface.",
            "The blocker is no longer paired-surface or promotion absence. Those are now foundation-ready, while market context closure remains unsatisfied only because two external boundary residuals still remain after the shadow overlay recheck.",
            "The 15-row shadow stub-replacement lane is now explicitly recognized as foundation-ready rather than being buried inside the generic replay backlog.",
        ]
        return V134OIAShareShadowExecutionStubReplacementPreconditionAuditV1Report(
            summary=summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134OIAShareShadowExecutionStubReplacementPreconditionAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134OIAShareShadowExecutionStubReplacementPreconditionAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134oi_a_share_shadow_execution_stub_replacement_precondition_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
