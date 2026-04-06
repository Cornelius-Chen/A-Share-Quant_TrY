from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.a_share_theme_overlap_resolver import (
    resolve_theme_governance,
)


PRIORITY_WEIGHT = {
    "p0": 4,
    "p1": 3,
    "p2": 2,
    "p3": 1,
}

IMPORTANCE_WEIGHT = {
    "tier_1_market_guidance": 4,
    "tier_1_risk_shock": 4,
    "tier_2_board_signal": 2,
    "tier_3_watch_only": 1,
    "none": 0,
}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _to_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _program_priority(row: dict[str, str]) -> float:
    guidance_weight = PRIORITY_WEIGHT.get(row["guidance_priority"], 0)
    importance_weight = IMPORTANCE_WEIGHT.get(row.get("importance_tier", "none"), 0)
    signal_score = abs(_to_float(row["decision_signal_score"]))
    return round(importance_weight * 10 + guidance_weight * 3 + signal_score, 4)


def _parse_ts(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


def _accepted_priority(delivery_state: str) -> int:
    return 1 if delivery_state.endswith("_after_rotation_acceptance") else 0


def _first_symbol(value: str) -> str:
    if not value:
        return ""
    return value.split(",")[0].strip()


def _focus_adjusted_priority(program_priority_score: float, focus_total_score: float) -> float:
    return round(program_priority_score + focus_total_score * 20.0, 4)


def _impact_decay_state(
    *,
    public_ts: datetime,
    impact_window_end_ts: datetime | None,
    snapshot_reference_ts: datetime,
) -> str:
    if impact_window_end_ts is None:
        return "not_in_impact_window"
    total_seconds = max((impact_window_end_ts - public_ts).total_seconds(), 1.0)
    remaining_seconds = max((impact_window_end_ts - snapshot_reference_ts).total_seconds(), 0.0)
    remaining_ratio = remaining_seconds / total_seconds
    if remaining_ratio >= 0.66:
        return "early_impact_window"
    if remaining_ratio >= 0.33:
        return "mid_impact_window"
    if remaining_ratio > 0:
        return "late_impact_window"
    return "expired_impact_window"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsTradingProgramIngressV1:
    summary: dict[str, Any]
    ingress_rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsTradingProgramIngressV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.deduped_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_deduped_event_stream_v1.csv"
        )
        self.enriched_queue_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_important_trading_queue_enriched_v1.csv"
        )
        self.retention_policy_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_internal_hot_news_retention_policy_v1.csv"
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
        self.ingress_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_trading_program_ingress_v1.csv"
        )
        self.serving_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_trading_program_ingress_view_v1.csv"
        )
        self.rotation_acceptance_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_primary_consumer_rotation_acceptance_registry_v1.csv"
        )
        self.focus_scoring_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_focus_scoring_surface_v1.csv"
        )

    def materialize(self) -> MaterializedAShareInternalHotNewsTradingProgramIngressV1:
        deduped_rows = _read_csv(self.deduped_path)
        enriched_queue_rows = _read_csv(self.enriched_queue_path)
        retention_rows = _read_csv(self.retention_policy_path)
        context_rows = _read_csv(self.context_path)
        impact_rows = _read_csv(self.impact_path)
        acceptance_rows = _read_csv(self.rotation_acceptance_path)
        focus_scoring_rows = _read_csv(self.focus_scoring_path)
        acceptance = acceptance_rows[0] if acceptance_rows else None
        queue_map = {
            row["telegraph_id"]: row
            for row in enriched_queue_rows
            if row.get("telegraph_id")
        }
        retention_days_map = {row["retention_class"]: int(row["ttl_days"]) for row in retention_rows}
        context_map = {
            (row["target_theme_slug"], row["target_board"], row["routing_bucket"]): row
            for row in context_rows
            if row.get("target_theme_slug") and row.get("target_board") and row.get("routing_bucket")
        }
        impact_map = {
            row["telegraph_id"]: row
            for row in impact_rows
            if row.get("telegraph_id")
        }
        focus_scoring_map = {
            (row["theme_slug"], row["watch_symbol"]): row for row in focus_scoring_rows
        }
        snapshot_reference_ts = max(_parse_ts(row["public_ts"]) for row in deduped_rows)

        ingress_rows: list[dict[str, Any]] = []
        for row in deduped_rows:
            queue_row = queue_map.get(row["telegraph_id"])
            importance_tier = queue_row["importance_tier"] if queue_row else "none"
            board_hit_state = queue_row["board_hit_state"] if queue_row else (
                "broad_market_only" if row["target_theme_slug"] == "broad_market" else "theme_surface_unchecked"
            )
            beneficiary_mapping_confidence = queue_row["beneficiary_mapping_confidence"] if queue_row else (
                "none" if row["target_theme_slug"] == "broad_market" else "unknown"
            )
            beneficiary_linkage_class = queue_row["beneficiary_linkage_class"] if queue_row else (
                "none" if row["target_theme_slug"] == "broad_market" else "unmapped"
            )
            beneficiary_symbols_top5 = queue_row["beneficiary_symbols_top5"] if queue_row else ""
            primary_theme_slug, secondary_theme_slug, theme_governance_state = resolve_theme_governance(
                self.repo_root,
                row["target_theme_slug"],
            )
            top_watch_symbol = _first_symbol(beneficiary_symbols_top5)
            focus_row = focus_scoring_map.get((primary_theme_slug, top_watch_symbol))
            focus_total_score = _to_float(focus_row["focus_total_score"]) if focus_row else 0.0
            focus_score_density = _to_float(focus_row["focus_score_density"]) if focus_row else 0.0
            program_priority_score = _program_priority(
                {
                    "guidance_priority": row["guidance_priority"],
                    "decision_signal_score": row["decision_signal_score"],
                    "importance_tier": importance_tier,
                }
            )
            focus_adjusted_priority_score = _focus_adjusted_priority(program_priority_score, focus_total_score)
            retention_class = "promote_to_important_layer" if importance_tier != "none" else "hot_layer_ttl_5d"
            ttl_days = retention_days_map.get(retention_class, 5)
            public_ts_dt = _parse_ts(row["public_ts"])
            hot_expires_at = public_ts_dt + timedelta(days=ttl_days)
            hot_window_state = "active_hot_window" if hot_expires_at >= snapshot_reference_ts else "expired_hot_window"
            important_copy_retained = "true" if importance_tier != "none" else "false"
            context_row = context_map.get((row["target_theme_slug"], row["target_board"], row["routing_bucket"]))
            impact_row = impact_map.get(row["telegraph_id"])
            impact_window_end_dt = (
                _parse_ts(impact_row["impact_window_end_ts"]) if impact_row and impact_row["impact_window_end_ts"] else None
            )

            ingress_rows.append(
                {
                    "cluster_id": row["cluster_id"],
                    "telegraph_id": row["telegraph_id"],
                    "public_ts": row["public_ts"],
                    "program_priority_score": f"{program_priority_score:.4f}",
                    "focus_adjusted_priority_score": f"{focus_adjusted_priority_score:.4f}",
                    "retention_class": retention_class,
                    "hot_ttl_days": str(ttl_days),
                    "hot_expires_at": hot_expires_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "hot_window_state": hot_window_state,
                    "important_copy_retained": important_copy_retained,
                    "context_message_count": context_row["message_count"] if context_row else "0",
                    "context_important_count": context_row["important_count"] if context_row else "0",
                    "context_recent_60m_count": context_row["recent_60m_count"] if context_row else "0",
                    "context_recent_180m_count": context_row["recent_180m_count"] if context_row else "0",
                    "context_net_decision_signal_score": (
                        context_row["net_decision_signal_score"] if context_row else "0.0000"
                    ),
                    "context_recency_weighted_signal_score": (
                        context_row["recency_weighted_signal_score"] if context_row else "0.0000"
                    ),
                    "context_action_bias": context_row["context_action_bias"] if context_row else "observe_context_only",
                    "context_velocity_state": (
                        context_row["context_velocity_state"] if context_row else "insufficient_context"
                    ),
                    "context_cooling_state": (
                        context_row["context_cooling_state"] if context_row else "insufficient_context"
                    ),
                    "impact_window_end_ts": impact_row["impact_window_end_ts"] if impact_row else "",
                    "impact_window_state": impact_row["impact_window_state"] if impact_row else "not_in_impact_window",
                    "impact_decay_state": _impact_decay_state(
                        public_ts=public_ts_dt,
                        impact_window_end_ts=impact_window_end_dt,
                        snapshot_reference_ts=snapshot_reference_ts,
                    ),
                    "importance_tier": importance_tier,
                    "guidance_priority": row["guidance_priority"],
                    "routing_bucket": row["routing_bucket"],
                    "target_scope": row["target_scope"],
                    "target_board": row["target_board"],
                    "target_theme_slug": row["target_theme_slug"],
                    "primary_theme_slug": primary_theme_slug,
                    "secondary_theme_slug": secondary_theme_slug,
                    "theme_governance_state": theme_governance_state,
                    "focus_total_score": f"{focus_total_score:.4f}",
                    "focus_score_density": f"{focus_score_density:.4f}",
                    "focus_cycle_state": focus_row["cycle_state"] if focus_row else "unscored_focus_cycle_state",
                    "focus_bias_class": focus_row["focus_bias_class"] if focus_row else "unscored_focus_bias",
                    "guidance_class": row["guidance_class"],
                    "event_direction": row["event_direction"],
                    "event_strength": row["event_strength"],
                    "decision_signal_score": row["decision_signal_score"],
                    "action_bias": row["action_bias"],
                    "board_hit_state": board_hit_state,
                    "beneficiary_mapping_confidence": beneficiary_mapping_confidence,
                    "beneficiary_linkage_class": beneficiary_linkage_class,
                    "beneficiary_symbols_top5": beneficiary_symbols_top5,
                    "delivery_state": "trading_program_ingress_ready",
                    "title": row["title"],
                }
            )

        if acceptance and acceptance.get("acceptance_state") == "accepted":
            accepted_symbol = acceptance["accepted_top_watch_symbol"]
            accepted_theme = acceptance["accepted_top_opportunity_theme"]
            accepted_row_id = acceptance["accepted_source_row_id"]
            accepted_source_family = acceptance["accepted_source_family"]
            accepted_focus_row = focus_scoring_map.get((accepted_theme, accepted_symbol))
            accepted_focus_total_score = (
                _to_float(accepted_focus_row["focus_total_score"]) if accepted_focus_row else 0.0
            )
            template = next(
                (row for row in ingress_rows if row["primary_theme_slug"] != "broad_market"),
                ingress_rows[0] if ingress_rows else None,
            )
            if template is not None:
                accepted_row = {
                    **template,
                    "cluster_id": f"accepted_rotation_cluster_{accepted_row_id}",
                    "telegraph_id": accepted_row_id,
                    "program_priority_score": template["program_priority_score"],
                    "focus_adjusted_priority_score": f"{_focus_adjusted_priority(_to_float(template['program_priority_score']), accepted_focus_total_score):.4f}",
                    "target_scope": "market_or_macro",
                    "target_board": accepted_theme,
                    "target_theme_slug": accepted_theme,
                    "primary_theme_slug": accepted_theme,
                    "secondary_theme_slug": "",
                    "theme_governance_state": "accepted_rotation_override",
                    "focus_total_score": (
                        accepted_focus_row["focus_total_score"] if accepted_focus_row else "0.0000"
                    ),
                    "focus_score_density": (
                        accepted_focus_row["focus_score_density"] if accepted_focus_row else "0.0000"
                    ),
                    "focus_cycle_state": (
                        accepted_focus_row["cycle_state"] if accepted_focus_row else "unscored_focus_cycle_state"
                    ),
                    "focus_bias_class": (
                        accepted_focus_row["focus_bias_class"] if accepted_focus_row else "unscored_focus_bias"
                    ),
                    "guidance_class": "guidance_event",
                    "event_direction": "positive_or_risk_on",
                    "event_strength": "decisive",
                    "decision_signal_score": template["decision_signal_score"],
                    "action_bias": "update_market_guidance",
                    "board_hit_state": "theme_detected_with_symbol_route",
                    "beneficiary_mapping_confidence": "medium",
                    "beneficiary_linkage_class": "direct_beneficiary",
                    "beneficiary_symbols_top5": accepted_symbol,
                    "delivery_state": "trading_program_ingress_ready_after_rotation_acceptance",
                    "title": f"accepted_rotation_from_{accepted_source_family}",
                }
                ingress_rows = [accepted_row] + [
                    row for row in ingress_rows if row["telegraph_id"] != accepted_row_id and row["beneficiary_symbols_top5"] != accepted_symbol
                ]

        ingress_rows.sort(
            key=lambda row: (
                -_to_float(row["focus_adjusted_priority_score"]),
                -_to_float(row["program_priority_score"]),
                -_accepted_priority(row["delivery_state"]),
                row["public_ts"],
                row["telegraph_id"],
            )
        )
        accepted_rows = [row for row in ingress_rows if row["delivery_state"].endswith("_after_rotation_acceptance")]
        if accepted_rows:
            accepted_ids = {row["telegraph_id"] for row in accepted_rows}
            ingress_rows = accepted_rows + [row for row in ingress_rows if row["telegraph_id"] not in accepted_ids]

        self.ingress_path.parent.mkdir(parents=True, exist_ok=True)
        with self.ingress_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(ingress_rows[0].keys()))
            writer.writeheader()
            writer.writerows(ingress_rows)

        serving_rows = [
            {
                "view_id": "internal_hot_news_trading_program_ingress",
                "consumer_mode": "research_shadow",
                "artifact_path": str(self.ingress_path.relative_to(self.repo_root)),
                "view_state": "read_ready_internal_only",
            }
        ]
        self.serving_path.parent.mkdir(parents=True, exist_ok=True)
        with self.serving_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(serving_rows[0].keys()))
            writer.writeheader()
            writer.writerows(serving_rows)

        summary = {
            "ingress_row_count": len(ingress_rows),
            "important_ingress_count": sum(row["importance_tier"] != "none" for row in ingress_rows),
            "board_specific_ingress_count": sum(row["target_theme_slug"] != "broad_market" for row in ingress_rows),
            "active_hot_window_count": sum(row["hot_window_state"] == "active_hot_window" for row in ingress_rows),
            "important_copy_retained_count": sum(row["important_copy_retained"] == "true" for row in ingress_rows),
            "impact_window_attached_count": sum(row["impact_window_state"] != "not_in_impact_window" for row in ingress_rows),
            "accelerating_ingress_count": sum(
                row["context_velocity_state"] == "fresh_accelerating_context" for row in ingress_rows
            ),
            "late_impact_window_count": sum(row["impact_decay_state"] == "late_impact_window" for row in ingress_rows),
            "focus_scored_ingress_count": sum(_to_float(row["focus_total_score"]) > 0 for row in ingress_rows),
            "top_focus_theme_slug": ingress_rows[0]["primary_theme_slug"] if ingress_rows else "none",
            "top_focus_adjusted_priority_score": (
                ingress_rows[0]["focus_adjusted_priority_score"] if ingress_rows else "0.0000"
            ),
            "authoritative_output": "a_share_internal_hot_news_trading_program_ingress_materialized",
        }
        return MaterializedAShareInternalHotNewsTradingProgramIngressV1(summary=summary, ingress_rows=ingress_rows)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsTradingProgramIngressV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
