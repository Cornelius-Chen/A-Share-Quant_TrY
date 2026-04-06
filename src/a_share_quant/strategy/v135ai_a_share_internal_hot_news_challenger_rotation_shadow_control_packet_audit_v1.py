from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_challenger_rotation_shadow_control_packet_v1 import (
    MaterializeAShareInternalHotNewsChallengerRotationShadowControlPacketV1,
)


@dataclass(slots=True)
class V135AIAShareInternalHotNewsChallengerRotationShadowControlPacketAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V135AIAShareInternalHotNewsChallengerRotationShadowControlPacketAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V135AIAShareInternalHotNewsChallengerRotationShadowControlPacketAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsChallengerRotationShadowControlPacketV1(self.repo_root).materialize()
        rows = [
            {
                "component": "challenger_rotation_shadow_control_packet",
                "component_state": "materialized",
                "metric": "current_top_opportunity_theme",
                "value": materialized.summary["current_top_opportunity_theme"],
            },
            {
                "component": "challenger_rotation_shadow_control_packet",
                "component_state": "materialized",
                "metric": "shadow_top_opportunity_theme",
                "value": materialized.summary["shadow_top_opportunity_theme"],
            },
            {
                "component": "challenger_rotation_shadow_control_packet",
                "component_state": "materialized",
                "metric": "current_top_watch_symbol",
                "value": materialized.summary["current_top_watch_symbol"],
            },
            {
                "component": "challenger_rotation_shadow_control_packet",
                "component_state": "materialized",
                "metric": "shadow_top_watch_symbol",
                "value": materialized.summary["shadow_top_watch_symbol"],
            },
        ]
        interpretation = [
            "This control packet shows how the top-level consumer control view would look if the challenger focus were accepted.",
            "It remains a shadow-only preview and does not promote the challenger into the primary chain.",
        ]
        return V135AIAShareInternalHotNewsChallengerRotationShadowControlPacketAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135AIAShareInternalHotNewsChallengerRotationShadowControlPacketAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135AIAShareInternalHotNewsChallengerRotationShadowControlPacketAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135ai_a_share_internal_hot_news_challenger_rotation_shadow_control_packet_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
