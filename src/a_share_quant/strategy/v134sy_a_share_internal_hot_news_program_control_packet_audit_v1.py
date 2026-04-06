from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_control_packet_v1 import (
    MaterializeAShareInternalHotNewsProgramControlPacketV1,
)


@dataclass(slots=True)
class V134SYAShareInternalHotNewsProgramControlPacketAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134SYAShareInternalHotNewsProgramControlPacketAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SYAShareInternalHotNewsProgramControlPacketAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsProgramControlPacketV1(self.repo_root).materialize()
        rows = [
            {
                "component": "program_control_packet",
                "component_state": "read_ready_internal_only",
                "metric": "packet_row_count",
                "value": str(materialized.summary["packet_row_count"]),
            },
            {
                "component": "driver_signal_mode",
                "component_state": "materialized",
                "metric": "program_driver_signal_mode",
                "value": materialized.summary["program_driver_signal_mode"],
            },
            {
                "component": "interrupt_required",
                "component_state": "materialized",
                "metric": "interrupt_required",
                "value": materialized.summary["interrupt_required"],
            },
            {
                "component": "top_risk_reference",
                "component_state": "materialized",
                "metric": "top_risk_telegraph_id",
                "value": materialized.summary["top_risk_telegraph_id"],
            },
            {
                "component": "top_opportunity_reference",
                "component_state": "materialized",
                "metric": "top_opportunity_telegraph_id",
                "value": materialized.summary["top_opportunity_telegraph_id"],
            },
            {
                "component": "top_opportunity_mapping",
                "component_state": "materialized",
                "metric": "top_opportunity_mapping_confidence",
                "value": materialized.summary["top_opportunity_mapping_confidence"],
            },
            {
                "component": "top_opportunity_mapping",
                "component_state": "materialized",
                "metric": "top_opportunity_linkage_class",
                "value": materialized.summary["top_opportunity_linkage_class"],
            },
            {
                "component": "top_opportunity_beneficiary_symbols",
                "component_state": "materialized",
                "metric": "top_opportunity_beneficiary_symbols_top5",
                "value": materialized.summary["top_opportunity_beneficiary_symbols_top5"],
            },
            {
                "component": "top_watch_symbol",
                "component_state": "materialized",
                "metric": "top_watch_symbol",
                "value": materialized.summary["top_watch_symbol"],
            },
            {
                "component": "top_watch_theme",
                "component_state": "materialized",
                "metric": "top_watch_primary_theme_slug",
                "value": materialized.summary["top_watch_primary_theme_slug"],
            },
            {
                "component": "top_watch_bundle",
                "component_state": "materialized",
                "metric": "top_watch_symbols_top5",
                "value": materialized.summary["top_watch_symbols_top5"],
            },
            {
                "component": "top_watch_bundle",
                "component_state": "materialized",
                "metric": "top_watch_linkage_class",
                "value": materialized.summary["top_watch_linkage_class"],
            },
            {
                "component": "top_watch_change_signal",
                "component_state": "materialized",
                "metric": "top_watch_symbol_change",
                "value": materialized.summary["top_watch_symbol_change"],
            },
            {
                "component": "top_watch_change_signal",
                "component_state": "materialized",
                "metric": "symbol_watch_change_signal_priority",
                "value": materialized.summary["symbol_watch_change_signal_priority"],
            },
            {
                "component": "primary_focus_replay_support",
                "component_state": "materialized",
                "metric": "primary_focus_match_row_count",
                "value": materialized.summary["primary_focus_match_row_count"],
            },
            {
                "component": "primary_focus_replay_support",
                "component_state": "materialized",
                "metric": "primary_focus_source_present_count",
                "value": materialized.summary["primary_focus_source_present_count"],
            },
            {
                "component": "primary_focus_replay_support",
                "component_state": "materialized",
                "metric": "primary_focus_dual_match_count",
                "value": materialized.summary["primary_focus_dual_match_count"],
            },
            {
                "component": "focus_competition_leaderboard",
                "component_state": "materialized",
                "metric": "current_primary_rank",
                "value": materialized.summary["current_primary_rank"],
            },
            {
                "component": "focus_competition_leaderboard",
                "component_state": "materialized",
                "metric": "incumbent_is_focus_leader",
                "value": materialized.summary["incumbent_is_focus_leader"],
            },
            {
                "component": "focus_governance_tension",
                "component_state": "materialized",
                "metric": "focus_governance_tension_state",
                "value": materialized.summary["focus_governance_tension_state"],
            },
            {
                "component": "focus_governance_tension",
                "component_state": "materialized",
                "metric": "focus_governance_tension_priority",
                "value": materialized.summary["focus_governance_tension_priority"],
            },
            {
                "component": "focus_rotation_readiness",
                "component_state": "materialized",
                "metric": "focus_rotation_readiness_state",
                "value": materialized.summary["focus_rotation_readiness_state"],
            },
            {
                "component": "focus_rotation_readiness",
                "component_state": "materialized",
                "metric": "focus_rotation_readiness_priority",
                "value": materialized.summary["focus_rotation_readiness_priority"],
            },
            {
                "component": "challenger_focus_board",
                "component_state": "materialized",
                "metric": "top_challenger_theme_slug",
                "value": materialized.summary["top_challenger_theme_slug"],
            },
            {
                "component": "challenger_focus_board",
                "component_state": "materialized",
                "metric": "top_challenger_symbol",
                "value": materialized.summary["top_challenger_symbol"],
            },
            {
                "component": "challenger_focus_board",
                "component_state": "materialized",
                "metric": "top_challenger_support_row_count",
                "value": materialized.summary["top_challenger_support_row_count"],
            },
            {
                "component": "challenger_review_attention",
                "component_state": "materialized",
                "metric": "challenger_review_state",
                "value": materialized.summary["challenger_review_state"],
            },
            {
                "component": "challenger_review_attention",
                "component_state": "materialized",
                "metric": "challenger_review_attention_state",
                "value": materialized.summary["challenger_review_attention_state"],
            },
            {
                "component": "challenger_review_attention",
                "component_state": "materialized",
                "metric": "challenger_review_attention_priority",
                "value": materialized.summary["challenger_review_attention_priority"],
            },
            {
                "component": "top_opportunity_theme_governance",
                "component_state": "materialized",
                "metric": "top_opportunity_primary_theme_slug",
                "value": materialized.summary["top_opportunity_primary_theme_slug"],
            },
            {
                "component": "top_opportunity_theme_governance",
                "component_state": "materialized",
                "metric": "top_opportunity_theme_governance_state",
                "value": materialized.summary["top_opportunity_theme_governance_state"],
            },
        ]
        interpretation = [
            "This control packet is the single-row outermost consumer artifact for the internal hot-news stack.",
            "A program can poll this one row to learn current health, timing context, driver signal mode, and the top risk/opportunity references.",
            "The top opportunity mapping payload is now also visible here so the outer control layer can forward beneficiary symbols without reopening lower consumer views.",
            "The current top watch symbol and top-five watch bundle are now also visible here, so symbol-first routing can stay on the control packet for the first decision.",
            "Linkage class is now visible here too, so the outer control layer can distinguish direct beneficiaries from proxy-quality watches.",
            "The packet now also carries symbol-watch change state, so the outer control layer can tell whether the watchset rotated without reopening lower symbol-watch surfaces.",
            "The top opportunity primary theme is now explicit here too, so overlap governance is already settled before the outer control layer reads the packet.",
            "The current accepted primary focus now also carries replay-support counts here, so the outer layer can see whether the top focus is still backed by real candidate-lane evidence.",
            "The packet now also carries leaderboard rank context, so the outer layer can see whether the incumbent is still first in the field or merely being held by review policy.",
            "The packet now also carries governance-tension state, so the outer layer can explicitly see when rank ordering and review policy disagree.",
            "The packet now also carries focus-rotation readiness, so the outer layer can read one explicit recommendation on whether to hold, monitor, or prepare the next rotation review.",
            "The strongest current challenger is now visible here too, so the outer layer can track the next likely rotation candidate without reopening the challenger board surface.",
            "The packet now also carries challenger review attention state, so the outer control layer can distinguish hold, raised review attention, and true open-rotation review from one row.",
        ]
        return V134SYAShareInternalHotNewsProgramControlPacketAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SYAShareInternalHotNewsProgramControlPacketAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SYAShareInternalHotNewsProgramControlPacketAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134sy_a_share_internal_hot_news_program_control_packet_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
