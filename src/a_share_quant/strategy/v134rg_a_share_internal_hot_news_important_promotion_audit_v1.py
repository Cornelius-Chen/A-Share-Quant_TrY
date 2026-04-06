from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_important_promotion_v1 import (
    MaterializeAShareInternalHotNewsImportantPromotionV1,
)


@dataclass(slots=True)
class V134RGAShareInternalHotNewsImportantPromotionAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134RGAShareInternalHotNewsImportantPromotionAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134RGAShareInternalHotNewsImportantPromotionAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsImportantPromotionV1(self.repo_root).materialize()
        rows = [
            {
                "component": "important_promotion_registry",
                "component_state": "materialized",
                "metric": "important_promotion_row_count",
                "value": str(materialized.summary["important_promotion_row_count"]),
            },
            {
                "component": "important_trading_queue",
                "component_state": "read_ready_internal_only",
                "metric": "important_queue_row_count",
                "value": str(materialized.summary["important_queue_row_count"]),
            },
            {
                "component": "tier_split",
                "component_state": "materialized",
                "metric": "tier_1_count",
                "value": str(materialized.summary["tier_1_count"]),
            },
        ]
        interpretation = [
            "Important hot-news promotion is now based on deduped trading semantics rather than only raw keyword hits.",
            "The trading layer can consume a refined important queue after clustering, scoring, and guidance classification.",
        ]
        return V134RGAShareInternalHotNewsImportantPromotionAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134RGAShareInternalHotNewsImportantPromotionAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134RGAShareInternalHotNewsImportantPromotionAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134rg_a_share_internal_hot_news_important_promotion_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
