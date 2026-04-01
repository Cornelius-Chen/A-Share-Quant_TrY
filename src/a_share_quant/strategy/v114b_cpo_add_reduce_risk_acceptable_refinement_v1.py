from __future__ import annotations

import json
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    V114ACPOConstrainedAddReducePolicySearchPilotAnalyzer,
    load_json_report,
)


@dataclass(slots=True)
class V114BCPOAddReduceRiskAcceptableRefinementReport:
    summary: dict[str, Any]
    recommended_config_row: dict[str, Any]
    curve_maximizing_config_row: dict[str, Any]
    risk_acceptable_config_row: dict[str, Any]
    frontier_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "recommended_config_row": self.recommended_config_row,
            "curve_maximizing_config_row": self.curve_maximizing_config_row,
            "risk_acceptable_config_row": self.risk_acceptable_config_row,
            "frontier_rows": self.frontier_rows,
            "interpretation": self.interpretation,
        }


class V114BCPOAddReduceRiskAcceptableRefinementAnalyzer:
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

    def _choose_recommended(
        self,
        *,
        config_rows: list[dict[str, Any]],
        baseline_curve: float,
        baseline_drawdown: float,
    ) -> dict[str, Any]:
        ranked_rows: list[dict[str, Any]] = []
        for row in config_rows:
            ranked = dict(row)
            ranked["efficiency_score"] = self._efficiency_score(
                ranked,
                baseline_curve=baseline_curve,
                baseline_drawdown=baseline_drawdown,
            )
            ranked_rows.append(ranked)

        ranked_rows.sort(
            key=lambda item: (
                item["efficiency_score"],
                item["final_curve"],
                -item["max_drawdown"],
            ),
            reverse=True,
        )
        return ranked_rows[0]

    def analyze(
        self,
        *,
        v113n_payload: dict[str, Any],
        v113v_payload: dict[str, Any],
        v114a_payload: dict[str, Any],
    ) -> V114BCPOAddReduceRiskAcceptableRefinementReport:
        summary_n = dict(v113n_payload.get("summary", {}))
        summary_v = dict(v113v_payload.get("summary", {}))
        summary_a = dict(v114a_payload.get("summary", {}))
        if str(summary_n.get("acceptance_posture")) != "freeze_v113n_cpo_real_board_episode_population_v1":
            raise ValueError("V1.14B expects V1.13N real board episode population.")
        if str(summary_v.get("acceptance_posture")) != "freeze_v113v_cpo_full_board_execution_main_feed_replay_v1":
            raise ValueError("V1.14B expects V1.13V replay.")
        if str(summary_a.get("acceptance_posture")) != "freeze_v114a_cpo_constrained_add_reduce_policy_search_pilot_v1":
            raise ValueError("V1.14B expects V1.14A constrained add/reduce pilot.")

        base_analyzer = V114ACPOConstrainedAddReducePolicySearchPilotAnalyzer(repo_root=self.repo_root)
        base_analyzer._replay_day_rows_from_payload = list(v113v_payload.get("replay_day_rows", []))
        episode_rows = sorted(
            list(v113n_payload.get("internal_point_rows", [])),
            key=self._trade_date,
        )
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

        best_config = dict(v114a_payload.get("best_config_row", {}).get("config", {}))
        if not best_config:
            raise ValueError("V1.14B requires a best config row from V1.14A.")

        config_rows: list[dict[str, Any]] = []
        for strong_board_uplift, derisk_keep_fraction, under_exposure_floor in product(
            [0.03, 0.04],
            [0.50],
            [0.30, 0.35],
        ):
            config = dict(best_config)
            config["strong_board_uplift"] = strong_board_uplift
            config["derisk_keep_fraction"] = derisk_keep_fraction
            config["under_exposure_floor"] = under_exposure_floor
            config_rows.append(
                base_analyzer._simulate_config(
                    config=config,
                    episode_rows=episode_rows,
                    board_symbols=board_symbols,
                    daily_bars=daily_bars,
                    risk_limits_path=risk_limits_path,
                )
            )

        curve_maximizing_config_row = max(
            config_rows,
            key=lambda item: (
                float(item["final_curve"]),
                -float(item["max_drawdown"]),
                float(item["capture_ratio_vs_board"]),
            ),
        )

        risk_acceptable_candidates = [
            row
            for row in config_rows
            if float(row["max_drawdown"]) <= baseline_drawdown + 0.05
            and float(row["final_curve"]) >= baseline_curve + 0.10
        ]
        if risk_acceptable_candidates:
            risk_acceptable_config_row = max(
                risk_acceptable_candidates,
                key=lambda item: (
                    self._efficiency_score(
                        item,
                        baseline_curve=baseline_curve,
                        baseline_drawdown=baseline_drawdown,
                    ),
                    float(item["final_curve"]),
                ),
            )
        else:
            risk_acceptable_config_row = min(
                config_rows,
                key=lambda item: (
                    abs(float(item["max_drawdown"]) - (baseline_drawdown + 0.05)),
                    -float(item["final_curve"]),
                ),
            )

        recommended_config_row = self._choose_recommended(
            config_rows=config_rows,
            baseline_curve=baseline_curve,
            baseline_drawdown=baseline_drawdown,
        )

        frontier_rows = sorted(
            (
                {
                    **row,
                    "efficiency_score": self._efficiency_score(
                        row,
                        baseline_curve=baseline_curve,
                        baseline_drawdown=baseline_drawdown,
                    ),
                }
                for row in config_rows
            ),
            key=lambda item: (
                item["efficiency_score"],
                item["final_curve"],
                -item["max_drawdown"],
            ),
            reverse=True,
        )[:10]

        summary = {
            "acceptance_posture": "freeze_v114b_cpo_add_reduce_risk_acceptable_refinement_v1",
            "tested_local_config_count": len(config_rows),
            "baseline_curve": round(baseline_curve, 4),
            "baseline_max_drawdown": round(baseline_drawdown, 4),
            "curve_maximizing_curve": round(float(curve_maximizing_config_row["final_curve"]), 4),
            "curve_maximizing_max_drawdown": round(float(curve_maximizing_config_row["max_drawdown"]), 4),
            "risk_acceptable_curve": round(float(risk_acceptable_config_row["final_curve"]), 4),
            "risk_acceptable_max_drawdown": round(float(risk_acceptable_config_row["max_drawdown"]), 4),
            "recommended_curve": round(float(recommended_config_row["final_curve"]), 4),
            "recommended_max_drawdown": round(float(recommended_config_row["max_drawdown"]), 4),
            "recommended_capture_ratio_vs_board": round(float(recommended_config_row["capture_ratio_vs_board"]), 4),
            "recommended_next_posture": "inject_recommended_risk_acceptable_add_reduce_policy_into_replay_before_more_symbol_expansion",
        }
        interpretation = [
            "V1.14B does not reopen stock selection. It only refines the V1.14A sizing seed around the few parameters that determine whether stronger expression is still risk-acceptable.",
            "The purpose is to separate three concepts that were previously mixed together: the curve-maximizing point, the risk-acceptable point, and the actual recommended point for replay injection.",
            "This keeps the add/reduce learning path auditable while avoiding the false choice between full aggression and a return to chronically timid sizing.",
        ]
        return V114BCPOAddReduceRiskAcceptableRefinementReport(
            summary=summary,
            recommended_config_row=recommended_config_row,
            curve_maximizing_config_row=curve_maximizing_config_row,
            risk_acceptable_config_row=risk_acceptable_config_row,
            frontier_rows=frontier_rows,
            interpretation=interpretation,
        )


def write_v114b_cpo_add_reduce_risk_acceptable_refinement_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V114BCPOAddReduceRiskAcceptableRefinementReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
