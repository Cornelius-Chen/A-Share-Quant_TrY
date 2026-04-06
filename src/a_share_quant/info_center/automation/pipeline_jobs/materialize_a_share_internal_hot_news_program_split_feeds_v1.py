from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _to_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _priority_band(row: dict[str, str]) -> str:
    score = _to_float(row["program_priority_score"])
    if score >= 45:
        return "critical"
    if score >= 20:
        return "high"
    if score >= 8:
        return "medium"
    return "low"


def _risk_entry_state(row: dict[str, str]) -> str:
    if row["consumer_action_class"] != "risk_guardrail":
        return "not_in_risk_feed"
    if row["window_state"] in {"active_impact_window", "active_hot_window"}:
        return "active_risk_guardrail"
    return "stale_risk_guardrail"


def _opportunity_entry_state(row: dict[str, str]) -> str:
    if row["consumer_action_class"] not in {"top_down_guidance", "theme_guidance", "board_watch_trigger"}:
        return "not_in_opportunity_feed"
    if row["window_state"] in {"active_impact_window", "active_hot_window"}:
        return "active_opportunity_signal"
    return "stale_opportunity_signal"


def _risk_consumer_gate(row: dict[str, str]) -> str:
    mode = row["session_handling_mode"]
    if mode == "live_session_monitoring":
        return "allow_live_risk_guardrail"
    if mode == "pre_open_prepare_only":
        return "prepare_risk_guardrail_before_open"
    if mode == "intraday_pause_hold_context":
        return "hold_risk_context_during_break"
    if mode == "post_close_review_only":
        return "review_risk_after_close"
    return "watch_risk_non_trading_day"


def _opportunity_consumer_gate(row: dict[str, str]) -> str:
    mode = row["session_handling_mode"]
    if mode == "live_session_monitoring":
        if row["consumer_focus_class"] == "symbol_focus_available":
            return "allow_live_opportunity_routing"
        return "allow_live_board_watch_only"
    if mode == "pre_open_prepare_only":
        return "prepare_opportunity_watch_before_open"
    if mode == "intraday_pause_hold_context":
        return "hold_opportunity_context_during_break"
    if mode == "post_close_review_only":
        return "review_opportunity_after_close"
    return "watch_opportunity_non_trading_day"


def _accepted_priority(delivery_state: str) -> int:
    return 1 if delivery_state.endswith("_after_rotation_acceptance") else 0


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramSplitFeedsV1:
    summary: dict[str, Any]
    risk_rows: list[dict[str, Any]]
    opportunity_rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramSplitFeedsV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.minimal_view_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_trading_program_minimal_view_v1.csv"
        )
        self.risk_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_risk_feed_v1.csv"
        )
        self.opportunity_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_opportunity_feed_v1.csv"
        )
        self.serving_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_split_feed_registry_v1.csv"
        )
        self.rotation_acceptance_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_primary_consumer_rotation_acceptance_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramSplitFeedsV1:
        minimal_rows = _read_csv(self.minimal_view_path)
        acceptance_rows = _read_csv(self.rotation_acceptance_path)
        acceptance = acceptance_rows[0] if acceptance_rows else None
        risk_rows: list[dict[str, Any]] = []
        opportunity_rows: list[dict[str, Any]] = []

        for row in minimal_rows:
            common = {
                "telegraph_id": row["telegraph_id"],
                "public_ts": row["public_ts"],
                "program_priority_score": row["program_priority_score"],
                "focus_adjusted_priority_score": row.get("focus_adjusted_priority_score", row["program_priority_score"]),
                "priority_band": _priority_band(row),
                "trading_day_state": row["trading_day_state"],
                "session_phase": row["session_phase"],
                "session_phase_confidence": row["session_phase_confidence"],
                "session_handling_mode": row["session_handling_mode"],
                "window_state": row["window_state"],
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
                "context_recency_weighted_signal_score": row["context_recency_weighted_signal_score"],
                "context_velocity_state": row["context_velocity_state"],
                "context_cooling_state": row["context_cooling_state"],
                "impact_decay_state": row["impact_decay_state"],
                "title": row["title"],
            }
            if row["consumer_action_class"] == "risk_guardrail":
                risk_rows.append(
                    {
                        **common,
                        "consumer_action_class": row["consumer_action_class"],
                        "risk_entry_state": _risk_entry_state(row),
                        "risk_consumer_gate": _risk_consumer_gate(row),
                        "risk_action_bias": row["action_bias"],
                        "delivery_state": "risk_feed_ready",
                    }
                )
            if row["consumer_action_class"] in {"top_down_guidance", "theme_guidance", "board_watch_trigger"}:
                opportunity_rows.append(
                    {
                        **common,
                        "consumer_action_class": row["consumer_action_class"],
                        "consumer_focus_class": row["consumer_focus_class"],
                        "board_hit_state": row["board_hit_state"],
                        "beneficiary_mapping_confidence": row["beneficiary_mapping_confidence"],
                        "beneficiary_linkage_class": row["beneficiary_linkage_class"],
                        "beneficiary_symbols_top5": row["beneficiary_symbols_top5"],
                        "opportunity_entry_state": _opportunity_entry_state(row),
                        "opportunity_consumer_gate": _opportunity_consumer_gate(row),
                        "opportunity_action_bias": row["action_bias"],
                        "delivery_state": "opportunity_feed_ready",
                    }
                )

        if acceptance and acceptance.get("acceptance_state") == "accepted":
            accepted_symbol = acceptance["accepted_top_watch_symbol"]
            accepted_theme = acceptance["accepted_top_opportunity_theme"]
            accepted_row_id = acceptance["accepted_source_row_id"]
            accepted_source_family = acceptance["accepted_source_family"]
            accepted_existing = next(
                (row for row in opportunity_rows if row["telegraph_id"] == accepted_row_id),
                None,
            )
            template = accepted_existing or (opportunity_rows[0] if opportunity_rows else {
                "public_ts": "",
                "program_priority_score": "55.9000",
                "focus_adjusted_priority_score": "55.9000",
                "priority_band": "critical",
                "trading_day_state": minimal_rows[0]["trading_day_state"] if minimal_rows else "unknown",
                "session_phase": minimal_rows[0]["session_phase"] if minimal_rows else "unknown",
                "session_phase_confidence": minimal_rows[0]["session_phase_confidence"] if minimal_rows else "unknown",
                "session_handling_mode": minimal_rows[0]["session_handling_mode"] if minimal_rows else "unknown",
                "window_state": "active_impact_window",
                "target_scope": "market_or_macro",
                "target_board": accepted_theme,
                "target_theme_slug": accepted_theme,
                "primary_theme_slug": accepted_theme,
                "secondary_theme_slug": "",
                "theme_governance_state": "accepted_rotation_override",
                "focus_total_score": "0.0000",
                "focus_score_density": "0.0000",
                "focus_cycle_state": "unscored_focus_cycle_state",
                "focus_bias_class": "unscored_focus_bias",
                "event_direction": "positive_or_risk_on",
                "event_strength": "decisive",
                "decision_signal_score": "3.9000",
                "context_recency_weighted_signal_score": "1.9500",
                "context_velocity_state": "accepted_rotation_override",
                "context_cooling_state": "accepted_rotation_override",
                "impact_decay_state": "early_impact_window",
                "opportunity_consumer_gate": "watch_opportunity_non_trading_day",
                "opportunity_action_bias": "update_market_guidance",
            })
            accepted_row = {
                **template,
                "telegraph_id": accepted_row_id,
                "target_board": accepted_theme,
                "target_theme_slug": accepted_theme,
                "primary_theme_slug": accepted_theme,
                "secondary_theme_slug": "",
                "theme_governance_state": "accepted_rotation_override",
                "consumer_action_class": "top_down_guidance",
                "consumer_focus_class": "symbol_focus_available",
                "board_hit_state": "theme_detected_with_symbol_route",
                "beneficiary_mapping_confidence": "medium",
                "beneficiary_linkage_class": "direct_beneficiary",
                "beneficiary_symbols_top5": accepted_symbol,
                "opportunity_entry_state": "active_opportunity_signal",
                "title": f"accepted_rotation_from_{accepted_source_family}",
                "delivery_state": "opportunity_feed_ready_after_rotation_acceptance",
            }
            remaining_rows = [row for row in opportunity_rows if row["telegraph_id"] != accepted_row_id and row["beneficiary_symbols_top5"] != accepted_symbol]
            opportunity_rows = [accepted_row] + remaining_rows

        risk_rows.sort(key=lambda row: (-_to_float(row["program_priority_score"]), row["public_ts"], row["telegraph_id"]))
        opportunity_rows.sort(
            key=lambda row: (
                -_to_float(row["focus_adjusted_priority_score"]),
                -_to_float(row["program_priority_score"]),
                -_accepted_priority(row["delivery_state"]),
                row["public_ts"],
                row["telegraph_id"],
            ))
        accepted_rows = [row for row in opportunity_rows if row["delivery_state"].endswith("_after_rotation_acceptance")]
        if accepted_rows:
            accepted_ids = {row["telegraph_id"] for row in accepted_rows}
            opportunity_rows = accepted_rows + [row for row in opportunity_rows if row["telegraph_id"] not in accepted_ids]

        self._write_csv(self.risk_path, risk_rows)
        self._write_csv(self.opportunity_path, opportunity_rows)

        serving_rows = [
            {
                "view_id": "internal_hot_news_program_risk_feed",
                "consumer_mode": "research_shadow",
                "artifact_path": str(self.risk_path.relative_to(self.repo_root)),
                "view_state": "read_ready_internal_only",
            },
            {
                "view_id": "internal_hot_news_program_opportunity_feed",
                "consumer_mode": "research_shadow",
                "artifact_path": str(self.opportunity_path.relative_to(self.repo_root)),
                "view_state": "read_ready_internal_only",
            },
        ]
        self._write_csv(self.serving_path, serving_rows)

        summary = {
            "risk_feed_row_count": len(risk_rows),
            "opportunity_feed_row_count": len(opportunity_rows),
            "critical_risk_count": sum(row["priority_band"] == "critical" for row in risk_rows),
            "critical_opportunity_count": sum(row["priority_band"] == "critical" for row in opportunity_rows),
            "trading_day_state": minimal_rows[0]["trading_day_state"] if minimal_rows else "unknown",
            "session_phase": minimal_rows[0]["session_phase"] if minimal_rows else "unknown",
            "session_handling_mode": minimal_rows[0]["session_handling_mode"] if minimal_rows else "unknown",
            "risk_consumer_gate": risk_rows[0]["risk_consumer_gate"] if risk_rows else "unknown",
            "opportunity_consumer_gate": (
                opportunity_rows[0]["opportunity_consumer_gate"] if opportunity_rows else "unknown"
            ),
            "top_opportunity_theme_slug": (
                opportunity_rows[0]["primary_theme_slug"] if opportunity_rows else "none"
            ),
            "top_opportunity_focus_total_score": (
                opportunity_rows[0]["focus_total_score"] if opportunity_rows else "0.0000"
            ),
            "authoritative_output": "a_share_internal_hot_news_program_split_feeds_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramSplitFeedsV1(
            summary=summary,
            risk_rows=risk_rows,
            opportunity_rows=opportunity_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramSplitFeedsV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
