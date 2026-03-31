from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

os.environ.setdefault("PANDAS_NO_USE_NUMEXPR", "1")
os.environ.setdefault("PANDAS_NO_USE_BOTTLENECK", "1")

import pandas as pd
import requests


@dataclass(slots=True)
class V112APriceCycleInferenceReport:
    summary: dict[str, Any]
    benchmark_rows: list[dict[str, Any]]
    inferred_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "benchmark_rows": self.benchmark_rows,
            "inferred_rows": self.inferred_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class TencentKlineClient:
    URL = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"

    def fetch_daily_bars(self, symbol: str, *, max_bars: int = 1500) -> pd.DataFrame:
        market = "sh" if symbol.startswith("6") else "sz"
        params = {"param": f"{market}{symbol},day,,,{max_bars},"}
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(self.URL, params=params, headers=headers, timeout=20)
        response.raise_for_status()
        payload = response.json()
        symbol_key = f"{market}{symbol}"
        rows = [list(item[:6]) for item in payload["data"][symbol_key]["day"]]
        frame = pd.DataFrame(rows, columns=["date", "open", "close", "high", "low", "volume"])
        frame["date"] = pd.to_datetime(frame["date"])
        for column in ["open", "close", "high", "low", "volume"]:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        return frame.sort_values("date").reset_index(drop=True)


class V112APriceCycleInferenceAnalyzer:
    """Infer coarse price-cycle windows for owner calibration."""

    ROLE_TRANSLATIONS = {
        "300308": "龙头/核心受益股",
        "300502": "高弹性核心受益股",
        "300394": "上游核心器件平台受益股",
    }

    NAME_TRANSLATIONS = {
        "300308": "中际旭创",
        "300502": "新易盛",
        "300394": "天孚通信",
    }

    # This is still a draft for owner calibration, so the cycle windows are intentionally coarse.
    SUGGESTED_WINDOWS = {
        "300502": {
            "first_markup_start": "2023-02",
            "first_markup_end": "2023-05",
            "cooling_and_box_start": "2023-06",
            "cooling_and_box_end": "2024-01",
            "second_markup_start": "2024-02",
            "second_markup_end": "2024-06",
            "long_box_reset_start": "2024-07",
            "long_box_reset_end": "2025-05",
            "major_markup_start": "2025-06",
            "major_markup_end": "2025-09",
            "high_level_consolidation_start": "2025-10",
            "high_level_consolidation_end": "2026-02",
            "rebound_window": "2026-03",
        },
        "300394": {
            "first_markup_start": "2023-02",
            "first_markup_end": "2023-06",
            "cooling_and_box_start": "2023-07",
            "cooling_and_box_end": "2024-01",
            "second_markup_start": "2024-02",
            "second_markup_end": "2024-04",
            "deep_box_reset_start": "2024-05",
            "deep_box_reset_end": "2025-06",
            "major_markup_start": "2025-07",
            "major_markup_end": "2026-02",
            "pullback_window": "2026-03",
        },
    }

    def analyze(
        self,
        *,
        pilot_dataset_draft_payload: dict[str, Any],
        inference_symbols: list[str],
    ) -> V112APriceCycleInferenceReport:
        dataset_rows = list(pilot_dataset_draft_payload.get("dataset_rows", []))
        dataset_map = {str(row.get("symbol")): dict(row) for row in dataset_rows}

        benchmark_rows: list[dict[str, Any]] = []
        inferred_rows: list[dict[str, Any]] = []
        client = TencentKlineClient()

        for symbol in inference_symbols:
            row = dataset_map.get(symbol, {})
            bars = client.fetch_daily_bars(symbol)
            monthly = self._build_monthly_table(bars)
            weekly = self._build_weekly_table(bars)
            monthly_tail = self._serialize_tail(monthly, 12)
            weekly_tail = self._serialize_tail(weekly, 10)

            if symbol == "300308":
                benchmark_rows.append(
                    {
                        "symbol": symbol,
                        "name": self.NAME_TRANSLATIONS[symbol],
                        "final_role_label_cn": self.ROLE_TRANSLATIONS[symbol],
                        "data_source": "tencent_day_kline_non_adjusted",
                        "date_range": {
                            "start": bars["date"].min().strftime("%Y-%m-%d"),
                            "end": bars["date"].max().strftime("%Y-%m-%d"),
                        },
                        "owner_cycle_window": dict(row.get("cycle_window", {})),
                        "price_structure_tail_monthly": monthly_tail,
                        "price_structure_tail_weekly": weekly_tail,
                        "status": "owner_anchor_present",
                    }
                )
                continue

            suggestion = dict(self.SUGGESTED_WINDOWS[symbol])
            inferred_rows.append(
                {
                    "symbol": symbol,
                    "name": self.NAME_TRANSLATIONS[symbol],
                    "final_role_label_cn": self.ROLE_TRANSLATIONS[symbol],
                    "data_source": "tencent_day_kline_non_adjusted",
                    "date_range": {
                        "start": bars["date"].min().strftime("%Y-%m-%d"),
                        "end": bars["date"].max().strftime("%Y-%m-%d"),
                    },
                    "bars_count": int(len(bars)),
                    "inference_confidence": "medium_owner_calibration_required",
                    "suggested_cycle_window": suggestion,
                    "price_structure_tail_monthly": monthly_tail,
                    "price_structure_tail_weekly": weekly_tail,
                    "notes_cn": self._notes_for_symbol(symbol),
                    "calibration_needed_fields": [
                        "cycle_window",
                        "major_markup_end",
                        "cooling_or_box_boundary",
                        "rebound_or_pullback_boundary",
                    ],
                }
            )

        summary = {
            "acceptance_posture": "freeze_v112a_price_cycle_inference_v1_for_owner_calibration",
            "benchmark_symbol_count": len(benchmark_rows),
            "inferred_symbol_count": len(inferred_rows),
            "ready_for_dataset_draft_v2_next": True,
        }
        interpretation = [
            "This is a price-structure draft built from daily bars and aggregated to weekly/monthly summaries.",
            "The windows are intentionally coarse because the owner will calibrate them before any training freeze.",
            "The goal here is not perfect cycle truth, but a usable first-pass price-state draft for calibration.",
        ]
        return V112APriceCycleInferenceReport(
            summary=summary,
            benchmark_rows=benchmark_rows,
            inferred_rows=inferred_rows,
            interpretation=interpretation,
        )

    def _build_monthly_table(self, bars: pd.DataFrame) -> pd.DataFrame:
        monthly = (
            bars.resample("ME", on="date")
            .agg({"open": "first", "close": "last", "high": "max", "low": "min", "volume": "sum"})
            .dropna()
            .copy()
        )
        monthly["mom"] = monthly["close"].pct_change() * 100
        monthly["qoq"] = monthly["close"].pct_change(3) * 100
        monthly["draw_from_12m_high"] = monthly["close"] / monthly["close"].rolling(12, min_periods=1).max() * 100 - 100
        return monthly

    def _build_weekly_table(self, bars: pd.DataFrame) -> pd.DataFrame:
        weekly = (
            bars.resample("W-FRI", on="date")
            .agg({"open": "first", "close": "last", "high": "max", "low": "min", "volume": "sum"})
            .dropna()
            .copy()
        )
        weekly["wow"] = weekly["close"].pct_change() * 100
        weekly["draw_from_26w_high"] = weekly["close"] / weekly["close"].rolling(26, min_periods=1).max() * 100 - 100
        return weekly

    def _serialize_tail(self, table: pd.DataFrame, rows: int) -> list[dict[str, Any]]:
        output: list[dict[str, Any]] = []
        for idx, (_, row) in enumerate(table.tail(rows).iterrows()):
            as_dict = {
                key: (round(float(value), 2) if pd.notna(value) else None)
                for key, value in row.items()
            }
            output.append({"index": idx, **as_dict})
        return output

    def _notes_for_symbol(self, symbol: str) -> str:
        if symbol == "300502":
            return (
                "价格结构更像 2023Q1-Q2 第一轮主升，2024Q1-Q2 第二轮抬升，"
                "2025-06 之后进入更陡的主升段，2026-03 形成一次明显反弹窗口。"
            )
        if symbol == "300394":
            return (
                "价格结构更像 2023Q1-Q2 第一轮主升，2024Q1 的二次抬升较短，"
                "2024-05 到 2025-06 属于较长重置区，2025-07 到 2026-02 为最新主升段。"
            )
        return ""


def write_v112a_price_cycle_inference_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112APriceCycleInferenceReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
