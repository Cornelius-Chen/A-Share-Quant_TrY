from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _zscore(value: float, mean_value: float, std_value: float) -> float:
    if std_value == 0.0:
        return 0.0
    return (value - mean_value) / std_value


def _balanced_accuracy(rows: list[dict[str, Any]], score_field: str, threshold: float) -> dict[str, float]:
    positives = [row for row in rows if bool(row.get("positive_label"))]
    negatives = [row for row in rows if not bool(row.get("positive_label"))]
    tp = sum(1 for row in positives if _to_float(row.get(score_field)) >= threshold)
    fp = sum(1 for row in negatives if _to_float(row.get(score_field)) >= threshold)
    tn = len(negatives) - fp
    tpr = tp / len(positives) if positives else 0.0
    tnr = tn / len(negatives) if negatives else 0.0
    return {
        "threshold": round(threshold, 6),
        "positive_recall": round(tpr, 6),
        "negative_reject_rate": round(tnr, 6),
        "balanced_accuracy": round((tpr + tnr) / 2.0, 6),
    }


def _quantile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return sorted_values[0]
    index = max(0, min(len(sorted_values) - 1, int(round((len(sorted_values) - 1) * q))))
    return sorted_values[index]


def _mean_std(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 1.0
    mean_value = sum(values) / len(values)
    variance = sum((value - mean_value) ** 2 for value in values) / len(values)
    return mean_value, math.sqrt(variance) or 1.0


@dataclass(slots=True)
class DailyResidualDownsideData:
    sample_rows: list[dict[str, Any]]
    feature_names: list[str]
    residual_interval_start: str
    residual_interval_end: str


def build_research_daily_state_map(*, repo_root: Path) -> dict[str, dict[str, Any]]:
    return {
        str(row["trade_date"]): row
        for row in _load_csv_rows(repo_root / "data" / "training" / "cpo_research_test_baseline_daily_state_v1.csv")
    }


def build_daily_residual_downside_sample(*, repo_root: Path, cash_ratio_floor: float = 0.6) -> DailyResidualDownsideData:
    drawdown_payload = _load_json(
        repo_root / "reports" / "analysis" / "v122y_cpo_baseline_vs_research_drawdown_compare_v1.json"
    )
    residual_row = next(row for row in drawdown_payload["interval_rows"] if int(row["rank"]) == 3)
    interval_start = str(residual_row["peak_date"])
    interval_end = str(residual_row["trough_date"])

    daily_state_rows = _load_csv_rows(repo_root / "data" / "training" / "cpo_research_test_baseline_daily_state_v1.csv")
    daily_bar_rows = _load_csv_rows(repo_root / "data" / "raw" / "daily_bars" / "sina_daily_bars_cpo_execution_main_feed_v1.csv")
    daily_basic_rows = _load_csv_rows(
        repo_root / "data" / "reference" / "tushare_daily_basic" / "tushare_cpo_daily_basic_v1.csv"
    )
    moneyflow_rows = _load_csv_rows(repo_root / "data" / "raw" / "moneyflow" / "tushare_cpo_moneyflow_v1.csv")

    board_map: dict[str, dict[str, float]] = {}
    symbol_ret_map: dict[tuple[str, str], float] = {}
    symbol_turnover_map: dict[tuple[str, str], float] = {}
    symbol_turnover_raw: dict[tuple[str, str], float] = {}
    symbol_sell_buy_ratio_map: dict[tuple[str, str], float] = {}
    symbol_net_mf_turnover_map: dict[tuple[str, str], float] = {}

    grouped_daily_bars: dict[str, list[dict[str, Any]]] = {}
    for row in daily_bar_rows:
        grouped_daily_bars.setdefault(str(row["trade_date"]), []).append(row)
        pre_close = _to_float(row.get("pre_close"))
        close = _to_float(row.get("close"))
        daily_ret = 0.0 if pre_close <= 0.0 else close / pre_close - 1.0
        symbol_ret_map[(str(row["trade_date"]), str(row["symbol"]))] = daily_ret

    for trade_date, rows in grouped_daily_bars.items():
        returns = [
            _to_float(symbol_ret_map[(trade_date, str(row["symbol"]))])
            for row in rows
            if (trade_date, str(row["symbol"])) in symbol_ret_map
        ]
        board_map[trade_date] = {
            "board_avg_return": sum(returns) / len(returns) if returns else 0.0,
            "board_breadth": sum(1 for value in returns if value > 0.0) / len(returns) if returns else 0.0,
        }

    for row in daily_basic_rows:
        trade_date = str(row["trade_date"])
        symbol = str(row["symbol"])
        symbol_turnover_map[(trade_date, symbol)] = _to_float(row.get("turnover_rate_f"))
        symbol_turnover_raw[(trade_date, symbol)] = _to_float(row.get("volume_ratio"))

    turnover_lookup: dict[tuple[str, str], float] = {}
    for row in daily_bar_rows:
        turnover_lookup[(str(row["trade_date"]), str(row["symbol"]))] = _to_float(row.get("turnover"))

    for row in moneyflow_rows:
        trade_date = str(row["trade_date"])
        symbol = str(row["symbol"])
        total_buy = _to_float(row.get("buy_lg_amount")) + _to_float(row.get("buy_elg_amount"))
        total_sell = _to_float(row.get("sell_lg_amount")) + _to_float(row.get("sell_elg_amount"))
        symbol_sell_buy_ratio_map[(trade_date, symbol)] = (total_sell + 1.0) / (total_buy + 1.0)
        turnover = turnover_lookup.get((trade_date, symbol), 0.0)
        symbol_net_mf_turnover_map[(trade_date, symbol)] = _to_float(row.get("net_mf_amount")) / (turnover + 1.0)

    sample_rows: list[dict[str, Any]] = []
    for row in daily_state_rows:
        trade_date = str(row["trade_date"])
        held_symbols = set() if str(row["held_symbols"]) == "CASH" else set(filter(None, str(row["held_symbols"]).split(",")))
        equity = _to_float(row.get("equity"), 1.0)
        cash = _to_float(row.get("cash"))
        cash_ratio = 0.0 if equity <= 0.0 else cash / equity
        if not {"300308", "300502"}.issubset(held_symbols):
            continue
        if cash_ratio <= cash_ratio_floor:
            continue
        compact_trade_date = trade_date.replace("-", "")
        pair_mean_return = (
            symbol_ret_map.get((trade_date, "300308"), 0.0) + symbol_ret_map.get((trade_date, "300502"), 0.0)
        ) / 2.0
        pair_worst_return = min(
            symbol_ret_map.get((trade_date, "300308"), 0.0),
            symbol_ret_map.get((trade_date, "300502"), 0.0),
        )
        pair_turnover_mean = (
            symbol_turnover_map.get((compact_trade_date, "300308"), 0.0)
            + symbol_turnover_map.get((compact_trade_date, "300502"), 0.0)
        ) / 2.0
        pair_volume_ratio_mean = (
            symbol_turnover_raw.get((compact_trade_date, "300308"), 0.0)
            + symbol_turnover_raw.get((compact_trade_date, "300502"), 0.0)
        ) / 2.0
        pair_sell_buy_ratio_mean = (
            symbol_sell_buy_ratio_map.get((compact_trade_date, "300308"), 1.0)
            + symbol_sell_buy_ratio_map.get((compact_trade_date, "300502"), 1.0)
        ) / 2.0
        pair_net_mf_turnover_mean = (
            symbol_net_mf_turnover_map.get((compact_trade_date, "300308"), 0.0)
            + symbol_net_mf_turnover_map.get((compact_trade_date, "300502"), 0.0)
        ) / 2.0
        pair_red_fraction = (
            int(symbol_ret_map.get((trade_date, "300308"), 0.0) < 0.0)
            + int(symbol_ret_map.get((trade_date, "300502"), 0.0) < 0.0)
        ) / 2.0
        sample_rows.append(
            {
                "trade_date": trade_date,
                "positive_label": interval_start <= trade_date <= interval_end,
                "cash_ratio": round(cash_ratio, 6),
                "board_avg_return": round(board_map.get(trade_date, {}).get("board_avg_return", 0.0), 6),
                "board_breadth": round(board_map.get(trade_date, {}).get("board_breadth", 0.0), 6),
                "ret_300308": round(symbol_ret_map.get((trade_date, "300308"), 0.0), 6),
                "ret_300502": round(symbol_ret_map.get((trade_date, "300502"), 0.0), 6),
                "pair_mean_return": round(pair_mean_return, 6),
                "pair_worst_return": round(pair_worst_return, 6),
                "pair_red_fraction": round(pair_red_fraction, 6),
                "turnover_rate_f_300308": round(symbol_turnover_map.get((compact_trade_date, "300308"), 0.0), 6),
                "turnover_rate_f_300502": round(symbol_turnover_map.get((compact_trade_date, "300502"), 0.0), 6),
                "pair_turnover_mean": round(pair_turnover_mean, 6),
                "pair_volume_ratio_mean": round(pair_volume_ratio_mean, 6),
                "sell_buy_ratio_300308": round(symbol_sell_buy_ratio_map.get((compact_trade_date, "300308"), 1.0), 6),
                "sell_buy_ratio_300502": round(symbol_sell_buy_ratio_map.get((compact_trade_date, "300502"), 1.0), 6),
                "pair_sell_buy_ratio_mean": round(pair_sell_buy_ratio_mean, 6),
                "net_mf_turnover_300308": round(symbol_net_mf_turnover_map.get((compact_trade_date, "300308"), 0.0), 6),
                "net_mf_turnover_300502": round(symbol_net_mf_turnover_map.get((compact_trade_date, "300502"), 0.0), 6),
                "pair_net_mf_turnover_mean": round(pair_net_mf_turnover_mean, 6),
            }
        )

    feature_names = [
        "board_avg_return",
        "board_breadth",
        "ret_300308",
        "ret_300502",
        "pair_mean_return",
        "pair_worst_return",
        "pair_red_fraction",
        "turnover_rate_f_300308",
        "turnover_rate_f_300502",
        "pair_turnover_mean",
        "pair_volume_ratio_mean",
        "sell_buy_ratio_300308",
        "sell_buy_ratio_300502",
        "pair_sell_buy_ratio_mean",
        "net_mf_turnover_300308",
        "net_mf_turnover_300502",
        "pair_net_mf_turnover_mean",
    ]
    return DailyResidualDownsideData(
        sample_rows=sample_rows,
        feature_names=feature_names,
        residual_interval_start=interval_start,
        residual_interval_end=interval_end,
    )


def score_daily_residual_candidates(sample_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    score_inputs = {
        "pair_mean_return": [_to_float(row["pair_mean_return"]) for row in sample_rows],
        "pair_worst_return": [_to_float(row["pair_worst_return"]) for row in sample_rows],
        "pair_red_fraction": [_to_float(row["pair_red_fraction"]) for row in sample_rows],
        "board_avg_return": [_to_float(row["board_avg_return"]) for row in sample_rows],
        "board_breadth": [_to_float(row["board_breadth"]) for row in sample_rows],
        "pair_turnover_mean": [_to_float(row["pair_turnover_mean"]) for row in sample_rows],
        "pair_volume_ratio_mean": [_to_float(row["pair_volume_ratio_mean"]) for row in sample_rows],
        "pair_sell_buy_ratio_mean": [_to_float(row["pair_sell_buy_ratio_mean"]) for row in sample_rows],
        "pair_net_mf_turnover_mean": [_to_float(row["pair_net_mf_turnover_mean"]) for row in sample_rows],
        "ret_300308": [_to_float(row["ret_300308"]) for row in sample_rows],
        "ret_300502": [_to_float(row["ret_300502"]) for row in sample_rows],
        "sell_buy_ratio_300308": [_to_float(row["sell_buy_ratio_300308"]) for row in sample_rows],
    }
    means_stds = {name: _mean_std(values) for name, values in score_inputs.items()}

    scored_rows: list[dict[str, Any]] = []
    for row in sample_rows:
        def z(name: str) -> float:
            mean_value, std_value = means_stds[name]
            return _zscore(_to_float(row[name]), mean_value, std_value)

        held_pair_deterioration_score = (
            -z("pair_mean_return")
            - 0.75 * z("board_avg_return")
            - 0.75 * z("board_breadth")
            + 0.50 * z("pair_turnover_mean")
            + 0.75 * z("pair_sell_buy_ratio_mean")
            - 0.50 * z("pair_net_mf_turnover_mean")
        )
        asymmetric_leader_damage_score = (
            -(z("ret_300308") - 0.50 * z("ret_300502"))
            + 0.75 * z("sell_buy_ratio_300308")
            - 0.50 * z("pair_net_mf_turnover_mean")
            - 0.25 * z("board_breadth")
        )
        breadth_plus_pair_red_day_score = (
            -z("board_breadth")
            - 0.75 * z("pair_worst_return")
            + 0.75 * z("pair_red_fraction")
            + 0.40 * z("pair_volume_ratio_mean")
        )
        scored_row = dict(row)
        scored_row.update(
            {
                "held_pair_deterioration_score": round(held_pair_deterioration_score, 6),
                "asymmetric_leader_damage_score": round(asymmetric_leader_damage_score, 6),
                "breadth_plus_pair_red_day_score": round(breadth_plus_pair_red_day_score, 6),
            }
        )
        scored_rows.append(scored_row)

    candidate_rows: list[dict[str, Any]] = []
    for score_field in (
        "held_pair_deterioration_score",
        "asymmetric_leader_damage_score",
        "breadth_plus_pair_red_day_score",
    ):
        values = sorted(_to_float(row[score_field]) for row in scored_rows)
        best_record = None
        for threshold in sorted(set(values), reverse=True):
            record = _balanced_accuracy(scored_rows, score_field, threshold)
            if best_record is None or record["balanced_accuracy"] > best_record["balanced_accuracy"]:
                best_record = record
        q75_threshold = _quantile(values, 0.75)
        q75_record = _balanced_accuracy(scored_rows, score_field, q75_threshold)
        positives = [row for row in scored_rows if bool(row["positive_label"])]
        negatives = [row for row in scored_rows if not bool(row["positive_label"])]
        positive_mean = sum(_to_float(row[score_field]) for row in positives) / len(positives)
        negative_mean = sum(_to_float(row[score_field]) for row in negatives) / len(negatives)
        candidate_rows.append(
            {
                "candidate_name": score_field,
                "positive_mean_score": round(positive_mean, 6),
                "negative_mean_score": round(negative_mean, 6),
                "discovery_mean_gap_positive_minus_negative": round(positive_mean - negative_mean, 6),
                "best_threshold": best_record["threshold"] if best_record is not None else 0.0,
                "best_balanced_accuracy": best_record["balanced_accuracy"] if best_record is not None else 0.0,
                "q75_threshold": round(q75_threshold, 6),
                "q75_balanced_accuracy": q75_record["balanced_accuracy"],
                "q75_positive_recall": q75_record["positive_recall"],
                "q75_negative_reject_rate": q75_record["negative_reject_rate"],
            }
        )
    candidate_rows.sort(
        key=lambda row: (_to_float(row["q75_balanced_accuracy"]), _to_float(row["discovery_mean_gap_positive_minus_negative"])),
        reverse=True,
    )
    return scored_rows, candidate_rows


def chronological_split_rows(
    *,
    rows: list[dict[str, Any]],
    score_field: str,
) -> list[dict[str, Any]]:
    sorted_rows = sorted(rows, key=lambda row: str(row["trade_date"]))
    split_rows: list[dict[str, Any]] = []
    total_count = len(sorted_rows)
    for fraction in (0.55, 0.65, 0.75):
        split_index = int(total_count * fraction)
        train_rows = sorted_rows[:split_index]
        test_rows = sorted_rows[split_index:]
        if len(train_rows) < 10 or len(test_rows) < 10:
            continue
        values = sorted(set(_to_float(row[score_field]) for row in train_rows))
        best_train = None
        for threshold in sorted(values, reverse=True):
            record = _balanced_accuracy(train_rows, score_field, threshold)
            if best_train is None or record["balanced_accuracy"] > best_train["balanced_accuracy"]:
                best_train = record
        best_train = best_train or {"threshold": 0.0, "balanced_accuracy": 0.0}
        test_record = _balanced_accuracy(test_rows, score_field, _to_float(best_train["threshold"]))
        split_rows.append(
            {
                "split_name": f"train_{int(fraction * 100)}_test_{100 - int(fraction * 100)}",
                "train_start": str(train_rows[0]["trade_date"]),
                "train_end": str(train_rows[-1]["trade_date"]),
                "test_start": str(test_rows[0]["trade_date"]),
                "test_end": str(test_rows[-1]["trade_date"]),
                "train_row_count": len(train_rows),
                "test_row_count": len(test_rows),
                "train_best_threshold": best_train["threshold"],
                "train_best_balanced_accuracy": best_train["balanced_accuracy"],
                "test_balanced_accuracy": test_record["balanced_accuracy"],
                "test_positive_recall": test_record["positive_recall"],
                "test_negative_reject_rate": test_record["negative_reject_rate"],
            }
        )
    return split_rows
