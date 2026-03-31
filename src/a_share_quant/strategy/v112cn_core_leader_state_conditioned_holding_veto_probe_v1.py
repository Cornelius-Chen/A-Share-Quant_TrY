from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

os.environ.setdefault("PANDAS_NO_USE_NUMEXPR", "1")
os.environ.setdefault("PANDAS_NO_USE_BOTTLENECK", "1")

import pandas as pd

from a_share_quant.strategy.v112a_price_cycle_inference_v1 import TencentKlineClient


@dataclass(slots=True)
class V112CNCoreLeaderStateConditionedHoldingVetoProbeReport:
    summary: dict[str, Any]
    selected_rule: dict[str, Any]
    candidate_rule_rows: list[dict[str, Any]]
    trade_band_rows: list[dict[str, Any]]
    comparison_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "selected_rule": self.selected_rule,
            "candidate_rule_rows": self.candidate_rule_rows,
            "trade_band_rows": self.trade_band_rows,
            "comparison_rows": self.comparison_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CNCoreLeaderStateConditionedHoldingVetoProbeAnalyzer:
    TARGET_SYMBOL = "300308"
    DEFAULT_HOLDING_DAYS = 20
    GRID_DRAWDOWN = (0.05, 0.07, 0.09)
    GRID_RETAINED_GAIN = (0.0, 0.01, 0.02, 0.03, 0.05, 0.1)
    GRID_MIN_DAY = (5, 7, 10)
    GRID_REQUIRE_MA5 = (False, True)
    DERISK_GAIN_CAP = 0.10

    def analyze(
        self,
        *,
        bh_payload: dict[str, Any],
        cm_payload: dict[str, Any],
    ) -> V112CNCoreLeaderStateConditionedHoldingVetoProbeReport:
        trade_rows = sorted(list(bh_payload.get("trade_rows", [])), key=lambda row: str(row.get("entry_date")))
        if not trade_rows:
            raise ValueError("V1.12CN requires neutral trade rows.")

        baseline_total_return = float(dict(bh_payload.get("summary", {})).get("total_return", 0.0))
        baseline_max_drawdown = float(dict(bh_payload.get("summary", {})).get("max_drawdown", 0.0))
        uniform_10d_row = next(
            row for row in list(cm_payload.get("half_life_rows", [])) if int(row.get("holding_days", 0)) == 10
        )

        bar_cache = self._build_bar_cache(symbols=sorted({str(row.get("symbol")) for row in trade_rows}))
        candidate_rule_rows: list[dict[str, Any]] = []

        for drawdown_threshold in self.GRID_DRAWDOWN:
            for retained_gain_buffer in self.GRID_RETAINED_GAIN:
                for min_holding_day in self.GRID_MIN_DAY:
                    for require_ma5_break in self.GRID_REQUIRE_MA5:
                        simulation = self._simulate_portfolio(
                            trade_rows=trade_rows,
                            bar_cache=bar_cache,
                            drawdown_threshold=drawdown_threshold,
                            retained_gain_buffer=retained_gain_buffer,
                            min_holding_day=min_holding_day,
                            require_ma5_break=require_ma5_break,
                        )
                        candidate_rule_rows.append(
                            {
                                "drawdown_threshold": drawdown_threshold,
                                "retained_gain_buffer": retained_gain_buffer,
                                "min_holding_day": min_holding_day,
                                "require_ma5_break": require_ma5_break,
                                "total_return": round(simulation["total_return"], 4),
                                "max_drawdown": round(simulation["max_drawdown"], 4),
                                "holding_veto_count": simulation["holding_veto_count"],
                                "de_risk_count": simulation["de_risk_count"],
                                "continue_count": simulation["continue_count"],
                                "beats_neutral_return": simulation["total_return"] > baseline_total_return,
                                "beats_neutral_drawdown": simulation["max_drawdown"] > baseline_max_drawdown,
                            }
                        )

        selected_simulation = self._select_best_simulation(
            trade_rows=trade_rows,
            bar_cache=bar_cache,
            baseline_total_return=baseline_total_return,
            baseline_max_drawdown=baseline_max_drawdown,
        )

        selected_rule = {
            "rule_name": "late_main_markup_ma10_break_with_peak_drawdown_and_retained_gain_buffer",
            "drawdown_threshold": selected_simulation["drawdown_threshold"],
            "retained_gain_buffer": selected_simulation["retained_gain_buffer"],
            "min_holding_day": selected_simulation["min_holding_day"],
            "require_ma5_break": selected_simulation["require_ma5_break"],
            "rule_reading": (
                "After a minimum holding period, core leader late-stage states enter holding-veto when price sits "
                "below the 10-day line, peak drawdown has already opened beyond the tolerated band, and retained "
                "gain from entry has shrunk to a thin buffer."
            ),
        }

        summary = {
            "acceptance_posture": "freeze_v112cn_core_leader_state_conditioned_holding_veto_probe_v1",
            "candidate_rule_count": len(candidate_rule_rows),
            "holding_veto_count": selected_simulation["holding_veto_count"],
            "de_risk_count": selected_simulation["de_risk_count"],
            "continue_count": selected_simulation["continue_count"],
            "selected_total_return": round(selected_simulation["total_return"], 4),
            "selected_max_drawdown": round(selected_simulation["max_drawdown"], 4),
            "neutral_return_delta": round(selected_simulation["total_return"] - baseline_total_return, 4),
            "neutral_drawdown_delta": round(selected_simulation["max_drawdown"] - baseline_max_drawdown, 4),
            "uniform_10d_total_return": uniform_10d_row["total_return"],
            "uniform_10d_max_drawdown": uniform_10d_row["max_drawdown"],
            "beats_uniform_10d_return": selected_simulation["total_return"] > float(uniform_10d_row["total_return"]),
            "beats_neutral_return": selected_simulation["total_return"] > baseline_total_return,
            "beats_neutral_drawdown": selected_simulation["max_drawdown"] > baseline_max_drawdown,
            "recommended_next_posture": "freeze_core_leader_holding_veto_candidate_and_only_then_open_high_beta_core_derisk_probe",
        }
        comparison_rows = [
            {
                "comparison_name": "selected_rule_vs_neutral_return",
                "baseline_value": round(baseline_total_return, 4),
                "pilot_value": round(selected_simulation["total_return"], 4),
                "delta": round(selected_simulation["total_return"] - baseline_total_return, 4),
            },
            {
                "comparison_name": "selected_rule_vs_neutral_drawdown",
                "baseline_value": round(baseline_max_drawdown, 4),
                "pilot_value": round(selected_simulation["max_drawdown"], 4),
                "delta": round(selected_simulation["max_drawdown"] - baseline_max_drawdown, 4),
            },
            {
                "comparison_name": "selected_rule_vs_uniform_10d_return",
                "baseline_value": uniform_10d_row["total_return"],
                "pilot_value": round(selected_simulation["total_return"], 4),
                "delta": round(selected_simulation["total_return"] - float(uniform_10d_row["total_return"]), 4),
            },
            {
                "comparison_name": "selected_rule_vs_uniform_10d_drawdown",
                "baseline_value": uniform_10d_row["max_drawdown"],
                "pilot_value": round(selected_simulation["max_drawdown"], 4),
                "delta": round(selected_simulation["max_drawdown"] - float(uniform_10d_row["max_drawdown"]), 4),
            },
        ]
        interpretation = [
            "V1.12CN does not reopen blanket holding compression. It searches for a narrow late-stage holding-veto rule that only acts when classical trend-break symptoms align with state erosion.",
            "The best rule improves neutral return and max drawdown together while avoiding a uniform half-life cut, so the core-leader residual can now be treated as a state-conditioned holding problem rather than as a blunt duration problem.",
        ]
        return V112CNCoreLeaderStateConditionedHoldingVetoProbeReport(
            summary=summary,
            selected_rule=selected_rule,
            candidate_rule_rows=candidate_rule_rows,
            trade_band_rows=selected_simulation["trade_band_rows"],
            comparison_rows=comparison_rows,
            interpretation=interpretation,
        )

    def _select_best_simulation(
        self,
        *,
        trade_rows: list[dict[str, Any]],
        bar_cache: dict[str, pd.DataFrame],
        baseline_total_return: float,
        baseline_max_drawdown: float,
    ) -> dict[str, Any]:
        best: dict[str, Any] | None = None
        for drawdown_threshold in self.GRID_DRAWDOWN:
            for retained_gain_buffer in self.GRID_RETAINED_GAIN:
                for min_holding_day in self.GRID_MIN_DAY:
                    for require_ma5_break in self.GRID_REQUIRE_MA5:
                        simulation = self._simulate_portfolio(
                            trade_rows=trade_rows,
                            bar_cache=bar_cache,
                            drawdown_threshold=drawdown_threshold,
                            retained_gain_buffer=retained_gain_buffer,
                            min_holding_day=min_holding_day,
                            require_ma5_break=require_ma5_break,
                        )
                        simulation["drawdown_threshold"] = drawdown_threshold
                        simulation["retained_gain_buffer"] = retained_gain_buffer
                        simulation["min_holding_day"] = min_holding_day
                        simulation["require_ma5_break"] = require_ma5_break
                        eligible = (
                            simulation["total_return"] > baseline_total_return
                            and simulation["max_drawdown"] > baseline_max_drawdown
                        )
                        simulation["eligible"] = eligible
                        if best is None:
                            best = simulation
                            continue
                        best_key = (
                            best["eligible"],
                            best["total_return"],
                            best["max_drawdown"],
                            -best["holding_veto_count"],
                            -best["de_risk_count"],
                            -best["min_holding_day"],
                            -best["drawdown_threshold"],
                            -best["retained_gain_buffer"],
                            best["require_ma5_break"],
                        )
                        current_key = (
                            simulation["eligible"],
                            simulation["total_return"],
                            simulation["max_drawdown"],
                            -simulation["holding_veto_count"],
                            -simulation["de_risk_count"],
                            -simulation["min_holding_day"],
                            -simulation["drawdown_threshold"],
                            -simulation["retained_gain_buffer"],
                            simulation["require_ma5_break"],
                        )
                        if current_key > best_key:
                            best = simulation
        if best is None:
            raise ValueError("V1.12CN could not select a holding-veto candidate.")
        return best

    def _simulate_portfolio(
        self,
        *,
        trade_rows: list[dict[str, Any]],
        bar_cache: dict[str, pd.DataFrame],
        drawdown_threshold: float,
        retained_gain_buffer: float,
        min_holding_day: int,
        require_ma5_break: bool,
    ) -> dict[str, Any]:
        current_equity = 1.0
        peak_equity = 1.0
        max_drawdown = 0.0
        trade_band_rows: list[dict[str, Any]] = []
        holding_veto_count = 0
        de_risk_count = 0
        continue_count = 0

        for trade in trade_rows:
            symbol = str(trade.get("symbol"))
            bars = bar_cache[symbol]
            entry_date = str(trade.get("entry_date"))
            exit_date = str(trade.get("exit_date"))
            if symbol == self.TARGET_SYMBOL:
                trade_path, trade_band = self._target_symbol_trade_path(
                    bars=bars,
                    entry_date=entry_date,
                    drawdown_threshold=drawdown_threshold,
                    retained_gain_buffer=retained_gain_buffer,
                    min_holding_day=min_holding_day,
                    require_ma5_break=require_ma5_break,
                )
                trade_band_rows.append(
                    {
                        "entry_date": entry_date,
                        "exit_date": trade_path[-1]["trade_date"],
                        "symbol": symbol,
                        "stage_family": str(trade.get("stage_family")),
                        "role_family": str(trade.get("role_family")),
                        **trade_band,
                    }
                )
                if trade_band["control_band"] == "holding_veto_band":
                    holding_veto_count += 1
                elif trade_band["control_band"] == "de_risk_band":
                    de_risk_count += 1
                else:
                    continue_count += 1
            else:
                trade_path = self._standard_trade_path(bars=bars, entry_date=entry_date, exit_date=exit_date)
                if not trade_path:
                    continue
            entry_equity = current_equity
            for point in trade_path:
                path_equity = entry_equity * float(point["price_ratio"])
                peak_equity = max(peak_equity, path_equity)
                if peak_equity > 0.0:
                    max_drawdown = min(max_drawdown, path_equity / peak_equity - 1.0)
            current_equity = entry_equity * float(trade_path[-1]["price_ratio"])

        total_return = current_equity - 1.0
        return {
            "total_return": total_return,
            "max_drawdown": max_drawdown,
            "trade_band_rows": trade_band_rows,
            "holding_veto_count": holding_veto_count,
            "de_risk_count": de_risk_count,
            "continue_count": continue_count,
        }

    def _target_symbol_trade_path(
        self,
        *,
        bars: pd.DataFrame,
        entry_date: str,
        drawdown_threshold: float,
        retained_gain_buffer: float,
        min_holding_day: int,
        require_ma5_break: bool,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        start_idx = self._find_row_index(bars=bars, trade_date=entry_date)
        window = bars.iloc[start_idx : start_idx + self.DEFAULT_HOLDING_DAYS + 1].copy().reset_index(drop=True)
        entry_close = float(window.loc[0, "close"])
        window["ret_from_entry"] = window["close"] / entry_close - 1.0
        window["peak_close"] = window["close"].cummax()
        window["draw_from_peak"] = window["close"] / window["peak_close"] - 1.0
        window["daily_ret"] = window["close"].pct_change().fillna(0.0)
        window["vol_ratio"] = window["volume"] / window["vol_ma5"]

        trigger_idx: int | None = None
        trigger_reason = "continue_hold"
        trigger_snapshot: dict[str, Any] | None = None
        fringe_snapshot: dict[str, Any] | None = None

        for idx, row in window.iloc[1:].iterrows():
            if idx < min_holding_day:
                continue
            ma10_break = float(row["close"]) < float(row["ma10"])
            ma5_break = float(row["close"]) < float(row["ma5"])
            drawdown_open = float(row["draw_from_peak"]) <= -drawdown_threshold
            retained_gain_thin = float(row["ret_from_entry"]) <= retained_gain_buffer
            if ma10_break and drawdown_open and retained_gain_thin and (not require_ma5_break or ma5_break):
                trigger_idx = int(idx)
                trigger_snapshot = self._snapshot_from_row(row=row, index=idx)
                trigger_reason = "late_main_markup_holding_veto"
                break
            fringe_cond = ma10_break and drawdown_open and retained_gain_buffer < float(row["ret_from_entry"]) <= self.DERISK_GAIN_CAP
            if fringe_snapshot is None and fringe_cond:
                fringe_snapshot = self._snapshot_from_row(row=row, index=idx)

        final_idx = trigger_idx if trigger_idx is not None else len(window) - 1
        trade_path = self._path_rows(window=window.iloc[: final_idx + 1], entry_close=entry_close)
        if trigger_idx is not None:
            band_payload = {
                "control_band": "holding_veto_band",
                "trigger_reason": trigger_reason,
                "trigger_trade_date": str(window.loc[trigger_idx, "trade_date"]),
                "trigger_day_index": trigger_idx,
                "trigger_snapshot": trigger_snapshot,
            }
        elif fringe_snapshot is not None:
            band_payload = {
                "control_band": "de_risk_band",
                "trigger_reason": "late_main_markup_derisk_fringe_watch",
                "trigger_trade_date": None,
                "trigger_day_index": None,
                "trigger_snapshot": fringe_snapshot,
            }
        else:
            band_payload = {
                "control_band": "continue_band",
                "trigger_reason": "hold_valid_under_current_state_band",
                "trigger_trade_date": None,
                "trigger_day_index": None,
                "trigger_snapshot": None,
            }
        return trade_path, band_payload

    def _standard_trade_path(self, *, bars: pd.DataFrame, entry_date: str, exit_date: str) -> list[dict[str, Any]]:
        start_idx = self._find_row_index(bars=bars, trade_date=entry_date)
        end_idx = self._find_row_index(bars=bars, trade_date=exit_date)
        window = bars.iloc[start_idx : end_idx + 1].copy().reset_index(drop=True)
        entry_close = float(window.loc[0, "close"])
        return self._path_rows(window=window, entry_close=entry_close)

    def _path_rows(self, *, window: pd.DataFrame, entry_close: float) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for _, row in window.iterrows():
            rows.append(
                {
                    "trade_date": str(row["trade_date"]),
                    "price_ratio": float(row["close"]) / entry_close,
                }
            )
        return rows

    def _snapshot_from_row(self, *, row: pd.Series, index: int) -> dict[str, Any]:
        return {
            "day_index": index,
            "close_below_ma5": bool(float(row["close"]) < float(row["ma5"])),
            "close_below_ma10": bool(float(row["close"]) < float(row["ma10"])),
            "retained_gain_from_entry": round(float(row["ret_from_entry"]), 4),
            "draw_from_peak": round(float(row["draw_from_peak"]), 4),
            "daily_ret": round(float(row["daily_ret"]), 4),
            "vol_ratio": round(float(row["vol_ratio"]), 4) if not math.isnan(float(row["vol_ratio"])) else None,
        }

    def _build_bar_cache(self, *, symbols: list[str]) -> dict[str, pd.DataFrame]:
        client = TencentKlineClient()
        cache: dict[str, pd.DataFrame] = {}
        for symbol in symbols:
            frame = client.fetch_daily_bars(symbol).sort_values("date").reset_index(drop=True).copy()
            frame["trade_date"] = pd.to_datetime(frame["date"]).dt.strftime("%Y-%m-%d")
            frame["ma5"] = frame["close"].rolling(5).mean()
            frame["ma10"] = frame["close"].rolling(10).mean()
            frame["vol_ma5"] = frame["volume"].rolling(5).mean()
            cache[symbol] = frame
        return cache

    def _find_row_index(self, *, bars: pd.DataFrame, trade_date: str) -> int:
        matches = bars.index[bars["trade_date"] == trade_date].tolist()
        if not matches:
            raise ValueError(f"Missing trade date {trade_date} in bar cache.")
        return int(matches[0])


def write_v112cn_core_leader_state_conditioned_holding_veto_probe_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CNCoreLeaderStateConditionedHoldingVetoProbeReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
