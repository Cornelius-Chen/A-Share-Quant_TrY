from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timedelta
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


def _parse_ts(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


def _impact_days(importance_tier: str) -> int:
    if importance_tier in {"tier_1_market_guidance", "tier_1_risk_shock"}:
        return 3
    if importance_tier == "tier_2_board_signal":
        return 2
    return 1


def _context_action_bias(routing_bucket: str, net_signal_score: float) -> str:
    if routing_bucket == "guidance_layer":
        return "update_top_down_guidance"
    if routing_bucket == "risk_layer" and net_signal_score < 0:
        return "tighten_risk_or_board_veto"
    if routing_bucket == "board_trigger_layer" and net_signal_score > 0:
        return "upgrade_board_watch"
    return "observe_context_only"


def _context_velocity_state(
    *,
    recent_60m_count: int,
    recent_180m_count: int,
    active_hot_count: int,
    net_signal_score: float,
    recency_weighted_signal_score: float,
) -> str:
    if active_hot_count == 0:
        return "expired_context"
    if recent_180m_count <= 0:
        return "single_point_context"
    density_ratio = recent_60m_count / recent_180m_count
    net_abs = abs(net_signal_score)
    recency_abs = abs(recency_weighted_signal_score)
    if density_ratio >= 0.5 and recency_abs >= max(net_abs * 0.6, 1.0):
        return "fresh_accelerating_context"
    if density_ratio >= 0.25 and recency_abs >= max(net_abs * 0.35, 0.8):
        return "active_persistent_context"
    if recency_abs > 0:
        return "cooling_but_active_context"
    return "stale_context"


def _context_cooling_state(
    *,
    recent_60m_count: int,
    recent_180m_count: int,
    active_hot_count: int,
) -> str:
    if active_hot_count == 0:
        return "expired_context"
    if recent_180m_count <= 0:
        return "insufficient_history"
    density_ratio = recent_60m_count / recent_180m_count
    if density_ratio <= 0.0:
        return "rapid_cooling"
    if density_ratio < 0.25:
        return "cooling"
    if density_ratio < 0.5:
        return "stable"
    return "heating_or_persistent"


def _recency_weighted_signal(rows: list[dict[str, str]], snapshot_reference_ts: datetime) -> float:
    weighted = 0.0
    for row in rows:
        age_minutes = max((snapshot_reference_ts - _parse_ts(row["public_ts"])).total_seconds() / 60.0, 0.0)
        if age_minutes <= 60:
            weight = 1.0
        elif age_minutes <= 180:
            weight = 0.5
        else:
            weight = 0.25
        weighted += _to_float(row["decision_signal_score"]) * weight
    return round(weighted, 4)


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsRollingContextV1:
    summary: dict[str, Any]
    context_rows: list[dict[str, Any]]
    impact_rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsRollingContextV1:
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
        self.context_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_rolling_context_surface_v1.csv"
        )
        self.impact_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_important_impact_window_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        fieldnames = list(materialized_rows[0].keys())
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsRollingContextV1:
        ingress_rows = _read_csv(self.ingress_path)
        snapshot_reference_ts = max(_parse_ts(row["public_ts"]) for row in ingress_rows)

        grouped: dict[tuple[str, str, str], list[dict[str, str]]] = {}
        for row in ingress_rows:
            key = (row["target_theme_slug"], row["target_board"], row["routing_bucket"])
            grouped.setdefault(key, []).append(row)

        context_rows: list[dict[str, Any]] = []
        for index, ((theme_slug, target_board, routing_bucket), rows) in enumerate(sorted(grouped.items()), start=1):
            rows_sorted = sorted(rows, key=lambda row: row["public_ts"], reverse=True)
            latest_row = rows_sorted[0]
            net_signal_score = sum(_to_float(row["decision_signal_score"]) for row in rows)
            important_count = sum(row["importance_tier"] != "none" for row in rows)
            active_hot_count = sum(row["hot_window_state"] == "active_hot_window" for row in rows)
            recent_60m_count = 0
            recent_180m_count = 0
            for row in rows:
                age_minutes = max((snapshot_reference_ts - _parse_ts(row["public_ts"])).total_seconds() / 60.0, 0.0)
                if age_minutes <= 60:
                    recent_60m_count += 1
                if age_minutes <= 180:
                    recent_180m_count += 1
            recency_weighted_signal_score = _recency_weighted_signal(rows, snapshot_reference_ts)
            context_velocity_state = _context_velocity_state(
                recent_60m_count=recent_60m_count,
                recent_180m_count=recent_180m_count,
                active_hot_count=active_hot_count,
                net_signal_score=net_signal_score,
                recency_weighted_signal_score=recency_weighted_signal_score,
            )
            context_cooling_state = _context_cooling_state(
                recent_60m_count=recent_60m_count,
                recent_180m_count=recent_180m_count,
                active_hot_count=active_hot_count,
            )
            context_rows.append(
                {
                    "context_id": f"hot_news_context_{index:03d}",
                    "target_theme_slug": theme_slug,
                    "target_board": target_board,
                    "routing_bucket": routing_bucket,
                    "message_count": str(len(rows)),
                    "important_count": str(important_count),
                    "active_hot_count": str(active_hot_count),
                    "recent_60m_count": str(recent_60m_count),
                    "recent_180m_count": str(recent_180m_count),
                    "max_program_priority_score": f"{max(_to_float(row['program_priority_score']) for row in rows):.4f}",
                    "net_decision_signal_score": f"{net_signal_score:.4f}",
                    "recency_weighted_signal_score": f"{recency_weighted_signal_score:.4f}",
                    "latest_public_ts": latest_row["public_ts"],
                    "top_title": latest_row["title"],
                    "context_action_bias": _context_action_bias(routing_bucket, net_signal_score),
                    "context_velocity_state": context_velocity_state,
                    "context_cooling_state": context_cooling_state,
                    "context_state": "rolling_context_ready",
                }
            )

        impact_rows: list[dict[str, Any]] = []
        for row in ingress_rows:
            if row["important_copy_retained"] != "true":
                continue
            public_ts = _parse_ts(row["public_ts"])
            impact_end_ts = public_ts + timedelta(days=_impact_days(row["importance_tier"]))
            impact_rows.append(
                {
                    "cluster_id": row["cluster_id"],
                    "telegraph_id": row["telegraph_id"],
                    "importance_tier": row["importance_tier"],
                    "target_board": row["target_board"],
                    "target_theme_slug": row["target_theme_slug"],
                    "public_ts": row["public_ts"],
                    "impact_window_end_ts": impact_end_ts.strftime("%Y-%m-%d %H:%M:%S"),
                    "impact_window_state": (
                        "active_impact_window" if impact_end_ts >= snapshot_reference_ts else "expired_impact_window"
                    ),
                    "decision_signal_score": row["decision_signal_score"],
                    "action_bias": row["action_bias"],
                    "title": row["title"],
                }
            )

        self._write_csv(self.context_path, context_rows)
        self._write_csv(self.impact_path, impact_rows)

        summary = {
            "context_row_count": len(context_rows),
            "important_impact_row_count": len(impact_rows),
            "active_impact_count": sum(row["impact_window_state"] == "active_impact_window" for row in impact_rows),
            "accelerating_context_count": sum(
                row["context_velocity_state"] == "fresh_accelerating_context" for row in context_rows
            ),
            "cooling_context_count": sum(
                row["context_cooling_state"] in {"rapid_cooling", "cooling"} for row in context_rows
            ),
            "authoritative_output": "a_share_internal_hot_news_rolling_context_and_impact_window_materialized",
        }
        return MaterializedAShareInternalHotNewsRollingContextV1(
            summary=summary,
            context_rows=context_rows,
            impact_rows=impact_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsRollingContextV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
