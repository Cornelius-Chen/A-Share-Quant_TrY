from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134zq_a_share_internal_hot_news_accepted_rotation_shadow_control_packet_audit_v1 import (
    V134ZQAShareInternalHotNewsAcceptedRotationShadowControlPacketAuditV1Analyzer,
)


@dataclass(slots=True)
class V134ZRAShareZQInternalHotNewsAcceptedRotationShadowControlDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134ZRAShareZQInternalHotNewsAcceptedRotationShadowControlDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ZRAShareZQInternalHotNewsAcceptedRotationShadowControlDirectionTriageV1Report:
        report = V134ZQAShareInternalHotNewsAcceptedRotationShadowControlPacketAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            **report.summary,
            "authoritative_status": "accepted_rotation_shadow_control_packet_ready_without_mutating_the_current_primary_control_packet",
        }
        triage_rows = [
            {
                "component": "shadow_control_visibility",
                "direction": "use the shadow control packet to inspect accepted post-rotation control state without touching the current primary packet",
            },
            {
                "component": "promotion_guard",
                "direction": "keep the primary control packet unchanged until the accepted rotation is deliberately promoted",
            },
            {
                "component": "control_consumer_review",
                "direction": "review shadow control impact before deciding whether top-level consumers should adopt the accepted rotation",
            },
        ]
        interpretation = [
            "The accepted rotation is now visible not only as a snapshot but also as a control-packet-level shadow state.",
            "This preserves promotion discipline while exposing the likely top-level control outcome.",
        ]
        return V134ZRAShareZQInternalHotNewsAcceptedRotationShadowControlDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ZRAShareZQInternalHotNewsAcceptedRotationShadowControlDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ZRAShareZQInternalHotNewsAcceptedRotationShadowControlDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134zr_a_share_zq_internal_hot_news_accepted_rotation_shadow_control_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
