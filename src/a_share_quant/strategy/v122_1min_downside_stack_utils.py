from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from a_share_quant.strategy.v122_1min_label_plane_utils import load_recent_1min_labeled_rows
from a_share_quant.strategy.v122_supportive_continuation_utils import _zscore


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _balanced_accuracy(y_true: list[bool], y_pred: list[bool]) -> float:
    positives = [index for index, value in enumerate(y_true) if value]
    negatives = [index for index, value in enumerate(y_true) if not value]
    positive_recall = sum(y_pred[index] for index in positives) / len(positives) if positives else 0.0
    negative_recall = sum((not y_pred[index]) for index in negatives) / len(negatives) if negatives else 0.0
    return (positive_recall + negative_recall) / 2.0


def _score_downside_failure(rows: list[dict[str, Any]]) -> None:
    burst_z = _zscore([_to_float(row["burst_then_fade_score"]) for row in rows])
    upper_shadow_z = _zscore([_to_float(row["upper_shadow_pct"]) for row in rows])
    pullback_z = _zscore([_to_float(row["micro_pullback_depth"]) for row in rows])
    push_z = _zscore([_to_float(row["push_efficiency"]) for row in rows])
    late_z = _zscore([_to_float(row["late_session_integrity_score"]) for row in rows])
    close_location_z = _zscore([_to_float(row["close_location"]) for row in rows])
    reclaim_z = _zscore([_to_float(row["reclaim_after_break_score"]) for row in rows])
    abs_close_vs_vwap_z = _zscore([abs(_to_float(row["close_vs_vwap"])) for row in rows])

    for index, row in enumerate(rows):
        row["downside_failure_score"] = float(
            0.26 * burst_z[index]
            + 0.18 * upper_shadow_z[index]
            + 0.16 * pullback_z[index]
            - 0.14 * push_z[index]
            - 0.12 * late_z[index]
            - 0.08 * close_location_z[index]
            - 0.04 * reclaim_z[index]
            + 0.02 * abs_close_vs_vwap_z[index]
        )


def load_recent_1min_rows_with_downside_stack(repo_root: Path) -> list[dict[str, Any]]:
    rows = load_recent_1min_labeled_rows(repo_root)
    if not rows:
        return []

    daily_basic_path = repo_root / "data" / "reference" / "tushare_daily_basic" / "tushare_cpo_daily_basic_v1.csv"
    moneyflow_path = repo_root / "data" / "raw" / "moneyflow" / "tushare_cpo_moneyflow_v1.csv"

    daily_basic_rows = {}
    if daily_basic_path.exists():
        with daily_basic_path.open("r", encoding="utf-8") as handle:
            daily_basic_rows = {
                (str(row["trade_date"]), str(row["symbol"])): row
                for row in csv.DictReader(handle)
            }
    moneyflow_rows = {}
    if moneyflow_path.exists():
        with moneyflow_path.open("r", encoding="utf-8") as handle:
            moneyflow_rows = {
                (str(row["trade_date"]), str(row["symbol"])): row
                for row in csv.DictReader(handle)
            }

    available_daily_dates_by_symbol: dict[str, list[str]] = defaultdict(list)
    for trade_date, symbol in daily_basic_rows:
        available_daily_dates_by_symbol[symbol].append(trade_date)
    for symbol in available_daily_dates_by_symbol:
        available_daily_dates_by_symbol[symbol].sort()

    def get_daily_context(trade_date: str, symbol: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        key = (trade_date.replace("-", ""), symbol)
        daily_basic = daily_basic_rows.get(key)
        moneyflow = moneyflow_rows.get(key)
        if daily_basic is not None and moneyflow is not None:
            return daily_basic, moneyflow

        symbol_dates = available_daily_dates_by_symbol.get(symbol, [])
        prior_dates = [candidate for candidate in symbol_dates if candidate < key[0]]
        if not prior_dates:
            return daily_basic, moneyflow
        fallback_key = (prior_dates[-1], symbol)
        return daily_basic_rows.get(fallback_key), moneyflow_rows.get(fallback_key)

    minute_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        minute_groups[(str(row["trade_date"]), str(row["clock_time"]))].append(row)

    for (_trade_date, _clock_time), group_rows in minute_groups.items():
        minute_returns = [_to_float(row["minute_return"]) for row in group_rows]
        close_vs_vwap_values = [_to_float(row["close_vs_vwap"]) for row in group_rows]
        burst_values = [_to_float(row["burst_then_fade_score"]) for row in group_rows]
        pullback_values = [_to_float(row["micro_pullback_depth"]) for row in group_rows]
        late_values = [_to_float(row["late_session_integrity_score"]) for row in group_rows]

        board_negative_breadth = sum(value <= 0.0 for value in minute_returns) / len(minute_returns)
        board_mean_minute_return = float(np.mean(minute_returns))
        board_mean_close_vs_vwap = float(np.mean(close_vs_vwap_values))
        board_mean_burst_then_fade = float(np.mean(burst_values))
        board_mean_pullback = float(np.mean(pullback_values))
        board_mean_late_session_integrity = float(np.mean(late_values))

        for row in group_rows:
            row["board_negative_breadth"] = board_negative_breadth
            row["board_mean_minute_return"] = board_mean_minute_return
            row["board_mean_close_vs_vwap"] = board_mean_close_vs_vwap
            row["board_mean_burst_then_fade"] = board_mean_burst_then_fade
            row["board_mean_pullback"] = board_mean_pullback
            row["board_mean_late_session_integrity"] = board_mean_late_session_integrity
            row["relative_weakness_vs_board"] = -(
                _to_float(row["minute_return"]) - board_mean_minute_return
            )

            daily_basic, moneyflow = get_daily_context(str(row["trade_date"]), str(row["symbol"]))
            row["turnover_rate_f"] = _to_float(daily_basic.get("turnover_rate_f") if daily_basic else 0.0)
            row["volume_ratio"] = _to_float(daily_basic.get("volume_ratio") if daily_basic else 0.0)
            total_buy = _to_float(moneyflow.get("buy_lg_amount") if moneyflow else 0.0) + _to_float(
                moneyflow.get("buy_elg_amount") if moneyflow else 0.0
            )
            total_sell = _to_float(moneyflow.get("sell_lg_amount") if moneyflow else 0.0) + _to_float(
                moneyflow.get("sell_elg_amount") if moneyflow else 0.0
            )
            row["large_sell_buy_ratio"] = (total_sell + 1.0) / (total_buy + 1.0)

    _score_downside_failure(rows)

    downside_z = _zscore([_to_float(row["downside_failure_score"]) for row in rows])
    board_negative_breadth_z = _zscore([_to_float(row["board_negative_breadth"]) for row in rows])
    relative_weakness_z = _zscore([_to_float(row["relative_weakness_vs_board"]) for row in rows])

    for index, row in enumerate(rows):
        row["board_micro_risk_stack_score"] = float(
            0.95 * downside_z[index]
            + 0.03 * board_negative_breadth_z[index]
            + 0.02 * relative_weakness_z[index]
        )
        row["risk_positive_label"] = str(row["proxy_action_label"]) in {"reduce_probe", "close_probe"}
    return rows


def evaluate_score(rows: list[dict[str, Any]], *, score_field: str) -> dict[str, float]:
    positives = [_to_float(row[score_field]) for row in rows if bool(row["risk_positive_label"])]
    negatives = [_to_float(row[score_field]) for row in rows if not bool(row["risk_positive_label"])]
    if not positives or not negatives:
        return {
            "mean_gap_positive_minus_negative": 0.0,
            "threshold_q75": 0.0,
            "balanced_accuracy_q75": 0.0,
        }
    threshold = float(np.quantile([_to_float(row[score_field]) for row in rows], 0.75))
    y_true = [bool(row["risk_positive_label"]) for row in rows]
    y_pred = [_to_float(row[score_field]) >= threshold for row in rows]
    return {
        "mean_gap_positive_minus_negative": round(float(np.mean(positives) - np.mean(negatives)), 8),
        "threshold_q75": round(threshold, 8),
        "balanced_accuracy_q75": round(_balanced_accuracy(y_true, y_pred), 8),
    }


def evaluate_date_split(rows: list[dict[str, Any]], *, score_field: str) -> dict[str, float]:
    unique_dates = sorted({str(row["trade_date"]) for row in rows})
    scores: list[float] = []
    for split_index in range(1, len(unique_dates)):
        train_dates = set(unique_dates[:split_index])
        test_dates = set(unique_dates[split_index:])
        train_rows = [row for row in rows if str(row["trade_date"]) in train_dates]
        test_rows = [row for row in rows if str(row["trade_date"]) in test_dates]
        if not train_rows or not test_rows:
            continue
        threshold = float(np.quantile([_to_float(row[score_field]) for row in train_rows], 0.75))
        y_true = [bool(row["risk_positive_label"]) for row in test_rows]
        y_pred = [_to_float(row[score_field]) >= threshold for row in test_rows]
        scores.append(_balanced_accuracy(y_true, y_pred))
    if not scores:
        return {"mean_test_balanced_accuracy": 0.0, "min_test_balanced_accuracy": 0.0}
    return {
        "mean_test_balanced_accuracy": round(float(np.mean(scores)), 8),
        "min_test_balanced_accuracy": round(float(np.min(scores)), 8),
    }


def evaluate_symbol_holdout(rows: list[dict[str, Any]], *, score_field: str) -> dict[str, float]:
    symbols = sorted({str(row["symbol"]) for row in rows})
    scores: list[float] = []
    for holdout_symbol in symbols:
        train_rows = [row for row in rows if str(row["symbol"]) != holdout_symbol]
        test_rows = [row for row in rows if str(row["symbol"]) == holdout_symbol]
        if not train_rows or not test_rows:
            continue
        threshold = float(np.quantile([_to_float(row[score_field]) for row in train_rows], 0.75))
        y_true = [bool(row["risk_positive_label"]) for row in test_rows]
        y_pred = [_to_float(row[score_field]) >= threshold for row in test_rows]
        scores.append(_balanced_accuracy(y_true, y_pred))
    if not scores:
        return {"mean_test_balanced_accuracy": 0.0, "min_test_balanced_accuracy": 0.0}
    return {
        "mean_test_balanced_accuracy": round(float(np.mean(scores)), 8),
        "min_test_balanced_accuracy": round(float(np.min(scores)), 8),
    }
