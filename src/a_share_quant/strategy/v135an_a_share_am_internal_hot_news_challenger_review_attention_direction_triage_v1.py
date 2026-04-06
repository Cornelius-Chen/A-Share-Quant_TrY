from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v135am_a_share_internal_hot_news_challenger_review_attention_packet_audit_v1 import (
    V135AMAShareInternalHotNewsChallengerReviewAttentionPacketAuditV1Analyzer,
)


@dataclass(slots=True)
class V135ANAShareAMInternalHotNewsChallengerReviewAttentionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V135ANAShareAMInternalHotNewsChallengerReviewAttentionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V135ANAShareAMInternalHotNewsChallengerReviewAttentionDirectionTriageV1Report:
        report = V135AMAShareInternalHotNewsChallengerReviewAttentionPacketAuditV1Analyzer(
            self.repo_root
        ).analyze()
        summary = {
            "incumbent_theme_slug": report.summary["incumbent_theme_slug"],
            "challenger_theme_slug": report.summary["challenger_theme_slug"],
            "support_delta_vs_incumbent": report.summary["support_delta_vs_incumbent"],
            "review_state": report.summary["review_state"],
            "attention_state": report.summary["attention_state"],
            "attention_priority": report.summary["attention_priority"],
            "authoritative_status": "challenger_review_attention_packet_materialized",
        }
        triage_rows = [
            {
                "component": "incumbent_hold",
                "direction": "keep the incumbent primary focus live while the challenger review attention packet remains below full open-rotation state.",
            },
            {
                "component": "challenger_attention",
                "direction": "raise or lower challenger review attention directly from the packet instead of reopening the full review chain for every poll.",
            },
            {
                "component": "rotation_gate",
                "direction": "only escalate from attention to full rotation once review state crosses into open-next-rotation territory.",
            },
        ]
        interpretation = [
            "This packet is the compact stopline between routine challenger monitoring and a new accepted-rotation rollout.",
            "It keeps top-level review semantics visible without silently promoting the challenger into the primary consumer chain.",
        ]
        return V135ANAShareAMInternalHotNewsChallengerReviewAttentionDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135ANAShareAMInternalHotNewsChallengerReviewAttentionDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135ANAShareAMInternalHotNewsChallengerReviewAttentionDirectionTriageV1Analyzer(
        repo_root
    ).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135an_a_share_am_internal_hot_news_challenger_review_attention_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
