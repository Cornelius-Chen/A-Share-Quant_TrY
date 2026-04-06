from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ta_a_share_internal_hot_news_program_control_packet_change_signal_audit_v1 import (
    V134TAAShareInternalHotNewsProgramControlPacketChangeSignalAuditV1Analyzer,
)


@dataclass(slots=True)
class V134TBAShareTAInternalHotNewsProgramControlPacketChangeDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134TBAShareTAInternalHotNewsProgramControlPacketChangeDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134TBAShareTAInternalHotNewsProgramControlPacketChangeDirectionTriageV1Report:
        report = V134TAAShareInternalHotNewsProgramControlPacketChangeSignalAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "signal_row_count": report.summary["signal_row_count"],
            "program_driver_signal_mode_change": report.summary["program_driver_signal_mode_change"],
            "interrupt_required_change": report.summary["interrupt_required_change"],
            "top_risk_reference_change": report.summary["top_risk_reference_change"],
            "top_opportunity_reference_change": report.summary["top_opportunity_reference_change"],
            "top_watch_symbol_change": report.summary["top_watch_symbol_change"],
            "top_watch_bundle_change": report.summary["top_watch_bundle_change"],
            "signal_priority": report.summary["signal_priority"],
            "authoritative_status": "continue_serving_control-packet_change_signal_above_the_single-row_control-packet",
        }
        triage_rows = [
            {
                "component": "stable_control_packet_branch",
                "direction": "keep_the_program_on_low-cost_single-row_control-packet polling when the packet-change signal remains stable",
            },
            {
                "component": "driver_rotation_branch",
                "direction": "treat_program_driver_signal_mode_change_or_interrupt_required_change_as_the_most_important_top-level packet flips",
            },
            {
                "component": "risk_reference_rotation_branch",
                "direction": "treat_top_risk_reference_change_as_a_legitimate_top-level packet update because it changes the current dominant risk anchor",
            },
            {
                "component": "opportunity_reference_rotation_branch",
                "direction": "treat_top_opportunity_reference_change_as_a_legitimate top-level packet update because it changes the current dominant opportunity anchor",
            },
            {
                "component": "symbol_watch_rotation_branch",
                "direction": "treat_top_watch_symbol_change_or_top_watch_bundle_change_as_a_legitimate top-level packet update because it changes the current symbol-first watchset",
            },
        ]
        interpretation = [
            "This is the topmost change detector for the single-row control packet.",
            "A consumer can stay on this layer most of the time and only reopen the control packet when it changes.",
            "The layer now also captures symbol-watch rotations, so symbol-first consumers can stop one layer higher.",
        ]
        return V134TBAShareTAInternalHotNewsProgramControlPacketChangeDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134TBAShareTAInternalHotNewsProgramControlPacketChangeDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134TBAShareTAInternalHotNewsProgramControlPacketChangeDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134tb_a_share_ta_internal_hot_news_program_control_packet_change_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
