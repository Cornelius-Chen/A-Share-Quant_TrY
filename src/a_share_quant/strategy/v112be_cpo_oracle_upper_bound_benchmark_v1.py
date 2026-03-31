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

import pandas as pd

from a_share_quant.strategy.v112a_price_cycle_inference_v1 import TencentKlineClient
from a_share_quant.strategy.v112am_cpo_extremely_small_core_skeleton_training_pilot_v1 import (
    V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer,
)
from a_share_quant.strategy.v112au_cpo_bounded_row_geometry_widen_pilot_v1 import (
    V112AUCPOBoundedRowGeometryWidenPilotAnalyzer,
)


@dataclass(slots=True)
class V112BECPOOracleUpperBoundBenchmarkReport:
    summary: dict[str, Any]
    trade_rows: list[dict[str, Any]]
    equity_curve_rows: list[dict[str, Any]]
    drawdown_curve_rows: list[dict[str, Any]]
    phase_capture_rows: list[dict[str, Any]]
    role_capture_rows: list[dict[str, Any]]
    plot_bundle_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "trade_rows": self.trade_rows,
            "equity_curve_rows": self.equity_curve_rows,
            "drawdown_curve_rows": self.drawdown_curve_rows,
            "phase_capture_rows": self.phase_capture_rows,
            "role_capture_rows": self.role_capture_rows,
            "plot_bundle_rows": self.plot_bundle_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BECPOOracleUpperBoundBenchmarkAnalyzer:
    HOLDING_DAYS = 20

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        v112bc_protocol_payload: dict[str, Any],
        v112bb_pilot_payload: dict[str, Any],
        training_layer_payload: dict[str, Any],
        cycle_reconstruction_payload: dict[str, Any],
    ) -> V112BECPOOracleUpperBoundBenchmarkReport:
        if not bool(dict(phase_charter_payload.get("summary", {})).get("do_open_v112be_now")):
            raise ValueError("V1.12BE must be open before the oracle benchmark runs.")
        if int(dict(v112bc_protocol_payload.get("summary", {})).get("oracle_track_count", 0)) != 1:
            raise ValueError("V1.12BE requires the oracle track from V1.12BC.")
        if not bool(dict(v112bb_pilot_payload.get("summary", {})).get("default_10_row_pilot_established")):
            raise ValueError("V1.12BE requires the default 10-row guarded baseline from V1.12BB.")

        training_layer_rows = list(training_layer_payload.get("training_layer_rows", []))
        if len(training_layer_rows) != 10:
            raise ValueError("V1.12BE expects the frozen 10-row training-facing layer.")

        pilot_analyzer = V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer()
        widen_analyzer = V112AUCPOBoundedRowGeometryWidenPilotAnalyzer()
        stage_map = pilot_analyzer._stage_map(list(cycle_reconstruction_payload.get("reconstructed_stage_rows", [])))  # noqa: SLF001
        samples = widen_analyzer._build_samples(  # noqa: SLF001
            widened_rows=training_layer_rows,
            stage_map=stage_map,
            pilot_analyzer=pilot_analyzer,
        )
        samples.sort(key=lambda item: item.trade_date)
        if not samples:
            raise ValueError("V1.12BE requires non-empty samples on the default 10-row layer.")

        by_date: dict[str, list[Any]] = {}
        for sample in samples:
            by_date.setdefault(sample.trade_date, []).append(sample)
        ordered_dates = sorted(by_date)
        bar_cache = self._bar_cache(symbols=sorted({sample.symbol for sample in samples}))

        equity_curve_rows: list[dict[str, Any]] = []
        trade_rows: list[dict[str, Any]] = []
        current_equity = 1.0
        idx = 0

        while idx < len(ordered_dates):
            trade_date = ordered_dates[idx]
            candidates = by_date[trade_date]
            best_sample = max(candidates, key=lambda item: float(item.forward_return_20d))
            if float(best_sample.forward_return_20d) <= 0.0:
                self._append_equity_point(
                    equity_curve_rows=equity_curve_rows,
                    trade_date=trade_date,
                    equity=current_equity,
                    position_state="cash",
                    symbol="CASH",
                )
                idx += 1
                continue

            trade_path = self._trade_path(sample=best_sample, bars=bar_cache[best_sample.symbol])
            if not trade_path:
                self._append_equity_point(
                    equity_curve_rows=equity_curve_rows,
                    trade_date=trade_date,
                    equity=current_equity,
                    position_state="cash",
                    symbol="CASH",
                )
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
                self._append_equity_point(
                    equity_curve_rows=equity_curve_rows,
                    trade_date=str(row["trade_date"]),
                    equity=path_equity,
                    position_state="long",
                    symbol=best_sample.symbol,
                )

            current_equity = float(equity_curve_rows[-1]["equity"])
            exit_date = str(trade_path[-1]["trade_date"])
            trade_rows.append(
                {
                    "entry_date": best_sample.trade_date,
                    "exit_date": exit_date,
                    "symbol": best_sample.symbol,
                    "stage_family": best_sample.stage_family,
                    "role_family": best_sample.role_family,
                    "catalyst_sequence_label": best_sample.catalyst_sequence_label,
                    "oracle_forward_return_20d": round(current_equity / entry_equity - 1.0, 4),
                    "sample_forward_return_20d": round(float(best_sample.forward_return_20d), 4),
                    "path_max_drawdown": round(float(max_path_drawdown), 4),
                    "entry_equity": round(entry_equity, 4),
                    "exit_equity": round(current_equity, 4),
                }
            )
            idx = self._next_index_after_exit(ordered_dates=ordered_dates, exit_date=exit_date)

        drawdown_curve_rows = self._drawdown_curve(equity_curve_rows=equity_curve_rows)
        total_return = float(equity_curve_rows[-1]["equity"]) - 1.0 if equity_curve_rows else 0.0
        max_drawdown = min((float(row["drawdown"]) for row in drawdown_curve_rows), default=0.0)
        positive_sum = sum(float(row["oracle_forward_return_20d"]) for row in trade_rows if float(row["oracle_forward_return_20d"]) > 0.0)
        negative_sum = sum(float(row["oracle_forward_return_20d"]) for row in trade_rows if float(row["oracle_forward_return_20d"]) < 0.0)
        profit_factor = positive_sum / abs(negative_sum) if negative_sum < 0.0 else math.inf
        hit_rate = sum(1 for row in trade_rows if float(row["oracle_forward_return_20d"]) > 0.0) / len(trade_rows) if trade_rows else 0.0
        cash_days = sum(1 for row in equity_curve_rows if str(row["position_state"]) == "cash")

        summary = {
            "acceptance_posture": "freeze_v112be_cpo_oracle_upper_bound_benchmark_v1",
            "track_name": "oracle_upper_bound_track",
            "future_information_allowed": True,
            "training_layer_row_count": len(training_layer_rows),
            "sample_count": len(samples),
            "trade_count": len(trade_rows),
            "equity_curve_point_count": len(equity_curve_rows),
            "drawdown_curve_point_count": len(drawdown_curve_rows),
            "total_return": round(total_return, 4),
            "max_drawdown": round(float(max_drawdown), 4),
            "profit_factor": round(float(profit_factor), 4) if profit_factor != math.inf else "inf",
            "hit_rate": round(float(hit_rate), 4),
            "cash_ratio": round(float(cash_days / len(equity_curve_rows)), 4) if equity_curve_rows else 0.0,
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": "open_aggressive_no_leak_black_box_portfolio_pilot_against_the_oracle_benchmark",
        }
        interpretation = [
            "This benchmark is hindsight-only and exists to estimate the ex-post profit ceiling on the frozen 10-row CPO layer.",
            "It is not a trainable model and cannot be used as a no-leak signal.",
            "Its value is to provide an upper-bound comparison target for later aggressive and neutral no-leak portfolio tracks.",
        ]
        return V112BECPOOracleUpperBoundBenchmarkReport(
            summary=summary,
            trade_rows=trade_rows,
            equity_curve_rows=equity_curve_rows,
            drawdown_curve_rows=drawdown_curve_rows,
            phase_capture_rows=self._capture_rows(
                values=[str(row["stage_family"]) for row in trade_rows],
                field_name="stage_family",
                total=len(trade_rows),
            ),
            role_capture_rows=self._capture_rows(
                values=[str(row["role_family"]) for row in trade_rows],
                field_name="role_family",
                total=len(trade_rows),
            ),
            plot_bundle_rows=[
                {
                    "plot_name": "oracle_equity_curve",
                    "series_name": "equity",
                    "point_count": len(equity_curve_rows),
                    "source_layer": "oracle_upper_bound_track",
                },
                {
                    "plot_name": "oracle_drawdown_curve",
                    "series_name": "drawdown",
                    "point_count": len(drawdown_curve_rows),
                    "source_layer": "oracle_upper_bound_track",
                },
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

    def _trade_path(self, *, sample: Any, bars: pd.DataFrame) -> list[dict[str, Any]]:
        matching = bars.index[bars["trade_date"] == sample.trade_date].tolist()
        if not matching:
            return []
        start_idx = int(matching[0])
        end_idx = start_idx + self.HOLDING_DAYS
        if end_idx >= len(bars):
            return []
        entry_close = float(bars.iloc[start_idx]["close"])
        if entry_close == 0.0:
            return []
        path: list[dict[str, Any]] = []
        for idx in range(start_idx, end_idx + 1):
            close = float(bars.iloc[idx]["close"])
            path.append(
                {
                    "trade_date": str(bars.iloc[idx]["trade_date"]),
                    "price_ratio": close / entry_close,
                }
            )
        return path

    def _append_equity_point(
        self,
        *,
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

    def _drawdown_curve(self, *, equity_curve_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        peak = 0.0
        rows: list[dict[str, Any]] = []
        for row in equity_curve_rows:
            equity = float(row["equity"])
            peak = max(peak, equity)
            drawdown = equity / peak - 1.0 if peak > 0.0 else 0.0
            rows.append(
                {
                    "trade_date": str(row["trade_date"]),
                    "drawdown": round(float(drawdown), 6),
                }
            )
        return rows

    def _capture_rows(self, *, values: list[str], field_name: str, total: int) -> list[dict[str, Any]]:
        counts: dict[str, int] = {}
        for value in values:
            counts[value] = counts.get(value, 0) + 1
        rows = []
        for key, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
            rows.append(
                {
                    field_name: key,
                    "trade_count": count,
                    "trade_ratio": round(float(count / total), 4) if total else 0.0,
                }
            )
        return rows

    def _next_index_after_exit(self, *, ordered_dates: list[str], exit_date: str) -> int:
        return bisect_right(ordered_dates, exit_date)


def write_v112be_cpo_oracle_upper_bound_benchmark_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BECPOOracleUpperBoundBenchmarkReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
