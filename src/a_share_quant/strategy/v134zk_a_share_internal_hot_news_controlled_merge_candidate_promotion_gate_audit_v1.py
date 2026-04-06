from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_controlled_merge_candidate_promotion_gate_v1 import (
    MaterializeAShareInternalHotNewsControlledMergeCandidatePromotionGateV1,
)


@dataclass(slots=True)
class V134ZKAShareInternalHotNewsControlledMergeCandidatePromotionGateAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134ZKAShareInternalHotNewsControlledMergeCandidatePromotionGateAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ZKAShareInternalHotNewsControlledMergeCandidatePromotionGateAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsControlledMergeCandidatePromotionGateV1(self.repo_root).materialize()
        rows = [
            {
                "component": "promotion_gate",
                "component_state": "materialized",
                "metric": "preview_row_count",
                "value": str(materialized.summary["preview_row_count"]),
            },
            {
                "component": "promotion_gate",
                "component_state": "materialized",
                "metric": "additive_preview_count",
                "value": str(materialized.summary["additive_preview_count"]),
            },
            {
                "component": "promotion_gate",
                "component_state": "measured",
                "metric": "top_opportunity_change_if_promoted",
                "value": materialized.summary["top_opportunity_change_if_promoted"],
            },
            {
                "component": "promotion_gate",
                "component_state": "measured",
                "metric": "top_watch_change_if_promoted",
                "value": materialized.summary["top_watch_change_if_promoted"],
            },
            {
                "component": "promotion_gate",
                "component_state": "decision_ready",
                "metric": "promotable_now",
                "value": "true" if materialized.summary["promotable_now"] else "false",
            },
        ]
        interpretation = [
            "This gate turns downstream consumer impact into an explicit promotion decision.",
            "It prevents silent second-source merge from rotating top opportunity or top watch without an intentional gate decision.",
        ]
        return V134ZKAShareInternalHotNewsControlledMergeCandidatePromotionGateAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ZKAShareInternalHotNewsControlledMergeCandidatePromotionGateAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ZKAShareInternalHotNewsControlledMergeCandidatePromotionGateAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134zk_a_share_internal_hot_news_controlled_merge_candidate_promotion_gate_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
