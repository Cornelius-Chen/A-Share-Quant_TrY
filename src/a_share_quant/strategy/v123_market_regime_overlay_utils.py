from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np


def zscore(values: list[float]) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    std = float(array.std())
    if std == 0.0:
        std = 1.0
    return (array - float(array.mean())) / std


def balanced_accuracy(y_true: list[bool], y_pred: list[bool]) -> float:
    positives = [idx for idx, value in enumerate(y_true) if value]
    negatives = [idx for idx, value in enumerate(y_true) if not value]
    pos_recall = sum(y_pred[idx] for idx in positives) / len(positives) if positives else 0.0
    neg_recall = sum((not y_pred[idx]) for idx in negatives) / len(negatives) if negatives else 0.0
    return (pos_recall + neg_recall) / 2.0


def load_market_regime_rows(repo_root: Path) -> list[dict[str, Any]]:
    compare_path = repo_root / "reports" / "analysis" / "v122y_cpo_baseline_vs_research_drawdown_compare_v1.json"
    with compare_path.open("r", encoding="utf-8") as handle:
        drawdown_report = json.load(handle)

    drawdown_dates: set[str] = set()
    for interval in drawdown_report["interval_rows"]:
        current = np.datetime64(interval["peak_date"])
        end = np.datetime64(interval["trough_date"])
        while current <= end:
            drawdown_dates.add(str(current))
            current = current + np.timedelta64(1, "D")

    feed_path = repo_root / "data" / "raw" / "daily_bars" / "sina_daily_bars_cpo_execution_main_feed_v1.csv"
    board_by_date: dict[str, list[dict[str, Any]]] = defaultdict(list)
    with feed_path.open("r", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            board_by_date[row["trade_date"]].append(row)

    board_state: dict[str, dict[str, float]] = {}
    for trade_date, rows in board_by_date.items():
        returns: list[float] = []
        turnovers: list[float] = []
        for row in rows:
            pre_close = float(row["pre_close"])
            close = float(row["close"])
            if pre_close != 0.0:
                returns.append(close / pre_close - 1.0)
            turnovers.append(float(row["turnover"]))
        positive_count = sum(value > 0.0 for value in returns)
        negative_count = sum(value < 0.0 for value in returns)
        sample_count = len(returns)
        board_state[trade_date] = {
            "board_avg_return": float(np.mean(returns)) if returns else 0.0,
            "board_breadth": (positive_count - negative_count) / sample_count if sample_count else 0.0,
            "board_turnover": float(np.sum(turnovers)),
        }

    index_path = repo_root / "data" / "raw" / "index_daily_bars" / "akshare_index_daily_bars_bootstrap.csv"
    index_by_date: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    with index_path.open("r", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            index_by_date[row["trade_date"]][row["symbol"]] = row

    common_dates = sorted(set(board_state) & set(index_by_date))

    for symbol in ["000001", "000300", "399006"]:
        series = [(trade_date, float(index_by_date[trade_date][symbol]["turnover"])) for trade_date in common_dates]
        for index, (trade_date, turnover) in enumerate(series):
            history = [item[1] for item in series[max(0, index - 5) : index]]
            baseline = float(np.mean(history)) if history else turnover
            index_by_date[trade_date][symbol]["turn_ratio_5"] = turnover / baseline if baseline else 1.0

    board_turn_series = [(trade_date, board_state[trade_date]["board_turnover"]) for trade_date in common_dates]
    for index, (trade_date, turnover) in enumerate(board_turn_series):
        history = [item[1] for item in board_turn_series[max(0, index - 5) : index]]
        baseline = float(np.mean(history)) if history else turnover
        board_state[trade_date]["board_turn_ratio_5"] = turnover / baseline if baseline else 1.0

    rows: list[dict[str, Any]] = []
    for trade_date in common_dates:
        index_rows = index_by_date[trade_date]
        row = {
            "trade_date": trade_date,
            "regime_risk_label": trade_date in drawdown_dates,
            "board_avg_return": board_state[trade_date]["board_avg_return"],
            "board_breadth": board_state[trade_date]["board_breadth"],
            "board_turn_ratio_5": board_state[trade_date]["board_turn_ratio_5"],
        }
        for symbol in ["000001", "000300", "399006"]:
            row[f"{symbol}_return"] = float(index_rows[symbol]["close"]) / float(index_rows[symbol]["pre_close"]) - 1.0
            row[f"{symbol}_turn_ratio_5"] = float(index_rows[symbol]["turn_ratio_5"])
        rows.append(row)
    return rows

