from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134my_a_share_daily_market_promotion_review_audit_v1 import (
    V134MYAShareDailyMarketPromotionReviewAuditV1Analyzer,
)


@dataclass(slots=True)
class V134MZAShareMYDailyMarketPromotionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134MZAShareMYDailyMarketPromotionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134MZAShareMYDailyMarketPromotionDirectionTriageV1Report:
        report = V134MYAShareDailyMarketPromotionReviewAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "promotable_now_count": report.summary["promotable_now_count"],
            "blocked_by_paired_surface_count": report.summary["blocked_by_paired_surface_count"],
            "authoritative_status": "daily_market_promotion_reopened_with_promotable_subset_after_semantic_pair_materialization",
        }
        triage_rows = [
            {
                "component": "daily_market_candidate_rows",
                "direction": "treat_promotable_rows_as_controlled_replay-facing_subset_not_as_execution_authority",
            },
            {
                "component": "paired_surfaces",
                "direction": "retire_old_pair-gap_language_and_use_the_semantic_pair_layer_as_the_new_replay_base",
            },
        ]
        interpretation = [
            "Controlled promotion review now confirms a promotable subset rather than a fully blocked paired-surface state.",
            "The next valid step is replay-side precondition recheck from this subset, not unilateral execution opening.",
        ]
        return V134MZAShareMYDailyMarketPromotionDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134MZAShareMYDailyMarketPromotionDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MZAShareMYDailyMarketPromotionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134mz_a_share_my_daily_market_promotion_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
