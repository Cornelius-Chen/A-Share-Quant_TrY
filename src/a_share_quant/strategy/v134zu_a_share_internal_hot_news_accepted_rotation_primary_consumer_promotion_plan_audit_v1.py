from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_accepted_rotation_primary_consumer_promotion_plan_v1 import (
    MaterializeAShareInternalHotNewsAcceptedRotationPrimaryConsumerPromotionPlanV1,
)


@dataclass(slots=True)
class V134ZUAShareInternalHotNewsAcceptedRotationPrimaryConsumerPromotionPlanAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134ZUAShareInternalHotNewsAcceptedRotationPrimaryConsumerPromotionPlanAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ZUAShareInternalHotNewsAcceptedRotationPrimaryConsumerPromotionPlanAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsAcceptedRotationPrimaryConsumerPromotionPlanV1(self.repo_root).materialize()
        rows = [
            {
                "component": "promotion_plan",
                "component_state": "materialized",
                "metric": "promotion_gate_state",
                "value": materialized.summary["promotion_gate_state"],
            },
            {
                "component": "promotion_plan",
                "component_state": "materialized",
                "metric": "shadow_change_signal_priority",
                "value": materialized.summary["shadow_change_signal_priority"],
            },
            {
                "component": "promotion_plan",
                "component_state": "materialized",
                "metric": "accepted_top_opportunity_theme",
                "value": materialized.summary["accepted_top_opportunity_theme"],
            },
            {
                "component": "promotion_plan",
                "component_state": "materialized",
                "metric": "accepted_top_watch_symbol",
                "value": materialized.summary["accepted_top_watch_symbol"],
            },
            {
                "component": "promotion_plan",
                "component_state": "materialized",
                "metric": "plan_step_count",
                "value": str(materialized.summary["plan_step_count"]),
            },
        ]
        interpretation = [
            "This plan converts the accepted rotation from a shadow delta into an explicit primary-consumer promotion sequence.",
            "It preserves discipline by making manual acceptance the first required step.",
        ]
        return V134ZUAShareInternalHotNewsAcceptedRotationPrimaryConsumerPromotionPlanAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ZUAShareInternalHotNewsAcceptedRotationPrimaryConsumerPromotionPlanAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ZUAShareInternalHotNewsAcceptedRotationPrimaryConsumerPromotionPlanAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134zu_a_share_internal_hot_news_accepted_rotation_primary_consumer_promotion_plan_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
