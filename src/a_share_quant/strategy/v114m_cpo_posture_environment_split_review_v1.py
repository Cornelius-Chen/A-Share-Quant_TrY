from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any

from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    load_json_report,
)
from a_share_quant.strategy.v114k_cpo_market_voice_state_transition_add_reduce_audit_replay_v1 import (
    V114KCpoMarketVoiceStateTransitionAddReduceAuditReplayAnalyzer,
)


@dataclass(slots=True)
class V114MCpoPostureEnvironmentSplitReviewReport:
    summary: dict[str, Any]
    posture_segment_rows: list[dict[str, Any]]
    segment_leader_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "posture_segment_rows": self.posture_segment_rows,
            "segment_leader_rows": self.segment_leader_rows,
            "interpretation": self.interpretation,
        }


class V114MCpoPostureEnvironmentSplitReviewAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit = V114KCpoMarketVoiceStateTransitionAddReduceAuditReplayAnalyzer(repo_root=repo_root)

    @staticmethod
    def _segment_name(row: dict[str, Any], *, add_threshold: float) -> str:
        if bool(row["board_strong"]):
            if float(row["board_avg_return"]) >= 0.08 and float(row["board_breadth"]) >= 0.9:
                return "euphoric_strong"
            if float(row["combined_add_readiness"]) >= add_threshold:
                return "high_readiness_strong"
            return "ordinary_strong"
        return "weak_or_mixed"

    def _simulate_posture(
        self,
        *,
        posture_name: str,
        config: dict[str, Any],
        episode_rows: list[dict[str, Any]],
        board_symbols: set[str],
        daily_bars: dict[tuple[str, Any], dict[str, Any]],
    ) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
        return self.audit._simulate_with_candidate_audit(
            config=config,
            episode_rows=episode_rows,
            board_symbols=board_symbols,
            daily_bars=daily_bars,
        )

    def analyze(
        self,
        *,
        v113n_payload: dict[str, Any],
        v113v_payload: dict[str, Any],
        v114d_payload: dict[str, Any],
        v114e_payload: dict[str, Any],
        v114j_payload: dict[str, Any],
    ) -> V114MCpoPostureEnvironmentSplitReviewReport:
        summary_n = dict(v113n_payload.get("summary", {}))
        summary_v = dict(v113v_payload.get("summary", {}))
        summary_d = dict(v114d_payload.get("summary", {}))
        summary_e = dict(v114e_payload.get("summary", {}))
        summary_j = dict(v114j_payload.get("summary", {}))
        if str(summary_n.get("acceptance_posture")) != "freeze_v113n_cpo_real_board_episode_population_v1":
            raise ValueError("V1.14M expects V1.13N real episode population.")
        if str(summary_v.get("acceptance_posture")) != "freeze_v113v_cpo_full_board_execution_main_feed_replay_v1":
            raise ValueError("V1.14M expects V1.13V full-board replay.")
        if str(summary_d.get("acceptance_posture")) != "freeze_v114d_cpo_stable_zone_replay_injection_v1":
            raise ValueError("V1.14M expects V1.14D stable-zone injection.")
        if str(summary_e.get("acceptance_posture")) != "freeze_v114e_cpo_default_sizing_replay_promotion_v1":
            raise ValueError("V1.14M expects V1.14E default sizing replay promotion.")
        if str(summary_j.get("acceptance_posture")) != "freeze_v114j_cpo_market_voice_state_transition_vector_prototype_v1":
            raise ValueError("V1.14M expects V1.14J vector prototype.")

        episode_rows = list(v113n_payload.get("internal_point_rows", []))
        board_symbols = {
            "300308", "300502", "300394", "002281", "603083", "688205", "301205", "300570",
            "688498", "688313", "300757", "601869", "600487", "600522", "000070", "603228",
            "001267", "300620", "300548", "000988",
        }
        daily_bars = self.audit.base._load_daily_bars(
            self.repo_root / "data" / "raw" / "daily_bars" / "sina_daily_bars_cpo_execution_main_feed_v1.csv"
        )
        self.audit.base._replay_day_rows_from_payload = list(v113v_payload.get("replay_day_rows", []))
        add_threshold = float(v114j_payload.get("prototype_summary", {}).get("market_voice_add_threshold", 0.398127))

        stable_rows = {str(row["candidate_name"]): dict(row) for row in list(v114d_payload.get("candidate_rows", []))}
        default_config = dict(v114e_payload.get("promoted_default_row", {}).get("config", {}))

        posture_configs = {
            "default_expectancy_mainline": {
                **default_config,
                "candidate_add_threshold": 99.0,
                "candidate_extra_uplift": 0.0,
                "candidate_floor": float(default_config["under_exposure_floor"]),
                "max_expression_weight": 0.10,
            },
            "conservative_guardrail": {
                **dict(stable_rows["conservative_stable_injection"]["config"]),
                "candidate_add_threshold": 99.0,
                "candidate_extra_uplift": 0.0,
                "candidate_floor": float(dict(stable_rows["conservative_stable_injection"]["config"])["under_exposure_floor"]),
                "max_expression_weight": 0.10,
            },
            "balanced_shadow": {
                **dict(stable_rows["balanced_injection"]["config"]),
                "candidate_add_threshold": 99.0,
                "candidate_extra_uplift": 0.0,
                "candidate_floor": float(dict(stable_rows["balanced_injection"]["config"])["under_exposure_floor"]),
                "max_expression_weight": 0.10,
            },
            "vector_overlay_experimental": {
                **default_config,
                "candidate_add_threshold": add_threshold,
                "candidate_extra_uplift": 0.02,
                "candidate_floor": 0.35,
                "max_expression_weight": 0.14,
            },
        }

        posture_segment_rows: list[dict[str, Any]] = []
        segment_groups = ["all_strong", "high_readiness_strong", "ordinary_strong", "euphoric_strong", "weak_or_mixed"]
        leader_candidates: dict[str, list[dict[str, Any]]] = {name: [] for name in segment_groups}

        for posture_name, config in posture_configs.items():
            summary_row, day_rows, action_rows = self._simulate_posture(
                posture_name=posture_name,
                config=config,
                episode_rows=episode_rows,
                board_symbols=board_symbols,
                daily_bars=daily_bars,
            )
            action_count_by_date: dict[str, int] = {}
            add_count_by_date: dict[str, int] = {}
            for action_row in action_rows:
                trade_date = str(action_row["trade_date"])
                action_count_by_date[trade_date] = action_count_by_date.get(trade_date, 0) + 1
                if str(action_row["action_mode"]) == "add":
                    add_count_by_date[trade_date] = add_count_by_date.get(trade_date, 0) + 1

            segment_bucket: dict[str, list[dict[str, Any]]] = {name: [] for name in segment_groups}
            for row in day_rows:
                segment_bucket["all_strong" if bool(row["board_strong"]) else "weak_or_mixed"].append(row)
                if bool(row["board_strong"]):
                    segment_bucket[self._segment_name(row, add_threshold=add_threshold)].append(row)

            for segment_name in segment_groups:
                rows = segment_bucket[segment_name]
                if not rows:
                    continue
                segment_curve = 1.0
                previous_equity = None
                for row in rows:
                    equity = float(row["equity_after_close"])
                    if previous_equity is not None and previous_equity > 0:
                        segment_curve *= equity / previous_equity
                    previous_equity = equity
                mean_exposure = mean(float(row["gross_exposure_after_close"]) for row in rows)
                mean_readiness = mean(float(row["combined_add_readiness"]) for row in rows)
                under_floor = sum(
                    1
                    for row in rows
                    if float(row["gross_exposure_after_close"]) < float(config["under_exposure_floor"])
                )
                action_count = sum(action_count_by_date.get(str(row["trade_date"]), 0) for row in rows)
                add_count = sum(add_count_by_date.get(str(row["trade_date"]), 0) for row in rows)
                record = {
                    "posture_name": posture_name,
                    "segment_name": segment_name,
                    "day_count": len(rows),
                    "segment_curve": round(segment_curve, 4),
                    "mean_exposure": round(mean_exposure, 6),
                    "mean_readiness": round(mean_readiness, 6),
                    "under_floor_count": under_floor,
                    "action_count": action_count,
                    "add_count": add_count,
                    "full_curve": round(float(summary_row["final_curve"]), 4),
                    "full_max_drawdown": round(float(summary_row["max_drawdown"]), 4),
                }
                posture_segment_rows.append(record)
                leader_candidates[segment_name].append(record)

        segment_leader_rows: list[dict[str, Any]] = []
        for segment_name, rows in leader_candidates.items():
            if not rows:
                continue
            best_row = max(rows, key=lambda row: (float(row["segment_curve"]), float(row["mean_exposure"])))
            segment_leader_rows.append(
                {
                    "segment_name": segment_name,
                    "leading_posture_name": best_row["posture_name"],
                    "segment_curve": best_row["segment_curve"],
                    "mean_exposure": best_row["mean_exposure"],
                    "under_floor_count": best_row["under_floor_count"],
                }
            )

        summary = {
            "acceptance_posture": "freeze_v114m_cpo_posture_environment_split_review_v1",
            "posture_count": len(posture_configs),
            "segment_count": len(segment_groups),
            "recommended_next_posture": "use_environment_split_to_keep_parallel_postures_and_avoid_over-collapsing_future_board_judgement",
        }
        interpretation = [
            "V1.14M compares retained CPO sizing postures inside the same board but across different environment slices instead of only comparing one total curve.",
            "The goal is to preserve multiple posture candidates for later board transfer: default, conservative, balanced, and vector-overlay do not need to win the same segment to stay useful.",
            "This keeps CPO from being over-collapsed into one universal parameter truth before other boards arrive.",
        ]

        return V114MCpoPostureEnvironmentSplitReviewReport(
            summary=summary,
            posture_segment_rows=posture_segment_rows,
            segment_leader_rows=segment_leader_rows,
            interpretation=interpretation,
        )


def write_v114m_cpo_posture_environment_split_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V114MCpoPostureEnvironmentSplitReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
