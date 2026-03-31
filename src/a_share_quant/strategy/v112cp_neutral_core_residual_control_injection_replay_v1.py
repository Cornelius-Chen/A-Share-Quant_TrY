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
class V112CPNeutralCoreResidualControlInjectionReplayReport:
    summary: dict[str, Any]
    replay_trade_rows: list[dict[str, Any]]
    comparison_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "replay_trade_rows": self.replay_trade_rows,
            "comparison_rows": self.comparison_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CPNeutralCoreResidualControlInjectionReplayAnalyzer:
    DEFAULT_HOLDING_DAYS = 20

    def analyze(
        self,
        *,
        bh_payload: dict[str, Any],
        cn_payload: dict[str, Any],
        co_payload: dict[str, Any],
    ) -> V112CPNeutralCoreResidualControlInjectionReplayReport:
        trade_rows = sorted(list(bh_payload.get("trade_rows", [])), key=lambda row: str(row.get("entry_date")))
        if not trade_rows:
            raise ValueError("V1.12CP requires neutral trade rows.")

        baseline_total_return = float(dict(bh_payload.get("summary", {})).get("total_return", 0.0))
        baseline_max_drawdown = float(dict(bh_payload.get("summary", {})).get("max_drawdown", 0.0))
        symbols = sorted({str(row.get("symbol")) for row in trade_rows})
        bar_cache = self._build_bar_cache(symbols=symbols)

        cn_rule = dict(cn_payload.get("selected_rule", {}))
        co_rule = dict(co_payload.get("selected_rule", {}))

        current_equity = 1.0
        peak_equity = 1.0
        max_drawdown = 0.0
        replay_trade_rows: list[dict[str, Any]] = []
        holding_veto_count = 0
        de_risk_count = 0

        for trade in trade_rows:
            symbol = str(trade.get("symbol"))
            entry_date = str(trade.get("entry_date"))
            exit_date = str(trade.get("exit_date"))
            bars = bar_cache[symbol]
            entry_equity = current_equity

            if symbol == "300308":
                trade_path, band_payload = self._core_leader_trade_path(
                    bars=bars,
                    entry_date=entry_date,
                    rule=cn_rule,
                )
                if band_payload["control_band"] == "holding_veto_band":
                    holding_veto_count += 1
            elif symbol == "300502":
                trade_path, band_payload = self._high_beta_core_trade_path(
                    bars=bars,
                    entry_date=entry_date,
                    rule=co_rule,
                )
                if band_payload["control_band"] == "de_risk_band":
                    de_risk_count += 1
            else:
                trade_path = self._standard_trade_path(bars=bars, entry_date=entry_date, exit_date=exit_date)
                band_payload = {
                    "control_band": "neutral_baseline_band",
                    "trigger_reason": "unchanged_neutral_path",
                    "trigger_trade_date": None,
                    "trigger_day_index": None,
                    "trigger_snapshot": None,
                }

            for point in trade_path:
                path_equity = entry_equity * float(point["price_ratio"])
                peak_equity = max(peak_equity, path_equity)
                max_drawdown = min(max_drawdown, path_equity / peak_equity - 1.0)
            current_equity = entry_equity * float(trade_path[-1]["price_ratio"])
            replay_trade_rows.append(
                {
                    "entry_date": entry_date,
                    "symbol": symbol,
                    "stage_family": str(trade.get("stage_family")),
                    "role_family": str(trade.get("role_family")),
                    "baseline_forward_return_20d": float(trade.get("realized_forward_return_20d", 0.0)),
                    "replay_forward_return_20d": round(float(trade_path[-1]["price_ratio"]) - 1.0, 4),
                    **band_payload,
                }
            )

        total_return = current_equity - 1.0
        summary = {
            "acceptance_posture": "freeze_v112cp_neutral_core_residual_control_injection_replay_v1",
            "replayed_trade_count": len(replay_trade_rows),
            "holding_veto_count": holding_veto_count,
            "de_risk_count": de_risk_count,
            "selected_total_return": round(total_return, 4),
            "selected_max_drawdown": round(max_drawdown, 4),
            "neutral_total_return": round(baseline_total_return, 4),
            "neutral_max_drawdown": round(baseline_max_drawdown, 4),
            "return_delta_vs_neutral": round(total_return - baseline_total_return, 4),
            "drawdown_delta_vs_neutral": round(max_drawdown - baseline_max_drawdown, 4),
            "beats_neutral_return": total_return > baseline_total_return,
            "beats_neutral_drawdown": max_drawdown > baseline_max_drawdown,
            "combined_promotion_ready": total_return > baseline_total_return and max_drawdown > baseline_max_drawdown,
            "recommended_next_posture": "keep_core_residual_controls_split_do_not_force_combined_promotion_yet",
        }
        comparison_rows = [
            {
                "comparison_name": "replay_vs_neutral_return",
                "baseline_value": round(baseline_total_return, 4),
                "pilot_value": round(total_return, 4),
                "delta": round(total_return - baseline_total_return, 4),
            },
            {
                "comparison_name": "replay_vs_neutral_drawdown",
                "baseline_value": round(baseline_max_drawdown, 4),
                "pilot_value": round(max_drawdown, 4),
                "delta": round(max_drawdown - baseline_max_drawdown, 4),
            },
        ]
        interpretation = [
            "V1.12CP injects the already-extracted 300308 holding-veto and 300502 de-risk controls back into the neutral baseline without reopening selector logic.",
            "The replay checks whether core residual controls can improve neutral as a combined action layer rather than as isolated contributor studies.",
            "If the combined replay improves drawdown but gives back some return, the right reading is not failure of the individual controls but remaining calibration tension between leader-exit discipline and high-beta expression retention.",
        ]
        return V112CPNeutralCoreResidualControlInjectionReplayReport(
            summary=summary,
            replay_trade_rows=replay_trade_rows,
            comparison_rows=comparison_rows,
            interpretation=interpretation,
        )

    def _core_leader_trade_path(
        self,
        *,
        bars: pd.DataFrame,
        entry_date: str,
        rule: dict[str, Any],
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
        for idx, row in window.iloc[1:].iterrows():
            if idx < int(rule["min_holding_day"]):
                continue
            ma10_break = float(row["close"]) < float(row["ma10"])
            ma5_break = float(row["close"]) < float(row["ma5"])
            if (
                ma10_break
                and float(row["draw_from_peak"]) <= -float(rule["drawdown_threshold"])
                and float(row["ret_from_entry"]) <= float(rule["retained_gain_buffer"])
                and (not bool(rule["require_ma5_break"]) or ma5_break)
            ):
                trigger_idx = int(idx)
                break

        final_idx = trigger_idx if trigger_idx is not None else len(window) - 1
        trade_path = self._path_rows(window=window.iloc[: final_idx + 1], entry_close=entry_close)
        if trigger_idx is None:
            return trade_path, {
                "control_band": "continue_band",
                "trigger_reason": "hold_valid_under_current_state_band",
                "trigger_trade_date": None,
                "trigger_day_index": None,
                "trigger_snapshot": None,
            }
        row = window.loc[trigger_idx]
        return trade_path, {
            "control_band": "holding_veto_band",
            "trigger_reason": "late_main_markup_holding_veto",
            "trigger_trade_date": str(row["trade_date"]),
            "trigger_day_index": trigger_idx,
            "trigger_snapshot": self._snapshot_from_row(row=row, index=trigger_idx),
        }

    def _high_beta_core_trade_path(
        self,
        *,
        bars: pd.DataFrame,
        entry_date: str,
        rule: dict[str, Any],
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
        for idx, row in window.iloc[1:].iterrows():
            if idx < int(rule["min_holding_day"]):
                continue
            ma5_break = float(row["close"]) < float(row["ma5"])
            ma10_break = float(row["close"]) < float(row["ma10"])
            if (
                (not bool(rule["require_ma5_break"]) or ma5_break)
                and (not bool(rule["require_ma10_break"]) or ma10_break)
                and float(row["draw_from_peak"]) <= -float(rule["drawdown_threshold"])
                and float(row["ret_from_entry"]) >= float(rule["retained_gain_floor"])
            ):
                trigger_idx = int(idx)
                break

        trade_path = self._derisk_path_rows(
            window=window,
            entry_close=entry_close,
            trigger_idx=trigger_idx,
            reduced_exposure=float(rule["reduced_exposure"]),
        )
        if trigger_idx is None:
            return trade_path, {
                "control_band": "continue_band",
                "trigger_reason": "expression_stays_eligible_under_current_state_band",
                "trigger_trade_date": None,
                "trigger_day_index": None,
                "trigger_snapshot": None,
            }
        row = window.loc[trigger_idx]
        return trade_path, {
            "control_band": "de_risk_band",
            "trigger_reason": "late_main_markup_expression_risk_derisk",
            "trigger_trade_date": str(row["trade_date"]),
            "trigger_day_index": trigger_idx,
            "trigger_snapshot": self._snapshot_from_row(row=row, index=trigger_idx),
        }

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

    def _derisk_path_rows(
        self,
        *,
        window: pd.DataFrame,
        entry_close: float,
        trigger_idx: int | None,
        reduced_exposure: float,
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        trigger_close = float(window.loc[trigger_idx, "close"]) if trigger_idx is not None else None
        for idx, row in window.iterrows():
            price_ratio = float(row["close"]) / entry_close
            if trigger_idx is not None and idx > trigger_idx and trigger_close is not None:
                pre_trigger_ratio = trigger_close / entry_close
                post_trigger_ratio = float(row["close"]) / trigger_close
                price_ratio = pre_trigger_ratio * ((1.0 - reduced_exposure) + reduced_exposure * post_trigger_ratio)
            rows.append({"trade_date": str(row["trade_date"]), "price_ratio": price_ratio})
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


def write_v112cp_neutral_core_residual_control_injection_replay_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CPNeutralCoreResidualControlInjectionReplayReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
