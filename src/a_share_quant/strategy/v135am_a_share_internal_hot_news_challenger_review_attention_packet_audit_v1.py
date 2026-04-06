from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_challenger_review_attention_packet_v1 import (
    MaterializeAShareInternalHotNewsChallengerReviewAttentionPacketV1,
)


@dataclass(slots=True)
class V135AMAShareInternalHotNewsChallengerReviewAttentionPacketAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V135AMAShareInternalHotNewsChallengerReviewAttentionPacketAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V135AMAShareInternalHotNewsChallengerReviewAttentionPacketAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsChallengerReviewAttentionPacketV1(
            self.repo_root
        ).materialize()
        rows = [
            {
                "component": "incumbent_focus",
                "component_state": "materialized",
                "metric": "incumbent_theme_slug",
                "value": materialized.summary["incumbent_theme_slug"],
            },
            {
                "component": "challenger_focus",
                "component_state": "materialized",
                "metric": "challenger_theme_slug",
                "value": materialized.summary["challenger_theme_slug"],
            },
            {
                "component": "challenger_review",
                "component_state": "materialized",
                "metric": "review_state",
                "value": materialized.summary["review_state"],
            },
            {
                "component": "challenger_review",
                "component_state": "materialized",
                "metric": "attention_state",
                "value": materialized.summary["attention_state"],
            },
            {
                "component": "challenger_review",
                "component_state": "materialized",
                "metric": "attention_priority",
                "value": materialized.summary["attention_priority"],
            },
        ]
        interpretation = [
            "This packet converts incumbent-vs-challenger review into one explicit attention payload for outer consumers.",
            "It lets the top control layer distinguish background monitoring from elevated challenger review without reopening lower review surfaces.",
        ]
        return V135AMAShareInternalHotNewsChallengerReviewAttentionPacketAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135AMAShareInternalHotNewsChallengerReviewAttentionPacketAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135AMAShareInternalHotNewsChallengerReviewAttentionPacketAuditV1Analyzer(
        repo_root
    ).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135am_a_share_internal_hot_news_challenger_review_attention_packet_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
