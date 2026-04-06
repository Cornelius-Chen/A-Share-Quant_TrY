from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134rc_a_share_internal_hot_news_trading_guidance_audit_v1 import (
    V134RCAShareInternalHotNewsTradingGuidanceAuditV1Analyzer,
)


@dataclass(slots=True)
class V134RDAShareRCInternalHotNewsGuidanceDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134RDAShareRCInternalHotNewsGuidanceDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134RDAShareRCInternalHotNewsGuidanceDirectionTriageV1Report:
        report = V134RCAShareInternalHotNewsTradingGuidanceAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "guidance_row_count": report.summary["guidance_row_count"],
            "guidance_event_count": report.summary["guidance_event_count"],
            "risk_event_count": report.summary["risk_event_count"],
            "trigger_event_count": report.summary["trigger_event_count"],
            "market_guidance_row_count": report.summary["market_guidance_row_count"],
            "board_signal_row_count": report.summary["board_signal_row_count"],
            "risk_queue_row_count": report.summary["risk_queue_row_count"],
            "decision_signal_row_count": report.summary["decision_signal_row_count"],
            "authoritative_status": "continue_fastlane_news_delivery_through_structured_trading_guidance_not_raw_message_fan-out",
        }
        triage_rows = [
            {
                "component": "message_normalization",
                "direction": "keep_converting_fastlane_messages_into_structured_guidance_fields_for_the_trading_layer",
            },
            {
                "component": "board_mapping",
                "direction": "route_theme-specific_messages_to_board_guidance_and_candidate_beneficiary_symbols_when_keyword_mapping_exists",
            },
            {
                "component": "trading_delivery",
                "direction": "feed_the_trading_program_from_the_guidance_surface_first_then_iterate_grading_rules",
            },
            {
                "component": "market_guidance_delivery",
                "direction": "deliver_guidance_events_to_a_dedicated_market_guidance_view_for_top-down_decision_updates",
            },
            {
                "component": "risk_queue_delivery",
                "direction": "deliver_risk_events_to_a_dedicated_risk_queue_view_for_veto_and_risk-tightening_logic",
            },
            {
                "component": "board_signal_delivery",
                "direction": "deliver_theme-bound_messages_to_a_board_signal_view_when_binding_confidence_is_not_none",
            },
            {
                "component": "decision_signal_delivery",
                "direction": "deliver_all_messages_to_a_decision_signal_view_with_scored_direction_strength_and_authority_fields",
            },
        ]
        interpretation = [
            "The pipeline now serves trading through structured guidance, not raw news text.",
            "The pipeline can now fan out one news stream into market guidance, board signal, risk queue, and decision signal views without reopening the source-side architecture.",
        ]
        return V134RDAShareRCInternalHotNewsGuidanceDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134RDAShareRCInternalHotNewsGuidanceDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134RDAShareRCInternalHotNewsGuidanceDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134rd_a_share_rc_internal_hot_news_guidance_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
