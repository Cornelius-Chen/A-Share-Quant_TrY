from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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


@dataclass(slots=True)
class V127ICommercialAerospaceSymbolPhaseAwareDeriskBudgetAuditReport:
    summary: dict[str, Any]
    variant_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "variant_rows": self.variant_rows,
            "interpretation": self.interpretation,
        }


class V127ICommercialAerospaceSymbolPhaseAwareDeriskBudgetAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.helper = V127GCommercialAerospacePrimaryReferenceAttributionAnalyzer(repo_root)
        self.daily_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"

    @staticmethod
    def _base_ratio_for_regime(regime_proxy_semantic: str, profile: str) -> float:
        if profile == "reference":
            mapping = {
                "risk_off_deterioration_proxy": 0.50,
                "sentiment_overdrive_transition_proxy": 0.50,
                "weak_drift_chop_proxy": 0.50,
            }
        elif profile == "light":
            mapping = {
                "risk_off_deterioration_proxy": 0.50,
                "sentiment_overdrive_transition_proxy": 0.50,
                "weak_drift_chop_proxy": 0.25,
            }
        elif profile == "strict":
            mapping = {
                "risk_off_deterioration_proxy": 0.75,
                "sentiment_overdrive_transition_proxy": 0.50,
                "weak_drift_chop_proxy": 0.25,
            }
        else:
            mapping = {
                "risk_off_deterioration_proxy": 0.50,
                "sentiment_overdrive_transition_proxy": 0.50,
                "weak_drift_chop_proxy": 0.25,
            }
        return mapping.get(regime_proxy_semantic, 0.25)

    def _symbol_adjustment(self, train_rows_z: list[dict[str, Any]], symbol: str) -> float:
        history = [
            float(row["forward_return_10"])
            for row in train_rows_z
            if row["symbol"] == symbol
            and row["regime_proxy_semantic"] in {"risk_off_deterioration_proxy", "sentiment_overdrive_transition_proxy", "weak_drift_chop_proxy"}
        ]
        if not history:
            return 0.0
        mean_forward = sum(history) / len(history)
        if mean_forward <= -0.03:
            return 0.25
        if mean_forward >= 0.01:
            return -0.25
        return 0.0

    def _simulate_variant(self, rows: list[dict[str, Any]], test_dates: list[str], date_to_idx: dict[str, int], config: _ReplayConfig, *, profile: str) -> dict[str, Any]:
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
                    order_rows.append({"execution_trade_date": trade_date, "symbol": order["symbol"], "action": "open", "reason": order["reason"], "quantity": quantity, "execution_price": round(next_open, 6), "notional": round(notional, 4), **costs})
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
                    order_rows.append({"execution_trade_date": trade_date, "symbol": order["symbol"], "action": "reduce", "reason": order["reason"], "quantity": quantity, "execution_price": round(next_open, 6), "notional": round(notional, 4), **costs})

            matured_cutoff_idx = current_idx - 10
            if matured_cutoff_idx >= 0:
                matured_dates = set(ordered_dates[: matured_cutoff_idx + 1])
                available_rows = [row for row in rows if row["trade_date"] in matured_dates]
                eval_rows = by_date.get(trade_date, [])
                if available_rows and eval_rows:
                    train_rows_z, eval_rows_z = self.helper._standardize(available_rows, eval_rows)
                    eligibility_train_scores = self.helper._score_rows(train_rows_z, train_rows_z, {"probe_eligibility_target", "full_eligibility_target"})
                    de_risk_train_scores = self.helper._score_rows(train_rows_z, train_rows_z, {"de_risk_target"})
                    eligibility_eval_scores = self.helper._score_rows(train_rows_z, eval_rows_z, {"probe_eligibility_target", "full_eligibility_target"})
                    de_risk_eval_scores = self.helper._score_rows(train_rows_z, eval_rows_z, {"de_risk_target"})

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
                                symbol_adjustment = 0.0 if profile == "reference" else self._symbol_adjustment(train_rows_z, symbol)
                                sell_ratio = self._base_ratio_for_regime(row["regime_proxy_semantic"], profile) + symbol_adjustment
                                sell_ratio = max(0.25, min(1.0, sell_ratio))
                                pending_orders.setdefault(next_trade_date, []).append({"symbol": symbol, "action": "sell", "reason": f"symbol_phase_budget_{profile}", "sell_ratio": sell_ratio})
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

                        preheat_candidates = sorted(preheat_candidates, key=lambda item: (item["score"], item["symbol"]))[: config.preheat_cap]
                        impulse_candidates = sorted(impulse_candidates, key=lambda item: (item["score"], item["symbol"]))[: config.impulse_cap]
                        for candidate in preheat_candidates + impulse_candidates:
                            existing = [p for p in pending_orders.get(next_trade_date, []) if p["symbol"] == candidate["symbol"] and p["action"] == "buy"]
                            if existing:
                                existing[0]["target_notional"] = max(existing[0]["target_notional"], candidate["target_notional"])
                            else:
                                pending_orders.setdefault(next_trade_date, []).append({"symbol": candidate["symbol"], "action": "buy", "reason": candidate["reason"], "target_notional": candidate["target_notional"]})

            market_value = 0.0
            for symbol, quantity in positions.items():
                bar = daily_map.get((symbol, trade_date))
                if bar:
                    market_value += quantity * float(bar["close"])
            equity = cash + market_value
            peak_equity = max(peak_equity, equity)
            drawdown = 0.0 if peak_equity <= 0 else 1.0 - (equity / peak_equity)
            daily_rows.append({"trade_date": trade_date, "equity": round(equity, 4), "drawdown": round(drawdown, 8)})

        return {
            "variant": config.name if profile == "reference" else f"{config.name}_{profile}",
            "executed_order_count": len(order_rows),
            "final_equity": round(daily_rows[-1]["equity"], 4) if daily_rows else 1_000_000.0,
            "max_drawdown": round(max((row["drawdown"] for row in daily_rows), default=0.0), 8),
            "reduce_order_count": sum(1 for row in order_rows if row["action"] == "reduce"),
        }

    def analyze(self) -> V127ICommercialAerospaceSymbolPhaseAwareDeriskBudgetAuditReport:
        base = self.helper._load_base_config()
        table = V126MCommercialAerospacePhaseGeometryLabelTableAnalyzer(self.repo_root).analyze()
        rows, test_dates, date_to_idx = self.helper._split_rows(table.training_rows)
        reference_config = _ReplayConfig("broad_half_reference", int(base["preheat_cap"]), int(base["impulse_cap"]), int(base["cooldown_days_after_sell"]), float(base["min_increment_notional"]), 70_000.0, "broad_half_reference", 0.5)
        variant_rows = [
            self._simulate_variant(rows, test_dates, date_to_idx, reference_config, profile="reference"),
            self._simulate_variant(rows, test_dates, date_to_idx, reference_config, profile="light"),
            self._simulate_variant(rows, test_dates, date_to_idx, reference_config, profile="balanced"),
            self._simulate_variant(rows, test_dates, date_to_idx, reference_config, profile="strict"),
        ]
        best_variant = min(variant_rows, key=lambda row: (row["max_drawdown"], -row["final_equity"]))
        summary = {
            "acceptance_posture": "freeze_v127i_commercial_aerospace_symbol_phase_aware_derisk_budget_audit_v1",
            "reference_variant": "broad_half_reference",
            "reference_final_equity": variant_rows[0]["final_equity"],
            "reference_max_drawdown": variant_rows[0]["max_drawdown"],
            "best_variant": best_variant["variant"],
            "best_variant_final_equity": best_variant["final_equity"],
            "best_variant_max_drawdown": best_variant["max_drawdown"],
        }
        interpretation = [
            "V1.27I tests whether the promoted broad-half primary reference can improve by reallocating de-risk budget across symbols and phases rather than by inventing a new downside family.",
            "Sell ratios are still lawful-shadow only: they use matured downside history inside the current replay chronology.",
        ]
        return V127ICommercialAerospaceSymbolPhaseAwareDeriskBudgetAuditReport(summary=summary, variant_rows=variant_rows, interpretation=interpretation)


def write_report(*, reports_dir: Path, report_name: str, result: V127ICommercialAerospaceSymbolPhaseAwareDeriskBudgetAuditReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V127ICommercialAerospaceSymbolPhaseAwareDeriskBudgetAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v127i_commercial_aerospace_symbol_phase_aware_derisk_budget_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
