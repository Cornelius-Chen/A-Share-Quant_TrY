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
class V114JCpoMarketVoiceStateTransitionVectorPrototypeReport:
    summary: dict[str, Any]
    prototype_summary: dict[str, Any]
    scored_strong_day_rows: list[dict[str, Any]]
    candidate_add_band_rows: list[dict[str, Any]]
    candidate_hold_band_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "prototype_summary": self.prototype_summary,
            "scored_strong_day_rows": self.scored_strong_day_rows,
            "candidate_add_band_rows": self.candidate_add_band_rows,
            "candidate_hold_band_rows": self.candidate_hold_band_rows,
            "interpretation": self.interpretation,
        }


class V114JCpoMarketVoiceStateTransitionVectorPrototypeAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    @staticmethod
    def _norm(value: float, minimum: float, maximum: float) -> float:
        if maximum <= minimum:
            return 0.0
        return (value - minimum) / (maximum - minimum)

    def analyze(
        self,
        *,
        v113v_payload: dict[str, Any],
        v114h_payload: dict[str, Any],
        v114i_payload: dict[str, Any],
    ) -> V114JCpoMarketVoiceStateTransitionVectorPrototypeReport:
        summary_v = dict(v113v_payload.get("summary", {}))
        summary_h = dict(v114h_payload.get("summary", {}))
        summary_i = dict(v114i_payload.get("summary", {}))
        if str(summary_v.get("acceptance_posture")) != "freeze_v113v_cpo_full_board_execution_main_feed_replay_v1":
            raise ValueError("V1.14J expects V1.13V full-board replay.")
        if str(summary_h.get("acceptance_posture")) != "freeze_v114h_cpo_promoted_sizing_behavior_audit_v1":
            raise ValueError("V1.14J expects V1.14H behavior audit.")
        if str(summary_i.get("acceptance_posture")) != "freeze_v114i_cpo_existing_info_vector_excavation_review_v1":
            raise ValueError("V1.14J expects V1.14I vector excavation review.")

        replay_rows = list(v113v_payload.get("replay_day_rows", []))
        ordered_rows = sorted(replay_rows, key=lambda row: str(row["trade_date"]))
        strong_rows: list[dict[str, Any]] = []
        improved_dates = {str(row["trade_date"]) for row in list(v114h_payload.get("top_improved_expression_rows", []))}
        under_dates = {str(row["trade_date"]) for row in list(v114h_payload.get("remaining_under_exposed_rows", []))}

        for idx, row in enumerate(ordered_rows):
            board_context = dict(row["board_context"])
            avg_return = float(board_context.get("avg_return", 0.0))
            breadth = float(board_context.get("breadth", 0.0))
            if avg_return < 0.05 or breadth < 0.8:
                continue
            previous_window = ordered_rows[max(0, idx - 5):idx]
            prev_strong_count_5d = sum(
                1
                for prev in previous_window
                if float(dict(prev["board_context"]).get("avg_return", 0.0)) >= 0.05
                and float(dict(prev["board_context"]).get("breadth", 0.0)) >= 0.8
            )
            prev_avg_return = mean(float(dict(prev["board_context"]).get("avg_return", 0.0)) for prev in previous_window) if previous_window else 0.0
            prev_breadth = mean(float(dict(prev["board_context"]).get("breadth", 0.0)) for prev in previous_window) if previous_window else 0.0
            prev_top3 = mean(float(dict(prev["board_context"]).get("top3_turnover_ratio", 0.0)) for prev in previous_window) if previous_window else 0.0
            holding_symbols = list(row.get("holding_symbols_after_close", []))
            strong_rows.append(
                {
                    "trade_date": str(row["trade_date"]),
                    "board_avg_return": avg_return,
                    "board_breadth": breadth,
                    "top3_turnover_ratio": float(board_context.get("top3_turnover_ratio", 0.0)),
                    "gross_exposure_after_close": float(row["gross_exposure_after_close"]),
                    "holding_count": len(holding_symbols),
                    "prev_strong_count_5d": float(prev_strong_count_5d),
                    "avg_return_accel_5d": avg_return - prev_avg_return,
                    "breadth_accel_5d": breadth - prev_breadth,
                    "top3_turnover_delta_5d": float(board_context.get("top3_turnover_ratio", 0.0)) - prev_top3,
                    "episode_count": int(row["episode_count"]),
                    "intent_count": int(row["intent_count"]),
                    "label_group": (
                        "improved_expression"
                        if str(row["trade_date"]) in improved_dates
                        else "remaining_under_exposed"
                        if str(row["trade_date"]) in under_dates
                        else "other_strong_day"
                    ),
                }
            )

        mins = {key: min(float(row[key]) for row in strong_rows) for key in [
            "board_avg_return",
            "board_breadth",
            "top3_turnover_ratio",
            "prev_strong_count_5d",
            "avg_return_accel_5d",
            "breadth_accel_5d",
        ]}
        maxs = {key: max(float(row[key]) for row in strong_rows) for key in mins}

        scored_rows: list[dict[str, Any]] = []
        for row in strong_rows:
            market_voice_score = (
                0.30 * self._norm(float(row["board_avg_return"]), mins["board_avg_return"], maxs["board_avg_return"])
                + 0.20 * self._norm(float(row["board_breadth"]), mins["board_breadth"], maxs["board_breadth"])
                + 0.30 * self._norm(float(row["prev_strong_count_5d"]), mins["prev_strong_count_5d"], maxs["prev_strong_count_5d"])
                + 0.20 * self._norm(float(row["top3_turnover_ratio"]), mins["top3_turnover_ratio"], maxs["top3_turnover_ratio"])
            )
            state_transition_score = (
                0.40 * self._norm(float(row["avg_return_accel_5d"]), mins["avg_return_accel_5d"], maxs["avg_return_accel_5d"])
                + 0.35 * self._norm(float(row["breadth_accel_5d"]), mins["breadth_accel_5d"], maxs["breadth_accel_5d"])
                + 0.25 * self._norm(float(row["prev_strong_count_5d"]), mins["prev_strong_count_5d"], maxs["prev_strong_count_5d"])
            )
            coverage_gap_score = max(0.0, 0.25 - float(row["gross_exposure_after_close"])) + 0.03 * max(0, 3 - int(row["holding_count"]))
            combined_add_readiness = 0.45 * market_voice_score + 0.35 * state_transition_score + 0.20 * coverage_gap_score
            scored = dict(row)
            scored["market_voice_score"] = round(market_voice_score, 6)
            scored["state_transition_score"] = round(state_transition_score, 6)
            scored["coverage_gap_score"] = round(coverage_gap_score, 6)
            scored["combined_add_readiness"] = round(combined_add_readiness, 6)
            scored_rows.append(scored)

        add_threshold = median(float(row["combined_add_readiness"]) for row in scored_rows if row["label_group"] == "improved_expression")
        hold_threshold = median(float(row["combined_add_readiness"]) for row in scored_rows if row["label_group"] == "remaining_under_exposed")

        candidate_add_band_rows = [
            row
            for row in sorted(scored_rows, key=lambda item: float(item["combined_add_readiness"]), reverse=True)
            if float(row["combined_add_readiness"]) >= add_threshold
        ][:10]
        candidate_hold_band_rows = [
            row
            for row in sorted(scored_rows, key=lambda item: float(item["combined_add_readiness"]))
            if float(row["combined_add_readiness"]) <= hold_threshold
        ][:10]

        prototype_summary = {
            "market_voice_add_threshold": round(add_threshold, 6),
            "state_transition_hold_threshold": round(hold_threshold, 6),
            "top_add_band_count": len(candidate_add_band_rows),
            "top_hold_band_count": len(candidate_hold_band_rows),
            "improved_expression_score_mean": round(mean(float(row["combined_add_readiness"]) for row in scored_rows if row["label_group"] == "improved_expression"), 6),
            "remaining_under_exposed_score_mean": round(mean(float(row["combined_add_readiness"]) for row in scored_rows if row["label_group"] == "remaining_under_exposed"), 6),
        }

        summary = {
            "acceptance_posture": "freeze_v114j_cpo_market_voice_state_transition_vector_prototype_v1",
            "strong_day_count": len(scored_rows),
            "candidate_add_band_count": len(candidate_add_band_rows),
            "candidate_hold_band_count": len(candidate_hold_band_rows),
            "market_voice_vector_ready_for_candidate_use": True,
            "state_transition_vector_ready_for_candidate_use": True,
            "recommended_next_posture": "bind_market_voice_and_state_transition_scores_into_candidate_add_reduce_audit_not_direct_law",
        }
        interpretation = [
            "V1.14J turns the V1.14I excavation into two prototype scores: a market-voice persistence score and a state-transition score.",
            "These scores are still candidate-only. They are meant to audit add/readiness on strong-board days, not to legislate direct action without later replay judgement.",
            "The prototypes already separate many improved-expression days from remaining under-exposed days, which means existing daily information still has useful headroom before intraday becomes mandatory.",
        ]

        return V114JCpoMarketVoiceStateTransitionVectorPrototypeReport(
            summary=summary,
            prototype_summary=prototype_summary,
            scored_strong_day_rows=scored_rows,
            candidate_add_band_rows=candidate_add_band_rows,
            candidate_hold_band_rows=candidate_hold_band_rows,
            interpretation=interpretation,
        )


def write_v114j_cpo_market_voice_state_transition_vector_prototype_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V114JCpoMarketVoiceStateTransitionVectorPrototypeReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path

