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


def _first_or_default(rows: list[dict[str, str]], default: dict[str, str]) -> dict[str, str]:
    return rows[0] if rows else default


def _first_timing_value(risk_rows: list[dict[str, str]], opportunity_rows: list[dict[str, str]], key: str, default: str) -> str:
    for rows in (risk_rows, opportunity_rows):
        if rows and key in rows[0]:
            return rows[0][key]
    return default


def _snapshot_consumer_gate_mode(risk_gate: str, opportunity_gate: str) -> str:
    if risk_gate.startswith("allow_live_") or opportunity_gate.startswith("allow_live_"):
        return "live_session_consumer_routing"
    if risk_gate.startswith("prepare_") or opportunity_gate.startswith("prepare_"):
        return "pre_open_consumer_prepare"
    if risk_gate.startswith("hold_") or opportunity_gate.startswith("hold_"):
        return "intraday_break_context_hold"
    if risk_gate.startswith("review_") or opportunity_gate.startswith("review_"):
        return "post_close_consumer_review"
    return "non_trading_day_watch_only"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramSnapshotV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramSnapshotV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
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
        self.symbol_watchlist_packet_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_symbol_watchlist_packet_v1.csv"
        )
        self.symbol_watch_summary_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_symbol_watch_summary_v1.csv"
        )
        self.rotation_acceptance_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_primary_consumer_rotation_acceptance_registry_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_snapshot_v1.csv"
        )
        self.serving_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_snapshot_registry_v1.csv"
        )

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramSnapshotV1:
        risk_rows = _read_csv(self.risk_path)
        opportunity_rows = _read_csv(self.opportunity_path)
        symbol_watch_rows = _read_csv(self.symbol_watchlist_packet_path)
        symbol_watch_summary_rows = _read_csv(self.symbol_watch_summary_path)
        rotation_acceptance_rows = _read_csv(self.rotation_acceptance_path)
        rotation_acceptance = rotation_acceptance_rows[0] if rotation_acceptance_rows else None

        empty = {
            "telegraph_id": "",
            "program_priority_score": "0.0000",
            "priority_band": "none",
            "target_theme_slug": "none",
            "consumer_focus_class": "unknown",
            "board_hit_state": "unknown",
            "beneficiary_mapping_confidence": "unknown",
            "beneficiary_symbols_top5": "",
            "event_direction": "neutral",
            "event_strength": "none",
            "window_state": "none",
            "title": "",
        }
        top_risk = _first_or_default(risk_rows, empty)
        top_opportunity = _first_or_default(opportunity_rows, empty)
        top_watch = _first_or_default(
            symbol_watch_rows,
            {
                "beneficiary_symbol": "",
                "primary_theme_slug": "none",
                "beneficiary_mapping_confidence": "unknown",
                "watch_rank": "",
            },
        )
        top_watch_summary = _first_or_default(
            symbol_watch_summary_rows,
            {
                "top_watch_symbols_top5": "",
                "top_watch_primary_themes_top5": "",
                "top_watch_linkage_class": "unknown",
            },
        )
        risk_consumer_gate = _first_timing_value(risk_rows, opportunity_rows, "risk_consumer_gate", "unknown")
        opportunity_consumer_gate = _first_timing_value(
            risk_rows,
            opportunity_rows,
            "opportunity_consumer_gate",
            "unknown",
        )

        snapshot_row = {
            "snapshot_id": "internal_hot_news_program_snapshot_latest",
            "risk_feed_row_count": str(len(risk_rows)),
            "opportunity_feed_row_count": str(len(opportunity_rows)),
            "trading_day_state": _first_timing_value(risk_rows, opportunity_rows, "trading_day_state", "unknown"),
            "session_phase": _first_timing_value(risk_rows, opportunity_rows, "session_phase", "unknown"),
            "session_phase_confidence": _first_timing_value(
                risk_rows,
                opportunity_rows,
                "session_phase_confidence",
                "unknown",
            ),
            "session_handling_mode": _first_timing_value(
                risk_rows,
                opportunity_rows,
                "session_handling_mode",
                "unknown",
            ),
            "risk_consumer_gate": risk_consumer_gate,
            "opportunity_consumer_gate": opportunity_consumer_gate,
            "snapshot_consumer_gate_mode": _snapshot_consumer_gate_mode(
                risk_consumer_gate,
                opportunity_consumer_gate,
            ),
            "top_risk_telegraph_id": top_risk["telegraph_id"],
            "top_risk_score": top_risk["program_priority_score"],
            "top_risk_band": top_risk["priority_band"],
            "top_risk_theme": top_risk["target_theme_slug"],
            "top_risk_direction": top_risk["event_direction"],
            "top_risk_strength": top_risk["event_strength"],
            "top_risk_window_state": top_risk["window_state"],
            "top_risk_title": top_risk["title"],
            "top_opportunity_telegraph_id": top_opportunity["telegraph_id"],
            "top_opportunity_score": top_opportunity["program_priority_score"],
            "top_opportunity_band": top_opportunity["priority_band"],
            "top_opportunity_theme": top_opportunity["target_theme_slug"],
            "top_opportunity_primary_theme_slug": top_opportunity.get("primary_theme_slug", top_opportunity["target_theme_slug"]),
            "top_opportunity_secondary_theme_slug": top_opportunity.get("secondary_theme_slug", ""),
            "top_opportunity_theme_governance_state": top_opportunity.get("theme_governance_state", "unknown"),
            "top_opportunity_focus_class": top_opportunity["consumer_focus_class"],
            "top_opportunity_board_hit_state": top_opportunity["board_hit_state"],
            "top_opportunity_mapping_confidence": top_opportunity["beneficiary_mapping_confidence"],
            "top_opportunity_linkage_class": top_opportunity.get("beneficiary_linkage_class", "unknown"),
            "top_opportunity_beneficiary_symbols_top5": top_opportunity["beneficiary_symbols_top5"],
            "top_watch_symbol": top_watch["beneficiary_symbol"],
            "top_watch_primary_theme_slug": top_watch["primary_theme_slug"],
            "top_watch_mapping_confidence": top_watch["beneficiary_mapping_confidence"],
            "top_watch_linkage_class": top_watch_summary["top_watch_linkage_class"],
            "top_watch_rank": top_watch["watch_rank"],
            "top_watch_symbols_top5": top_watch_summary["top_watch_symbols_top5"],
            "top_watch_primary_themes_top5": top_watch_summary["top_watch_primary_themes_top5"],
            "top_opportunity_direction": top_opportunity["event_direction"],
            "top_opportunity_strength": top_opportunity["event_strength"],
            "top_opportunity_window_state": top_opportunity["window_state"],
            "top_opportunity_title": top_opportunity["title"],
            "program_mode": "research_shadow_internal_only",
            "snapshot_state": "program_snapshot_ready",
        }
        if rotation_acceptance and rotation_acceptance.get("acceptance_state") == "accepted":
            accepted_theme = rotation_acceptance["accepted_top_opportunity_theme"]
            accepted_symbol = rotation_acceptance["accepted_top_watch_symbol"]
            accepted_row_id = rotation_acceptance["accepted_source_row_id"]
            accepted_source_family = rotation_acceptance["accepted_source_family"]
            snapshot_row["top_opportunity_telegraph_id"] = accepted_row_id
            snapshot_row["top_opportunity_theme"] = accepted_theme
            snapshot_row["top_opportunity_primary_theme_slug"] = accepted_theme
            snapshot_row["top_opportunity_secondary_theme_slug"] = ""
            snapshot_row["top_opportunity_theme_governance_state"] = "accepted_rotation_override"
            snapshot_row["top_opportunity_focus_class"] = "symbol_focus_available"
            snapshot_row["top_opportunity_board_hit_state"] = "theme_detected_with_symbol_route"
            snapshot_row["top_opportunity_mapping_confidence"] = "medium"
            snapshot_row["top_opportunity_linkage_class"] = "direct_beneficiary"
            snapshot_row["top_opportunity_beneficiary_symbols_top5"] = accepted_symbol
            snapshot_row["top_opportunity_title"] = f"accepted_rotation_from_{accepted_source_family}"
            snapshot_row["top_watch_symbol"] = accepted_symbol
            snapshot_row["top_watch_primary_theme_slug"] = accepted_theme
            snapshot_row["top_watch_mapping_confidence"] = "medium"
            snapshot_row["top_watch_linkage_class"] = "direct_beneficiary"
            snapshot_row["top_watch_rank"] = "1"
            snapshot_row["top_watch_symbols_top5"] = top_watch_summary["top_watch_symbols_top5"]
            snapshot_row["top_watch_primary_themes_top5"] = top_watch_summary["top_watch_primary_themes_top5"]
            snapshot_row["snapshot_state"] = "program_snapshot_ready_after_rotation_acceptance"

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with self.output_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(snapshot_row.keys()))
            writer.writeheader()
            writer.writerow(snapshot_row)

        serving_rows = [
            {
                "view_id": "internal_hot_news_program_snapshot",
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
            "snapshot_row_count": 1,
            "risk_feed_row_count": len(risk_rows),
            "opportunity_feed_row_count": len(opportunity_rows),
            "trading_day_state": snapshot_row["trading_day_state"],
            "session_phase": snapshot_row["session_phase"],
            "session_handling_mode": snapshot_row["session_handling_mode"],
            "risk_consumer_gate": snapshot_row["risk_consumer_gate"],
            "opportunity_consumer_gate": snapshot_row["opportunity_consumer_gate"],
            "snapshot_consumer_gate_mode": snapshot_row["snapshot_consumer_gate_mode"],
            "top_risk_score": _to_float(top_risk["program_priority_score"]),
            "top_opportunity_score": _to_float(top_opportunity["program_priority_score"]),
            "top_opportunity_primary_theme_slug": snapshot_row["top_opportunity_primary_theme_slug"],
            "top_opportunity_secondary_theme_slug": snapshot_row["top_opportunity_secondary_theme_slug"],
            "top_opportunity_theme_governance_state": snapshot_row["top_opportunity_theme_governance_state"],
            "top_opportunity_focus_class": snapshot_row["top_opportunity_focus_class"],
            "top_opportunity_board_hit_state": snapshot_row["top_opportunity_board_hit_state"],
            "top_opportunity_mapping_confidence": snapshot_row["top_opportunity_mapping_confidence"],
            "top_opportunity_linkage_class": snapshot_row["top_opportunity_linkage_class"],
            "top_opportunity_beneficiary_symbols_top5": snapshot_row["top_opportunity_beneficiary_symbols_top5"],
            "top_watch_symbol": snapshot_row["top_watch_symbol"],
            "top_watch_primary_theme_slug": snapshot_row["top_watch_primary_theme_slug"],
            "top_watch_mapping_confidence": snapshot_row["top_watch_mapping_confidence"],
            "top_watch_linkage_class": snapshot_row["top_watch_linkage_class"],
            "top_watch_symbols_top5": snapshot_row["top_watch_symbols_top5"],
            "authoritative_output": "a_share_internal_hot_news_program_snapshot_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramSnapshotV1(summary=summary, rows=[snapshot_row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramSnapshotV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
