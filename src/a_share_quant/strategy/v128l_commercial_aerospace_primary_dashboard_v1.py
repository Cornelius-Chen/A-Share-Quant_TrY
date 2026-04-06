from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from a_share_quant.strategy.v126m_commercial_aerospace_phase_geometry_label_table_v1 import (
    V126MCommercialAerospacePhaseGeometryLabelTableAnalyzer,
)
from a_share_quant.strategy.v127g_commercial_aerospace_primary_reference_attribution_v1 import (
    V127GCommercialAerospacePrimaryReferenceAttributionAnalyzer,
    _ReplayConfig,
    _load_csv,
    _quantile,
    _trade_costs,
)
from a_share_quant.strategy.v127m_commercial_aerospace_phase_conditioned_drag_veto_audit_v1 import (
    _VetoPolicy,
    V127MCommercialAerospacePhaseConditionedDragVetoAuditAnalyzer,
)


WINDOW_START = "20260112"
WINDOW_END = "20260212"
POST_WINDOW_START = "20260213"


@dataclass(slots=True)
class V128LCommercialAerospacePrimaryDashboardReport:
    summary: dict[str, Any]
    grouped_action_rows: list[dict[str, Any]]
    top_drawdown_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "grouped_action_rows": self.grouped_action_rows,
            "top_drawdown_rows": self.top_drawdown_rows,
            "interpretation": self.interpretation,
        }


class V128LCommercialAerospacePrimaryDashboardAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.helper = V127GCommercialAerospacePrimaryReferenceAttributionAnalyzer(repo_root)
        self.policy_analyzer = V127MCommercialAerospacePhaseConditionedDragVetoAuditAnalyzer(repo_root)
        self.daily_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
        self.control_core_report_path = repo_root / "reports" / "analysis" / "v124v_commercial_aerospace_control_core_thinning_retriage_v1.json"

    @staticmethod
    def _parse_trade_date(value: str) -> datetime.date:
        return datetime.strptime(value, "%Y%m%d").date()

    @staticmethod
    def _current_primary_config() -> dict[str, float | str]:
        return {
            "name": "tail_weakdrift_full",
            "main_riskoff_sell_ratio": 1.0,
            "main_weakdrift_sell_ratio": 0.75,
            "main_sentiment_sell_ratio": 0.75,
            "main_impulse_sell_ratio": 0.75,
            "post_weakdrift_sell_ratio": 1.0,
            "post_sentiment_sell_ratio": 0.75,
            "post_impulse_sell_ratio": 0.75,
        }

    def _load_control_core_symbols(self) -> list[str]:
        payload = json.loads(self.control_core_report_path.read_text(encoding="utf-8"))
        return [row["symbol"] for row in payload["control_core_rows"]]

    def _simulate_current_primary(self) -> dict[str, Any]:
        base = self.helper._load_base_config()
        drag_trio = set(self.policy_analyzer._drag_symbols()[:3])
        veto_policy = _VetoPolicy("veto_drag_trio_impulse_only", set(), set(), drag_trio)
        label_table = V126MCommercialAerospacePhaseGeometryLabelTableAnalyzer(self.repo_root).analyze()
        rows, test_dates, date_to_idx = self.helper._split_rows(label_table.training_rows)
        rows = [row for row in rows if not self.policy_analyzer._blocked(row, veto_policy)]

        replay_config = _ReplayConfig(
            name="tail_weakdrift_full",
            preheat_cap=int(base["preheat_cap"]),
            impulse_cap=int(base["impulse_cap"]),
            cooldown_days_after_sell=int(base["cooldown_days_after_sell"]),
            min_increment_notional=float(base["min_increment_notional"]),
            preheat_full_target_notional=70_000.0,
            family="tail_weakdrift_full",
            sell_ratio=0.5,
        )
        config = self._current_primary_config()

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
                    if incremental_notional < replay_config.min_increment_notional:
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
                    action = "open" if current_qty <= 0 else "add"
                    positions[order["symbol"]] = current_qty + quantity
                    order_rows.append(
                        {
                            "execution_trade_date": trade_date,
                            "signal_trade_date": order["signal_trade_date"],
                            "symbol": order["symbol"],
                            "action": action,
                            "reason": order["reason"],
                            "quantity": quantity,
                            "execution_price": round(next_open, 6),
                            "notional": round(notional, 4),
                            "weight_vs_initial_capital": round(notional / 1_000_000.0, 8),
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
                    action = "reduce" if remaining > 0 else "close"
                    if remaining > 0:
                        positions[order["symbol"]] = remaining
                    else:
                        positions.pop(order["symbol"], None)
                    last_sell_idx_by_symbol[order["symbol"]] = current_idx
                    order_rows.append(
                        {
                            "execution_trade_date": trade_date,
                            "signal_trade_date": order["signal_trade_date"],
                            "symbol": order["symbol"],
                            "action": action,
                            "reason": order["reason"],
                            "quantity": quantity,
                            "execution_price": round(next_open, 6),
                            "notional": round(notional, 4),
                            "weight_vs_initial_capital": round(notional / 1_000_000.0, 8),
                            **costs,
                        }
                    )

            matured_cutoff_idx = current_idx - 10
            if matured_cutoff_idx >= 0:
                matured_dates = set(ordered_dates[: matured_cutoff_idx + 1])
                available_rows = [row for row in rows if row["trade_date"] in matured_dates]
                eval_rows = by_date.get(trade_date, [])
                if available_rows and eval_rows:
                    train_rows_z, eval_rows_z = self.helper._standardize(available_rows, eval_rows)
                    eligibility_train_scores = self.helper._score_rows(
                        train_rows_z,
                        train_rows_z,
                        {"probe_eligibility_target", "full_eligibility_target"},
                    )
                    de_risk_train_scores = self.helper._score_rows(train_rows_z, train_rows_z, {"de_risk_target"})
                    eligibility_eval_scores = self.helper._score_rows(
                        train_rows_z,
                        eval_rows_z,
                        {"probe_eligibility_target", "full_eligibility_target"},
                    )
                    de_risk_eval_scores = self.helper._score_rows(train_rows_z, eval_rows_z, {"de_risk_target"})

                    preheat_full_scores = [
                        score
                        for row, score in zip(train_rows_z, eligibility_train_scores, strict=False)
                        if row["phase_window_semantic"] == "preheat_window"
                        and row["supervised_action_label_pg"] == "full_eligibility_target"
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
                        if row["phase_window_semantic"] == "impulse_window"
                        and row["supervised_action_label_pg"] == "full_eligibility_target"
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
                        if row["regime_proxy_semantic"]
                        in {"risk_off_deterioration_proxy", "sentiment_overdrive_transition_proxy", "weak_drift_chop_proxy"}
                    ]
                    impulse_derisk_scores = [
                        score
                        for row, score in zip(train_rows_z, de_risk_train_scores, strict=False)
                        if row["phase_window_semantic"] == "impulse_window"
                        and row["supervised_action_label_pg"] == "de_risk_target"
                    ]
                    preheat_full_threshold = _quantile(preheat_full_scores, 0.6) if preheat_full_scores else 0.0
                    preheat_probe_threshold = _quantile(preheat_probe_scores, 0.7) if preheat_probe_scores else 0.0
                    impulse_full_threshold = _quantile(impulse_full_scores, 0.6) if impulse_full_scores else 0.0
                    impulse_probe_threshold = _quantile(impulse_probe_scores, 0.7) if impulse_probe_scores else 0.0
                    de_risk_threshold = _quantile(risk_scores, 0.8) if risk_scores else 0.0
                    impulse_derisk_threshold = _quantile(impulse_derisk_scores, 0.8) if impulse_derisk_scores else 0.0

                    next_trade_date = next_trade_date_map.get(trade_date)
                    if next_trade_date:
                        risk_candidates: list[dict[str, Any]] = []
                        preheat_candidates: list[dict[str, Any]] = []
                        impulse_candidates: list[dict[str, Any]] = []
                        for row, es, ds in zip(eval_rows_z, eligibility_eval_scores, de_risk_eval_scores, strict=False):
                            symbol = row["symbol"]
                            in_main_window = WINDOW_START <= trade_date <= WINDOW_END
                            in_post_window = trade_date >= POST_WINDOW_START
                            if (
                                row["regime_proxy_semantic"]
                                in {"risk_off_deterioration_proxy", "sentiment_overdrive_transition_proxy", "weak_drift_chop_proxy"}
                                and ds <= de_risk_threshold
                                and symbol in positions
                                and all(p["symbol"] != symbol or p["action"] != "sell" for p in pending_orders.get(next_trade_date, []))
                            ):
                                sell_ratio = 0.5
                                if in_main_window and row["regime_proxy_semantic"] == "risk_off_deterioration_proxy":
                                    sell_ratio = float(config["main_riskoff_sell_ratio"])
                                elif in_main_window and row["regime_proxy_semantic"] == "weak_drift_chop_proxy":
                                    sell_ratio = float(config["main_weakdrift_sell_ratio"])
                                elif in_main_window and row["regime_proxy_semantic"] == "sentiment_overdrive_transition_proxy":
                                    sell_ratio = float(config["main_sentiment_sell_ratio"])
                                elif in_post_window and row["regime_proxy_semantic"] == "weak_drift_chop_proxy":
                                    sell_ratio = float(config["post_weakdrift_sell_ratio"])
                                elif in_post_window and row["regime_proxy_semantic"] == "sentiment_overdrive_transition_proxy":
                                    sell_ratio = float(config["post_sentiment_sell_ratio"])
                                risk_candidates.append(
                                    {
                                        "symbol": symbol,
                                        "sell_ratio": sell_ratio,
                                        "reason": f"tail_derisk_{row['regime_proxy_semantic']}",
                                        "signal_trade_date": trade_date,
                                    }
                                )
                            if (
                                row["phase_window_semantic"] == "impulse_window"
                                and row["supervised_action_label_pg"] == "de_risk_target"
                                and ds <= impulse_derisk_threshold
                                and symbol in positions
                                and all(p["symbol"] != symbol or p["action"] != "sell" for p in pending_orders.get(next_trade_date, []))
                            ):
                                impulse_sell_ratio = 0.5
                                if in_main_window:
                                    impulse_sell_ratio = float(config["main_impulse_sell_ratio"])
                                elif in_post_window:
                                    impulse_sell_ratio = float(config["post_impulse_sell_ratio"])
                                risk_candidates.append(
                                    {
                                        "symbol": symbol,
                                        "sell_ratio": impulse_sell_ratio,
                                        "reason": "tail_derisk_impulse_target",
                                        "signal_trade_date": trade_date,
                                    }
                                )
                            cooldown_anchor = last_sell_idx_by_symbol.get(symbol)
                            if cooldown_anchor is not None and current_idx - cooldown_anchor < replay_config.cooldown_days_after_sell:
                                continue
                            if row["phase_window_semantic"] == "preheat_window":
                                if preheat_full_scores and es <= preheat_full_threshold:
                                    preheat_candidates.append(
                                        {
                                            "symbol": symbol,
                                            "score": es,
                                            "target_notional": replay_config.preheat_full_target_notional,
                                            "reason": "phase_geometry_preheat_full",
                                            "signal_trade_date": trade_date,
                                        }
                                    )
                                elif es <= preheat_probe_threshold:
                                    preheat_candidates.append(
                                        {
                                            "symbol": symbol,
                                            "score": es,
                                            "target_notional": 40_000.0,
                                            "reason": "phase_geometry_preheat_probe",
                                            "signal_trade_date": trade_date,
                                        }
                                    )
                            elif row["phase_window_semantic"] == "impulse_window":
                                if impulse_full_scores and es <= impulse_full_threshold:
                                    impulse_candidates.append(
                                        {
                                            "symbol": symbol,
                                            "score": es,
                                            "target_notional": 100_000.0,
                                            "reason": "phase_geometry_impulse_full",
                                            "signal_trade_date": trade_date,
                                        }
                                    )
                                elif es <= impulse_probe_threshold:
                                    impulse_candidates.append(
                                        {
                                            "symbol": symbol,
                                            "score": es,
                                            "target_notional": 40_000.0,
                                            "reason": "phase_geometry_impulse_probe",
                                            "signal_trade_date": trade_date,
                                        }
                                    )

                        merged_sells: dict[str, dict[str, Any]] = {}
                        for candidate in risk_candidates:
                            existing = merged_sells.get(candidate["symbol"])
                            if existing is None or candidate["sell_ratio"] > existing["sell_ratio"]:
                                merged_sells[candidate["symbol"]] = candidate
                        for candidate in merged_sells.values():
                            pending_orders.setdefault(next_trade_date, []).append(
                                {
                                    "symbol": candidate["symbol"],
                                    "action": "sell",
                                    "reason": candidate["reason"],
                                    "sell_ratio": candidate["sell_ratio"],
                                    "signal_trade_date": candidate["signal_trade_date"],
                                }
                            )

                        preheat_candidates = sorted(preheat_candidates, key=lambda item: (item["score"], item["symbol"]))[: replay_config.preheat_cap]
                        impulse_candidates = sorted(impulse_candidates, key=lambda item: (item["score"], item["symbol"]))[: replay_config.impulse_cap]
                        for candidate in preheat_candidates + impulse_candidates:
                            existing = [
                                p for p in pending_orders.get(next_trade_date, [])
                                if p["symbol"] == candidate["symbol"] and p["action"] == "buy"
                            ]
                            if existing:
                                prior = existing[0]["target_notional"]
                                existing[0]["target_notional"] = max(prior, candidate["target_notional"])
                                if candidate["target_notional"] > prior:
                                    existing[0]["reason"] = candidate["reason"]
                                    existing[0]["signal_trade_date"] = candidate["signal_trade_date"]
                            else:
                                pending_orders.setdefault(next_trade_date, []).append(
                                    {
                                        "symbol": candidate["symbol"],
                                        "action": "buy",
                                        "reason": candidate["reason"],
                                        "target_notional": candidate["target_notional"],
                                        "signal_trade_date": candidate["signal_trade_date"],
                                    }
                                )

            market_value = 0.0
            held_symbols: list[str] = []
            for symbol, quantity in sorted(positions.items()):
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
                    "held_symbols": ",".join(held_symbols),
                }
            )

        return {
            "variant": "tail_weakdrift_full",
            "final_equity": round(daily_rows[-1]["equity"], 4) if daily_rows else 1_000_000.0,
            "max_drawdown": round(max((row["drawdown"] for row in daily_rows), default=0.0), 8),
            "executed_order_count": len(order_rows),
            "daily_rows": daily_rows,
            "order_rows": order_rows,
        }

    def _board_overlay_rows(self, trade_dates: list[str]) -> list[dict[str, Any]]:
        control_symbols = self._load_control_core_symbols()
        daily_rows = _load_csv(self.daily_path)
        date_symbol_close = {
            (row["trade_date"], row["symbol"]): float(row["close"])
            for row in daily_rows
            if row["symbol"] in control_symbols
        }
        baseline_close: dict[str, float] = {}
        overlay_rows: list[dict[str, Any]] = []
        for trade_date in trade_dates:
            ratios: list[float] = []
            active_symbols = 0
            for symbol in control_symbols:
                close_value = date_symbol_close.get((trade_date, symbol))
                if close_value is None:
                    continue
                baseline_close.setdefault(symbol, close_value)
                base = baseline_close[symbol]
                if base > 0:
                    ratios.append(close_value / base)
                    active_symbols += 1
            board_equity = 1_000_000.0 if not ratios else 1_000_000.0 * sum(ratios) / len(ratios)
            overlay_rows.append(
                {
                    "trade_date": trade_date,
                    "board_overlay_equity": round(board_equity, 4),
                    "active_symbol_count": active_symbols,
                }
            )
        return overlay_rows

    @staticmethod
    def _drawdown_rows(daily_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        episodes: list[dict[str, Any]] = []
        peak_row = None
        trough_row = None
        peak_equity = -1.0
        current_max_drawdown = 0.0
        for row in daily_rows:
            equity = float(row["equity"])
            if equity >= peak_equity:
                if peak_row is not None and trough_row is not None and current_max_drawdown > 0:
                    episodes.append(
                        {
                            "peak_trade_date": peak_row["trade_date"],
                            "peak_equity": peak_row["equity"],
                            "trough_trade_date": trough_row["trade_date"],
                            "trough_equity": trough_row["equity"],
                            "drawdown": round(current_max_drawdown, 8),
                            "drawdown_amount": round(float(peak_row["equity"]) - float(trough_row["equity"]), 4),
                        }
                    )
                peak_row = row
                trough_row = row
                peak_equity = equity
                current_max_drawdown = 0.0
                continue
            drawdown = 1.0 - (equity / peak_equity) if peak_equity > 0 else 0.0
            if drawdown >= current_max_drawdown:
                current_max_drawdown = drawdown
                trough_row = row
        if peak_row is not None and trough_row is not None and current_max_drawdown > 0:
            episodes.append(
                {
                    "peak_trade_date": peak_row["trade_date"],
                    "peak_equity": peak_row["equity"],
                    "trough_trade_date": trough_row["trade_date"],
                    "trough_equity": trough_row["equity"],
                    "drawdown": round(current_max_drawdown, 8),
                    "drawdown_amount": round(float(peak_row["equity"]) - float(trough_row["equity"]), 4),
                }
            )
        return sorted(episodes, key=lambda row: (-row["drawdown"], row["peak_trade_date"]))[:3]

    @staticmethod
    def _group_action_rows(order_rows: list[dict[str, Any]], equity_by_date: dict[str, float]) -> list[dict[str, Any]]:
        grouped: dict[str, dict[str, Any]] = {}
        for row in order_rows:
            trade_date = row["execution_trade_date"]
            bucket = grouped.setdefault(
                trade_date,
                {
                    "trade_date": trade_date,
                    "open_count": 0,
                    "add_count": 0,
                    "reduce_count": 0,
                    "close_count": 0,
                    "buy_weight": 0.0,
                    "sell_weight": 0.0,
                    "symbols": [],
                    "equity": equity_by_date.get(trade_date, 0.0),
                },
            )
            action = row["action"]
            bucket[f"{action}_count"] += 1
            weight = float(row["weight_vs_initial_capital"])
            if action in {"open", "add"}:
                bucket["buy_weight"] += weight
            else:
                bucket["sell_weight"] += weight
            bucket["symbols"].append(row["symbol"])

        grouped_rows: list[dict[str, Any]] = []
        for trade_date, row in sorted(grouped.items()):
            symbols = sorted(set(row["symbols"]))
            display_symbols = "/".join(symbols[:3]) + (f"/+{len(symbols) - 3}" if len(symbols) > 3 else "")
            label_bits = []
            if row["open_count"]:
                label_bits.append(f"O{row['open_count']}")
            if row["add_count"]:
                label_bits.append(f"A{row['add_count']}")
            if row["reduce_count"]:
                label_bits.append(f"R{row['reduce_count']}")
            if row["close_count"]:
                label_bits.append(f"C{row['close_count']}")
            net_weight = row["buy_weight"] - row["sell_weight"]
            grouped_rows.append(
                {
                    "trade_date": trade_date,
                    "open_count": row["open_count"],
                    "add_count": row["add_count"],
                    "reduce_count": row["reduce_count"],
                    "close_count": row["close_count"],
                    "buy_weight": round(row["buy_weight"], 8),
                    "sell_weight": round(row["sell_weight"], 8),
                    "net_weight": round(net_weight, 8),
                    "display_symbols": display_symbols,
                    "display_label": f"{trade_date[4:6]}-{trade_date[6:8]} {' '.join(label_bits)} {net_weight:+.1%}\n{display_symbols}",
                    "equity": round(row["equity"], 4),
                }
            )
        return grouped_rows

    @staticmethod
    def _write_csv(output_path: Path, rows: list[dict[str, Any]]) -> None:
        fieldnames = list(rows[0].keys()) if rows else []
        with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

    @staticmethod
    def _marker_size(abs_net_weight: float) -> float:
        if abs_net_weight >= 0.10:
            return 140.0
        if abs_net_weight >= 0.05:
            return 95.0
        return 60.0

    def _plot_dashboard(self, *, daily_rows: list[dict[str, Any]], grouped_action_rows: list[dict[str, Any]], output_path: Path) -> None:
        trade_dates = [self._parse_trade_date(row["trade_date"]) for row in daily_rows]
        equity_curve = [float(row["equity"]) for row in daily_rows]
        cash_curve = [float(row["cash"]) for row in daily_rows]
        board_curve = [float(row["board_overlay_equity"]) for row in daily_rows]
        equity_by_date = {self._parse_trade_date(row["trade_date"]): float(row["equity"]) for row in daily_rows}

        fig, ax = plt.subplots(figsize=(22, 10))
        ax.plot(trade_dates, equity_curve, color="#111111", linewidth=2.4, label="Equity")
        ax.plot(trade_dates, cash_curve, color="#1f77b4", linewidth=1.6, linestyle="--", label="Cash")
        ax.plot(trade_dates, board_curve, color="#7f8c8d", linewidth=1.8, linestyle="-.", label="Board Overlay")
        ax.set_title("Commercial Aerospace Primary Replay Dashboard: tail_weakdrift_full")
        ax.set_ylabel("CNY")
        ax.grid(alpha=0.18)

        styles = {
            "buy": {"color": "#1f77b4", "marker": "s", "label": "Buy Day"},
            "sell": {"color": "#ff7f0e", "marker": "^", "label": "Sell Day"},
            "mixed": {"color": "#6a3d9a", "marker": "D", "label": "Mixed Day"},
        }
        labeled_rows = sorted(grouped_action_rows, key=lambda row: (-abs(float(row["net_weight"])), row["trade_date"]))[:14]
        labeled_dates = {row["trade_date"] for row in labeled_rows}
        for idx, row in enumerate(grouped_action_rows):
            dt = self._parse_trade_date(row["trade_date"])
            equity = equity_by_date[dt]
            buy_count = int(row["open_count"]) + int(row["add_count"])
            sell_count = int(row["reduce_count"]) + int(row["close_count"])
            if buy_count > 0 and sell_count == 0:
                key = "buy"
            elif sell_count > 0 and buy_count == 0:
                key = "sell"
            else:
                key = "mixed"
            style = styles[key]
            color = style["color"]
            marker_size = self._marker_size(abs(float(row["net_weight"])))
            ax.scatter(
                dt,
                equity,
                s=marker_size,
                marker=style["marker"],
                edgecolors=color,
                facecolors="white",
                linewidths=1.7,
                zorder=7,
            )
            if row["trade_date"] in labeled_dates:
                if buy_count > 0 and sell_count == 0:
                    short_label = "B"
                elif sell_count > 0 and buy_count == 0:
                    short_label = "S"
                else:
                    short_label = "M"
                offset_y = (14 + (idx % 3) * 8) if idx % 2 == 0 else -(16 + (idx % 3) * 8)
                ax.annotate(
                    f"{dt.strftime('%m-%d')} {short_label}\n{row['display_symbols']}",
                    xy=(dt, equity),
                    xytext=(4, offset_y),
                    textcoords="offset points",
                    fontsize=6.5,
                    color=color,
                    bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.92},
                )

        legend_handles = [
            Line2D([0], [0], color="#111111", linewidth=2.4, label="Equity"),
            Line2D([0], [0], color="#1f77b4", linewidth=1.6, linestyle="--", label="Cash"),
            Line2D([0], [0], color="#7f8c8d", linewidth=1.8, linestyle="-.", label="Board Overlay"),
            Line2D([0], [0], marker="s", color="none", markeredgecolor="#1f77b4", markerfacecolor="white", label="Buy Day", markersize=7),
            Line2D([0], [0], marker="^", color="none", markeredgecolor="#ff7f0e", markerfacecolor="white", label="Sell Day", markersize=7),
            Line2D([0], [0], marker="D", color="none", markeredgecolor="#6a3d9a", markerfacecolor="white", label="Mixed Day", markersize=7),
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#555555", markerfacecolor="white", label="Small <5%", markersize=6),
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#555555", markerfacecolor="white", label="Medium 5-10%", markersize=8),
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#555555", markerfacecolor="white", label="Large >10%", markersize=10),
        ]
        ax.legend(handles=legend_handles, loc="upper left", ncol=5, fontsize=8, framealpha=0.92)

        plt.tight_layout()
        plt.savefig(output_path, dpi=180)
        plt.close(fig)

    def analyze(self) -> V128LCommercialAerospacePrimaryDashboardReport:
        replay = self._simulate_current_primary()
        board_overlay_rows = self._board_overlay_rows([row["trade_date"] for row in replay["daily_rows"]])
        overlay_map = {row["trade_date"]: row for row in board_overlay_rows}
        for row in replay["daily_rows"]:
            row["board_overlay_equity"] = overlay_map[row["trade_date"]]["board_overlay_equity"]
            row["board_active_symbol_count"] = overlay_map[row["trade_date"]]["active_symbol_count"]

        daily_csv_path = self.repo_root / "data" / "training" / "commercial_aerospace_tail_weakdrift_full_daily_state_v1.csv"
        orders_csv_path = self.repo_root / "data" / "training" / "commercial_aerospace_tail_weakdrift_full_orders_v1.csv"
        grouped_csv_path = self.repo_root / "data" / "training" / "commercial_aerospace_tail_weakdrift_full_grouped_actions_v1.csv"
        png_path = self.repo_root / "reports" / "analysis" / "v128l_commercial_aerospace_primary_dashboard_v1.png"

        daily_csv_path.parent.mkdir(parents=True, exist_ok=True)
        png_path.parent.mkdir(parents=True, exist_ok=True)

        self._write_csv(daily_csv_path, replay["daily_rows"])
        self._write_csv(orders_csv_path, replay["order_rows"])

        equity_by_date = {row["trade_date"]: float(row["equity"]) for row in replay["daily_rows"]}
        grouped_action_rows = self._group_action_rows(replay["order_rows"], equity_by_date)
        self._write_csv(grouped_csv_path, grouped_action_rows)
        self._plot_dashboard(daily_rows=replay["daily_rows"], grouped_action_rows=grouped_action_rows, output_path=png_path)

        drawdown_rows = self._drawdown_rows(replay["daily_rows"])
        summary = {
            "acceptance_posture": "freeze_v128l_commercial_aerospace_primary_dashboard_v1",
            "variant": replay["variant"],
            "initial_capital": 1000000.0,
            "final_equity": replay["final_equity"],
            "max_drawdown": replay["max_drawdown"],
            "executed_order_count": replay["executed_order_count"],
            "daily_state_csv": str(daily_csv_path.relative_to(self.repo_root)),
            "orders_csv": str(orders_csv_path.relative_to(self.repo_root)),
            "grouped_actions_csv": str(grouped_csv_path.relative_to(self.repo_root)),
            "dashboard_png": str(png_path.relative_to(self.repo_root)),
            "board_overlay_definition": "equal_weight_normalized_control_core_close_index_scaled_to_1000000",
        }
        interpretation = [
            "V1.28L rebuilds the current commercial-aerospace authoritative primary replay into a chart-ready lawful daily state.",
            "The dashboard overlays equity, cash, and a normalized control-core board path, with grouped open/add/reduce/close markers on the same curve.",
        ]
        return V128LCommercialAerospacePrimaryDashboardReport(
            summary=summary,
            grouped_action_rows=grouped_action_rows,
            top_drawdown_rows=drawdown_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V128LCommercialAerospacePrimaryDashboardReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V128LCommercialAerospacePrimaryDashboardAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128l_commercial_aerospace_primary_dashboard_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
