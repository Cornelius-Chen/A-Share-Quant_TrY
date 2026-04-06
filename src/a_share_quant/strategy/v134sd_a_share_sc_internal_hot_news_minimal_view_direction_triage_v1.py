from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134sc_a_share_internal_hot_news_trading_program_minimal_view_audit_v1 import (
    V134SCAShareInternalHotNewsTradingProgramMinimalViewAuditV1Analyzer,
)


@dataclass(slots=True)
class V134SDAShareSCInternalHotNewsMinimalViewDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134SDAShareSCInternalHotNewsMinimalViewDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SDAShareSCInternalHotNewsMinimalViewDirectionTriageV1Report:
        report = V134SCAShareInternalHotNewsTradingProgramMinimalViewAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "minimal_view_row_count": report.summary["minimal_view_row_count"],
            "risk_guardrail_count": report.summary["risk_guardrail_count"],
            "top_down_guidance_count": report.summary["top_down_guidance_count"],
            "board_watch_trigger_count": report.summary["board_watch_trigger_count"],
            "symbol_focus_available_count": report.summary["symbol_focus_available_count"],
            "authoritative_status": "continue_serving_downstream_with_compact_trading_program_minimal_view",
        }
        triage_rows = [
            {
                "component": "consumer_entry",
                "direction": "prefer_the_minimal_view_when_the_trading_program_needs_a_short_stable_schema_for_first-pass_routing",
            },
            {
                "component": "risk_handling",
                "direction": "use_consumer_action_class_risk_guardrail_as_the_first_filter_before_finer_symbol_or_board_logic",
            },
            {
                "component": "focus_selection",
                "direction": "use_consumer_focus_class_to_separate_market_level_board_level_and_symbol_ready_messages",
            },
        ]
        interpretation = [
            "The next consumer does not need to read every enrichment field from the full ingress surface.",
            "The minimal view is the better first-pass feed; the full ingress remains available for deeper joins and diagnostics.",
        ]
        return V134SDAShareSCInternalHotNewsMinimalViewDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SDAShareSCInternalHotNewsMinimalViewDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SDAShareSCInternalHotNewsMinimalViewDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134sd_a_share_sc_internal_hot_news_minimal_view_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
