from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from a_share_quant.info_center.automation.pipeline_jobs.a_share_trade_timing import (
    resolve_trade_timing,
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _to_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _consumer_action_class(row: dict[str, str]) -> str:
    if row["routing_bucket"] == "risk_layer":
        return "risk_guardrail"
    if row["importance_tier"] == "tier_1_market_guidance":
        return "top_down_guidance"
    if row["routing_bucket"] == "guidance_layer":
        return "theme_guidance"
    if row["routing_bucket"] == "board_trigger_layer":
        return "board_watch_trigger"
    return "watch_only"


def _consumer_focus_class(row: dict[str, str]) -> str:
    if row["target_theme_slug"] == "broad_market":
        return "market_level"
    if row["board_hit_state"] == "theme_detected_but_member_surface_missing":
        return "theme_only_mapping_gap"
    if row["board_hit_state"] in {
        "theme_detected_and_curated_beneficiary_matched",
        "theme_detected_and_member_surface_matched",
        "theme_detected_with_symbol_route",
    } and row["beneficiary_mapping_confidence"] in {"high", "medium"}:
        return "symbol_focus_available"
    return "board_level"


def _window_state(row: dict[str, str]) -> str:
    if row["impact_window_state"] != "not_in_impact_window":
        return row["impact_window_state"]
    return row["hot_window_state"]


def _accepted_priority(delivery_state: str) -> int:
    return 1 if delivery_state.endswith("_after_rotation_acceptance") else 0


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsTradingProgramMinimalViewV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsTradingProgramMinimalViewV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.ingress_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_trading_program_ingress_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_trading_program_minimal_view_v1.csv"
        )
        self.serving_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_trading_program_minimal_view_registry_v1.csv"
        )

    def materialize(self) -> MaterializedAShareInternalHotNewsTradingProgramMinimalViewV1:
        ingress_rows = _read_csv(self.ingress_path)
        timing = resolve_trade_timing(self.repo_root, now_cn=datetime.now(ZoneInfo("Asia/Shanghai")))
        minimal_rows: list[dict[str, Any]] = []
        for row in ingress_rows:
            minimal_rows.append(
                {
                    "telegraph_id": row["telegraph_id"],
                    "public_ts": row["public_ts"],
                    "program_priority_score": row["program_priority_score"],
                    "focus_adjusted_priority_score": row.get("focus_adjusted_priority_score", row["program_priority_score"]),
                    "consumer_action_class": _consumer_action_class(row),
                    "consumer_focus_class": _consumer_focus_class(row),
                    "window_state": _window_state(row),
                    "guidance_priority": row["guidance_priority"],
                    "importance_tier": row["importance_tier"],
                    "routing_bucket": row["routing_bucket"],
                    "target_scope": row["target_scope"],
                    "target_board": row["target_board"],
                    "target_theme_slug": row["target_theme_slug"],
                    "primary_theme_slug": row["primary_theme_slug"],
                    "secondary_theme_slug": row["secondary_theme_slug"],
                    "theme_governance_state": row["theme_governance_state"],
                    "focus_total_score": row.get("focus_total_score", "0.0000"),
                    "focus_score_density": row.get("focus_score_density", "0.0000"),
                    "focus_cycle_state": row.get("focus_cycle_state", "unscored_focus_cycle_state"),
                    "focus_bias_class": row.get("focus_bias_class", "unscored_focus_bias"),
                    "event_direction": row["event_direction"],
                    "event_strength": row["event_strength"],
                    "decision_signal_score": row["decision_signal_score"],
                    "action_bias": row["action_bias"],
                    "context_recency_weighted_signal_score": row["context_recency_weighted_signal_score"],
                    "context_velocity_state": row["context_velocity_state"],
                    "context_cooling_state": row["context_cooling_state"],
                    "impact_decay_state": row["impact_decay_state"],
                    "trading_day_state": timing["trading_day_state"],
                    "session_phase": timing["session_phase"],
                    "session_phase_confidence": timing["session_phase_confidence"],
                    "session_handling_mode": timing["session_handling_mode"],
                    "board_hit_state": row["board_hit_state"],
                    "beneficiary_mapping_confidence": row["beneficiary_mapping_confidence"],
                    "beneficiary_linkage_class": row["beneficiary_linkage_class"],
                    "beneficiary_symbols_top5": row["beneficiary_symbols_top5"],
                    "title": row["title"],
                    "delivery_state": (
                        "minimal_consumer_view_ready_after_rotation_acceptance"
                        if row["delivery_state"].endswith("_after_rotation_acceptance")
                        else "minimal_consumer_view_ready"
                    ),
                }
            )

        minimal_rows.sort(
            key=lambda row: (
                -_to_float(row["focus_adjusted_priority_score"]),
                -_to_float(row["program_priority_score"]),
                -_accepted_priority(row["delivery_state"]),
                row["public_ts"],
                row["telegraph_id"],
            )
        )

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with self.output_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(minimal_rows[0].keys()))
            writer.writeheader()
            writer.writerows(minimal_rows)

        serving_rows = [
            {
                "view_id": "internal_hot_news_trading_program_minimal_view",
                "consumer_mode": "research_shadow",
                "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                "view_state": "read_ready_internal_only",
            }
        ]
        self.serving_path.parent.mkdir(parents=True, exist_ok=True)
        with self.serving_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(serving_rows[0].keys()))
            writer.writeheader()
            writer.writerows(serving_rows)

        summary = {
            "minimal_view_row_count": len(minimal_rows),
            "risk_guardrail_count": sum(row["consumer_action_class"] == "risk_guardrail" for row in minimal_rows),
            "top_down_guidance_count": sum(row["consumer_action_class"] == "top_down_guidance" for row in minimal_rows),
            "board_watch_trigger_count": sum(row["consumer_action_class"] == "board_watch_trigger" for row in minimal_rows),
            "symbol_focus_available_count": sum(
                row["consumer_focus_class"] == "symbol_focus_available" for row in minimal_rows
            ),
            "trading_day_state": timing["trading_day_state"],
            "session_phase": timing["session_phase"],
            "session_handling_mode": timing["session_handling_mode"],
            "authoritative_output": "a_share_internal_hot_news_trading_program_minimal_view_materialized",
        }
        return MaterializedAShareInternalHotNewsTradingProgramMinimalViewV1(summary=summary, rows=minimal_rows)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsTradingProgramMinimalViewV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
