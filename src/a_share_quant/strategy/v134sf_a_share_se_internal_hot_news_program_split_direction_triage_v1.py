from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134se_a_share_internal_hot_news_program_split_feeds_audit_v1 import (
    V134SEAShareInternalHotNewsProgramSplitFeedsAuditV1Analyzer,
)


@dataclass(slots=True)
class V134SFAShareSEInternalHotNewsProgramSplitDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134SFAShareSEInternalHotNewsProgramSplitDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SFAShareSEInternalHotNewsProgramSplitDirectionTriageV1Report:
        report = V134SEAShareInternalHotNewsProgramSplitFeedsAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "risk_feed_row_count": report.summary["risk_feed_row_count"],
            "opportunity_feed_row_count": report.summary["opportunity_feed_row_count"],
            "critical_risk_count": report.summary["critical_risk_count"],
            "critical_opportunity_count": report.summary["critical_opportunity_count"],
            "session_handling_mode": report.summary["session_handling_mode"],
            "risk_consumer_gate": report.summary["risk_consumer_gate"],
            "opportunity_consumer_gate": report.summary["opportunity_consumer_gate"],
            "authoritative_status": "continue_serving_programs_with_split_risk_and_opportunity_feeds",
        }
        triage_rows = [
            {
                "component": "risk_first_consumer",
                "direction": "subscribe_to_program_risk_feed_first_when_the_consumer_needs_guardrail_or_veto_behavior_and_follow_the_explicit_risk_consumer_gate_for_session-specific_handling",
            },
            {
                "component": "opportunity_first_consumer",
                "direction": "subscribe_to_program_opportunity_feed_when_the_consumer_needs_guidance_or_board_watch_routing_and_follow_the_explicit_opportunity_consumer_gate_for_session-specific_handling",
            },
            {
                "component": "fallback",
                "direction": "fall_back_to_the_full_ingress_or_minimal_view_only_when_deeper_debugging_or_join_behavior_is_needed",
            },
        ]
        interpretation = [
            "This split is for consumer convenience, not a new semantic layer.",
            "The risk feed should remain stricter and shorter than the opportunity feed, while both now expose direct session-specific consumer gates.",
        ]
        return V134SFAShareSEInternalHotNewsProgramSplitDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SFAShareSEInternalHotNewsProgramSplitDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SFAShareSEInternalHotNewsProgramSplitDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134sf_a_share_se_internal_hot_news_program_split_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
