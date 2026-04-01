from __future__ import annotations

import csv
import json
from pathlib import Path

from a_share_quant.strategy.v115e_cpo_broader_repaired_intraday_threshold_calibration_v1 import (
    V115ECpoBroaderRepairedIntradayThresholdCalibrationAnalyzer,
)


def _write_daily_feed(path: Path) -> None:
    rows = [
        {"symbol": "300502", "trade_date": "2023-05-03", "open": 10, "high": 10.2, "low": 9.9, "close": 10.1},
        {"symbol": "300502", "trade_date": "2023-05-04", "open": 10.1, "high": 10.5, "low": 10.0, "close": 10.4},
        {"symbol": "300502", "trade_date": "2023-05-05", "open": 10.5, "high": 10.8, "low": 10.3, "close": 10.7},
        {"symbol": "300502", "trade_date": "2023-05-08", "open": 10.7, "high": 11.0, "low": 10.6, "close": 10.9},
        {"symbol": "300502", "trade_date": "2023-05-09", "open": 10.8, "high": 10.9, "low": 10.1, "close": 10.2},
        {"symbol": "300502", "trade_date": "2023-05-10", "open": 10.0, "high": 10.1, "low": 9.4, "close": 9.5},
        {"symbol": "300308", "trade_date": "2023-05-03", "open": 20, "high": 20.2, "low": 19.9, "close": 20.1},
        {"symbol": "300308", "trade_date": "2023-05-04", "open": 20.1, "high": 20.8, "low": 20.0, "close": 20.6},
        {"symbol": "300308", "trade_date": "2023-05-05", "open": 20.6, "high": 21.0, "low": 20.4, "close": 20.9},
        {"symbol": "300308", "trade_date": "2023-05-08", "open": 21.0, "high": 21.2, "low": 20.8, "close": 21.1},
        {"symbol": "300308", "trade_date": "2023-05-09", "open": 20.8, "high": 20.9, "low": 20.0, "close": 20.1},
        {"symbol": "300308", "trade_date": "2023-05-10", "open": 19.9, "high": 20.0, "low": 19.2, "close": 19.4},
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["symbol", "trade_date", "open", "high", "low", "close"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _fetch_rows(symbol: str, trade_date: str, frequency: str) -> list[dict[str, object]]:
    strong_map = {
        "2023-05-03": [10.0, 10.4, 10.8, 10.9],
        "2023-05-04": [10.2, 10.6, 10.9, 11.0],
        "2023-05-05": [10.1, 10.2, 10.0, 9.9],
        "2023-05-08": [10.0, 9.9, 9.7, 9.6],
    }
    closes = strong_map.get(trade_date, [10.0, 10.1, 10.0, 10.0])
    rows = []
    for idx, close in enumerate(closes):
        rows.append(
            {
                "date": trade_date,
                "time": f"{93000 + idx:06d}",
                "code": symbol,
                "open": close - 0.05,
                "high": close + 0.1,
                "low": close - 0.1,
                "close": close,
                "volume": 1000 + idx * 100,
                "amount": (1000 + idx * 100) * close,
                "adjustflag": "2",
            }
        )
    return rows


def test_v115e_broader_calibration(tmp_path: Path) -> None:
    repo_root = tmp_path
    _write_daily_feed(repo_root / "data" / "raw" / "daily_bars" / "sina_daily_bars_cpo_execution_main_feed_v1.csv")

    v114t_payload = {
        "summary": {"acceptance_posture": "freeze_v114t_cpo_replay_integrity_repair_v1"},
        "executed_order_rows": [
            {"execution_trade_date": "2023-05-03", "symbol": "300502", "quantity": 100, "action": "buy"},
            {"execution_trade_date": "2023-05-04", "symbol": "300308", "quantity": 100, "action": "buy"},
        ],
        "replay_day_rows": [
            {
                "trade_date": "2023-05-03",
                "executed_today_order_count": 1,
                "gross_exposure_after_close": 0.10,
                "board_context": {"avg_return": 0.07, "breadth": 0.9},
            },
            {
                "trade_date": "2023-05-04",
                "executed_today_order_count": 1,
                "gross_exposure_after_close": 0.28,
                "board_context": {"avg_return": 0.06, "breadth": 0.8},
            },
            {
                "trade_date": "2023-05-05",
                "executed_today_order_count": 0,
                "gross_exposure_after_close": 0.25,
                "board_context": {"avg_return": -0.04, "breadth": -0.7},
            },
            {
                "trade_date": "2023-05-08",
                "executed_today_order_count": 0,
                "gross_exposure_after_close": 0.22,
                "board_context": {"avg_return": -0.05, "breadth": -0.8},
            },
        ],
    }
    v114w_payload = {
        "summary": {"acceptance_posture": "freeze_v114w_cpo_under_exposure_attribution_repaired_v1"},
        "top_opportunity_miss_rows": [{"trade_date": "2023-05-03"}],
    }

    analyzer = V115ECpoBroaderRepairedIntradayThresholdCalibrationAnalyzer(repo_root=repo_root)
    report, rows = analyzer.analyze(
        v114t_payload=v114t_payload,
        v114w_payload=v114w_payload,
        fetch_window_rows=_fetch_rows,
    )

    assert report.summary["acceptance_posture"] == "freeze_v115e_cpo_broader_repaired_intraday_threshold_calibration_v1"
    assert report.summary["selected_replay_day_count"] >= 3
    assert report.summary["successful_row_count"] >= 3
    assert len(report.threshold_rows) == 2
    assert any(row["context_label"] == "strong_under_exposed" for row in report.context_rows)
    assert any(row["context_label"] == "risk_pressure" for row in report.context_rows)
    assert any(bool(row.get("is_top_miss_day")) for row in rows if row.get("fetch_status") == "success")
