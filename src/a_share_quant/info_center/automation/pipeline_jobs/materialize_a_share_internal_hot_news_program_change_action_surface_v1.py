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


def _risk_action(change_state: str, score: float) -> str:
    if change_state == "top_entity_changed":
        return "refresh_risk_guardrail_and_recompute_veto"
    if change_state == "major_score_shift":
        return "tighten_risk_review"
    if change_state == "minor_score_shift":
        return "refresh_risk_ranking"
    if score >= 45:
        return "maintain_risk_guardrail"
    return "observe_only"


def _opportunity_action(change_state: str, score: float) -> str:
    if change_state == "top_entity_changed":
        return "rerank_opportunity_and_refresh_watchlist"
    if change_state == "major_score_shift":
        return "refresh_opportunity_priority"
    if change_state == "minor_score_shift":
        return "observe_opportunity_drift"
    if score >= 45:
        return "maintain_top_opportunity_watch"
    return "observe_only"


def _global_action(risk_score: float, opportunity_score: float) -> str:
    if risk_score >= 45 and opportunity_score >= 45:
        return "dual_focus_risk_and_opportunity"
    if risk_score >= 45:
        return "risk_first_mode"
    if opportunity_score >= 45:
        return "opportunity_first_mode"
    return "balanced_observe_mode"


def _session_action_gate(session_handling_mode: str) -> str:
    if session_handling_mode == "live_session_monitoring":
        return "allow_live_routing"
    if session_handling_mode == "intraday_pause_hold_context":
        return "hold_context_no_new_session_push"
    if session_handling_mode == "pre_open_prepare_only":
        return "prepare_only_before_continuous_session"
    if session_handling_mode == "post_close_review_only":
        return "review_only_after_close"
    return "watch_only_non_trading_day"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramChangeActionSurfaceV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramChangeActionSurfaceV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.change_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_snapshot_change_signal_v1.csv"
        )
        self.snapshot_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_snapshot_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_change_action_surface_v1.csv"
        )
        self.serving_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_change_action_registry_v1.csv"
        )

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramChangeActionSurfaceV1:
        change = _read_csv(self.change_path)[0]
        snapshot = _read_csv(self.snapshot_path)[0]
        top_risk_score = _to_float(snapshot["top_risk_score"])
        top_opportunity_score = _to_float(snapshot["top_opportunity_score"])

        row = {
            "action_surface_id": "internal_hot_news_program_change_action_latest",
            "top_risk_change_state": change["top_risk_change_state"],
            "top_risk_changed": change["top_risk_changed"],
            "top_risk_score": snapshot["top_risk_score"],
            "top_risk_action": _risk_action(change["top_risk_change_state"], top_risk_score),
            "top_opportunity_change_state": change["top_opportunity_change_state"],
            "top_opportunity_changed": change["top_opportunity_changed"],
            "top_opportunity_score": snapshot["top_opportunity_score"],
            "top_opportunity_action": _opportunity_action(
                change["top_opportunity_change_state"],
                top_opportunity_score,
            ),
            "global_program_action_mode": _global_action(top_risk_score, top_opportunity_score),
            "trading_day_state": snapshot["trading_day_state"],
            "session_phase": snapshot["session_phase"],
            "session_handling_mode": snapshot["session_handling_mode"],
            "session_action_gate": _session_action_gate(snapshot["session_handling_mode"]),
            "snapshot_state": snapshot["snapshot_state"],
            "delivery_state": "program_change_action_ready",
        }

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with self.output_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
            writer.writeheader()
            writer.writerow(row)

        serving_rows = [
            {
                "view_id": "internal_hot_news_program_change_action_surface",
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
            "action_row_count": 1,
            "top_risk_action": row["top_risk_action"],
            "top_opportunity_action": row["top_opportunity_action"],
            "global_program_action_mode": row["global_program_action_mode"],
            "session_handling_mode": row["session_handling_mode"],
            "session_action_gate": row["session_action_gate"],
            "authoritative_output": "a_share_internal_hot_news_program_change_action_surface_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramChangeActionSurfaceV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramChangeActionSurfaceV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
