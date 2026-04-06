from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v125x_commercial_aerospace_eod_binary_action_pilot_v1 import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    _mean,
    _std,
)
from a_share_quant.strategy.v126m_commercial_aerospace_phase_geometry_label_table_v1 import (
    V126MCommercialAerospacePhaseGeometryLabelTableAnalyzer,
)


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * q)))
    return ordered[idx]


def _trade_costs(*, action: str, notional: float) -> dict[str, float]:
    commission_rate = 0.0003
    min_commission = 5.0
    stamp_tax_rate = 0.001 if action == "sell" else 0.0
    slippage_bps = 5.0
    commission = max(min_commission, notional * commission_rate) if notional > 0 else 0.0
    stamp_tax = notional * stamp_tax_rate
    slippage = notional * (slippage_bps / 10000.0)
    total_cost = commission + stamp_tax + slippage
    return {
        "commission": round(commission, 4),
        "stamp_tax": round(stamp_tax, 4),
        "slippage": round(slippage, 4),
        "total_cost": round(total_cost, 4),
    }


@dataclass(slots=True)
class V126TCommercialAerospacePreheatTieredShadowReplayReport:
    summary: dict[str, Any]
    daily_rows: list[dict[str, Any]]
    order_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "daily_rows": self.daily_rows,
            "order_rows": self.order_rows,
            "interpretation": self.interpretation,
        }


class V126TCommercialAerospacePreheatTieredShadowReplayAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.daily_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"

    def _split_rows(self, rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
        ordered_dates = sorted({row["trade_date"] for row in rows})
        split_idx = max(1, round(len(ordered_dates) * 0.8))
        return rows, ordered_dates[split_idx:]

    def _standardize(self, train_rows: list[dict[str, Any]], eval_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        stats: dict[str, tuple[float, float]] = {}
        for feature in NUMERIC_FEATURES:
            values = [float(row[feature]) for row in train_rows]
            mean = _mean(values)
            std = _std(values, mean)
            stats[feature] = (mean, std)

        def transform(rows_in: list[dict[str, Any]]) -> list[dict[str, Any]]:
            out: list[dict[str, Any]] = []
            for row in rows_in:
                enriched = dict(row)
                for feature in NUMERIC_FEATURES:
                    mean, std = stats[feature]
                    enriched[f"{feature}_z"] = (float(row[feature]) - mean) / std
                out.append(enriched)
            return out

        return transform(train_rows), transform(eval_rows)

    def _score_rows(self, train_rows: list[dict[str, Any]], eval_rows: list[dict[str, Any]], positive_labels: set[str]) -> list[float]:
        positives = [row for row in train_rows if row["supervised_action_label_pg"] in positive_labels]
        negatives = [row for row in train_rows if row["supervised_action_label_pg"] not in positive_labels]
        pos_numeric = {feature: _mean([float(row[f"{feature}_z"]) for row in positives]) for feature in NUMERIC_FEATURES}
        neg_numeric = {feature: _mean([float(row[f"{feature}_z"]) for row in negatives]) for feature in NUMERIC_FEATURES}
        pos_cat = {
            feature: max(
                {value for value in (row[feature] for row in positives)},
                key=lambda candidate: sum(1 for row in positives if row[feature] == candidate),
            )
            for feature in CATEGORICAL_FEATURES
        }
        neg_cat = {
            feature: max(
                {value for value in (row[feature] for row in negatives)},
                key=lambda candidate: sum(1 for row in negatives if row[feature] == candidate),
            )
            for feature in CATEGORICAL_FEATURES
        }
        scores: list[float] = []
        for row in eval_rows:
            numeric_score = sum(
                abs(float(row[f"{feature}_z"]) - neg_numeric[feature]) - abs(float(row[f"{feature}_z"]) - pos_numeric[feature])
                for feature in NUMERIC_FEATURES
            )
            cat_score = sum(
                (0.5 if row[feature] == pos_cat[feature] else 0.0) - (0.5 if row[feature] == neg_cat[feature] else 0.0)
                for feature in CATEGORICAL_FEATURES
            )
            scores.append(numeric_score + cat_score)
        return scores

    def analyze(self) -> V126TCommercialAerospacePreheatTieredShadowReplayReport:
        table = V126MCommercialAerospacePhaseGeometryLabelTableAnalyzer(self.repo_root).analyze()
        rows = table.training_rows
        rows, test_dates = self._split_rows(rows)
        ordered_dates = sorted({row["trade_date"] for row in rows})
        date_to_idx = {trade_date: idx for idx, trade_date in enumerate(ordered_dates)}
        by_date: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            by_date.setdefault(row["trade_date"], []).append(row)

        daily_bars = _load_csv(self.daily_path)
        daily_map = {(row["symbol"], row["trade_date"]): row for row in daily_bars}
        next_trade_date_map = {ordered_dates[idx]: ordered_dates[idx + 1] for idx in range(len(ordered_dates) - 1)}

        cash = 1_000_000.0
        positions: dict[str, int] = {}
        peak_equity = 1_000_000.0
        lot_size = 100
        pending_orders: dict[str, list[dict[str, Any]]] = {}
        daily_rows: list[dict[str, Any]] = []
        order_rows: list[dict[str, Any]] = []

        for trade_date in test_dates:
            todays_orders = pending_orders.pop(trade_date, [])
            for order in todays_orders:
                next_open = float(daily_map[(order["symbol"], trade_date)]["open"])
                if order["action"] == "buy":
                    current_qty = positions.get(order["symbol"], 0)
                    current_notional = current_qty * next_open
                    incremental_notional = max(0.0, order["target_notional"] - current_notional)
                    quantity = int(incremental_notional // next_open // lot_size) * lot_size
                    if quantity <= 0:
                        continue
                    notional = quantity * next_open
                    costs = _trade_costs(action="buy", notional=notional)
                    total_needed = notional + costs["total_cost"]
                    if total_needed > cash:
                        continue
                    cash -= total_needed
                    positions[order["symbol"]] = current_qty + quantity
                    order_rows.append(
                        {
                            "execution_trade_date": trade_date,
                            "symbol": order["symbol"],
                            "action": "open",
                            "reason": order["reason"],
                            "quantity": quantity,
                            "execution_price": round(next_open, 6),
                            "notional": round(notional, 4),
                            **costs,
                        }
                    )
                elif order["action"] == "sell" and positions.get(order["symbol"], 0) > 0:
                    current_qty = positions[order["symbol"]]
                    quantity = int((current_qty * order["sell_ratio"]) // lot_size) * lot_size
                    if quantity <= 0:
                        quantity = current_qty
                    quantity = min(quantity, current_qty)
                    notional = quantity * next_open
                    costs = _trade_costs(action="sell", notional=notional)
                    cash += notional - costs["total_cost"]
                    remaining = current_qty - quantity
                    if remaining > 0:
                        positions[order["symbol"]] = remaining
                    else:
                        positions.pop(order["symbol"], None)
                    order_rows.append(
                        {
                            "execution_trade_date": trade_date,
                            "symbol": order["symbol"],
                            "action": "reduce",
                            "reason": order["reason"],
                            "quantity": quantity,
                            "execution_price": round(next_open, 6),
                            "notional": round(notional, 4),
                            **costs,
                        }
                    )

            current_idx = date_to_idx[trade_date]
            matured_cutoff_idx = current_idx - 10
            if matured_cutoff_idx >= 0:
                matured_dates = set(ordered_dates[: matured_cutoff_idx + 1])
                available_rows = [row for row in rows if row["trade_date"] in matured_dates]
                eval_rows = by_date.get(trade_date, [])
                if available_rows and eval_rows:
                    train_rows_z, eval_rows_z = self._standardize(available_rows, eval_rows)
                    eligibility_train_scores = self._score_rows(
                        train_rows_z,
                        train_rows_z,
                        {"probe_eligibility_target", "full_eligibility_target"},
                    )
                    de_risk_train_scores = self._score_rows(train_rows_z, train_rows_z, {"de_risk_target"})
                    eligibility_eval_scores = self._score_rows(
                        train_rows_z,
                        eval_rows_z,
                        {"probe_eligibility_target", "full_eligibility_target"},
                    )
                    de_risk_eval_scores = self._score_rows(train_rows_z, eval_rows_z, {"de_risk_target"})

                    preheat_full_scores = [
                        score
                        for row, score in zip(train_rows_z, eligibility_train_scores, strict=False)
                        if row["phase_window_semantic"] == "preheat_window" and row["supervised_action_label_pg"] == "full_eligibility_target"
                    ]
                    preheat_probe_scores = [
                        score
                        for row, score in zip(train_rows_z, eligibility_train_scores, strict=False)
                        if row["phase_window_semantic"] == "preheat_window"
                        and row["supervised_action_label_pg"] in {"probe_eligibility_target", "full_eligibility_target"}
                    ]
                    impulse_full_scores = [
                        score
                        for row, score in zip(train_rows_z, eligibility_train_scores, strict=False)
                        if row["phase_window_semantic"] == "impulse_window" and row["supervised_action_label_pg"] == "full_eligibility_target"
                    ]
                    impulse_probe_scores = [
                        score
                        for row, score in zip(train_rows_z, eligibility_train_scores, strict=False)
                        if row["phase_window_semantic"] == "impulse_window"
                        and row["supervised_action_label_pg"] in {"probe_eligibility_target", "full_eligibility_target"}
                    ]
                    risk_scores = [
                        score
                        for row, score in zip(train_rows_z, de_risk_train_scores, strict=False)
                        if row["regime_proxy_semantic"] in {"risk_off_deterioration_proxy", "sentiment_overdrive_transition_proxy"}
                    ]

                    preheat_full_threshold = _quantile(preheat_full_scores, 0.6) if preheat_full_scores else 0.0
                    preheat_probe_threshold = _quantile(preheat_probe_scores, 0.7) if preheat_probe_scores else 0.0
                    impulse_full_threshold = _quantile(impulse_full_scores, 0.6) if impulse_full_scores else 0.0
                    impulse_probe_threshold = _quantile(impulse_probe_scores, 0.7) if impulse_probe_scores else 0.0
                    de_risk_threshold = _quantile(risk_scores, 0.8) if risk_scores else 0.0

                    next_trade_date = next_trade_date_map.get(trade_date)
                    if next_trade_date:
                        for row, es, ds in zip(eval_rows_z, eligibility_eval_scores, de_risk_eval_scores, strict=False):
                            symbol = row["symbol"]
                            if row["phase_window_semantic"] == "preheat_window":
                                target_notional = 0.0
                                reason = ""
                                if preheat_full_scores and es <= preheat_full_threshold:
                                    target_notional = 70_000.0
                                    reason = "phase_geometry_preheat_full"
                                elif es <= preheat_probe_threshold:
                                    target_notional = 40_000.0
                                    reason = "phase_geometry_preheat_probe"
                                if target_notional > 0:
                                    existing = [p for p in pending_orders.get(next_trade_date, []) if p["symbol"] == symbol and p["action"] == "buy"]
                                    if existing:
                                        prior = existing[0]["target_notional"]
                                        existing[0]["target_notional"] = max(prior, target_notional)
                                        if target_notional > prior:
                                            existing[0]["reason"] = reason
                                    else:
                                        pending_orders.setdefault(next_trade_date, []).append(
                                            {"symbol": symbol, "action": "buy", "reason": reason, "target_notional": target_notional}
                                        )
                            elif row["phase_window_semantic"] == "impulse_window":
                                target_notional = 0.0
                                reason = ""
                                if impulse_full_scores and es <= impulse_full_threshold:
                                    target_notional = 100_000.0
                                    reason = "phase_geometry_impulse_full"
                                elif es <= impulse_probe_threshold:
                                    target_notional = 40_000.0
                                    reason = "phase_geometry_impulse_probe"
                                if target_notional > 0:
                                    existing = [p for p in pending_orders.get(next_trade_date, []) if p["symbol"] == symbol and p["action"] == "buy"]
                                    if existing:
                                        prior = existing[0]["target_notional"]
                                        existing[0]["target_notional"] = max(prior, target_notional)
                                        if target_notional > prior:
                                            existing[0]["reason"] = reason
                                    else:
                                        pending_orders.setdefault(next_trade_date, []).append(
                                            {"symbol": symbol, "action": "buy", "reason": reason, "target_notional": target_notional}
                                        )

                            if (
                                row["regime_proxy_semantic"] in {"risk_off_deterioration_proxy", "sentiment_overdrive_transition_proxy"}
                                and ds <= de_risk_threshold
                                and symbol in positions
                                and all(p["symbol"] != symbol or p["action"] != "sell" for p in pending_orders.get(next_trade_date, []))
                            ):
                                pending_orders.setdefault(next_trade_date, []).append(
                                    {"symbol": symbol, "action": "sell", "reason": "phase_geometry_risk_low_pass", "sell_ratio": 0.5}
                                )

            market_value = 0.0
            held_symbols: list[str] = []
            for symbol, quantity in positions.items():
                bar = daily_map.get((symbol, trade_date))
                if bar:
                    market_value += quantity * float(bar["close"])
                    held_symbols.append(symbol)
            equity = cash + market_value
            peak_equity = max(peak_equity, equity)
            drawdown = 0.0 if peak_equity <= 0 else 1.0 - (equity / peak_equity)
            daily_rows.append(
                {
                    "trade_date": trade_date,
                    "cash": round(cash, 4),
                    "market_value": round(market_value, 4),
                    "equity": round(equity, 4),
                    "drawdown": round(drawdown, 8),
                    "held_symbols": ",".join(sorted(held_symbols)),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v126t_commercial_aerospace_preheat_tiered_shadow_replay_v1",
            "initial_capital": 1_000_000.0,
            "test_date_count": len(test_dates),
            "executed_order_count": len(order_rows),
            "final_equity": round(daily_rows[-1]["equity"], 4) if daily_rows else 1_000_000.0,
            "max_drawdown": round(max((row["drawdown"] for row in daily_rows), default=0.0), 8),
            "authoritative_status": "commercial_aerospace_preheat_tiered_shadow_replay_candidate",
        }
        interpretation = [
            "V1.26T upgrades lawful replay to recognize a stronger preheat full tier where V1.26M already created matured full-support before the main impulse dates.",
            "This tests whether the missing 11-14 to 12-23 participation was partly caused by replay sizing, not only by label support.",
        ]
        return V126TCommercialAerospacePreheatTieredShadowReplayReport(summary=summary, daily_rows=daily_rows, order_rows=order_rows, interpretation=interpretation)


def write_report(*, reports_dir: Path, report_name: str, result: V126TCommercialAerospacePreheatTieredShadowReplayReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V126TCommercialAerospacePreheatTieredShadowReplayAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v126t_commercial_aerospace_preheat_tiered_shadow_replay_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
