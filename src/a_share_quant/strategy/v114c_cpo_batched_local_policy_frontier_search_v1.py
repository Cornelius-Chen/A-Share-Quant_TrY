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
class V114CCPOBatchedLocalPolicyFrontierSearchReport:
    summary: dict[str, Any]
    batch_rows: list[dict[str, Any]]
    top_config_rows: list[dict[str, Any]]
    stable_zone_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "batch_rows": self.batch_rows,
            "top_config_rows": self.top_config_rows,
            "stable_zone_rows": self.stable_zone_rows,
            "interpretation": self.interpretation,
        }


class V114CCPOBatchedLocalPolicyFrontierSearchAnalyzer:
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

    def _build_batch_plan(self, *, best_config: dict[str, Any]) -> list[dict[str, Any]]:
        seen: set[tuple[float, float, float]] = set()
        plan: list[dict[str, Any]] = []

        def add_config(batch_name: str, uplift: float, derisk_keep: float, under_floor: float) -> None:
            key = (round(uplift, 4), round(derisk_keep, 4), round(under_floor, 4))
            if key in seen:
                return
            seen.add(key)
            config = dict(best_config)
            config["strong_board_uplift"] = uplift
            config["derisk_keep_fraction"] = derisk_keep
            config["under_exposure_floor"] = under_floor
            plan.append(
                {
                    "batch_name": batch_name,
                    "config": config,
                }
            )

        base_uplift = float(best_config["strong_board_uplift"])
        base_derisk = float(best_config["derisk_keep_fraction"])
        base_floor = float(best_config["under_exposure_floor"])

        for uplift in [0.02, 0.03, 0.04, 0.05]:
            add_config("uplift_sweep", uplift, base_derisk, base_floor)
        for under_floor in [0.25, 0.30, 0.35, 0.40]:
            add_config("under_exposure_floor_sweep", base_uplift, base_derisk, under_floor)
        for derisk_keep in [0.40, 0.50, 0.60]:
            add_config("derisk_keep_fraction_sweep", base_uplift, derisk_keep, base_floor)
        for uplift, under_floor in [(0.03, 0.30), (0.03, 0.35), (0.04, 0.30), (0.04, 0.35)]:
            add_config("uplift_floor_interaction", uplift, base_derisk, under_floor)

        return plan

    def analyze(
        self,
        *,
        v113n_payload: dict[str, Any],
        v113v_payload: dict[str, Any],
        v114a_payload: dict[str, Any],
    ) -> V114CCPOBatchedLocalPolicyFrontierSearchReport:
        summary_n = dict(v113n_payload.get("summary", {}))
        summary_v = dict(v113v_payload.get("summary", {}))
        summary_a = dict(v114a_payload.get("summary", {}))
        if str(summary_n.get("acceptance_posture")) != "freeze_v113n_cpo_real_board_episode_population_v1":
            raise ValueError("V1.14C expects V1.13N real board episode population.")
        if str(summary_v.get("acceptance_posture")) != "freeze_v113v_cpo_full_board_execution_main_feed_replay_v1":
            raise ValueError("V1.14C expects V1.13V replay.")
        if str(summary_a.get("acceptance_posture")) != "freeze_v114a_cpo_constrained_add_reduce_policy_search_pilot_v1":
            raise ValueError("V1.14C expects V1.14A constrained add/reduce pilot.")

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

        best_config = dict(v114a_payload.get("best_config_row", {}).get("config", {}))
        if not best_config:
            raise ValueError("V1.14C requires a best config row from V1.14A.")

        batch_plan = self._build_batch_plan(best_config=best_config)
        config_rows: list[dict[str, Any]] = []
        for planned in batch_plan:
            result = base_analyzer._simulate_config(
                config=planned["config"],
                episode_rows=episode_rows,
                board_symbols=board_symbols,
                daily_bars=daily_bars,
                risk_limits_path=risk_limits_path,
            )
            config_rows.append(
                {
                    "batch_name": planned["batch_name"],
                    **result,
                    "efficiency_score": self._efficiency_score(
                        result,
                        baseline_curve=baseline_curve,
                        baseline_drawdown=baseline_drawdown,
                    ),
                }
            )

        batch_names = sorted({str(row["batch_name"]) for row in config_rows})
        batch_rows: list[dict[str, Any]] = []
        for batch_name in batch_names:
            rows = [row for row in config_rows if str(row["batch_name"]) == batch_name]
            best_row = max(rows, key=lambda item: (float(item["efficiency_score"]), float(item["final_curve"])))
            batch_rows.append(
                {
                    "batch_name": batch_name,
                    "config_count": len(rows),
                    "best_curve": round(float(best_row["final_curve"]), 4),
                    "best_max_drawdown": round(float(best_row["max_drawdown"]), 4),
                    "best_capture_ratio_vs_board": round(float(best_row["capture_ratio_vs_board"]), 4),
                    "best_efficiency_score": round(float(best_row["efficiency_score"]), 6),
                    "best_config": dict(best_row["config"]),
                }
            )

        top_config_rows = sorted(
            config_rows,
            key=lambda item: (float(item["efficiency_score"]), float(item["final_curve"]), -float(item["max_drawdown"])),
            reverse=True,
        )[:10]

        stable_zone_rows = [
            row
            for row in top_config_rows
            if float(row["final_curve"]) >= baseline_curve + 0.25
            and float(row["max_drawdown"]) <= baseline_drawdown + 0.06
        ]

        best_row = top_config_rows[0]
        stable_zone_uplifts = sorted(
            {
                float(row["config"]["strong_board_uplift"])
                for row in stable_zone_rows
            }
        )
        stable_zone_floors = sorted(
            {
                float(row["config"]["under_exposure_floor"])
                for row in stable_zone_rows
            }
        )
        stable_zone_derisks = sorted(
            {
                float(row["config"]["derisk_keep_fraction"])
                for row in stable_zone_rows
            }
        )

        summary = {
            "acceptance_posture": "freeze_v114c_cpo_batched_local_policy_frontier_search_v1",
            "tested_config_count": len(config_rows),
            "batch_count": len(batch_rows),
            "baseline_curve": round(baseline_curve, 4),
            "baseline_max_drawdown": round(baseline_drawdown, 4),
            "best_curve": round(float(best_row["final_curve"]), 4),
            "best_max_drawdown": round(float(best_row["max_drawdown"]), 4),
            "best_capture_ratio_vs_board": round(float(best_row["capture_ratio_vs_board"]), 4),
            "stable_zone_count": len(stable_zone_rows),
            "stable_zone_strong_board_uplift_values": stable_zone_uplifts,
            "stable_zone_under_exposure_floor_values": stable_zone_floors,
            "stable_zone_derisk_keep_fraction_values": stable_zone_derisks,
            "recommended_next_posture": "use_stable_zone_as_replay_injection_candidate_set_before_wider_search",
        }
        interpretation = [
            "V1.14C uses structural batches rather than random sweeps: uplift, exposure-floor, de-risk, and the key uplift-floor interaction are tested separately and then aggregated.",
            "This preserves interpretability. The result is not just a single best point, but a first local frontier and a first stable zone around it.",
            "The purpose is to approach an optimal policy as a reproducible zone rather than chase a lucky point that looks good only in one replay path.",
        ]
        return V114CCPOBatchedLocalPolicyFrontierSearchReport(
            summary=summary,
            batch_rows=batch_rows,
            top_config_rows=top_config_rows,
            stable_zone_rows=stable_zone_rows,
            interpretation=interpretation,
        )


def write_v114c_cpo_batched_local_policy_frontier_search_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V114CCPOBatchedLocalPolicyFrontierSearchReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
