from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134sy_a_share_internal_hot_news_program_control_packet_audit_v1 import (
    V134SYAShareInternalHotNewsProgramControlPacketAuditV1Analyzer,
)


@dataclass(slots=True)
class V134SZAShareSYInternalHotNewsProgramControlPacketDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134SZAShareSYInternalHotNewsProgramControlPacketDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SZAShareSYInternalHotNewsProgramControlPacketDirectionTriageV1Report:
        report = V134SYAShareInternalHotNewsProgramControlPacketAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "packet_row_count": report.summary["packet_row_count"],
            "program_driver_signal_mode": report.summary["program_driver_signal_mode"],
            "interrupt_required": report.summary["interrupt_required"],
            "trading_day_state": report.summary["trading_day_state"],
            "session_phase": report.summary["session_phase"],
            "top_opportunity_primary_theme_slug": report.summary["top_opportunity_primary_theme_slug"],
            "top_opportunity_theme_governance_state": report.summary["top_opportunity_theme_governance_state"],
            "top_opportunity_mapping_confidence": report.summary["top_opportunity_mapping_confidence"],
            "top_opportunity_linkage_class": report.summary["top_opportunity_linkage_class"],
            "top_opportunity_beneficiary_symbols_top5": report.summary["top_opportunity_beneficiary_symbols_top5"],
            "top_watch_symbol": report.summary["top_watch_symbol"],
            "top_watch_primary_theme_slug": report.summary["top_watch_primary_theme_slug"],
            "top_watch_mapping_confidence": report.summary["top_watch_mapping_confidence"],
            "top_watch_linkage_class": report.summary["top_watch_linkage_class"],
            "top_watch_symbols_top5": report.summary["top_watch_symbols_top5"],
            "top_watch_symbol_change": report.summary["top_watch_symbol_change"],
            "symbol_watch_change_signal_priority": report.summary["symbol_watch_change_signal_priority"],
            "authoritative_status": "continue_serving_single-row_control-packet_above_status_snapshot_and_driver-signal_layers",
        }
        triage_rows = [
            {
                "component": "passive_control_packet_branch",
                "direction": "keep_the_program_on_low-cost_single-row_polling_when_the_control_packet_stays_in_passive_mode",
            },
            {
                "component": "elevated_control_packet_branch",
                "direction": "escalate_attention_when_the_control_packet_rotates_into_elevated_driver_signal_mode",
            },
            {
                "component": "interrupt_control_packet_branch",
                "direction": "interrupt_the_current_consumer_loop_when_the_control_packet_sets_interrupt_required_to_true",
            },
            {
                "component": "timing_context_branch",
                "direction": "always interpret_the_top_risk_and_top_opportunity references through the packet trading-day and session-phase context",
            },
        ]
        interpretation = [
            "This is the single-row topmost control surface for the internal hot-news program stack.",
            "A consumer can stop at this layer unless it needs to open lower tables for deeper detail.",
            "The control packet now carries top-opportunity beneficiary mapping detail, reducing the need for an extra round-trip into the opportunity feed.",
            "It also carries the top governed watch symbol and top-five watch bundle, so a symbol-first consumer can start routing from the packet itself.",
            "Because symbol-watch change state is also embedded here, an outer consumer can decide whether to reopen symbol-level views without another layer hop.",
            "It also carries the governed primary theme so top-level routing does not need to flatten overlapping theme hits on its own.",
        ]
        return V134SZAShareSYInternalHotNewsProgramControlPacketDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SZAShareSYInternalHotNewsProgramControlPacketDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SZAShareSYInternalHotNewsProgramControlPacketDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134sz_a_share_sy_internal_hot_news_program_control_packet_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
