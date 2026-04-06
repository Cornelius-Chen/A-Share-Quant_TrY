from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134sa_a_share_internal_hot_news_rolling_context_audit_v1 import (
    V134SAAShareInternalHotNewsRollingContextAuditV1Analyzer,
)


@dataclass(slots=True)
class V134SBAShareSAInternalHotNewsRollingContextDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134SBAShareSAInternalHotNewsRollingContextDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SBAShareSAInternalHotNewsRollingContextDirectionTriageV1Report:
        report = V134SAAShareInternalHotNewsRollingContextAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "context_row_count": report.summary["context_row_count"],
            "important_impact_row_count": report.summary["important_impact_row_count"],
            "active_impact_count": report.summary["active_impact_count"],
            "accelerating_context_count": report.summary["accelerating_context_count"],
            "cooling_context_count": report.summary["cooling_context_count"],
            "authoritative_status": "continue_serving_trading_with_rolling_context_and_important_impact_memory",
        }
        triage_rows = [
            {
                "component": "rolling_context_delivery",
                "direction": "use_the_rolling_context_surface_for_theme_or_market-level_state_inference_with_recent_message_density_recency-weighted_signal_velocity_and_cooling_states",
            },
            {
                "component": "important_memory_delivery",
                "direction": "use_the_important_impact_window_surface_for_short-horizon_memory_of_high-impact_events",
            },
            {
                "component": "consumer_behavior",
                "direction": "combine_single-message_ingress_with_context_and_impact_memory_instead_of_overweighting_any_single_row",
            },
        ]
        interpretation = [
            "The consumer can now look at both the latest message and the rolling context around it.",
            "The next refinement should tune aggregation windows, velocity thresholds, and grouping quality rather than create more parallel consumer tables.",
        ]
        return V134SBAShareSAInternalHotNewsRollingContextDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SBAShareSAInternalHotNewsRollingContextDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SBAShareSAInternalHotNewsRollingContextDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134sb_a_share_sa_internal_hot_news_rolling_context_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
