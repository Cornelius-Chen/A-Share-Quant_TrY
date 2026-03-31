from __future__ import annotations

import json
import math
import os
from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path
from typing import Any

os.environ.setdefault("PANDAS_NO_USE_NUMEXPR", "1")
os.environ.setdefault("PANDAS_NO_USE_BOTTLENECK", "1")

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from a_share_quant.strategy.v112a_price_cycle_inference_v1 import TencentKlineClient
from a_share_quant.strategy.v112am_cpo_extremely_small_core_skeleton_training_pilot_v1 import (
    V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer,
)
from a_share_quant.strategy.v112ao_cpo_role_layer_patch_pilot_v1 import (
    V112AOCPORoleLayerPatchPilotAnalyzer,
)
from a_share_quant.strategy.v112au_cpo_bounded_row_geometry_widen_pilot_v1 import (
    V112AUCPOBoundedRowGeometryWidenPilotAnalyzer,
)
from a_share_quant.strategy.v112av_cpo_branch_role_geometry_patch_pilot_v1 import (
    V112AVCPOBranchRoleGeometryPatchPilotAnalyzer,
)


@dataclass(slots=True)
class V112BICPOCrossSectionalRankerPilotReport:
    summary: dict[str, Any]
    trade_rows: list[dict[str, Any]]
    equity_curve_rows: list[dict[str, Any]]
    drawdown_curve_rows: list[dict[str, Any]]
    comparison_rows: list[dict[str, Any]]
    plot_bundle_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "trade_rows": self.trade_rows,
            "equity_curve_rows": self.equity_curve_rows,
            "drawdown_curve_rows": self.drawdown_curve_rows,
            "comparison_rows": self.comparison_rows,
            "plot_bundle_rows": self.plot_bundle_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BICPOCrossSectionalRankerPilotAnalyzer:
    HOLDING_DAYS = 20
    MIN_TRAIN_SAMPLES = 120

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        oracle_benchmark_payload: dict[str, Any],
        aggressive_pilot_payload: dict[str, Any],
        neutral_pilot_payload: dict[str, Any],
        training_layer_payload: dict[str, Any],
        cycle_reconstruction_payload: dict[str, Any],
    ) -> V112BICPOCrossSectionalRankerPilotReport:
        if not bool(dict(phase_charter_payload.get("summary", {})).get("do_open_v112bi_now")):
            raise ValueError("V1.12BI must be open before the ranker pilot runs.")

        oracle_summary = dict(oracle_benchmark_payload.get("summary", {}))
        aggressive_summary = dict(aggressive_pilot_payload.get("summary", {}))
        neutral_summary = dict(neutral_pilot_payload.get("summary", {}))
        training_layer_rows = list(training_layer_payload.get("training_layer_rows", []))
        if len(training_layer_rows) != 10:
            raise ValueError("V1.12BI expects the frozen 10-row training-facing layer.")

        pilot_analyzer = V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer()
        widen_analyzer = V112AUCPOBoundedRowGeometryWidenPilotAnalyzer()
        role_patch = V112AOCPORoleLayerPatchPilotAnalyzer()
        branch_patch = V112AVCPOBranchRoleGeometryPatchPilotAnalyzer()
        stage_map = pilot_analyzer._stage_map(list(cycle_reconstruction_payload.get("reconstructed_stage_rows", [])))  # noqa: SLF001
        samples = widen_analyzer._build_samples(  # noqa: SLF001
            widened_rows=training_layer_rows,
            stage_map=stage_map,
            pilot_analyzer=pilot_analyzer,
        )
        samples.sort(key=lambda item: item.trade_date)
        truth_index = {str(row.get("symbol")): row for row in training_layer_rows}
        impl_features = widen_analyzer._implementation_feature_map(samples=samples, truth_index=truth_index)  # noqa: SLF001
        feature_names = (
            list(pilot_analyzer.FEATURE_NAMES)
            + list(role_patch.PATCH_FEATURE_NAMES)
            + list(widen_analyzer.IMPLEMENTATION_FEATURE_NAMES)
            + list(branch_patch.BRANCH_PATCH_FEATURE_NAMES)
        )

        sample_rows: list[dict[str, Any]] = []
        for sample in samples:
            row = {
                "trade_date": sample.trade_date,
                "symbol": sample.symbol,
                "stage_family": sample.stage_family,
                "role_family": sample.role_family,
                "catalyst_sequence_label": sample.catalyst_sequence_label,
                "forward_return_20d": float(sample.forward_return_20d),
                "max_drawdown_20d": float(sample.max_drawdown_20d),
            }
            for name in pilot_analyzer.FEATURE_NAMES:
                row[name] = float(sample.feature_values[name])
            for name in role_patch.PATCH_FEATURE_NAMES:
                row[name] = float(sample.feature_values[name])
            for name in widen_analyzer.IMPLEMENTATION_FEATURE_NAMES:
                row[name] = float(impl_features[(sample.trade_date, sample.symbol)][name])
            branch_values = branch_patch._branch_patch_values(sample=sample)  # noqa: SLF001
            for idx, name in enumerate(branch_patch.BRANCH_PATCH_FEATURE_NAMES):
                row[name] = float(branch_values[idx])
            sample_rows.append(row)

        frame = pd.DataFrame(sample_rows).sort_values(["trade_date", "symbol"]).reset_index(drop=True)
        bar_cache = self._bar_cache(symbols=sorted(frame["symbol"].unique().tolist()))
        ordered_dates = sorted(frame["trade_date"].unique().tolist())
        equity_curve_rows: list[dict[str, Any]] = []
        trade_rows: list[dict[str, Any]] = []
        current_equity = 1.0
        idx = 0

        while idx < len(ordered_dates):
            trade_date = ordered_dates[idx]
            decision_idx = idx - self.HOLDING_DAYS
            if decision_idx < 0:
                self._append_equity_point(equity_curve_rows, trade_date, current_equity, "cash", "CASH")
                idx += 1
                continue
            cutoff_date = ordered_dates[decision_idx]
            train_frame = frame[frame["trade_date"] <= cutoff_date]
            if len(train_frame) < self.MIN_TRAIN_SAMPLES:
                self._append_equity_point(equity_curve_rows, trade_date, current_equity, "cash", "CASH")
                idx += 1
                continue

            model = HistGradientBoostingRegressor(max_depth=4, learning_rate=0.05, max_iter=150, random_state=42)
            x_train = train_frame[feature_names].to_numpy(dtype=float)
            y_train = train_frame["forward_return_20d"].to_numpy(dtype=float)
            model.fit(x_train, y_train)
            positive_train = train_frame[train_frame["forward_return_20d"] > 0.0]["forward_return_20d"].to_numpy(dtype=float)
            positive_mean = float(np.mean(positive_train)) if len(positive_train) else 0.0
            predicted_floor = max(0.03, positive_mean * 0.25)

            current_frame = frame[frame["trade_date"] == trade_date].copy()
            x_current = current_frame[feature_names].to_numpy(dtype=float)
            predicted_returns = model.predict(x_current)
            current_frame["predicted_return_20d"] = predicted_returns
            current_frame["ranker_score"] = (
                current_frame["predicted_return_20d"]
                + 0.04 * current_frame["weighted_breadth_ratio"]
                + 0.03 * current_frame["catalyst_presence_proxy"]
                + 0.02 * current_frame["confidence_tier_numeric"]
                - 0.02 * current_frame["turnover_state_numeric"]
                - 0.02 * current_frame["window_uncertainty_numeric"]
            )
            chosen_row = current_frame.sort_values(
                ["ranker_score", "predicted_return_20d", "forward_return_20d"],
                ascending=[False, False, False],
            ).iloc[0]

            if float(chosen_row["predicted_return_20d"]) <= predicted_floor:
                self._append_equity_point(equity_curve_rows, trade_date, current_equity, "cash", "CASH")
                idx += 1
                continue

            trade_path = self._trade_path(
                symbol=str(chosen_row["symbol"]),
                entry_date=str(chosen_row["trade_date"]),
                bars=bar_cache[str(chosen_row["symbol"])],
            )
            if not trade_path:
                self._append_equity_point(equity_curve_rows, trade_date, current_equity, "cash", "CASH")
                idx += 1
                continue

            entry_equity = current_equity
            path_peak = entry_equity
            max_path_drawdown = 0.0
            for row in trade_path:
                path_equity = entry_equity * float(row["price_ratio"])
                path_peak = max(path_peak, path_equity)
                if path_peak > 0.0:
                    max_path_drawdown = min(max_path_drawdown, path_equity / path_peak - 1.0)
                self._append_equity_point(equity_curve_rows, str(row["trade_date"]), path_equity, "long", str(chosen_row["symbol"]))

            current_equity = float(equity_curve_rows[-1]["equity"])
            exit_date = str(trade_path[-1]["trade_date"])
            trade_rows.append(
                {
                    "entry_date": str(chosen_row["trade_date"]),
                    "exit_date": exit_date,
                    "symbol": str(chosen_row["symbol"]),
                    "stage_family": str(chosen_row["stage_family"]),
                    "role_family": str(chosen_row["role_family"]),
                    "catalyst_sequence_label": str(chosen_row["catalyst_sequence_label"]),
                    "predicted_return_20d": round(float(chosen_row["predicted_return_20d"]), 4),
                    "ranker_score": round(float(chosen_row["ranker_score"]), 4),
                    "prediction_floor": round(float(predicted_floor), 4),
                    "realized_forward_return_20d": round(current_equity / entry_equity - 1.0, 4),
                    "sample_forward_return_20d": round(float(chosen_row["forward_return_20d"]), 4),
                    "path_max_drawdown": round(float(max_path_drawdown), 4),
                    "entry_equity": round(entry_equity, 4),
                    "exit_equity": round(current_equity, 4),
                }
            )
            idx = self._next_index_after_exit(ordered_dates=ordered_dates, exit_date=exit_date)

        drawdown_curve_rows = self._drawdown_curve(equity_curve_rows)
        total_return = float(equity_curve_rows[-1]["equity"]) - 1.0 if equity_curve_rows else 0.0
        max_drawdown = min((float(row["drawdown"]) for row in drawdown_curve_rows), default=0.0)
        positive_sum = sum(float(row["realized_forward_return_20d"]) for row in trade_rows if float(row["realized_forward_return_20d"]) > 0.0)
        negative_sum = sum(float(row["realized_forward_return_20d"]) for row in trade_rows if float(row["realized_forward_return_20d"]) < 0.0)
        profit_factor = positive_sum / abs(negative_sum) if negative_sum < 0.0 else math.inf
        hit_rate = sum(1 for row in trade_rows if float(row["realized_forward_return_20d"]) > 0.0) / len(trade_rows) if trade_rows else 0.0
        cash_days = sum(1 for row in equity_curve_rows if str(row["position_state"]) == "cash")

        comparison_rows = [
            {
                "comparison_name": "return_vs_aggressive",
                "aggressive_value": aggressive_summary.get("total_return"),
                "ranker_value": round(total_return, 4),
                "delta": round(total_return - float(aggressive_summary.get("total_return", 0.0)), 4),
            },
            {
                "comparison_name": "return_vs_neutral",
                "neutral_value": neutral_summary.get("total_return"),
                "ranker_value": round(total_return, 4),
                "delta": round(total_return - float(neutral_summary.get("total_return", 0.0)), 4),
            },
            {
                "comparison_name": "max_drawdown_vs_neutral",
                "neutral_value": neutral_summary.get("max_drawdown"),
                "ranker_value": round(float(max_drawdown), 4),
                "delta": round(float(max_drawdown) - float(neutral_summary.get("max_drawdown", 0.0)), 4),
            },
            {
                "comparison_name": "return_gap_vs_oracle",
                "oracle_value": oracle_summary.get("total_return"),
                "ranker_value": round(total_return, 4),
                "gap": round(float(oracle_summary.get("total_return", 0.0)) - total_return, 4),
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v112bi_cpo_cross_sectional_ranker_pilot_v1",
            "track_name": "cross_sectional_ranker_track",
            "no_leak_enforced": True,
            "training_layer_row_count": len(training_layer_rows),
            "sample_count": len(frame),
            "trade_count": len(trade_rows),
            "equity_curve_point_count": len(equity_curve_rows),
            "drawdown_curve_point_count": len(drawdown_curve_rows),
            "total_return": round(total_return, 4),
            "max_drawdown": round(float(max_drawdown), 4),
            "profit_factor": round(float(profit_factor), 4) if profit_factor != math.inf else "inf",
            "hit_rate": round(float(hit_rate), 4),
            "cash_ratio": round(float(cash_days / len(equity_curve_rows)), 4) if equity_curve_rows else 0.0,
            "oracle_return_gap": round(float(oracle_summary.get("total_return", 0.0)) - total_return, 4),
            "aggressive_return_delta": round(total_return - float(aggressive_summary.get("total_return", 0.0)), 4),
            "neutral_return_delta": round(total_return - float(neutral_summary.get("total_return", 0.0)), 4),
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": "compare_ranker_vs_classifier_tracks_and_only_expand_model_zoo_if_marginal_gain_is_real",
        }
        interpretation = [
            "The ranker line tests whether direct return ordering is a better target function than winner classification on the same lawful 10-row CPO layer.",
            "It remains point-in-time and non-deployable.",
            "Its value is comparative: if ranking does not improve the current lines, the project should avoid unnecessary model-zoo expansion.",
        ]
        return V112BICPOCrossSectionalRankerPilotReport(
            summary=summary,
            trade_rows=trade_rows,
            equity_curve_rows=equity_curve_rows,
            drawdown_curve_rows=drawdown_curve_rows,
            comparison_rows=comparison_rows,
            plot_bundle_rows=[
                {"plot_name": "ranker_equity_curve", "series_name": "equity", "point_count": len(equity_curve_rows)},
                {"plot_name": "ranker_drawdown_curve", "series_name": "drawdown", "point_count": len(drawdown_curve_rows)},
            ],
            interpretation=interpretation,
        )

    def _bar_cache(self, *, symbols: list[str]) -> dict[str, pd.DataFrame]:
        client = TencentKlineClient()
        cache: dict[str, pd.DataFrame] = {}
        for symbol in symbols:
            frame = client.fetch_daily_bars(symbol).sort_values("date").reset_index(drop=True).copy()
            frame["trade_date"] = pd.to_datetime(frame["date"]).dt.strftime("%Y-%m-%d")
            cache[symbol] = frame
        return cache

    def _trade_path(self, *, symbol: str, entry_date: str, bars: pd.DataFrame) -> list[dict[str, Any]]:
        matching = bars.index[bars["trade_date"] == entry_date].tolist()
        if not matching:
            return []
        start_idx = int(matching[0])
        end_idx = start_idx + self.HOLDING_DAYS
        if end_idx >= len(bars):
            return []
        entry_close = float(bars.iloc[start_idx]["close"])
        if entry_close == 0.0:
            return []
        rows: list[dict[str, Any]] = []
        for idx in range(start_idx, end_idx + 1):
            close = float(bars.iloc[idx]["close"])
            rows.append({"trade_date": str(bars.iloc[idx]["trade_date"]), "price_ratio": close / entry_close})
        return rows

    def _append_equity_point(
        self,
        equity_curve_rows: list[dict[str, Any]],
        trade_date: str,
        equity: float,
        position_state: str,
        symbol: str,
    ) -> None:
        row = {
            "trade_date": trade_date,
            "equity": round(float(equity), 6),
            "position_state": position_state,
            "symbol": symbol,
        }
        if equity_curve_rows and str(equity_curve_rows[-1]["trade_date"]) == trade_date:
            equity_curve_rows[-1] = row
        else:
            equity_curve_rows.append(row)

    def _drawdown_curve(self, equity_curve_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        peak = 0.0
        rows: list[dict[str, Any]] = []
        for row in equity_curve_rows:
            equity = float(row["equity"])
            peak = max(peak, equity)
            drawdown = equity / peak - 1.0 if peak > 0.0 else 0.0
            rows.append({"trade_date": str(row["trade_date"]), "drawdown": round(float(drawdown), 6)})
        return rows

    def _next_index_after_exit(self, *, ordered_dates: list[str], exit_date: str) -> int:
        return bisect_right(ordered_dates, exit_date)


def write_v112bi_cpo_cross_sectional_ranker_pilot_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BICPOCrossSectionalRankerPilotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
