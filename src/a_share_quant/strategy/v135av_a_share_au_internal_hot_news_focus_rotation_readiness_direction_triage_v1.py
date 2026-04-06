from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v135au_a_share_internal_hot_news_focus_rotation_readiness_packet_audit_v1 import (
    V135AUAShareInternalHotNewsFocusRotationReadinessPacketAuditV1Analyzer,
)


@dataclass(slots=True)
class V135AVAShareAUInternalHotNewsFocusRotationReadinessDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V135AVAShareAUInternalHotNewsFocusRotationReadinessDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V135AVAShareAUInternalHotNewsFocusRotationReadinessDirectionTriageV1Report:
        report = V135AUAShareInternalHotNewsFocusRotationReadinessPacketAuditV1Analyzer(
            self.repo_root
        ).analyze()
        summary = {
            "current_primary_theme_slug": report.summary["current_primary_theme_slug"],
            "current_primary_rank": report.summary["current_primary_rank"],
            "leader_theme_slug": report.summary["leader_theme_slug"],
            "review_state": report.summary["review_state"],
            "tension_state": report.summary["tension_state"],
            "rotation_readiness_state": report.summary["rotation_readiness_state"],
            "rotation_readiness_priority": report.summary["rotation_readiness_priority"],
            "authoritative_status": "focus_rotation_readiness_packet_materialized",
        }
        triage_rows = [
            {
                "component": "single_row_readiness",
                "direction": "use this packet as the one-row answer for whether focus rotation should remain cold, warm up, or fully open.",
            },
            {
                "component": "review_discipline",
                "direction": "keep rotation closed when readiness says rank alone is insufficient, even if the incumbent is no longer leader.",
            },
            {
                "component": "promotion_gate",
                "direction": "only escalate to shadow promotion or acceptance when readiness climbs into the explicit open-review state.",
            },
        ]
        interpretation = [
            "This packet reduces several interacting governance surfaces to one operational readiness judgement.",
            "It is useful for top-level consumers that do not want to reason through rank, tension, and review separately every cycle.",
        ]
        return V135AVAShareAUInternalHotNewsFocusRotationReadinessDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135AVAShareAUInternalHotNewsFocusRotationReadinessDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135AVAShareAUInternalHotNewsFocusRotationReadinessDirectionTriageV1Analyzer(
        repo_root
    ).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135av_a_share_au_internal_hot_news_focus_rotation_readiness_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
