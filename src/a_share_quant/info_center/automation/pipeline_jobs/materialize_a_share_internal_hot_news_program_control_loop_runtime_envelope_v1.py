from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _poll_interval_seconds(*, loop_signal_mode: str, signal_priority: str, session_phase_current: str) -> str:
    if loop_signal_mode == "interrupt":
        return "0"
    if loop_signal_mode == "elevate_attention":
        return "15"
    if session_phase_current in {
        "opening_call_auction",
        "morning_continuous_session",
        "afternoon_continuous_session",
        "closing_call_auction",
    }:
        return "30"
    if session_phase_current in {"pre_open", "pre_continuous_auction_buffer", "lunch_break", "post_close"}:
        return "60"
    if signal_priority == "p1":
        return "30"
    return "300"


def _attention_level(loop_signal_mode: str, signal_priority: str) -> str:
    if loop_signal_mode == "interrupt":
        return "high"
    if loop_signal_mode == "elevate_attention" or signal_priority == "p1":
        return "medium"
    return "low"


def _runtime_consumer_mode(loop_signal_mode: str, reopen_target: str) -> str:
    if loop_signal_mode == "interrupt":
        return "interrupt_and_reopen"
    if loop_signal_mode == "elevate_attention" and reopen_target != "none":
        return "elevate_and_reopen"
    if loop_signal_mode == "elevate_attention":
        return "elevate_polling"
    return "passive_polling_only"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramControlLoopRuntimeEnvelopeV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramControlLoopRuntimeEnvelopeV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.control_packet_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_control_packet_v1.csv"
        )
        self.control_loop_signal_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_control_loop_signal_feed_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_control_loop_runtime_envelope_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_control_loop_runtime_envelope_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramControlLoopRuntimeEnvelopeV1:
        control_packet = _read_csv(self.control_packet_path)[0]
        control_loop_signal = _read_csv(self.control_loop_signal_path)[0]
        loop_signal_mode = control_loop_signal["loop_signal_mode"]
        signal_priority = control_loop_signal["signal_priority"]
        reopen_target = control_loop_signal["reopen_target"]
        session_phase_current = control_loop_signal["session_phase_current"]

        row = {
            "runtime_envelope_id": "internal_hot_news_program_control_loop_runtime_envelope_latest",
            "loop_signal_mode": loop_signal_mode,
            "signal_priority": signal_priority,
            "interrupt_required": control_loop_signal["interrupt_required"],
            "reopen_target": reopen_target,
            "runtime_consumer_mode": _runtime_consumer_mode(loop_signal_mode, reopen_target),
            "runtime_attention_level": _attention_level(loop_signal_mode, signal_priority),
            "suggested_poll_interval_seconds": _poll_interval_seconds(
                loop_signal_mode=loop_signal_mode,
                signal_priority=signal_priority,
                session_phase_current=session_phase_current,
            ),
            "program_health_state": control_packet["program_health_state"],
            "freshness_state": control_packet["freshness_state"],
            "trading_day_state": control_packet["trading_day_state"],
            "session_phase": control_packet["session_phase"],
            "top_risk_telegraph_id": control_packet["top_risk_telegraph_id"],
            "top_opportunity_telegraph_id": control_packet["top_opportunity_telegraph_id"],
            "delivery_state": "program_control_loop_runtime_envelope_ready",
        }

        self._write_csv(self.output_path, [row])
        self._write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_program_control_loop_runtime_envelope",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "envelope_row_count": 1,
            "loop_signal_mode": row["loop_signal_mode"],
            "runtime_consumer_mode": row["runtime_consumer_mode"],
            "runtime_attention_level": row["runtime_attention_level"],
            "suggested_poll_interval_seconds": row["suggested_poll_interval_seconds"],
            "reopen_target": row["reopen_target"],
            "authoritative_output": "a_share_internal_hot_news_program_control_loop_runtime_envelope_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramControlLoopRuntimeEnvelopeV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramControlLoopRuntimeEnvelopeV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
