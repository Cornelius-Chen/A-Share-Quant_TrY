from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_challenger_primary_consumer_promotion_plan_v1 import (
    MaterializeAShareInternalHotNewsChallengerPrimaryConsumerPromotionPlanV1,
)


@dataclass(slots=True)
class V135AKAShareInternalHotNewsChallengerPrimaryConsumerPromotionPlanAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V135AKAShareInternalHotNewsChallengerPrimaryConsumerPromotionPlanAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V135AKAShareInternalHotNewsChallengerPrimaryConsumerPromotionPlanAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsChallengerPrimaryConsumerPromotionPlanV1(self.repo_root).materialize()
        rows = [
            {
                "component": "challenger_promotion_plan",
                "component_state": "materialized",
                "metric": "rotation_review_state",
                "value": materialized.summary["rotation_review_state"],
            },
            {
                "component": "challenger_promotion_plan",
                "component_state": "materialized",
                "metric": "shadow_change_signal_priority",
                "value": materialized.summary["shadow_change_signal_priority"],
            },
            {
                "component": "challenger_promotion_plan",
                "component_state": "materialized",
                "metric": "challenger_top_opportunity_theme",
                "value": materialized.summary["challenger_top_opportunity_theme"],
            },
            {
                "component": "challenger_promotion_plan",
                "component_state": "materialized",
                "metric": "challenger_top_watch_symbol",
                "value": materialized.summary["challenger_top_watch_symbol"],
            },
            {
                "component": "challenger_promotion_plan",
                "component_state": "materialized",
                "metric": "plan_step_count",
                "value": str(materialized.summary["plan_step_count"]),
            },
        ]
        interpretation = [
            "This plan converts the challenger shadow delta into an explicit primary-consumer promotion sequence.",
            "It preserves discipline by making manual acceptance the first required step even after the challenger review opens.",
        ]
        return V135AKAShareInternalHotNewsChallengerPrimaryConsumerPromotionPlanAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135AKAShareInternalHotNewsChallengerPrimaryConsumerPromotionPlanAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135AKAShareInternalHotNewsChallengerPrimaryConsumerPromotionPlanAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135ak_a_share_internal_hot_news_challenger_primary_consumer_promotion_plan_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
