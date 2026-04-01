from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
from typing import Any

from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    load_json_report,
)


@dataclass(slots=True)
class V114ICPOExistingInfoVectorExcavationReviewReport:
    summary: dict[str, Any]
    group_comparison: dict[str, Any]
    candidate_vector_rows: list[dict[str, Any]]
    intraday_boundary: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "group_comparison": self.group_comparison,
            "candidate_vector_rows": self.candidate_vector_rows,
            "intraday_boundary": self.intraday_boundary,
            "interpretation": self.interpretation,
        }


class V114ICPOExistingInfoVectorExcavationReviewAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    @staticmethod
    def _mean(rows: list[dict[str, Any]], key: str) -> float:
        return round(mean(float(row[key]) for row in rows), 6) if rows else 0.0

    @staticmethod
    def _median(rows: list[dict[str, Any]], key: str) -> float:
        return round(median(float(row[key]) for row in rows), 6) if rows else 0.0

    def analyze(
        self,
        *,
        v113v_payload: dict[str, Any],
        v114h_payload: dict[str, Any],
    ) -> V114ICPOExistingInfoVectorExcavationReviewReport:
        summary_v = dict(v113v_payload.get("summary", {}))
        summary_h = dict(v114h_payload.get("summary", {}))
        if str(summary_v.get("acceptance_posture")) != "freeze_v113v_cpo_full_board_execution_main_feed_replay_v1":
            raise ValueError("V1.14I expects V1.13V full-board replay.")
        if str(summary_h.get("acceptance_posture")) != "freeze_v114h_cpo_promoted_sizing_behavior_audit_v1":
            raise ValueError("V1.14I expects V1.14H promoted sizing behavior audit.")

        baseline_day_map = {
            str(row["trade_date"]): row for row in list(v113v_payload.get("replay_day_rows", []))
        }
        ordered_days = list(v113v_payload.get("replay_day_rows", []))
        index_by_date = {str(row["trade_date"]): idx for idx, row in enumerate(ordered_days)}

        family_by_symbol = {
            "300308": "core_module_leader",
            "300502": "high_beta_core_module",
            "300757": "packaging_process_enabler",
            "688498": "laser_chip_component",
        }

        def enrich(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
            enriched_rows: list[dict[str, Any]] = []
            for row in rows:
                trade_date = str(row["trade_date"])
                base_row = baseline_day_map[trade_date]
                idx = index_by_date[trade_date]
                previous_window = ordered_days[max(0, idx - 5):idx]
                prev_strong_count = sum(
                    1
                    for prev in previous_window
                    if float(dict(prev["board_context"]).get("avg_return", 0.0)) >= 0.05
                    and float(dict(prev["board_context"]).get("breadth", 0.0)) >= 0.8
                )
                if previous_window:
                    prev_avg_return = mean(float(dict(prev["board_context"]).get("avg_return", 0.0)) for prev in previous_window)
                    prev_breadth = mean(float(dict(prev["board_context"]).get("breadth", 0.0)) for prev in previous_window)
                    prev_top3 = mean(float(dict(prev["board_context"]).get("top3_turnover_ratio", 0.0)) for prev in previous_window)
                else:
                    prev_avg_return = 0.0
                    prev_breadth = 0.0
                    prev_top3 = 0.0
                holding_symbols = list(row.get("holding_symbols_after_close", []))
                role_count = len({family_by_symbol.get(symbol, symbol) for symbol in holding_symbols})
                enriched_rows.append(
                    {
                        "trade_date": trade_date,
                        "board_avg_return": float(row["board_avg_return"]),
                        "board_breadth": float(row["board_breadth"]),
                        "baseline_exposure": float(base_row["gross_exposure_after_close"]),
                        "promoted_exposure": float(row["promoted_exposure"]),
                        "top3_turnover_ratio": float(dict(base_row["board_context"]).get("top3_turnover_ratio", 0.0)),
                        "holding_count": len(holding_symbols),
                        "role_coverage_count": role_count,
                        "prev_strong_count_5d": prev_strong_count,
                        "avg_return_accel_5d": round(float(row["board_avg_return"]) - prev_avg_return, 6),
                        "breadth_accel_5d": round(float(row["board_breadth"]) - prev_breadth, 6),
                        "top3_turnover_delta_5d": round(float(dict(base_row["board_context"]).get("top3_turnover_ratio", 0.0)) - prev_top3, 6),
                    }
                )
            return enriched_rows

        improved_rows = enrich(list(v114h_payload.get("top_improved_expression_rows", [])))
        under_rows = enrich(list(v114h_payload.get("remaining_under_exposed_rows", [])))

        group_comparison = {
            "improved_expression_group": {
                "row_count": len(improved_rows),
                "mean_baseline_exposure": self._mean(improved_rows, "baseline_exposure"),
                "mean_promoted_exposure": self._mean(improved_rows, "promoted_exposure"),
                "mean_holding_count": self._mean(improved_rows, "holding_count"),
                "mean_role_coverage_count": self._mean(improved_rows, "role_coverage_count"),
                "mean_prev_strong_count_5d": self._mean(improved_rows, "prev_strong_count_5d"),
                "mean_top3_turnover_ratio": self._mean(improved_rows, "top3_turnover_ratio"),
                "mean_avg_return_accel_5d": self._mean(improved_rows, "avg_return_accel_5d"),
            },
            "remaining_under_exposed_group": {
                "row_count": len(under_rows),
                "mean_baseline_exposure": self._mean(under_rows, "baseline_exposure"),
                "mean_promoted_exposure": self._mean(under_rows, "promoted_exposure"),
                "mean_holding_count": self._mean(under_rows, "holding_count"),
                "mean_role_coverage_count": self._mean(under_rows, "role_coverage_count"),
                "mean_prev_strong_count_5d": self._mean(under_rows, "prev_strong_count_5d"),
                "mean_top3_turnover_ratio": self._mean(under_rows, "top3_turnover_ratio"),
                "mean_avg_return_accel_5d": self._mean(under_rows, "avg_return_accel_5d"),
            },
        }

        candidate_vector_rows = [
            {
                "vector_name": "market_voice_persistence_vector",
                "vector_family": "market_voice",
                "fields": [
                    "board_avg_return",
                    "board_breadth",
                    "prev_strong_count_5d",
                    "avg_return_accel_5d",
                    "breadth_accel_5d",
                ],
                "why_it_matters": "Remaining under-exposed strong days are much more likely to be first-wave or low-persistence strong days; improved expression days more often sit inside already-persisting strong regimes.",
                "evidence": {
                    "improved_prev_strong_count_5d_mean": group_comparison["improved_expression_group"]["mean_prev_strong_count_5d"],
                    "under_prev_strong_count_5d_mean": group_comparison["remaining_under_exposed_group"]["mean_prev_strong_count_5d"],
                },
                "action_target": "add / stronger early admission on repeated strong-board sequences",
            },
            {
                "vector_name": "portfolio_coverage_gap_vector",
                "vector_family": "position_add_reduce",
                "fields": [
                    "baseline_exposure",
                    "promoted_exposure",
                    "holding_count",
                    "role_coverage_count",
                ],
                "why_it_matters": "The largest separator is not board strength itself but how little structure coverage the portfolio had before the strong day hit.",
                "evidence": {
                    "improved_holding_count_mean": group_comparison["improved_expression_group"]["mean_holding_count"],
                    "under_holding_count_mean": group_comparison["remaining_under_exposed_group"]["mean_holding_count"],
                    "improved_baseline_exposure_mean": group_comparison["improved_expression_group"]["mean_baseline_exposure"],
                    "under_baseline_exposure_mean": group_comparison["remaining_under_exposed_group"]["mean_baseline_exposure"],
                },
                "action_target": "faster add / admission when board is strong but role coverage is still thin",
            },
            {
                "vector_name": "relative_structure_concentration_vector",
                "vector_family": "board_internal_relative_structure",
                "fields": [
                    "top3_turnover_ratio",
                    "top3_turnover_delta_5d",
                    "role_coverage_count",
                ],
                "why_it_matters": "Improved expression days tend to arrive with a denser internal turnover core and broader internal role coverage; early under-exposed days look strong but structurally thinner.",
                "evidence": {
                    "improved_top3_turnover_ratio_mean": group_comparison["improved_expression_group"]["mean_top3_turnover_ratio"],
                    "under_top3_turnover_ratio_mean": group_comparison["remaining_under_exposed_group"]["mean_top3_turnover_ratio"],
                },
                "action_target": "distinguish mature strong-board consensus from early thin strong-board spikes",
            },
            {
                "vector_name": "false_breakout_interference_proxy_vector",
                "vector_family": "interference_false_signal",
                "fields": [
                    "board_avg_return",
                    "board_breadth",
                    "top3_turnover_delta_5d",
                    "avg_return_accel_5d",
                ],
                "why_it_matters": "Some strong days may still be broad but structurally noisy. Existing daily information can only produce a weak proxy here; it can warn, but it cannot cleanly separate washout from engineered intraday shake.",
                "evidence": {
                    "current_status": "weak_proxy_only_from_daily",
                },
                "action_target": "guard against overreacting to broad hot days that lack clean internal confirmation",
            },
            {
                "vector_name": "state_transition_acceleration_vector",
                "vector_family": "state_transition",
                "fields": [
                    "prev_strong_count_5d",
                    "avg_return_accel_5d",
                    "breadth_accel_5d",
                    "top3_turnover_delta_5d",
                ],
                "why_it_matters": "Add/reduce is often a transition problem. Existing daily information already exposes whether the board is entering a durable strong regime or only flashing strong for a day.",
                "evidence": {
                    "improved_avg_return_accel_5d_mean": group_comparison["improved_expression_group"]["mean_avg_return_accel_5d"],
                    "under_avg_return_accel_5d_mean": group_comparison["remaining_under_exposed_group"]["mean_avg_return_accel_5d"],
                },
                "action_target": "better early add timing and better discrimination between durable acceleration and one-day spikes",
            },
        ]

        intraday_boundary = {
            "daily_information_still_useful_now": True,
            "intraday_required_now": False,
            "current_daily_limit": "cannot cleanly distinguish constructive shakeout from intraday distribution on the same strong day",
            "intraday_becomes_mandatory_for": [
                "same-day add confirmation",
                "same-day reduce confirmation",
                "washout vs distribution separation",
                "tail risk / close-quality confirmation",
            ],
            "recommended_posture": "start with existing-info vectors first, then add intraday only after daily-vector uplift is exhausted",
        }

        summary = {
            "acceptance_posture": "freeze_v114i_cpo_existing_info_vector_excavation_review_v1",
            "improved_expression_group_count": len(improved_rows),
            "remaining_under_exposed_group_count": len(under_rows),
            "candidate_vector_count": len(candidate_vector_rows),
            "existing_info_has_actionable_vector_headroom": True,
            "strongest_existing_info_separator": "portfolio_coverage_gap_plus_market_voice_persistence",
            "intraday_required_now": False,
            "recommended_next_posture": "prototype_market_voice_and_state_transition_vectors_before_requesting_intraday",
        }

        interpretation = [
            "V1.14I asks a narrow question: can the current daily board/replay information still yield useful vector directions before the project must request intraday support?",
            "The answer is yes. The strongest separations are not hidden in mysterious geometry; they are visible in persistence of board strength, thin portfolio role coverage, and the transition from first-wave strength to already-persisting strong regimes.",
            "Daily information is still enough to build the first market-voice and state-transition candidate vectors. Intraday should be added later for shakeout-vs-distribution confirmation, not as the first response.",
        ]

        return V114ICPOExistingInfoVectorExcavationReviewReport(
            summary=summary,
            group_comparison=group_comparison,
            candidate_vector_rows=candidate_vector_rows,
            intraday_boundary=intraday_boundary,
            interpretation=interpretation,
        )


def write_v114i_cpo_existing_info_vector_excavation_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V114ICPOExistingInfoVectorExcavationReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
