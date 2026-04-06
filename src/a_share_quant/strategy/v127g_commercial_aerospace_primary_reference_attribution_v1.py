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
class _ReplayConfig:
    name: str
    preheat_cap: int
    impulse_cap: int
    cooldown_days_after_sell: int
    min_increment_notional: float
    preheat_full_target_notional: float
    family: str
    sell_ratio: float


@dataclass(slots=True)
class V127GCommercialAerospacePrimaryReferenceAttributionReport:
    summary: dict[str, Any]
    variant_rows: list[dict[str, Any]]
    symbol_attribution_rows: list[dict[str, Any]]
    drawdown_compare_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "variant_rows": self.variant_rows,
            "symbol_attribution_rows": self.symbol_attribution_rows,
            "drawdown_compare_rows": self.drawdown_compare_rows,
            "interpretation": self.interpretation,
        }


class V127GCommercialAerospacePrimaryReferenceAttributionAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.daily_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
        self.audit_path = repo_root / "reports" / "analysis" / "v126p_commercial_aerospace_execution_surface_pruning_audit_v1.json"
        self.v126o_path = repo_root / "reports" / "analysis" / "v126o_commercial_aerospace_phase_geometry_walk_forward_shadow_replay_v1.json"
        self.v126q_path = repo_root / "reports" / "analysis" / "v126q_commercial_aerospace_pruned_phase_geometry_shadow_replay_v1.json"

    def _load_base_config(self) -> dict[str, float | int]:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        best_name = audit["summary"]["best_variant"]
        row = next(item for item in audit["variant_rows"] if item["variant"] == best_name)
        return {
            "preheat_cap": int(row["preheat_cap"]),
            "impulse_cap": int(row["impulse_cap"]),
            "cooldown_days_after_sell": int(row["cooldown_days_after_sell"]),
            "min_increment_notional": float(row["min_increment_notional"]),
        }

    @staticmethod
    def _split_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str], dict[str, int]]:
        ordered_dates = sorted({row["trade_date"] for row in rows})
        split_idx = max(1, round(len(ordered_dates) * 0.8))
        date_to_idx = {trade_date: idx for idx, trade_date in enumerate(ordered_dates)}
        return rows, ordered_dates[split_idx:], date_to_idx

    @staticmethod
    def _standardize(train_rows: list[dict[str, Any]], eval_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
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

    @staticmethod
    def _score_rows(train_rows: list[dict[str, Any]], eval_rows: list[dict[str, Any]], positive_labels: set[str]) -> list[float]:
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

    @staticmethod
    def _family_match(candidate: dict[str, Any], family: str) -> bool:
        if family == "broad_half_reference":
            return True
        return (
            candidate["regime_proxy_semantic"] == "weak_drift_chop_proxy"
            and candidate["event_state"] == "event_neutral"
            and candidate["phase_window_semantic"] == "other_window"
        )

    def _simulate_variant_detailed(
        self,
        rows: list[dict[str, Any]],
        test_dates: list[str],
        date_to_idx: dict[str, int],
        config: _ReplayConfig,
    ) -> dict[str, Any]:
        ordered_dates = sorted({row["trade_date"] for row in rows})
        by_date: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            by_date.setdefault(row["trade_date"], []).append(row)

        daily_bars = _load_csv(self.daily_path)
        daily_map = {(row["symbol"], row["trade_date"]): row for row in daily_bars}
        next_trade_date_map = {ordered_dates[idx]: ordered_dates[idx + 1] for idx in range(len(ordered_dates) - 1)}

        cash = 1_000_000.0
        positions: dict[str, int] = {}
        peak_equity = 1_000_000.0
        pending_orders: dict[str, list[dict[str, Any]]] = {}
        last_sell_idx_by_symbol: dict[str, int] = {}
        daily_rows: list[dict[str, Any]] = []
        order_rows: list[dict[str, Any]] = []
        lot_size = 100

        for trade_date in test_dates:
            current_idx = date_to_idx[trade_date]
            todays_orders = pending_orders.pop(trade_date, [])
            for order in todays_orders:
                next_open = float(daily_map[(order["symbol"], trade_date)]["open"])
                if order["action"] == "buy":
                    current_qty = positions.get(order["symbol"], 0)
                    current_notional = current_qty * next_open
                    incremental_notional = max(0.0, order["target_notional"] - current_notional)
                    if incremental_notional < config.min_increment_notional:
                        continue
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
                    last_sell_idx_by_symbol[order["symbol"]] = current_idx
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

            matured_cutoff_idx = current_idx - 10
            if matured_cutoff_idx >= 0:
                matured_dates = set(ordered_dates[: matured_cutoff_idx + 1])
                available_rows = [row for row in rows if row["trade_date"] in matured_dates]
                eval_rows = by_date.get(trade_date, [])
                if available_rows and eval_rows:
                    train_rows_z, eval_rows_z = self._standardize(available_rows, eval_rows)
                    eligibility_train_scores = self._score_rows(train_rows_z, train_rows_z, {"probe_eligibility_target", "full_eligibility_target"})
                    de_risk_train_scores = self._score_rows(train_rows_z, train_rows_z, {"de_risk_target"})
                    eligibility_eval_scores = self._score_rows(train_rows_z, eval_rows_z, {"probe_eligibility_target", "full_eligibility_target"})
                    de_risk_eval_scores = self._score_rows(train_rows_z, eval_rows_z, {"de_risk_target"})

                    preheat_full_scores = [
                        score for row, score in zip(train_rows_z, eligibility_train_scores, strict=False)
                        if row["phase_window_semantic"] == "preheat_window" and row["supervised_action_label_pg"] == "full_eligibility_target"
                    ]
                    preheat_probe_scores = [
                        score for row, score in zip(train_rows_z, eligibility_train_scores, strict=False)
                        if row["phase_window_semantic"] == "preheat_window" and row["supervised_action_label_pg"] in {"probe_eligibility_target", "full_eligibility_target"}
                    ]
                    impulse_full_scores = [
                        score for row, score in zip(train_rows_z, eligibility_train_scores, strict=False)
                        if row["phase_window_semantic"] == "impulse_window" and row["supervised_action_label_pg"] == "full_eligibility_target"
                    ]
                    impulse_probe_scores = [
                        score for row, score in zip(train_rows_z, eligibility_train_scores, strict=False)
                        if row["phase_window_semantic"] == "impulse_window" and row["supervised_action_label_pg"] in {"probe_eligibility_target", "full_eligibility_target"}
                    ]
                    risk_scores = [
                        score for row, score in zip(train_rows_z, de_risk_train_scores, strict=False)
                        if row["regime_proxy_semantic"] in {"risk_off_deterioration_proxy", "sentiment_overdrive_transition_proxy", "weak_drift_chop_proxy"}
                    ]
                    preheat_full_threshold = _quantile(preheat_full_scores, 0.6) if preheat_full_scores else 0.0
                    preheat_probe_threshold = _quantile(preheat_probe_scores, 0.7) if preheat_probe_scores else 0.0
                    impulse_full_threshold = _quantile(impulse_full_scores, 0.6) if impulse_full_scores else 0.0
                    impulse_probe_threshold = _quantile(impulse_probe_scores, 0.7) if impulse_probe_scores else 0.0
                    de_risk_threshold = _quantile(risk_scores, 0.8) if risk_scores else 0.0

                    next_trade_date = next_trade_date_map.get(trade_date)
                    if next_trade_date:
                        risk_candidates: list[dict[str, Any]] = []
                        preheat_candidates: list[dict[str, Any]] = []
                        impulse_candidates: list[dict[str, Any]] = []
                        for row, es, ds in zip(eval_rows_z, eligibility_eval_scores, de_risk_eval_scores, strict=False):
                            symbol = row["symbol"]
                            if (
                                row["regime_proxy_semantic"] in {"risk_off_deterioration_proxy", "sentiment_overdrive_transition_proxy", "weak_drift_chop_proxy"}
                                and ds <= de_risk_threshold
                                and symbol in positions
                                and all(p["symbol"] != symbol or p["action"] != "sell" for p in pending_orders.get(next_trade_date, []))
                            ):
                                risk_candidates.append(
                                    {
                                        "symbol": symbol,
                                        "eligibility_score": es,
                                        "regime_proxy_semantic": row["regime_proxy_semantic"],
                                        "event_state": row["event_state"],
                                        "phase_window_semantic": row["phase_window_semantic"],
                                    }
                                )
                            cooldown_anchor = last_sell_idx_by_symbol.get(symbol)
                            if cooldown_anchor is not None and current_idx - cooldown_anchor < config.cooldown_days_after_sell:
                                continue
                            if row["phase_window_semantic"] == "preheat_window":
                                if preheat_full_scores and es <= preheat_full_threshold:
                                    preheat_candidates.append({"symbol": symbol, "score": es, "target_notional": config.preheat_full_target_notional, "reason": "phase_geometry_preheat_full"})
                                elif es <= preheat_probe_threshold:
                                    preheat_candidates.append({"symbol": symbol, "score": es, "target_notional": 40_000.0, "reason": "phase_geometry_preheat_probe"})
                            elif row["phase_window_semantic"] == "impulse_window":
                                if impulse_full_scores and es <= impulse_full_threshold:
                                    impulse_candidates.append({"symbol": symbol, "score": es, "target_notional": 100_000.0, "reason": "phase_geometry_impulse_full"})
                                elif es <= impulse_probe_threshold:
                                    impulse_candidates.append({"symbol": symbol, "score": es, "target_notional": 40_000.0, "reason": "phase_geometry_impulse_probe"})

                        selected_risk = [c for c in risk_candidates if self._family_match(c, config.family)]
                        for candidate in selected_risk:
                            pending_orders.setdefault(next_trade_date, []).append(
                                {
                                    "symbol": candidate["symbol"],
                                    "action": "sell",
                                    "reason": f"orthogonal_downside_{config.family}",
                                    "sell_ratio": config.sell_ratio,
                                }
                            )

                        preheat_candidates = sorted(preheat_candidates, key=lambda item: (item["score"], item["symbol"]))[: config.preheat_cap]
                        impulse_candidates = sorted(impulse_candidates, key=lambda item: (item["score"], item["symbol"]))[: config.impulse_cap]
                        for candidate in preheat_candidates + impulse_candidates:
                            existing = [p for p in pending_orders.get(next_trade_date, []) if p["symbol"] == candidate["symbol"] and p["action"] == "buy"]
                            if existing:
                                prior = existing[0]["target_notional"]
                                existing[0]["target_notional"] = max(prior, candidate["target_notional"])
                                if candidate["target_notional"] > prior:
                                    existing[0]["reason"] = candidate["reason"]
                            else:
                                pending_orders.setdefault(next_trade_date, []).append(
                                    {"symbol": candidate["symbol"], "action": "buy", "reason": candidate["reason"], "target_notional": candidate["target_notional"]}
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

        return {
            "variant": config.name,
            "summary": {
                "final_equity": round(daily_rows[-1]["equity"], 4) if daily_rows else 1_000_000.0,
                "max_drawdown": round(max((row["drawdown"] for row in daily_rows), default=0.0), 8),
                "executed_order_count": len(order_rows),
            },
            "daily_rows": daily_rows,
            "order_rows": order_rows,
        }

    @staticmethod
    def _load_existing_variant(path: Path, variant_name: str) -> dict[str, Any]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return {
            "variant": variant_name,
            "summary": payload["summary"],
            "daily_rows": payload["daily_rows"],
            "order_rows": payload["order_rows"],
        }

    @staticmethod
    def _held_day_count(daily_rows: list[dict[str, Any]], symbol: str) -> int:
        total = 0
        for row in daily_rows:
            held_symbols = [item for item in row.get("held_symbols", "").split(",") if item]
            if symbol in held_symbols:
                total += 1
        return total

    def _symbol_attribution_rows(
        self,
        *,
        variant_name: str,
        daily_rows: list[dict[str, Any]],
        order_rows: list[dict[str, Any]],
        daily_map: dict[tuple[str, str], dict[str, str]],
    ) -> list[dict[str, Any]]:
        if not daily_rows:
            return []
        final_trade_date = daily_rows[-1]["trade_date"]
        rows: list[dict[str, Any]] = []
        for symbol in sorted({row["symbol"] for row in order_rows}):
            lots: list[tuple[int, float]] = []
            gross_buy = 0.0
            gross_sell = 0.0
            buy_order_count = 0
            sell_order_count = 0
            realized_pnl = 0.0
            for order in [item for item in order_rows if item["symbol"] == symbol]:
                quantity = int(order["quantity"])
                notional = float(order["notional"])
                total_cost = float(order["total_cost"])
                if order["action"] == "open":
                    gross_buy += notional
                    buy_order_count += 1
                    lots.append((quantity, (notional + total_cost) / quantity))
                else:
                    gross_sell += notional
                    sell_order_count += 1
                    net_proceeds_per_share = (notional - total_cost) / quantity
                    remaining = quantity
                    new_lots: list[tuple[int, float]] = []
                    for lot_qty, lot_cost in lots:
                        if remaining <= 0:
                            new_lots.append((lot_qty, lot_cost))
                            continue
                        matched = min(remaining, lot_qty)
                        realized_pnl += matched * (net_proceeds_per_share - lot_cost)
                        leftover = lot_qty - matched
                        if leftover > 0:
                            new_lots.append((leftover, lot_cost))
                        remaining -= matched
                    lots = new_lots
            end_close = float(daily_map[(symbol, final_trade_date)]["close"])
            ending_quantity = sum(qty for qty, _ in lots)
            unrealized_pnl = sum(qty * (end_close - lot_cost) for qty, lot_cost in lots)
            rows.append(
                {
                    "variant": variant_name,
                    "symbol": symbol,
                    "buy_order_count": buy_order_count,
                    "sell_order_count": sell_order_count,
                    "gross_buy_notional": round(gross_buy, 4),
                    "gross_sell_notional": round(gross_sell, 4),
                    "ending_quantity": ending_quantity,
                    "ending_market_value": round(ending_quantity * end_close, 4),
                    "realized_pnl": round(realized_pnl, 4),
                    "unrealized_pnl": round(unrealized_pnl, 4),
                    "total_pnl": round(realized_pnl + unrealized_pnl, 4),
                    "held_day_count": self._held_day_count(daily_rows, symbol),
                }
            )
        return rows

    @staticmethod
    def _drawdown_episodes(daily_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not daily_rows:
            return []
        peak_row = daily_rows[0]
        trough_row = daily_rows[0]
        active = False
        episodes: list[dict[str, Any]] = []
        for row in daily_rows[1:]:
            if float(row["equity"]) >= float(peak_row["equity"]):
                if active:
                    peak_equity = float(peak_row["equity"])
                    trough_equity = float(trough_row["equity"])
                    episodes.append(
                        {
                            "peak_trade_date": peak_row["trade_date"],
                            "peak_equity": round(peak_equity, 4),
                            "trough_trade_date": trough_row["trade_date"],
                            "trough_equity": round(trough_equity, 4),
                            "drawdown": round(1.0 - (trough_equity / peak_equity), 8),
                        }
                    )
                    active = False
                peak_row = row
                trough_row = row
            else:
                if not active:
                    active = True
                    trough_row = row
                elif float(row["equity"]) <= float(trough_row["equity"]):
                    trough_row = row
        if active:
            peak_equity = float(peak_row["equity"])
            trough_equity = float(trough_row["equity"])
            episodes.append(
                {
                    "peak_trade_date": peak_row["trade_date"],
                    "peak_equity": round(peak_equity, 4),
                    "trough_trade_date": trough_row["trade_date"],
                    "trough_equity": round(trough_equity, 4),
                    "drawdown": round(1.0 - (trough_equity / peak_equity), 8),
                }
            )
        return sorted(episodes, key=lambda item: (-float(item["drawdown"]), item["peak_trade_date"]))

    @staticmethod
    def _window_drawdown(daily_rows: list[dict[str, Any]], peak_trade_date: str, trough_trade_date: str) -> float:
        row_map = {row["trade_date"]: row for row in daily_rows}
        peak_equity = float(row_map[peak_trade_date]["equity"])
        trough_equity = float(row_map[trough_trade_date]["equity"])
        return round(1.0 - (trough_equity / peak_equity), 8)

    @staticmethod
    def _reduce_orders_in_window(order_rows: list[dict[str, Any]], start: str, end: str) -> tuple[int, float]:
        reduce_rows = [
            row for row in order_rows
            if row["action"] == "reduce" and start <= row["execution_trade_date"] <= end
        ]
        return len(reduce_rows), round(sum(float(row["notional"]) for row in reduce_rows), 4)

    def analyze(self) -> V127GCommercialAerospacePrimaryReferenceAttributionReport:
        base = self._load_base_config()
        label_table = V126MCommercialAerospacePhaseGeometryLabelTableAnalyzer(self.repo_root).analyze()
        rows, test_dates, date_to_idx = self._split_rows(label_table.training_rows)
        daily_bars = _load_csv(self.daily_path)
        daily_map = {(row["symbol"], row["trade_date"]): row for row in daily_bars}

        primary = self._simulate_variant_detailed(
            rows,
            test_dates,
            date_to_idx,
            _ReplayConfig(
                name="v127e_broad_half_reference",
                preheat_cap=int(base["preheat_cap"]),
                impulse_cap=int(base["impulse_cap"]),
                cooldown_days_after_sell=int(base["cooldown_days_after_sell"]),
                min_increment_notional=float(base["min_increment_notional"]),
                preheat_full_target_notional=70_000.0,
                family="broad_half_reference",
                sell_ratio=0.5,
            ),
        )
        aggressive = self._simulate_variant_detailed(
            rows,
            test_dates,
            date_to_idx,
            _ReplayConfig(
                name="weak_drift_event_neutral_half",
                preheat_cap=int(base["preheat_cap"]),
                impulse_cap=int(base["impulse_cap"]),
                cooldown_days_after_sell=int(base["cooldown_days_after_sell"]),
                min_increment_notional=float(base["min_increment_notional"]),
                preheat_full_target_notional=70_000.0,
                family="weak_drift_event_neutral_half",
                sell_ratio=0.5,
            ),
        )
        v126o = self._load_existing_variant(self.v126o_path, "v126o_economic_reference")
        v126q = self._load_existing_variant(self.v126q_path, "v126q_cleaner_reference")

        variants = [v126o, v126q, primary, aggressive]
        variant_rows: list[dict[str, Any]] = []
        symbol_attribution_rows: list[dict[str, Any]] = []
        for variant in variants:
            summary = variant["summary"]
            order_rows = variant["order_rows"]
            daily_rows = variant["daily_rows"]
            variant_rows.append(
                {
                    "variant": variant["variant"],
                    "final_equity": round(float(summary["final_equity"]), 4),
                    "max_drawdown": round(float(summary["max_drawdown"]), 8),
                    "executed_order_count": int(summary["executed_order_count"]),
                    "open_order_count": sum(1 for row in order_rows if row["action"] == "open"),
                    "reduce_order_count": sum(1 for row in order_rows if row["action"] == "reduce"),
                    "peak_trade_date": max(daily_rows, key=lambda row: float(row["equity"]))["trade_date"],
                    "peak_equity": round(max(float(row["equity"]) for row in daily_rows), 4),
                }
            )
            symbol_attribution_rows.extend(
                self._symbol_attribution_rows(
                    variant_name=variant["variant"],
                    daily_rows=daily_rows,
                    order_rows=order_rows,
                    daily_map=daily_map,
                )
            )

        primary_episodes = self._drawdown_episodes(primary["daily_rows"])[:3]
        drawdown_compare_rows: list[dict[str, Any]] = []
        for idx, episode in enumerate(primary_episodes, start=1):
            reduce_count, reduce_notional = self._reduce_orders_in_window(
                primary["order_rows"],
                episode["peak_trade_date"],
                episode["trough_trade_date"],
            )
            drawdown_compare_rows.append(
                {
                    "reference_variant": primary["variant"],
                    "comparator_variant": primary["variant"],
                    "rank": idx,
                    "peak_trade_date": episode["peak_trade_date"],
                    "trough_trade_date": episode["trough_trade_date"],
                    "window_drawdown": episode["drawdown"],
                    "reduce_order_count_in_window": reduce_count,
                    "reduce_notional_in_window": reduce_notional,
                }
            )
            for comparator in (v126o, v126q, aggressive):
                drawdown_compare_rows.append(
                    {
                        "reference_variant": primary["variant"],
                        "comparator_variant": comparator["variant"],
                        "rank": idx,
                        "peak_trade_date": episode["peak_trade_date"],
                        "trough_trade_date": episode["trough_trade_date"],
                        "window_drawdown": self._window_drawdown(
                            comparator["daily_rows"],
                            episode["peak_trade_date"],
                            episode["trough_trade_date"],
                        ),
                        "reduce_order_count_in_window": self._reduce_orders_in_window(
                            comparator["order_rows"],
                            episode["peak_trade_date"],
                            episode["trough_trade_date"],
                        )[0],
                        "reduce_notional_in_window": self._reduce_orders_in_window(
                            comparator["order_rows"],
                            episode["peak_trade_date"],
                            episode["trough_trade_date"],
                        )[1],
                    }
                )

        summary = {
            "acceptance_posture": "freeze_v127g_commercial_aerospace_primary_reference_attribution_v1",
            "primary_variant": primary["variant"],
            "primary_final_equity": round(float(primary["summary"]["final_equity"]), 4),
            "primary_max_drawdown": round(float(primary["summary"]["max_drawdown"]), 8),
            "primary_vs_v126o_equity_delta": round(float(primary["summary"]["final_equity"]) - float(v126o["summary"]["final_equity"]), 4),
            "primary_vs_v126o_drawdown_delta": round(float(primary["summary"]["max_drawdown"]) - float(v126o["summary"]["max_drawdown"]), 8),
            "primary_vs_v126q_equity_delta": round(float(primary["summary"]["final_equity"]) - float(v126q["summary"]["final_equity"]), 4),
            "primary_vs_v126q_drawdown_delta": round(float(primary["summary"]["max_drawdown"]) - float(v126q["summary"]["max_drawdown"]), 8),
            "aggressive_shadow_variant": aggressive["variant"],
            "aggressive_shadow_final_equity": round(float(aggressive["summary"]["final_equity"]), 4),
            "aggressive_shadow_max_drawdown": round(float(aggressive["summary"]["max_drawdown"]), 8),
        }
        interpretation = [
            "V1.27G aligns the old economic reference, the cleaner reference, the new primary reference, and the retained aggressive shadow on one attribution plane.",
            "The point is to explain why V1.27E broad-half improved the replay frontier, not to open another tuning branch.",
        ]
        return V127GCommercialAerospacePrimaryReferenceAttributionReport(
            summary=summary,
            variant_rows=variant_rows,
            symbol_attribution_rows=symbol_attribution_rows,
            drawdown_compare_rows=drawdown_compare_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V127GCommercialAerospacePrimaryReferenceAttributionReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V127GCommercialAerospacePrimaryReferenceAttributionAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v127g_commercial_aerospace_primary_reference_attribution_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
