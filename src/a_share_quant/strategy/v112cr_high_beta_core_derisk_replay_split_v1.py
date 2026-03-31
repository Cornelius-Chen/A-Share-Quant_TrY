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
class V112CRHighBetaCoreDeriskReplaySplitReport:
    summary: dict[str, Any]
    replay_rows: list[dict[str, Any]]
    comparison_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "replay_rows": self.replay_rows,
            "comparison_rows": self.comparison_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CRHighBetaCoreDeriskReplaySplitAnalyzer:
    DEFAULT_HOLDING_DAYS = 20

    def analyze(
        self,
        *,
        bh_payload: dict[str, Any],
        cq_payload: dict[str, Any],
    ) -> V112CRHighBetaCoreDeriskReplaySplitReport:
        trade_rows = sorted(list(bh_payload.get("trade_rows", [])), key=lambda row: str(row.get("entry_date")))
        if not trade_rows:
            raise ValueError("V1.12CR requires neutral trade rows.")

        baseline_total_return = float(dict(bh_payload.get("summary", {})).get("total_return", 0.0))
        baseline_max_drawdown = float(dict(bh_payload.get("summary", {})).get("max_drawdown", 0.0))
        band_rows = list(cq_payload.get("band_rows", []))
        mild_band = next(row for row in band_rows if str(row.get("band_name")) == "neutral_safe_mild_derisk_band")
        strong_band = next(row for row in band_rows if str(row.get("band_name")) == "evidence_optimizing_stronger_derisk_band")

        symbols = sorted({str(row.get("symbol")) for row in trade_rows})
        bar_cache = self._build_bar_cache(symbols=symbols)

        mild_replay = self._simulate_replay(trade_rows=trade_rows, bars=bar_cache, rule=mild_band)
        strong_replay = self._simulate_replay(trade_rows=trade_rows, bars=bar_cache, rule=strong_band)

        summary = {
            "acceptance_posture": "freeze_v112cr_high_beta_core_derisk_replay_split_v1",
            "baseline_total_return": round(baseline_total_return, 4),
            "baseline_max_drawdown": round(baseline_max_drawdown, 4),
            "mild_total_return": round(mild_replay["total_return"], 4),
            "mild_max_drawdown": round(mild_replay["max_drawdown"], 4),
            "mild_return_delta_vs_neutral": round(mild_replay["total_return"] - baseline_total_return, 4),
            "mild_drawdown_delta_vs_neutral": round(mild_replay["max_drawdown"] - baseline_max_drawdown, 4),
            "strong_total_return": round(strong_replay["total_return"], 4),
            "strong_max_drawdown": round(strong_replay["max_drawdown"], 4),
            "strong_return_delta_vs_neutral": round(strong_replay["total_return"] - baseline_total_return, 4),
            "strong_drawdown_delta_vs_neutral": round(strong_replay["max_drawdown"] - baseline_max_drawdown, 4),
            "mild_trigger_count": mild_replay["trigger_count"],
            "strong_trigger_count": strong_replay["trigger_count"],
            "preferred_band": self._select_preferred_band(
                baseline_total_return=baseline_total_return,
                baseline_max_drawdown=baseline_max_drawdown,
                mild_replay=mild_replay,
                strong_replay=strong_replay,
            ),
            "recommended_next_posture": "use_mild_band_as_neutral_safe_default_keep_strong_band_as_evidence_optimizing_sidecar",
        }
        comparison_rows = [
            {
                "comparison_name": "mild_vs_neutral_return",
                "baseline_value": round(baseline_total_return, 4),
                "pilot_value": round(mild_replay["total_return"], 4),
                "delta": round(mild_replay["total_return"] - baseline_total_return, 4),
            },
            {
                "comparison_name": "mild_vs_neutral_drawdown",
                "baseline_value": round(baseline_max_drawdown, 4),
                "pilot_value": round(mild_replay["max_drawdown"], 4),
                "delta": round(mild_replay["max_drawdown"] - baseline_max_drawdown, 4),
            },
            {
                "comparison_name": "strong_vs_neutral_return",
                "baseline_value": round(baseline_total_return, 4),
                "pilot_value": round(strong_replay["total_return"], 4),
                "delta": round(strong_replay["total_return"] - baseline_total_return, 4),
            },
            {
                "comparison_name": "strong_vs_neutral_drawdown",
                "baseline_value": round(baseline_max_drawdown, 4),
                "pilot_value": round(strong_replay["max_drawdown"], 4),
                "delta": round(strong_replay["max_drawdown"] - baseline_max_drawdown, 4),
            },
        ]
        interpretation = [
            "V1.12CR replays the two calibrated 300502 de-risk bands inside neutral separately instead of forcing a single promoted rule.",
            "The purpose is to decide which band is closer to neutral-safe deployment and which should remain an evidence-optimizing sidecar.",
        ]
        replay_rows = [
            {
                "band_name": "neutral_safe_mild_derisk_band",
                **mild_replay,
            },
            {
                "band_name": "evidence_optimizing_stronger_derisk_band",
                **strong_replay,
            },
        ]
        return V112CRHighBetaCoreDeriskReplaySplitReport(
            summary=summary,
            replay_rows=replay_rows,
            comparison_rows=comparison_rows,
            interpretation=interpretation,
        )

    def _select_preferred_band(
        self,
        *,
        baseline_total_return: float,
        baseline_max_drawdown: float,
        mild_replay: dict[str, Any],
        strong_replay: dict[str, Any],
    ) -> str:
        mild_key = (
            mild_replay["total_return"] - baseline_total_return >= -0.01,
            mild_replay["max_drawdown"] - baseline_max_drawdown,
            mild_replay["total_return"] - baseline_total_return,
        )
        strong_key = (
            strong_replay["total_return"] - baseline_total_return >= -0.01,
            strong_replay["max_drawdown"] - baseline_max_drawdown,
            strong_replay["total_return"] - baseline_total_return,
        )
        return "neutral_safe_mild_derisk_band" if mild_key >= strong_key else "evidence_optimizing_stronger_derisk_band"

    def _simulate_replay(
        self,
        *,
        trade_rows: list[dict[str, Any]],
        bars: dict[str, pd.DataFrame],
        rule: dict[str, Any],
    ) -> dict[str, Any]:
        current_equity = 1.0
        peak_equity = 1.0
        max_drawdown = 0.0
        trigger_count = 0

        for trade in trade_rows:
            symbol = str(trade.get("symbol"))
            entry_date = str(trade.get("entry_date"))
            exit_date = str(trade.get("exit_date"))
            frame = bars[symbol]
            if symbol == "300502":
                trade_path, triggered = self._high_beta_core_trade_path(
                    bars=frame,
                    entry_date=entry_date,
                    rule=rule,
                )
                if triggered:
                    trigger_count += 1
            else:
                trade_path = self._standard_trade_path(bars=frame, entry_date=entry_date, exit_date=exit_date)

            entry_equity = current_equity
            for point in trade_path:
                path_equity = entry_equity * float(point["price_ratio"])
                peak_equity = max(peak_equity, path_equity)
                max_drawdown = min(max_drawdown, path_equity / peak_equity - 1.0)
            current_equity = entry_equity * float(trade_path[-1]["price_ratio"])

        return {
            "total_return": round(current_equity - 1.0, 4),
            "max_drawdown": round(max_drawdown, 4),
            "trigger_count": trigger_count,
        }

    def _high_beta_core_trade_path(
        self,
        *,
        bars: pd.DataFrame,
        entry_date: str,
        rule: dict[str, Any],
    ) -> tuple[list[dict[str, Any]], bool]:
        start_idx = self._find_row_index(bars=bars, trade_date=entry_date)
        window = bars.iloc[start_idx : start_idx + self.DEFAULT_HOLDING_DAYS + 1].copy().reset_index(drop=True)
        entry_close = float(window.loc[0, "close"])
        window["ret_from_entry"] = window["close"] / entry_close - 1.0
        window["peak_close"] = window["close"].cummax()
        window["draw_from_peak"] = window["close"] / window["peak_close"] - 1.0

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
        return trade_path, trigger_idx is not None

    def _standard_trade_path(self, *, bars: pd.DataFrame, entry_date: str, exit_date: str) -> list[dict[str, Any]]:
        start_idx = self._find_row_index(bars=bars, trade_date=entry_date)
        end_idx = self._find_row_index(bars=bars, trade_date=exit_date)
        window = bars.iloc[start_idx : end_idx + 1].copy().reset_index(drop=True)
        entry_close = float(window.loc[0, "close"])
        return self._path_rows(window=window, entry_close=entry_close)

    def _path_rows(self, *, window: pd.DataFrame, entry_close: float) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for _, row in window.iterrows():
            rows.append({"trade_date": str(row["trade_date"]), "price_ratio": float(row["close"]) / entry_close})
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

    def _build_bar_cache(self, *, symbols: list[str]) -> dict[str, pd.DataFrame]:
        client = TencentKlineClient()
        cache: dict[str, pd.DataFrame] = {}
        for symbol in symbols:
            frame = client.fetch_daily_bars(symbol).sort_values("date").reset_index(drop=True).copy()
            frame["trade_date"] = pd.to_datetime(frame["date"]).dt.strftime("%Y-%m-%d")
            frame["ma5"] = frame["close"].rolling(5).mean()
            frame["ma10"] = frame["close"].rolling(10).mean()
            cache[symbol] = frame
        return cache

    def _find_row_index(self, *, bars: pd.DataFrame, trade_date: str) -> int:
        matches = bars.index[bars["trade_date"] == trade_date].tolist()
        if not matches:
            raise ValueError(f"Missing trade date {trade_date} in bar cache.")
        return int(matches[0])


def write_v112cr_high_beta_core_derisk_replay_split_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CRHighBetaCoreDeriskReplaySplitReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
