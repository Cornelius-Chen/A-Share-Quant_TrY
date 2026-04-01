from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    load_json_report,
)
from a_share_quant.strategy.v114k_cpo_market_voice_state_transition_add_reduce_audit_replay_v1 import (
    V114KCpoMarketVoiceStateTransitionAddReduceAuditReplayAnalyzer,
)
from a_share_quant.strategy.v114m_cpo_posture_environment_split_review_v1 import (
    V114MCpoPostureEnvironmentSplitReviewAnalyzer,
)


@dataclass(slots=True)
class V114NCpoVectorOverlayRefinementReviewReport:
    summary: dict[str, Any]
    candidate_rows: list[dict[str, Any]]
    recommended_row: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_rows": self.candidate_rows,
            "recommended_row": self.recommended_row,
            "interpretation": self.interpretation,
        }


class V114NCpoVectorOverlayRefinementReviewAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit = V114KCpoMarketVoiceStateTransitionAddReduceAuditReplayAnalyzer(repo_root=repo_root)
        self.segmenter = V114MCpoPostureEnvironmentSplitReviewAnalyzer(repo_root=repo_root)

    @staticmethod
    def _segment_name(row: dict[str, Any], *, add_threshold: float) -> str:
        return V114MCpoPostureEnvironmentSplitReviewAnalyzer._segment_name(row, add_threshold=add_threshold)

    def _segment_curve(self, rows: list[dict[str, Any]]) -> float:
        segment_curve = 1.0
        previous_equity = None
        for row in rows:
            equity = float(row["equity_after_close"])
            if previous_equity is not None and previous_equity > 0:
                segment_curve *= equity / previous_equity
            previous_equity = equity
        return round(segment_curve, 4)

    def analyze(
        self,
        *,
        v113n_payload: dict[str, Any],
        v113v_payload: dict[str, Any],
        v114e_payload: dict[str, Any],
        v114j_payload: dict[str, Any],
        v114m_payload: dict[str, Any],
    ) -> V114NCpoVectorOverlayRefinementReviewReport:
        summary_n = dict(v113n_payload.get("summary", {}))
        summary_v = dict(v113v_payload.get("summary", {}))
        summary_e = dict(v114e_payload.get("summary", {}))
        summary_j = dict(v114j_payload.get("summary", {}))
        summary_m = dict(v114m_payload.get("summary", {}))
        if str(summary_n.get("acceptance_posture")) != "freeze_v113n_cpo_real_board_episode_population_v1":
            raise ValueError("V1.14N expects V1.13N real board episode population.")
        if str(summary_v.get("acceptance_posture")) != "freeze_v113v_cpo_full_board_execution_main_feed_replay_v1":
            raise ValueError("V1.14N expects V1.13V full-board replay.")
        if str(summary_e.get("acceptance_posture")) != "freeze_v114e_cpo_default_sizing_replay_promotion_v1":
            raise ValueError("V1.14N expects V1.14E default sizing replay promotion.")
        if str(summary_j.get("acceptance_posture")) != "freeze_v114j_cpo_market_voice_state_transition_vector_prototype_v1":
            raise ValueError("V1.14N expects V1.14J vector prototype.")
        if str(summary_m.get("acceptance_posture")) != "freeze_v114m_cpo_posture_environment_split_review_v1":
            raise ValueError("V1.14N expects V1.14M posture environment split review.")

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

        default_config = dict(v114e_payload.get("promoted_default_row", {}).get("config", {}))
        prototype_threshold = round(
            float(v114j_payload.get("prototype_summary", {}).get("market_voice_add_threshold", 0.398127)),
            6,
        )
        baseline_segments = {
            row["segment_name"]: row
            for row in list(v114m_payload.get("posture_segment_rows", []))
            if row.get("posture_name") == "default_expectancy_mainline"
        }
        vector_segments = {
            row["segment_name"]: row
            for row in list(v114m_payload.get("posture_segment_rows", []))
            if row.get("posture_name") == "vector_overlay_experimental"
        }
        base_vector_curve = round(float(v114m_payload.get("summary", {}).get("vector_overlay_full_curve", 3.0841)), 4)
        base_vector_drawdown = round(float(v114m_payload.get("summary", {}).get("vector_overlay_full_max_drawdown", 0.2862)), 4)
        if base_vector_curve == 0.0:
            base_vector_curve = 3.0841
        if base_vector_drawdown == 0.0:
            base_vector_drawdown = 0.2862

        thresholds = [prototype_threshold, round(prototype_threshold + 0.03, 6), round(prototype_threshold + 0.06, 6)]
        extra_uplifts = [0.01, 0.02]
        candidate_floors = [0.30, 0.35]

        candidate_rows: list[dict[str, Any]] = []
        for threshold in thresholds:
            for extra_uplift in extra_uplifts:
                for candidate_floor in candidate_floors:
                    config = dict(default_config)
                    config.update(
                        {
                            "candidate_add_threshold": threshold,
                            "candidate_extra_uplift": extra_uplift,
                            "candidate_floor": candidate_floor,
                            "max_expression_weight": 0.14,
                        }
                    )
                    summary_row, day_rows, action_rows = self.audit._simulate_with_candidate_audit(
                        config=config,
                        episode_rows=episode_rows,
                        board_symbols=board_symbols,
                        daily_bars=daily_bars,
                    )
                    all_strong_rows = [row for row in day_rows if bool(row["board_strong"])]
                    high_readiness_rows = [
                        row
                        for row in all_strong_rows
                        if self._segment_name(row, add_threshold=threshold) == "high_readiness_strong"
                    ]
                    ordinary_strong_rows = [
                        row
                        for row in all_strong_rows
                        if self._segment_name(row, add_threshold=threshold) == "ordinary_strong"
                    ]
                    all_strong_curve = self._segment_curve(all_strong_rows) if all_strong_rows else 1.0
                    high_readiness_curve = self._segment_curve(high_readiness_rows) if high_readiness_rows else 1.0
                    ordinary_strong_curve = self._segment_curve(ordinary_strong_rows) if ordinary_strong_rows else 1.0
                    all_strong_mean_exposure = (
                        round(sum(float(row["gross_exposure_after_close"]) for row in all_strong_rows) / len(all_strong_rows), 6)
                        if all_strong_rows else 0.0
                    )
                    under_floor_count = sum(
                        1 for row in all_strong_rows if float(row["gross_exposure_after_close"]) < float(default_config["under_exposure_floor"])
                    )
                    refinement_score = (
                        (float(summary_row["final_curve"]) - 1.0)
                        - 1.85 * float(summary_row["max_drawdown"])
                        + 0.18 * (all_strong_curve - 1.0)
                        + 0.10 * (high_readiness_curve - 1.0)
                        - 0.01 * under_floor_count
                    )
                    candidate_rows.append(
                        {
                            "candidate_name": f"thr_{threshold:.6f}_uplift_{extra_uplift:.2f}_floor_{candidate_floor:.2f}",
                            "config": {
                                "candidate_add_threshold": threshold,
                                "candidate_extra_uplift": extra_uplift,
                                "candidate_floor": candidate_floor,
                            },
                            "full_curve": round(float(summary_row["final_curve"]), 4),
                            "full_max_drawdown": round(float(summary_row["max_drawdown"]), 4),
                            "capture_ratio_vs_board": round(float(summary_row["capture_ratio_vs_board"]), 4),
                            "executed_order_count": int(summary_row["executed_order_count"]),
                            "add_action_count": len([row for row in action_rows if row["action_mode"] == "add"]),
                            "all_strong_curve": all_strong_curve,
                            "high_readiness_strong_curve": high_readiness_curve,
                            "ordinary_strong_curve": ordinary_strong_curve,
                            "all_strong_mean_exposure": all_strong_mean_exposure,
                            "under_floor_count": under_floor_count,
                            "beats_default_all_strong": all_strong_curve > float(baseline_segments.get("all_strong", {}).get("segment_curve", 0.0)),
                            "beats_default_high_readiness": high_readiness_curve > float(baseline_segments.get("high_readiness_strong", {}).get("segment_curve", 0.0)),
                            "beats_vector_all_strong": all_strong_curve >= float(vector_segments.get("all_strong", {}).get("segment_curve", 0.0)),
                            "beats_vector_high_readiness": high_readiness_curve >= float(vector_segments.get("high_readiness_strong", {}).get("segment_curve", 0.0)),
                            "drawdown_reduction_vs_vector": round(base_vector_drawdown - float(summary_row["max_drawdown"]), 4),
                            "curve_gap_vs_vector": round(float(summary_row["final_curve"]) - base_vector_curve, 4),
                            "refinement_score": round(refinement_score, 6),
                        }
                    )

        candidate_rows = sorted(
            candidate_rows,
            key=lambda row: (
                float(row["refinement_score"]),
                float(row["full_curve"]),
                -float(row["full_max_drawdown"]),
            ),
            reverse=True,
        )
        preferred_rows = [
            row
            for row in candidate_rows
            if float(row["drawdown_reduction_vs_vector"]) > 0.0
            and bool(row["beats_default_all_strong"])
            and bool(row["beats_default_high_readiness"])
        ]
        recommended_row = dict(preferred_rows[0] if preferred_rows else candidate_rows[0])
        summary = {
            "acceptance_posture": "freeze_v114n_cpo_vector_overlay_refinement_review_v1",
            "candidate_count": len(candidate_rows),
            "base_vector_overlay_curve": base_vector_curve,
            "base_vector_overlay_max_drawdown": base_vector_drawdown,
            "recommended_candidate_name": recommended_row["candidate_name"],
            "recommended_curve": recommended_row["full_curve"],
            "recommended_max_drawdown": recommended_row["full_max_drawdown"],
            "recommended_drawdown_reduction_vs_vector": recommended_row["drawdown_reduction_vs_vector"],
            "recommended_curve_gap_vs_vector": recommended_row["curve_gap_vs_vector"],
            "recommended_next_posture": "use_refined_vector_overlay_as_parallel_candidate_only_until_cross_board_or_harsher_environment_judgement",
        }
        interpretation = [
            "V1.14N refines only the vector-overlay candidate and does not reopen default sizing search.",
            "The objective is to keep the overlay's strong-segment lead while compressing drawdown, not to discover a new universal parameter truth from CPO alone.",
            "Recommended candidates remain candidate-only until later board transfer or harsher-environment judgement confirms the gain is not CPO-specific luck.",
        ]
        return V114NCpoVectorOverlayRefinementReviewReport(
            summary=summary,
            candidate_rows=candidate_rows,
            recommended_row=recommended_row,
            interpretation=interpretation,
        )


def write_v114n_cpo_vector_overlay_refinement_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V114NCpoVectorOverlayRefinementReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V114NCpoVectorOverlayRefinementReviewAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113n_payload=load_json_report(repo_root / "reports" / "analysis" / "v113n_cpo_real_board_episode_population_v1.json"),
        v113v_payload=load_json_report(repo_root / "reports" / "analysis" / "v113v_cpo_full_board_execution_main_feed_replay_v1.json"),
        v114e_payload=load_json_report(repo_root / "reports" / "analysis" / "v114e_cpo_default_sizing_replay_promotion_v1.json"),
        v114j_payload=load_json_report(repo_root / "reports" / "analysis" / "v114j_cpo_market_voice_state_transition_vector_prototype_v1.json"),
        v114m_payload=load_json_report(repo_root / "reports" / "analysis" / "v114m_cpo_posture_environment_split_review_v1.json"),
    )
    output_path = write_v114n_cpo_vector_overlay_refinement_review_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v114n_cpo_vector_overlay_refinement_review_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
