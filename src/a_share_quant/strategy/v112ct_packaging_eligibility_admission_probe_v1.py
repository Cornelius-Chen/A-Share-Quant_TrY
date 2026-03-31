from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

os.environ.setdefault("PANDAS_NO_USE_NUMEXPR", "1")
os.environ.setdefault("PANDAS_NO_USE_BOTTLENECK", "1")

import pandas as pd

from a_share_quant.strategy.v112a_price_cycle_inference_v1 import TencentKlineClient


@dataclass(slots=True)
class V112CTPackagingEligibilityAdmissionProbeReport:
    summary: dict[str, Any]
    mode_rows: list[dict[str, Any]]
    admission_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "mode_rows": self.mode_rows,
            "admission_rows": self.admission_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CTPackagingEligibilityAdmissionProbeAnalyzer:
    DEFAULT_HOLDING_DAYS = 20
    PACKAGING_SYMBOL = "300757"

    def analyze(
        self,
        *,
        bh_payload: dict[str, Any],
        cj_payload: dict[str, Any],
    ) -> V112CTPackagingEligibilityAdmissionProbeReport:
        neutral_rows = sorted(list(bh_payload.get("trade_rows", [])), key=lambda row: str(row.get("entry_date")))
        if not neutral_rows:
            raise ValueError("V1.12CT requires neutral trade rows.")

        packaging_dates = sorted(
            [
                str(row.get("trade_date"))
                for row in list(cj_payload.get("packaging_window_rows", []))
                if str(row.get("residual_reading")) == "missed_packaging_eligibility_window"
            ]
        )
        if not packaging_dates:
            raise ValueError("V1.12CT requires missed packaging eligibility windows.")

        baseline_total_return = float(dict(bh_payload.get("summary", {})).get("total_return", 0.0))
        baseline_max_drawdown = float(dict(bh_payload.get("summary", {})).get("max_drawdown", 0.0))
        symbols = sorted({str(row.get("symbol")) for row in neutral_rows} | {self.PACKAGING_SYMBOL})
        bar_cache = self._build_bar_cache(symbols=symbols)

        full20 = self._simulate_admission_mode(
            neutral_rows=neutral_rows,
            packaging_dates=packaging_dates,
            bars=bar_cache,
            mode_name="full_20d_admission",
        )
        cut_next = self._simulate_admission_mode(
            neutral_rows=neutral_rows,
            packaging_dates=packaging_dates,
            bars=bar_cache,
            mode_name="cut_at_next_neutral_entry",
        )

        preferred_mode = "full_20d_admission" if self._mode_key(full20, baseline_total_return, baseline_max_drawdown) >= self._mode_key(cut_next, baseline_total_return, baseline_max_drawdown) else "cut_at_next_neutral_entry"

        summary = {
            "acceptance_posture": "freeze_v112ct_packaging_eligibility_admission_probe_v1",
            "packaging_eligibility_window_count": len(packaging_dates),
            "baseline_total_return": round(baseline_total_return, 4),
            "baseline_max_drawdown": round(baseline_max_drawdown, 4),
            "preferred_mode": preferred_mode,
            "recommended_next_posture": "promote_full_20d_packaging_admission_candidate_if_replay_beats_neutral_without_reopening_packaging_template_logic",
        }
        mode_rows = [
            {
                "mode_name": "full_20d_admission",
                **full20,
                "return_delta_vs_neutral": round(full20["total_return"] - baseline_total_return, 4),
                "drawdown_delta_vs_neutral": round(full20["max_drawdown"] - baseline_max_drawdown, 4),
                "beats_neutral_return": full20["total_return"] > baseline_total_return,
                "beats_neutral_drawdown": full20["max_drawdown"] > baseline_max_drawdown,
            },
            {
                "mode_name": "cut_at_next_neutral_entry",
                **cut_next,
                "return_delta_vs_neutral": round(cut_next["total_return"] - baseline_total_return, 4),
                "drawdown_delta_vs_neutral": round(cut_next["max_drawdown"] - baseline_max_drawdown, 4),
                "beats_neutral_return": cut_next["total_return"] > baseline_total_return,
                "beats_neutral_drawdown": cut_next["max_drawdown"] > baseline_max_drawdown,
            },
        ]
        admission_rows = [
            {
                "trade_date": packaging_dates[0],
                "mode_name": "full_20d_admission",
                "exit_date": full20["admission_exit_dates"][0],
            },
            {
                "trade_date": packaging_dates[1],
                "mode_name": "full_20d_admission",
                "exit_date": full20["admission_exit_dates"][1],
            },
            {
                "trade_date": packaging_dates[0],
                "mode_name": "cut_at_next_neutral_entry",
                "exit_date": cut_next["admission_exit_dates"][0],
            },
            {
                "trade_date": packaging_dates[1],
                "mode_name": "cut_at_next_neutral_entry",
                "exit_date": cut_next["admission_exit_dates"][1],
            },
        ]
        interpretation = [
            "V1.12CT does not retrain neutral and does not reopen packaging template learning. It only asks whether previously missed packaging eligibility windows deserve explicit admission handling.",
            "The probe compares a full 20-day packaging admission against an admission clipped at the next neutral entry to see whether packaging wake-up logic can be introduced without violating time-ordering.",
        ]
        return V112CTPackagingEligibilityAdmissionProbeReport(
            summary=summary,
            mode_rows=mode_rows,
            admission_rows=admission_rows,
            interpretation=interpretation,
        )

    def _mode_key(
        self,
        replay: dict[str, Any],
        baseline_total_return: float,
        baseline_max_drawdown: float,
    ) -> tuple[bool, float, float]:
        return (
            replay["total_return"] > baseline_total_return and replay["max_drawdown"] > baseline_max_drawdown,
            replay["total_return"] - baseline_total_return,
            replay["max_drawdown"] - baseline_max_drawdown,
        )

    def _simulate_admission_mode(
        self,
        *,
        neutral_rows: list[dict[str, Any]],
        packaging_dates: list[str],
        bars: dict[str, pd.DataFrame],
        mode_name: str,
    ) -> dict[str, Any]:
        events: list[tuple[str, str, dict[str, Any]]] = []
        for row in neutral_rows:
            events.append(("neutral", str(row["entry_date"]), row))
        for trade_date in packaging_dates:
            events.append(("packaging", trade_date, {"entry_date": trade_date, "symbol": self.PACKAGING_SYMBOL}))
        events.sort(key=lambda item: item[1])

        current_equity = 1.0
        peak_equity = 1.0
        max_drawdown = 0.0
        current_exit_date = "0000-00-00"
        admission_count = 0
        skipped_neutral_count = 0
        admission_exit_dates: list[str] = []

        for kind, start_date, payload in events:
            if start_date <= current_exit_date:
                if kind == "neutral":
                    skipped_neutral_count += 1
                continue

            if kind == "neutral":
                trade_path, exit_date = self._neutral_trade_path(
                    bars=bars[str(payload["symbol"])],
                    entry_date=str(payload["entry_date"]),
                    exit_date=str(payload["exit_date"]),
                )
            else:
                trade_path, exit_date = self._packaging_admission_path(
                    bars=bars[self.PACKAGING_SYMBOL],
                    entry_date=start_date,
                    neutral_rows=neutral_rows,
                    mode_name=mode_name,
                )
                admission_count += 1
                admission_exit_dates.append(exit_date)

            entry_equity = current_equity
            for point in trade_path:
                path_equity = entry_equity * float(point["price_ratio"])
                peak_equity = max(peak_equity, path_equity)
                max_drawdown = min(max_drawdown, path_equity / peak_equity - 1.0)
            current_equity = entry_equity * float(trade_path[-1]["price_ratio"])
            current_exit_date = exit_date

        return {
            "total_return": round(current_equity - 1.0, 4),
            "max_drawdown": round(max_drawdown, 4),
            "admission_count": admission_count,
            "skipped_neutral_count": skipped_neutral_count,
            "admission_exit_dates": admission_exit_dates,
        }

    def _neutral_trade_path(
        self,
        *,
        bars: pd.DataFrame,
        entry_date: str,
        exit_date: str,
    ) -> tuple[list[dict[str, Any]], str]:
        start_idx = self._find_row_index(bars=bars, trade_date=entry_date)
        end_idx = self._find_row_index(bars=bars, trade_date=exit_date)
        window = bars.iloc[start_idx : end_idx + 1].copy().reset_index(drop=True)
        entry_close = float(window.loc[0, "close"])
        return self._path_rows(window=window, entry_close=entry_close), str(window.iloc[-1]["trade_date"])

    def _packaging_admission_path(
        self,
        *,
        bars: pd.DataFrame,
        entry_date: str,
        neutral_rows: list[dict[str, Any]],
        mode_name: str,
    ) -> tuple[list[dict[str, Any]], str]:
        start_idx = self._find_row_index(bars=bars, trade_date=entry_date)
        default_end_idx = min(start_idx + self.DEFAULT_HOLDING_DAYS, len(bars) - 1)
        if mode_name == "full_20d_admission":
            end_idx = default_end_idx
        else:
            next_neutral_dates = [str(row["entry_date"]) for row in neutral_rows if str(row["entry_date"]) > entry_date]
            if next_neutral_dates:
                next_idx = self._find_row_index(bars=bars, trade_date=next_neutral_dates[0]) - 1
                end_idx = min(default_end_idx, next_idx)
            else:
                end_idx = default_end_idx
        window = bars.iloc[start_idx : end_idx + 1].copy().reset_index(drop=True)
        entry_close = float(window.loc[0, "close"])
        return self._path_rows(window=window, entry_close=entry_close), str(window.iloc[-1]["trade_date"])

    def _path_rows(self, *, window: pd.DataFrame, entry_close: float) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for _, row in window.iterrows():
            rows.append({"trade_date": str(row["trade_date"]), "price_ratio": float(row["close"]) / entry_close})
        return rows

    def _build_bar_cache(self, *, symbols: list[str]) -> dict[str, pd.DataFrame]:
        client = TencentKlineClient()
        cache: dict[str, pd.DataFrame] = {}
        for symbol in symbols:
            frame = client.fetch_daily_bars(symbol).sort_values("date").reset_index(drop=True).copy()
            frame["trade_date"] = pd.to_datetime(frame["date"]).dt.strftime("%Y-%m-%d")
            cache[symbol] = frame
        return cache

    def _find_row_index(self, *, bars: pd.DataFrame, trade_date: str) -> int:
        matches = bars.index[bars["trade_date"] == trade_date].tolist()
        if not matches:
            raise ValueError(f"Missing trade date {trade_date} in bar cache.")
        return int(matches[0])


def write_v112ct_packaging_eligibility_admission_probe_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CTPackagingEligibilityAdmissionProbeReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
