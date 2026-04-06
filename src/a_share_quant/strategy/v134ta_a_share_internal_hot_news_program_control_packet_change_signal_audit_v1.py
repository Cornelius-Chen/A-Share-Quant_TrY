from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_control_packet_change_signal_v1 import (
    MaterializeAShareInternalHotNewsProgramControlPacketChangeSignalV1,
)


@dataclass(slots=True)
class V134TAAShareInternalHotNewsProgramControlPacketChangeSignalAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134TAAShareInternalHotNewsProgramControlPacketChangeSignalAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134TAAShareInternalHotNewsProgramControlPacketChangeSignalAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsProgramControlPacketChangeSignalV1(self.repo_root).materialize()
        rows = [
            {
                "component": "control_packet_change_signal",
                "component_state": "read_ready_internal_only",
                "metric": "signal_row_count",
                "value": str(materialized.summary["signal_row_count"]),
            },
            {
                "component": "driver_signal_mode_change",
                "component_state": "materialized",
                "metric": "program_driver_signal_mode_change",
                "value": materialized.summary["program_driver_signal_mode_change"],
            },
            {
                "component": "interrupt_required_change",
                "component_state": "materialized",
                "metric": "interrupt_required_change",
                "value": materialized.summary["interrupt_required_change"],
            },
            {
                "component": "top_risk_reference_change",
                "component_state": "materialized",
                "metric": "top_risk_reference_change",
                "value": materialized.summary["top_risk_reference_change"],
            },
            {
                "component": "top_opportunity_reference_change",
                "component_state": "materialized",
                "metric": "top_opportunity_reference_change",
                "value": materialized.summary["top_opportunity_reference_change"],
            },
            {
                "component": "top_watch_symbol_change",
                "component_state": "materialized",
                "metric": "top_watch_symbol_change",
                "value": materialized.summary["top_watch_symbol_change"],
            },
            {
                "component": "top_watch_bundle_change",
                "component_state": "materialized",
                "metric": "top_watch_bundle_change",
                "value": materialized.summary["top_watch_bundle_change"],
            },
            {
                "component": "primary_focus_replay_support_change",
                "component_state": "materialized",
                "metric": "primary_focus_source_present_change",
                "value": materialized.summary["primary_focus_source_present_change"],
            },
            {
                "component": "challenger_focus_change",
                "component_state": "materialized",
                "metric": "top_challenger_theme_change",
                "value": materialized.summary["top_challenger_theme_change"],
            },
            {
                "component": "challenger_review_attention_change",
                "component_state": "materialized",
                "metric": "challenger_review_state_change",
                "value": materialized.summary["challenger_review_state_change"],
            },
            {
                "component": "challenger_review_attention_change",
                "component_state": "materialized",
                "metric": "challenger_review_attention_state_change",
                "value": materialized.summary["challenger_review_attention_state_change"],
            },
            {
                "component": "focus_governance_tension_change",
                "component_state": "materialized",
                "metric": "focus_governance_tension_state_change",
                "value": materialized.summary["focus_governance_tension_state_change"],
            },
            {
                "component": "focus_governance_tension_change",
                "component_state": "materialized",
                "metric": "focus_governance_tension_priority_change",
                "value": materialized.summary["focus_governance_tension_priority_change"],
            },
            {
                "component": "focus_rotation_readiness_change",
                "component_state": "materialized",
                "metric": "focus_rotation_readiness_state_change",
                "value": materialized.summary["focus_rotation_readiness_state_change"],
            },
            {
                "component": "focus_rotation_readiness_change",
                "component_state": "materialized",
                "metric": "focus_rotation_readiness_priority_change",
                "value": materialized.summary["focus_rotation_readiness_priority_change"],
            },
        ]
        interpretation = [
            "This change signal sits directly above the single-row control packet.",
            "A consumer can watch this layer to know whether the topmost packet itself materially changed without reopening lower packet fields every cycle.",
            "Symbol-watch rotation is now part of that topmost packet-change decision.",
            "Primary-focus replay-support change is now also visible here, so the outer layer can detect support erosion even when the top focus reference itself has not rotated.",
            "Top challenger change is now visible here too, so the outer layer can detect the next likely rotation candidate changing before a full promotion review opens.",
            "Challenger review attention change is now visible here too, so the outer layer can react when review semantics move between background monitoring, raised attention, and open rotation review.",
            "Governance tension change is now visible here too, so the outer layer can react when ranking-vs-policy mismatch itself appears, escalates, or resolves.",
            "Focus-rotation readiness change is now visible here too, so the outer layer can react when the overall recommendation moves between hold, monitor, and rotation-review-ready states.",
        ]
        return V134TAAShareInternalHotNewsProgramControlPacketChangeSignalAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134TAAShareInternalHotNewsProgramControlPacketChangeSignalAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134TAAShareInternalHotNewsProgramControlPacketChangeSignalAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ta_a_share_internal_hot_news_program_control_packet_change_signal_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
