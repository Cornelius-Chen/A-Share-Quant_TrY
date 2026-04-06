from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_focus_rotation_readiness_packet_v1 import (
    MaterializeAShareInternalHotNewsFocusRotationReadinessPacketV1,
)


@dataclass(slots=True)
class V135AUAShareInternalHotNewsFocusRotationReadinessPacketAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V135AUAShareInternalHotNewsFocusRotationReadinessPacketAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V135AUAShareInternalHotNewsFocusRotationReadinessPacketAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsFocusRotationReadinessPacketV1(
            self.repo_root
        ).materialize()
        rows = [
            {
                "component": "focus_rotation_readiness",
                "component_state": "materialized",
                "metric": "current_primary_rank",
                "value": str(materialized.summary["current_primary_rank"]),
            },
            {
                "component": "focus_rotation_readiness",
                "component_state": "materialized",
                "metric": "review_state",
                "value": materialized.summary["review_state"],
            },
            {
                "component": "focus_rotation_readiness",
                "component_state": "materialized",
                "metric": "tension_state",
                "value": materialized.summary["tension_state"],
            },
            {
                "component": "focus_rotation_readiness",
                "component_state": "materialized",
                "metric": "rotation_readiness_state",
                "value": materialized.summary["rotation_readiness_state"],
            },
            {
                "component": "focus_rotation_readiness",
                "component_state": "materialized",
                "metric": "rotation_readiness_priority",
                "value": materialized.summary["rotation_readiness_priority"],
            },
        ]
        interpretation = [
            "This packet compresses leaderboard rank, review state, and governance tension into one top-level readiness judgement.",
            "It is the simplest one-row answer to whether focus rotation should stay cold, warm up, or open immediately.",
        ]
        return V135AUAShareInternalHotNewsFocusRotationReadinessPacketAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135AUAShareInternalHotNewsFocusRotationReadinessPacketAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135AUAShareInternalHotNewsFocusRotationReadinessPacketAuditV1Analyzer(
        repo_root
    ).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135au_a_share_internal_hot_news_focus_rotation_readiness_packet_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
