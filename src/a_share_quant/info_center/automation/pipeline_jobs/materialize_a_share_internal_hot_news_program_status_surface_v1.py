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


def _needs_attention(signal_priority: str) -> str:
    return "true" if signal_priority == "p0" else "false"


def _program_health(snapshot_state: str, action_delivery_state: str, signal_delivery_state: str) -> str:
    if (
        snapshot_state.startswith("program_snapshot_ready")
        and action_delivery_state == "program_change_action_ready"
        and signal_delivery_state == "program_change_action_signal_ready"
    ):
        return "healthy_internal_only"
    return "degraded"


def _freshness_state(lag_minutes: float) -> str:
    if lag_minutes <= 30:
        return "fresh"
    if lag_minutes <= 180:
        return "warming_stale"
    return "stale"


def _heartbeat_timeout_state(freshness_state: str) -> str:
    if freshness_state == "fresh":
        return "within_timeout"
    if freshness_state == "warming_stale":
        return "near_timeout"
    return "timed_out"


def _stale_alert_level(freshness_state: str) -> str:
    if freshness_state == "fresh":
        return "none"
    if freshness_state == "warming_stale":
        return "warning"
    return "critical"


def _force_refresh(freshness_state: str) -> str:
    return "true" if freshness_state != "fresh" else "false"


def _program_consumer_gate_mode(
    *,
    freshness_state: str,
    heartbeat_timeout_state: str,
    snapshot_consumer_gate_mode: str,
    session_action_gate: str,
) -> str:
    if heartbeat_timeout_state == "timed_out" or freshness_state == "stale":
        return "stale_block_until_refresh"
    if freshness_state == "warming_stale":
        return "degraded_watch_until_refresh"
    if session_action_gate == "watch_only_non_trading_day" or snapshot_consumer_gate_mode == "non_trading_day_watch_only":
        return "watch_only_non_trading_day"
    if session_action_gate == "review_only_after_close" or snapshot_consumer_gate_mode == "post_close_consumer_review":
        return "review_only_after_close"
    if session_action_gate == "hold_context_no_new_session_push" or snapshot_consumer_gate_mode == "intraday_break_context_hold":
        return "hold_context_during_break"
    if session_action_gate == "prepare_only_before_continuous_session" or snapshot_consumer_gate_mode == "pre_open_consumer_prepare":
        return "prepare_only_before_open"
    return "allow_live_session_routing"


def _program_driver_action_mode(program_consumer_gate_mode: str) -> str:
    mapping = {
        "watch_only_non_trading_day": "watch_only",
        "prepare_only_before_open": "prepare",
        "allow_live_session_routing": "live_route",
        "hold_context_during_break": "break_hold",
        "review_only_after_close": "review",
        "degraded_watch_until_refresh": "degraded_watch",
        "stale_block_until_refresh": "stale_block",
    }
    return mapping.get(program_consumer_gate_mode, "watch_only")


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramStatusSurfaceV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramStatusSurfaceV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.snapshot_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_snapshot_v1.csv"
        )
        self.action_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_change_action_surface_v1.csv"
        )
        self.signal_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_change_action_signal_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_status_surface_v1.csv"
        )
        self.serving_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_status_registry_v1.csv"
        )

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramStatusSurfaceV1:
        snapshot = _read_csv(self.snapshot_path)[0]
        action = _read_csv(self.action_path)[0]
        signal = _read_csv(self.signal_path)[0]
        generated_at = datetime.now(ZoneInfo("Asia/Shanghai"))
        freshest_input_dt = max(
            datetime.fromtimestamp(self.snapshot_path.stat().st_mtime, ZoneInfo("Asia/Shanghai")),
            datetime.fromtimestamp(self.action_path.stat().st_mtime, ZoneInfo("Asia/Shanghai")),
            datetime.fromtimestamp(self.signal_path.stat().st_mtime, ZoneInfo("Asia/Shanghai")),
        )
        freshness_lag_minutes = max((generated_at - freshest_input_dt).total_seconds() / 60.0, 0.0)
        freshness_state = _freshness_state(freshness_lag_minutes)
        timing = resolve_trade_timing(self.repo_root, now_cn=generated_at)

        program_consumer_gate_mode = _program_consumer_gate_mode(
            freshness_state=freshness_state,
            heartbeat_timeout_state=_heartbeat_timeout_state(freshness_state),
            snapshot_consumer_gate_mode=snapshot.get("snapshot_consumer_gate_mode", "unknown"),
            session_action_gate=action.get("session_action_gate", "unknown"),
        )

        row = {
            "program_status_id": "internal_hot_news_program_status_latest",
            "program_mode": snapshot["program_mode"],
            "program_health_state": _program_health(
                snapshot["snapshot_state"],
                action["delivery_state"],
                signal["delivery_state"],
            ),
            "top_risk_telegraph_id": snapshot["top_risk_telegraph_id"],
            "top_risk_score": snapshot["top_risk_score"],
            "top_opportunity_telegraph_id": snapshot["top_opportunity_telegraph_id"],
            "top_opportunity_score": snapshot["top_opportunity_score"],
            "global_program_action_mode": action["global_program_action_mode"],
            "top_risk_action": action["top_risk_action"],
            "top_opportunity_action": action["top_opportunity_action"],
            "change_signal_priority": signal["signal_priority"],
            "global_program_action_mode_state": signal["global_program_action_mode_state"],
            "top_risk_action_state": signal["top_risk_action_state"],
            "top_opportunity_action_state": signal["top_opportunity_action_state"],
            "needs_attention": _needs_attention(signal["signal_priority"]),
            "status_generated_at": generated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "freshest_input_ts": freshest_input_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "trading_day_state": timing["trading_day_state"],
            "session_phase": timing["session_phase"],
            "session_phase_confidence": timing["session_phase_confidence"],
            "session_handling_mode": timing["session_handling_mode"],
            "freshness_lag_minutes": f"{freshness_lag_minutes:.2f}",
            "freshness_state": freshness_state,
            "heartbeat_timeout_state": _heartbeat_timeout_state(freshness_state),
            "stale_alert_level": _stale_alert_level(freshness_state),
            "force_refresh": _force_refresh(freshness_state),
            "program_consumer_gate_mode": program_consumer_gate_mode,
            "program_driver_action_mode": _program_driver_action_mode(program_consumer_gate_mode),
            "delivery_state": "program_status_surface_ready",
        }

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with self.output_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
            writer.writeheader()
            writer.writerow(row)

        serving_rows = [
            {
                "view_id": "internal_hot_news_program_status_surface",
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
            "status_row_count": 1,
            "program_health_state": row["program_health_state"],
            "global_program_action_mode": row["global_program_action_mode"],
            "change_signal_priority": row["change_signal_priority"],
            "needs_attention": row["needs_attention"],
            "trading_day_state": row["trading_day_state"],
            "session_phase": row["session_phase"],
            "session_phase_confidence": row["session_phase_confidence"],
            "session_handling_mode": row["session_handling_mode"],
            "program_consumer_gate_mode": row["program_consumer_gate_mode"],
            "program_driver_action_mode": row["program_driver_action_mode"],
            "freshness_state": row["freshness_state"],
            "heartbeat_timeout_state": row["heartbeat_timeout_state"],
            "stale_alert_level": row["stale_alert_level"],
            "force_refresh": row["force_refresh"],
            "authoritative_output": "a_share_internal_hot_news_program_status_surface_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramStatusSurfaceV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramStatusSurfaceV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
