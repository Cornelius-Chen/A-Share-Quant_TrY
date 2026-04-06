from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134rk_a_share_internal_hot_news_trading_program_ingress_audit_v1 import (
    V134RKAShareInternalHotNewsTradingProgramIngressAuditV1Analyzer,
)


@dataclass(slots=True)
class V134RLAShareRKInternalHotNewsIngressDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134RLAShareRKInternalHotNewsIngressDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134RLAShareRKInternalHotNewsIngressDirectionTriageV1Report:
        report = V134RKAShareInternalHotNewsTradingProgramIngressAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "ingress_row_count": report.summary["ingress_row_count"],
            "important_ingress_count": report.summary["important_ingress_count"],
            "board_specific_ingress_count": report.summary["board_specific_ingress_count"],
            "active_hot_window_count": report.summary["active_hot_window_count"],
            "important_copy_retained_count": report.summary["important_copy_retained_count"],
            "impact_window_attached_count": report.summary["impact_window_attached_count"],
            "accelerating_ingress_count": report.summary["accelerating_ingress_count"],
            "late_impact_window_count": report.summary["late_impact_window_count"],
            "authoritative_status": "continue_feeding_downstream_from_single_internal_hot_news_ingress_surface",
        }
        triage_rows = [
            {
                "component": "consumer_entry",
                "direction": "prefer_the_single_ingress_surface_as_the_default_consumer_entry_for_trading_programs",
            },
            {
                "component": "priority_ordering",
                "direction": "use_program_priority_score_as_the_default_sort_key_before_specialized_board_or_risk_subviews",
            },
            {
                "component": "mapping_awareness",
                "direction": "respect_board_hit_state_and_beneficiary_mapping_confidence_when_a_strategy_requires_symbol-level_routing",
            },
            {
                "component": "retention_awareness",
                "direction": "respect_hot_window_state_and_important_copy_retained_when_the_consumer_needs_time-decay_or_longer-lived_message_memory",
            },
            {
                "component": "context_awareness",
                "direction": "respect_context_message_count_recent_message_density_context_recency_weighted_signal_context_velocity_context_cooling_and_impact_window_state_when_the_consumer_needs_multi-message_context",
            },
            {
                "component": "impact_decay_awareness",
                "direction": "respect_impact_decay_state_when_the_consumer_needs_to_distinguish_early_mid_or_late_memory_of_an_important_event",
            },
        ]
        interpretation = [
            "The pipeline now exposes one consumer-ready ingress surface instead of forcing the trading program to join multiple intermediate tables.",
            "Further refinements should improve mapping quality, event clustering, and decay heuristics, not re-fragment the consumer interface.",
        ]
        return V134RLAShareRKInternalHotNewsIngressDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134RLAShareRKInternalHotNewsIngressDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134RLAShareRKInternalHotNewsIngressDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134rl_a_share_rk_internal_hot_news_ingress_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
