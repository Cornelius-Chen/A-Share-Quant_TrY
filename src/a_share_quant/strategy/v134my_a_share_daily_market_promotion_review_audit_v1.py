from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.market.materialize_a_share_daily_market_promotion_review_v1 import (
    MaterializeAShareDailyMarketPromotionReviewV1,
)


@dataclass(slots=True)
class V134MYAShareDailyMarketPromotionReviewAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134MYAShareDailyMarketPromotionReviewAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_daily_market_promotion_review_status_v1.csv"

    def analyze(self) -> V134MYAShareDailyMarketPromotionReviewAuditV1Report:
        materialized = MaterializeAShareDailyMarketPromotionReviewV1(self.repo_root).materialize()
        summary = materialized.summary
        rows = [
            {
                "component": "daily_market_promotion_review",
                "component_state": "materialized_controlled_review_surface_with_promotable_subset",
                "artifact_path": summary["review_path"],
                "coverage_note": f"promotable_now_count = {summary['promotable_now_count']}",
            },
            {
                "component": "promotion_review_residual",
                "component_state": "materialized_named_residuals",
                "artifact_path": summary["residual_path"],
                "coverage_note": f"blocked_no_candidate_count = {summary['blocked_no_candidate_count']}",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        report_summary = {
            "review_row_count": summary["review_row_count"],
            "promotable_now_count": summary["promotable_now_count"],
            "blocked_by_paired_surface_count": summary["blocked_by_paired_surface_count"],
            "blocked_no_candidate_count": summary["blocked_no_candidate_count"],
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_daily_market_promotion_review_surface_materialized",
        }
        interpretation = [
            "Daily market extension is no longer just a candidate layer; it now has a controlled promotion review with a promotable subset.",
            "Most shadow rows are now promotable under the semantic pair layer, while a smaller named residual remains blocked by missing candidate cover.",
        ]
        return V134MYAShareDailyMarketPromotionReviewAuditV1Report(
            summary=report_summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134MYAShareDailyMarketPromotionReviewAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MYAShareDailyMarketPromotionReviewAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134my_a_share_daily_market_promotion_review_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
