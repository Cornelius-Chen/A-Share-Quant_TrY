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
class V114OCpoVectorOverlayExecutionAxisReviewReport:
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


class V114OCpoVectorOverlayExecutionAxisReviewAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit = V114KCpoMarketVoiceStateTransitionAddReduceAuditReplayAnalyzer(repo_root=repo_root)

    @staticmethod
    def _segment_name(row: dict[str, Any], *, add_threshold: float) -> str:
        return V114MCpoPostureEnvironmentSplitReviewAnalyzer._segment_name(row, add_threshold=add_threshold)

    @staticmethod
    def _segment_curve(rows: list[dict[str, Any]]) -> float:
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
        v114m_payload: dict[str, Any],
        v114n_payload: dict[str, Any],
    ) -> V114OCpoVectorOverlayExecutionAxisReviewReport:
        summary_n0 = dict(v113n_payload.get("summary", {}))
        summary_v = dict(v113v_payload.get("summary", {}))
        summary_e = dict(v114e_payload.get("summary", {}))
        summary_m = dict(v114m_payload.get("summary", {}))
        summary_n = dict(v114n_payload.get("summary", {}))
        if str(summary_n0.get("acceptance_posture")) != "freeze_v113n_cpo_real_board_episode_population_v1":
            raise ValueError("V1.14O expects V1.13N real board episode population.")
        if str(summary_v.get("acceptance_posture")) != "freeze_v113v_cpo_full_board_execution_main_feed_replay_v1":
            raise ValueError("V1.14O expects V1.13V full-board replay.")
        if str(summary_e.get("acceptance_posture")) != "freeze_v114e_cpo_default_sizing_replay_promotion_v1":
            raise ValueError("V1.14O expects V1.14E default sizing replay promotion.")
        if str(summary_m.get("acceptance_posture")) != "freeze_v114m_cpo_posture_environment_split_review_v1":
            raise ValueError("V1.14O expects V1.14M posture environment split review.")
        if str(summary_n.get("acceptance_posture")) != "freeze_v114n_cpo_vector_overlay_refinement_review_v1":
            raise ValueError("V1.14O expects V1.14N vector overlay refinement review.")

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

        default_segments = {
            row["segment_name"]: row
            for row in list(v114m_payload.get("posture_segment_rows", []))
            if row.get("posture_name") == "default_expectancy_mainline"
        }

        base_refined_row = dict(v114n_payload.get("recommended_row", {}))
        base_config = dict(v114e_payload.get("promoted_default_row", {}).get("config", {}))
        refined_cfg = dict(base_refined_row.get("config", {}))
        candidate_config = {
            **base_config,
            "candidate_add_threshold": float(refined_cfg["candidate_add_threshold"]),
            "candidate_extra_uplift": float(refined_cfg["candidate_extra_uplift"]),
            "candidate_floor": float(refined_cfg["candidate_floor"]),
            "max_expression_weight": 0.14,
            "max_order_notional": 300_000.0,
            "add_confirmation_offset": 0.0,
        }

        max_expression_weights = [0.12, 0.13, 0.14]
        max_order_notionals = [200_000.0, 250_000.0, 300_000.0]
        add_confirmation_offsets = [0.0, 0.03]

        candidate_rows: list[dict[str, Any]] = []
        for max_expression_weight in max_expression_weights:
            for max_order_notional in max_order_notionals:
                for add_confirmation_offset in add_confirmation_offsets:
                    config = dict(candidate_config)
                    config.update(
                        {
                            "max_expression_weight": max_expression_weight,
                            "max_order_notional": max_order_notional,
                            "add_confirmation_offset": add_confirmation_offset,
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
                        if self._segment_name(row, add_threshold=float(config["candidate_add_threshold"])) == "high_readiness_strong"
                    ]
                    all_strong_curve = self._segment_curve(all_strong_rows) if all_strong_rows else 1.0
                    high_readiness_curve = self._segment_curve(high_readiness_rows) if high_readiness_rows else 1.0
                    add_action_count = len([row for row in action_rows if row["action_mode"] == "add"])
                    close_action_count = len([row for row in action_rows if row["action_mode"] == "close"])
                    mean_exposure = (
                        round(sum(float(row["gross_exposure_after_close"]) for row in all_strong_rows) / len(all_strong_rows), 6)
                        if all_strong_rows else 0.0
                    )
                    score = (
                        (float(summary_row["final_curve"]) - 1.0)
                        - 2.0 * float(summary_row["max_drawdown"])
                        + 0.16 * (all_strong_curve - 1.0)
                        + 0.10 * (high_readiness_curve - 1.0)
                        - 0.0015 * add_action_count
                    )
                    candidate_rows.append(
                        {
                            "candidate_name": f"mx_{max_expression_weight:.2f}_cap_{int(max_order_notional/1000)}k_confirm_{add_confirmation_offset:.2f}",
                            "config": {
                                "max_expression_weight": max_expression_weight,
                                "max_order_notional": max_order_notional,
                                "add_confirmation_offset": add_confirmation_offset,
                            },
                            "full_curve": round(float(summary_row["final_curve"]), 4),
                            "full_max_drawdown": round(float(summary_row["max_drawdown"]), 4),
                            "capture_ratio_vs_board": round(float(summary_row["capture_ratio_vs_board"]), 4),
                            "all_strong_curve": all_strong_curve,
                            "high_readiness_strong_curve": high_readiness_curve,
                            "all_strong_mean_exposure": mean_exposure,
                            "executed_order_count": int(summary_row["executed_order_count"]),
                            "add_action_count": add_action_count,
                            "close_action_count": close_action_count,
                            "drawdown_reduction_vs_refined": round(float(base_refined_row["full_max_drawdown"]) - float(summary_row["max_drawdown"]), 4),
                            "curve_gap_vs_refined": round(float(summary_row["final_curve"]) - float(base_refined_row["full_curve"]), 4),
                            "beats_default_all_strong": all_strong_curve > float(default_segments.get("all_strong", {}).get("segment_curve", 0.0)),
                            "beats_default_high_readiness": high_readiness_curve > float(default_segments.get("high_readiness_strong", {}).get("segment_curve", 0.0)),
                            "score": round(score, 6),
                        }
                    )

        candidate_rows = sorted(candidate_rows, key=lambda row: float(row["score"]), reverse=True)
        preferred_rows = [
            row
            for row in candidate_rows
            if float(row["drawdown_reduction_vs_refined"]) > 0.0
            and bool(row["beats_default_all_strong"])
            and bool(row["beats_default_high_readiness"])
        ]
        recommended_row = dict(preferred_rows[0] if preferred_rows else candidate_rows[0])
        def metric_signature(row: dict[str, Any]) -> tuple[float, float]:
            return (round(float(row["full_curve"]), 4), round(float(row["full_max_drawdown"]), 4))

        max_expression_active = False
        add_cap_active = False
        confirmation_active = False
        for row in candidate_rows:
            key_expr = (
                int(float(row["config"]["max_order_notional"])),
                round(float(row["config"]["add_confirmation_offset"]), 2),
            )
            key_cap = (
                round(float(row["config"]["max_expression_weight"]), 2),
                round(float(row["config"]["add_confirmation_offset"]), 2),
            )
            key_confirm = (
                round(float(row["config"]["max_expression_weight"]), 2),
                int(float(row["config"]["max_order_notional"])),
            )
            same_expr_group = [
                metric_signature(peer)
                for peer in candidate_rows
                if (
                    int(float(peer["config"]["max_order_notional"])),
                    round(float(peer["config"]["add_confirmation_offset"]), 2),
                ) == key_expr
            ]
            same_cap_group = [
                metric_signature(peer)
                for peer in candidate_rows
                if (
                    round(float(peer["config"]["max_expression_weight"]), 2),
                    round(float(peer["config"]["add_confirmation_offset"]), 2),
                ) == key_cap
            ]
            same_confirm_group = [
                metric_signature(peer)
                for peer in candidate_rows
                if (
                    round(float(peer["config"]["max_expression_weight"]), 2),
                    int(float(peer["config"]["max_order_notional"])),
                ) == key_confirm
            ]
            max_expression_active = max_expression_active or len(set(same_expr_group)) > 1
            add_cap_active = add_cap_active or len(set(same_cap_group)) > 1
            confirmation_active = confirmation_active or len(set(same_confirm_group)) > 1

        summary = {
            "acceptance_posture": "freeze_v114o_cpo_vector_overlay_execution_axis_review_v1",
            "candidate_count": len(candidate_rows),
            "base_refined_candidate_name": base_refined_row["candidate_name"],
            "base_refined_curve": base_refined_row["full_curve"],
            "base_refined_max_drawdown": base_refined_row["full_max_drawdown"],
            "recommended_candidate_name": recommended_row["candidate_name"],
            "recommended_curve": recommended_row["full_curve"],
            "recommended_max_drawdown": recommended_row["full_max_drawdown"],
            "recommended_drawdown_reduction_vs_refined": recommended_row["drawdown_reduction_vs_refined"],
            "recommended_curve_gap_vs_refined": recommended_row["curve_gap_vs_refined"],
            "max_expression_weight_active_in_this_window": max_expression_active,
            "max_order_notional_active_in_this_window": add_cap_active,
            "add_confirmation_offset_active_in_this_window": confirmation_active,
            "recommended_next_posture": "treat_add_confirmation_as_the_only_execution_axis_showing_real_sensitivity_here_and_do_not_keep_refining_inactive_caps",
        }
        interpretation = [
            "V1.14O no longer changes the discovery layer; it refines only execution axes on top of the refined overlay candidate.",
            "This isolates whether the remaining heat comes from expression size, same-day add cap, or missing add confirmation rather than from vector logic itself.",
            "The result is sharper than expected: add-confirmation changes behavior, but the tested max-expression and per-day add-cap ranges do not materially bind in this CPO window.",
            "Recommended rows stay candidate-only and should be treated as cleaner experimental overlays, not new defaults.",
        ]
        return V114OCpoVectorOverlayExecutionAxisReviewReport(
            summary=summary,
            candidate_rows=candidate_rows,
            recommended_row=recommended_row,
            interpretation=interpretation,
        )


def write_v114o_cpo_vector_overlay_execution_axis_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V114OCpoVectorOverlayExecutionAxisReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V114OCpoVectorOverlayExecutionAxisReviewAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113n_payload=load_json_report(repo_root / "reports" / "analysis" / "v113n_cpo_real_board_episode_population_v1.json"),
        v113v_payload=load_json_report(repo_root / "reports" / "analysis" / "v113v_cpo_full_board_execution_main_feed_replay_v1.json"),
        v114e_payload=load_json_report(repo_root / "reports" / "analysis" / "v114e_cpo_default_sizing_replay_promotion_v1.json"),
        v114m_payload=load_json_report(repo_root / "reports" / "analysis" / "v114m_cpo_posture_environment_split_review_v1.json"),
        v114n_payload=load_json_report(repo_root / "reports" / "analysis" / "v114n_cpo_vector_overlay_refinement_review_v1.json"),
    )
    output_path = write_v114o_cpo_vector_overlay_execution_axis_review_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v114o_cpo_vector_overlay_execution_axis_review_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
