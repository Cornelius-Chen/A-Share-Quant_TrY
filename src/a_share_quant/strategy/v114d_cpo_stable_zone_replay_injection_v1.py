from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    V114ACPOConstrainedAddReducePolicySearchPilotAnalyzer,
    load_json_report,
)


@dataclass(slots=True)
class V114DCPOStableZoneReplayInjectionReport:
    summary: dict[str, Any]
    candidate_rows: list[dict[str, Any]]
    recommended_candidate_row: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_rows": self.candidate_rows,
            "recommended_candidate_row": self.recommended_candidate_row,
            "interpretation": self.interpretation,
        }


class V114DCPOStableZoneReplayInjectionAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _trade_date(self, row: dict[str, Any]) -> str:
        return str(row["trade_date"])

    def _efficiency_score(self, row: dict[str, Any], *, baseline_curve: float, baseline_drawdown: float) -> float:
        curve_gain = float(row["final_curve"]) - baseline_curve
        drawdown_uplift = float(row["max_drawdown"]) - baseline_drawdown
        capture = float(row["capture_ratio_vs_board"])
        order_cost = 0.002 * float(row["executed_order_count"])
        under_exposure_penalty = 0.20 * float(row["under_exposure_penalty"])
        return round(curve_gain - 0.9 * max(0.0, drawdown_uplift) + 0.20 * capture - order_cost - under_exposure_penalty, 6)

    def analyze(
        self,
        *,
        v113n_payload: dict[str, Any],
        v113v_payload: dict[str, Any],
        v114c_payload: dict[str, Any],
    ) -> V114DCPOStableZoneReplayInjectionReport:
        summary_n = dict(v113n_payload.get("summary", {}))
        summary_v = dict(v113v_payload.get("summary", {}))
        summary_c = dict(v114c_payload.get("summary", {}))
        if str(summary_n.get("acceptance_posture")) != "freeze_v113n_cpo_real_board_episode_population_v1":
            raise ValueError("V1.14D expects V1.13N real board episode population.")
        if str(summary_v.get("acceptance_posture")) != "freeze_v113v_cpo_full_board_execution_main_feed_replay_v1":
            raise ValueError("V1.14D expects V1.13V replay.")
        if str(summary_c.get("acceptance_posture")) != "freeze_v114c_cpo_batched_local_policy_frontier_search_v1":
            raise ValueError("V1.14D expects V1.14C batched frontier search.")

        base_analyzer = V114ACPOConstrainedAddReducePolicySearchPilotAnalyzer(repo_root=self.repo_root)
        base_analyzer._replay_day_rows_from_payload = list(v113v_payload.get("replay_day_rows", []))
        episode_rows = sorted(list(v113n_payload.get("internal_point_rows", [])), key=self._trade_date)
        board_symbols = {
            "300308",
            "300502",
            "300394",
            "002281",
            "603083",
            "688205",
            "301205",
            "300570",
            "688498",
            "688313",
            "300757",
            "601869",
            "600487",
            "600522",
            "000070",
            "603228",
            "001267",
            "300620",
            "300548",
            "000988",
        }
        daily_bars = base_analyzer._load_daily_bars(
            self.repo_root / "data" / "raw" / "daily_bars" / "sina_daily_bars_cpo_execution_main_feed_v1.csv"
        )
        risk_limits_path = self.repo_root / "PROJECT_LIMITATION" / "risk_limits.yaml"

        baseline_curve = float(summary_v.get("final_equity", 0.0)) / float(summary_v.get("initial_capital", 1.0))
        baseline_drawdown = 0.0
        baseline_peak = None
        for row in base_analyzer._replay_day_rows_from_payload:
            equity = float(row["equity_after_close"])
            baseline_peak = equity if baseline_peak is None else max(baseline_peak, equity)
            baseline_drawdown = max(
                baseline_drawdown,
                0.0 if baseline_peak <= 0 else 1.0 - equity / baseline_peak,
            )

        candidate_definitions = [
            {
                "candidate_name": "expectancy_max_injection",
                "config": {
                    "core_module_leader_base_weight": 0.1,
                    "packaging_process_enabler_base_weight": 0.08,
                    "high_beta_core_module_base_weight": 0.06,
                    "laser_chip_component_base_weight": 0.04,
                    "board_avg_return_min": 0.05,
                    "board_breadth_min": 0.8,
                    "strong_board_uplift": 0.04,
                    "derisk_keep_fraction": 0.5,
                    "under_exposure_floor": 0.25,
                },
            },
            {
                "candidate_name": "balanced_injection",
                "config": {
                    "core_module_leader_base_weight": 0.1,
                    "packaging_process_enabler_base_weight": 0.08,
                    "high_beta_core_module_base_weight": 0.06,
                    "laser_chip_component_base_weight": 0.04,
                    "board_avg_return_min": 0.05,
                    "board_breadth_min": 0.8,
                    "strong_board_uplift": 0.04,
                    "derisk_keep_fraction": 0.5,
                    "under_exposure_floor": 0.30,
                },
            },
            {
                "candidate_name": "conservative_stable_injection",
                "config": {
                    "core_module_leader_base_weight": 0.1,
                    "packaging_process_enabler_base_weight": 0.08,
                    "high_beta_core_module_base_weight": 0.06,
                    "laser_chip_component_base_weight": 0.04,
                    "board_avg_return_min": 0.05,
                    "board_breadth_min": 0.8,
                    "strong_board_uplift": 0.03,
                    "derisk_keep_fraction": 0.5,
                    "under_exposure_floor": 0.30,
                },
            },
        ]

        candidate_rows: list[dict[str, Any]] = []
        for candidate in candidate_definitions:
            simulated = base_analyzer._simulate_config(
                config=dict(candidate["config"]),
                episode_rows=episode_rows,
                board_symbols=board_symbols,
                daily_bars=daily_bars,
                risk_limits_path=risk_limits_path,
            )
            simulated["candidate_name"] = candidate["candidate_name"]
            simulated["curve_delta_vs_baseline"] = round(float(simulated["final_curve"]) - baseline_curve, 4)
            simulated["drawdown_delta_vs_baseline"] = round(float(simulated["max_drawdown"]) - baseline_drawdown, 4)
            simulated["efficiency_score"] = self._efficiency_score(
                simulated,
                baseline_curve=baseline_curve,
                baseline_drawdown=baseline_drawdown,
            )
            candidate_rows.append(simulated)

        recommended_candidate_row = max(
            candidate_rows,
            key=lambda item: (
                float(item["efficiency_score"]),
                float(item["final_curve"]),
                -float(item["max_drawdown"]),
            ),
        )

        summary = {
            "acceptance_posture": "freeze_v114d_cpo_stable_zone_replay_injection_v1",
            "candidate_count": len(candidate_rows),
            "baseline_curve": round(baseline_curve, 4),
            "baseline_max_drawdown": round(baseline_drawdown, 4),
            "recommended_candidate_name": str(recommended_candidate_row["candidate_name"]),
            "recommended_curve": round(float(recommended_candidate_row["final_curve"]), 4),
            "recommended_max_drawdown": round(float(recommended_candidate_row["max_drawdown"]), 4),
            "recommended_capture_ratio_vs_board": round(float(recommended_candidate_row["capture_ratio_vs_board"]), 4),
            "recommended_next_posture": "promote_recommended_stable_zone_injection_as_default_probability_expectancy_sizing_candidate",
        }
        interpretation = [
            "V1.14D no longer searches. It injects three representative stable-zone points back into replay so the default sizing candidate is chosen from actual path behavior rather than only parameter scores.",
            "The three representatives intentionally span the current frontier: expectancy-max, balanced, and conservative-stable.",
            "This is the last step before promotion: decide which stable-zone representative should become the default probability-expectancy sizing candidate in the live replay stack.",
        ]
        return V114DCPOStableZoneReplayInjectionReport(
            summary=summary,
            candidate_rows=candidate_rows,
            recommended_candidate_row=recommended_candidate_row,
            interpretation=interpretation,
        )


def write_v114d_cpo_stable_zone_replay_injection_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V114DCPOStableZoneReplayInjectionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
