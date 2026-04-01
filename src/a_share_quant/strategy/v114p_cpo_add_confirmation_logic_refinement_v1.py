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
class V114PCpoAddConfirmationLogicRefinementReport:
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


class V114PCpoAddConfirmationLogicRefinementAnalyzer:
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
        v114o_payload: dict[str, Any],
    ) -> V114PCpoAddConfirmationLogicRefinementReport:
        summary_n0 = dict(v113n_payload.get("summary", {}))
        summary_v = dict(v113v_payload.get("summary", {}))
        summary_e = dict(v114e_payload.get("summary", {}))
        summary_m = dict(v114m_payload.get("summary", {}))
        summary_n = dict(v114n_payload.get("summary", {}))
        summary_o = dict(v114o_payload.get("summary", {}))
        if str(summary_n0.get("acceptance_posture")) != "freeze_v113n_cpo_real_board_episode_population_v1":
            raise ValueError("V1.14P expects V1.13N real board episode population.")
        if str(summary_v.get("acceptance_posture")) != "freeze_v113v_cpo_full_board_execution_main_feed_replay_v1":
            raise ValueError("V1.14P expects V1.13V full-board replay.")
        if str(summary_e.get("acceptance_posture")) != "freeze_v114e_cpo_default_sizing_replay_promotion_v1":
            raise ValueError("V1.14P expects V1.14E default sizing replay promotion.")
        if str(summary_m.get("acceptance_posture")) != "freeze_v114m_cpo_posture_environment_split_review_v1":
            raise ValueError("V1.14P expects V1.14M posture environment split review.")
        if str(summary_n.get("acceptance_posture")) != "freeze_v114n_cpo_vector_overlay_refinement_review_v1":
            raise ValueError("V1.14P expects V1.14N vector overlay refinement review.")
        if str(summary_o.get("acceptance_posture")) != "freeze_v114o_cpo_vector_overlay_execution_axis_review_v1":
            raise ValueError("V1.14P expects V1.14O execution axis review.")

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

        base_vector_row = dict(v114n_payload.get("recommended_row", {}))
        exec_row = dict(v114o_payload.get("recommended_row", {}))
        base_config = dict(v114e_payload.get("promoted_default_row", {}).get("config", {}))

        candidate_configs = [
            {
                "candidate_name": "constant_offset_0.03",
                "candidate_add_threshold": float(base_vector_row["config"]["candidate_add_threshold"]),
                "candidate_extra_uplift": float(base_vector_row["config"]["candidate_extra_uplift"]),
                "candidate_floor": float(base_vector_row["config"]["candidate_floor"]),
                "add_confirmation_mode": "constant",
                "add_confirmation_offset": 0.03,
                "max_expression_weight": 0.14,
                "max_order_notional": 300_000.0,
            },
            {
                "candidate_name": "persistence_relaxed",
                "candidate_add_threshold": float(base_vector_row["config"]["candidate_add_threshold"]),
                "candidate_extra_uplift": float(base_vector_row["config"]["candidate_extra_uplift"]),
                "candidate_floor": float(base_vector_row["config"]["candidate_floor"]),
                "add_confirmation_mode": "persistence_relaxed",
                "add_confirmation_offset": 0.03,
                "max_expression_weight": 0.14,
                "max_order_notional": 300_000.0,
            },
            {
                "candidate_name": "voice_relaxed",
                "candidate_add_threshold": float(base_vector_row["config"]["candidate_add_threshold"]),
                "candidate_extra_uplift": float(base_vector_row["config"]["candidate_extra_uplift"]),
                "candidate_floor": float(base_vector_row["config"]["candidate_floor"]),
                "add_confirmation_mode": "voice_relaxed",
                "add_confirmation_offset": 0.03,
                "max_expression_weight": 0.14,
                "max_order_notional": 300_000.0,
            },
            {
                "candidate_name": "thin_coverage_relaxed",
                "candidate_add_threshold": float(base_vector_row["config"]["candidate_add_threshold"]),
                "candidate_extra_uplift": float(base_vector_row["config"]["candidate_extra_uplift"]),
                "candidate_floor": float(base_vector_row["config"]["candidate_floor"]),
                "add_confirmation_mode": "thin_coverage_relaxed",
                "add_confirmation_offset": 0.03,
                "max_expression_weight": 0.14,
                "max_order_notional": 300_000.0,
            },
            {
                "candidate_name": "two_stage_confirmation",
                "candidate_add_threshold": float(base_vector_row["config"]["candidate_add_threshold"]),
                "candidate_extra_uplift": float(base_vector_row["config"]["candidate_extra_uplift"]),
                "candidate_floor": float(base_vector_row["config"]["candidate_floor"]),
                "add_confirmation_mode": "two_stage",
                "add_confirmation_offset": 0.03,
                "max_expression_weight": 0.14,
                "max_order_notional": 300_000.0,
            },
            {
                "candidate_name": "execution_trimmed_reference",
                "candidate_add_threshold": float(base_vector_row["config"]["candidate_add_threshold"]),
                "candidate_extra_uplift": float(base_vector_row["config"]["candidate_extra_uplift"]),
                "candidate_floor": float(base_vector_row["config"]["candidate_floor"]),
                "add_confirmation_mode": "constant",
                "add_confirmation_offset": float(exec_row["config"]["add_confirmation_offset"]),
                "max_expression_weight": float(exec_row["config"]["max_expression_weight"]),
                "max_order_notional": float(exec_row["config"]["max_order_notional"]),
            },
        ]

        candidate_rows: list[dict[str, Any]] = []
        for config_seed in candidate_configs:
            config = {**base_config, **config_seed}
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
            candidate_rows.append(
                {
                    "candidate_name": str(config_seed["candidate_name"]),
                    "config": {
                        "add_confirmation_mode": str(config["add_confirmation_mode"]),
                        "add_confirmation_offset": float(config["add_confirmation_offset"]),
                        "max_expression_weight": float(config["max_expression_weight"]),
                        "max_order_notional": float(config["max_order_notional"]),
                    },
                    "full_curve": round(float(summary_row["final_curve"]), 4),
                    "full_max_drawdown": round(float(summary_row["max_drawdown"]), 4),
                    "capture_ratio_vs_board": round(float(summary_row["capture_ratio_vs_board"]), 4),
                    "all_strong_curve": all_strong_curve,
                    "high_readiness_strong_curve": high_readiness_curve,
                    "executed_order_count": int(summary_row["executed_order_count"]),
                    "add_action_count": len([row for row in action_rows if row["action_mode"] == "add"]),
                    "drawdown_reduction_vs_hot_overlay": round(0.2862 - float(summary_row["max_drawdown"]), 4),
                    "curve_gap_vs_hot_overlay": round(float(summary_row["final_curve"]) - 3.0841, 4),
                    "beats_default_all_strong": all_strong_curve > float(default_segments.get("all_strong", {}).get("segment_curve", 0.0)),
                    "beats_default_high_readiness": high_readiness_curve > float(default_segments.get("high_readiness_strong", {}).get("segment_curve", 0.0)),
                }
            )

        def rank_key(row: dict[str, Any]) -> tuple[Any, ...]:
            return (
                bool(row["beats_default_all_strong"]) and bool(row["beats_default_high_readiness"]),
                float(row["drawdown_reduction_vs_hot_overlay"]) > 0.0,
                float(row["full_curve"]),
                -float(row["full_max_drawdown"]),
            )

        candidate_rows = sorted(candidate_rows, key=rank_key, reverse=True)
        preferred_rows = [
            row
            for row in candidate_rows
            if bool(row["beats_default_all_strong"])
            and bool(row["beats_default_high_readiness"])
            and float(row["drawdown_reduction_vs_hot_overlay"]) > 0.0
        ]
        recommended_row = dict(preferred_rows[0] if preferred_rows else candidate_rows[0])

        summary = {
            "acceptance_posture": "freeze_v114p_cpo_add_confirmation_logic_refinement_v1",
            "candidate_count": len(candidate_rows),
            "recommended_candidate_name": recommended_row["candidate_name"],
            "recommended_curve": recommended_row["full_curve"],
            "recommended_max_drawdown": recommended_row["full_max_drawdown"],
            "recommended_drawdown_reduction_vs_hot_overlay": recommended_row["drawdown_reduction_vs_hot_overlay"],
            "recommended_curve_gap_vs_hot_overlay": recommended_row["curve_gap_vs_hot_overlay"],
            "recommended_next_posture": "use_daily_confirmation_logic_if_it_preserves_more_curve_than_constant_offset_else_prepare_intraday_confirmation_layer",
        }
        interpretation = [
            "V1.14P no longer searches generic caps. It asks a narrower question: can conditional daily confirmation outperform a blunt constant confirmation offset?",
            "The candidate modes use only existing daily information already judged useful: persistence, market voice, thin coverage, and simple two-stage confirmation.",
            "This is the last daily-only confirmation pass before intraday becomes the cleaner next layer if conditional confirmation still gives away too much curve.",
        ]
        return V114PCpoAddConfirmationLogicRefinementReport(
            summary=summary,
            candidate_rows=candidate_rows,
            recommended_row=recommended_row,
            interpretation=interpretation,
        )


def write_v114p_cpo_add_confirmation_logic_refinement_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V114PCpoAddConfirmationLogicRefinementReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V114PCpoAddConfirmationLogicRefinementAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113n_payload=load_json_report(repo_root / "reports" / "analysis" / "v113n_cpo_real_board_episode_population_v1.json"),
        v113v_payload=load_json_report(repo_root / "reports" / "analysis" / "v113v_cpo_full_board_execution_main_feed_replay_v1.json"),
        v114e_payload=load_json_report(repo_root / "reports" / "analysis" / "v114e_cpo_default_sizing_replay_promotion_v1.json"),
        v114m_payload=load_json_report(repo_root / "reports" / "analysis" / "v114m_cpo_posture_environment_split_review_v1.json"),
        v114n_payload=load_json_report(repo_root / "reports" / "analysis" / "v114n_cpo_vector_overlay_refinement_review_v1.json"),
        v114o_payload=load_json_report(repo_root / "reports" / "analysis" / "v114o_cpo_vector_overlay_execution_axis_review_v1.json"),
    )
    output_path = write_v114p_cpo_add_confirmation_logic_refinement_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v114p_cpo_add_confirmation_logic_refinement_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
