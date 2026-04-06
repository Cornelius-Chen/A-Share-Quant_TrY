from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134zm_a_share_internal_hot_news_accepted_rotation_candidate_packet_audit_v1 import (
    V134ZMAShareInternalHotNewsAcceptedRotationCandidatePacketAuditV1Analyzer,
)


@dataclass(slots=True)
class V134ZNAShareZMInternalHotNewsAcceptedRotationCandidateDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134ZNAShareZMInternalHotNewsAcceptedRotationCandidateDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ZNAShareZMInternalHotNewsAcceptedRotationCandidateDirectionTriageV1Report:
        report = V134ZMAShareInternalHotNewsAcceptedRotationCandidatePacketAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            **report.summary,
            "authoritative_status": "accepted_rotation_preview_ready_without_changing_the_current_primary_consumer_chain",
        }
        triage_rows = [
            {
                "component": "accepted_rotation_preview",
                "direction": "use this packet to inspect the accepted-state outcome before any actual promotion into primary consumers",
            },
            {
                "component": "focus_rotation_visibility",
                "direction": "treat the accepted packet as an explicit visibility layer for opportunity and symbol focus rotation",
            },
            {
                "component": "promotion_discipline",
                "direction": "keep the current chain unchanged until the accepted rotation state is deliberately chosen",
            },
        ]
        interpretation = [
            "This packet makes the accepted post-rotation state visible without silently applying it.",
            "It lets downstream users compare current and accepted focus side by side.",
        ]
        return V134ZNAShareZMInternalHotNewsAcceptedRotationCandidateDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ZNAShareZMInternalHotNewsAcceptedRotationCandidateDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ZNAShareZMInternalHotNewsAcceptedRotationCandidateDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134zn_a_share_zm_internal_hot_news_accepted_rotation_candidate_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
