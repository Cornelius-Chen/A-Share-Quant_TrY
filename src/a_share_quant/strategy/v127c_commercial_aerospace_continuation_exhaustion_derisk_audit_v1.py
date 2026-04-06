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
class _Config:
    name: str
    preheat_cap: int
    impulse_cap: int
    cooldown_days_after_sell: int
    min_increment_notional: float
    preheat_full_target_notional: float
    derisk_mode: str
    sell_ratio: float


@dataclass(slots=True)
class V127CCommercialAerospaceContinuationExhaustionDeriskAuditReport:
    summary: dict[str, Any]
    variant_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "variant_rows": self.variant_rows,
            "interpretation": self.interpretation,
        }


class V127CCommercialAerospaceContinuationExhaustionDeriskAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.daily_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
        self.audit_path = repo_root / "reports" / "analysis" / "v126p_commercial_aerospace_execution_surface_pruning_audit_v1.json"
        self.v126o_path = repo_root / "reports" / "analysis" / "v126o_commercial_aerospace_phase_geometry_walk_forward_shadow_replay_v1.json"
        self.v126q_path = repo_root / "reports" / "analysis" / "v126q_commercial_aerospace_pruned_phase_geometry_shadow_replay_v1.json"
        self.v127a_path = repo_root / "reports" / "analysis" / "v127a_commercial_aerospace_phase_aware_derisk_audit_v1.json"

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

    def _split_rows(self, rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str], dict[str, int]]:
        ordered_dates = sorted({row["trade_date"] for row in rows})
        split_idx = max(1, round(len(ordered_dates) * 0.8))
        date_to_idx = {trade_date: idx for idx, trade_date in enumerate(ordered_dates)}
        return rows, ordered_dates[split_idx:], date_to_idx

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

    def _filter_risk_candidates(self, risk_candidates: list[dict[str, Any]], mode: str) -> list[dict[str, Any]]:
        if mode == "broad_half_reference":
            return risk_candidates
        if mode == "continuation_exhaustion_half":
            return [
                c
                for c in risk_candidates
                if c["current_phase"] == "risk_or_overdrive_window" and c["event_state"] == "continuation_active"
            ]
        return [
            c
            for c in risk_candidates
            if c["current_phase"] == "risk_or_overdrive_window"
            and c["event_state"] == "continuation_active"
            and c["eligibility_score"] > c["impulse_probe_threshold"]
        ]

    def _simulate_variant(self, rows: list[dict[str, Any]], test_dates: list[str], date_to_idx: dict[str, int], config: _Config) -> dict[str, Any]:
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
                        if row["regime_proxy_semantic"] in {"risk_off_deterioration_proxy", "sentiment_overdrive_transition_proxy"}
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
                                row["regime_proxy_semantic"] in {"risk_off_deterioration_proxy", "sentiment_overdrive_transition_proxy"}
                                and ds <= de_risk_threshold
                                and symbol in positions
                                and all(p["symbol"] != symbol or p["action"] != "sell" for p in pending_orders.get(next_trade_date, []))
                            ):
                                risk_candidates.append(
                                    {
                                        "symbol": symbol,
                                        "eligibility_score": es,
                                        "event_state": row["event_state"],
                                        "current_phase": row["phase_window_semantic"],
                                        "impulse_probe_threshold": impulse_probe_threshold,
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

                        selected_risk = self._filter_risk_candidates(risk_candidates, config.derisk_mode)
                        for candidate in selected_risk:
                            pending_orders.setdefault(next_trade_date, []).append(
                                {
                                    "symbol": candidate["symbol"],
                                    "action": "sell",
                                    "reason": f"continuation_exhaustion_{config.derisk_mode}",
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
            "executed_order_count": len(order_rows),
            "final_equity": round(daily_rows[-1]["equity"], 4) if daily_rows else 1_000_000.0,
            "max_drawdown": round(max((row["drawdown"] for row in daily_rows), default=0.0), 8),
        }

    def analyze(self) -> V127CCommercialAerospaceContinuationExhaustionDeriskAuditReport:
        base = self._load_base_config()
        table = V126MCommercialAerospacePhaseGeometryLabelTableAnalyzer(self.repo_root).analyze()
        rows, test_dates, date_to_idx = self._split_rows(table.training_rows)
        variants = [
            _Config("broad_half_reference", int(base["preheat_cap"]), int(base["impulse_cap"]), int(base["cooldown_days_after_sell"]), float(base["min_increment_notional"]), 70_000.0, "broad_half_reference", 0.5),
            _Config("continuation_exhaustion_half", int(base["preheat_cap"]), int(base["impulse_cap"]), int(base["cooldown_days_after_sell"]), float(base["min_increment_notional"]), 70_000.0, "continuation_exhaustion_half", 0.5),
            _Config("continuation_exhaustion_full", int(base["preheat_cap"]), int(base["impulse_cap"]), int(base["cooldown_days_after_sell"]), float(base["min_increment_notional"]), 70_000.0, "continuation_exhaustion_full", 1.0),
        ]
        variant_rows = [self._simulate_variant(rows, test_dates, date_to_idx, variant) for variant in variants]

        v126o = json.loads(self.v126o_path.read_text(encoding="utf-8"))["summary"]
        v126q = json.loads(self.v126q_path.read_text(encoding="utf-8"))["summary"]
        v127a = json.loads(self.v127a_path.read_text(encoding="utf-8"))["summary"]
        best_variant = min(variant_rows, key=lambda row: (row["max_drawdown"], -row["final_equity"]))
        summary = {
            "acceptance_posture": "freeze_v127c_commercial_aerospace_continuation_exhaustion_derisk_audit_v1",
            "reference_v126o_final_equity": v126o["final_equity"],
            "reference_v126o_max_drawdown": v126o["max_drawdown"],
            "reference_v126q_final_equity": v126q["final_equity"],
            "reference_v126q_max_drawdown": v126q["max_drawdown"],
            "reference_v127a_best_variant": v127a["best_variant"],
            "reference_v127a_best_final_equity": v127a["best_variant_final_equity"],
            "reference_v127a_best_max_drawdown": v127a["best_variant_max_drawdown"],
            "best_variant": best_variant["variant"],
            "best_variant_final_equity": best_variant["final_equity"],
            "best_variant_max_drawdown": best_variant["max_drawdown"],
            "best_variant_executed_order_count": best_variant["executed_order_count"],
        }
        interpretation = [
            "V1.27C narrows downside further: only names in risk/overdrive windows with still-active continuation narrative are de-risked, i.e. continuation-exhaustion instead of general weakness.",
            "This tests whether commercial-aerospace downside is really about story continuation failing under overheated structure rather than broad risk-off alone.",
        ]
        return V127CCommercialAerospaceContinuationExhaustionDeriskAuditReport(
            summary=summary,
            variant_rows=variant_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V127CCommercialAerospaceContinuationExhaustionDeriskAuditReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V127CCommercialAerospaceContinuationExhaustionDeriskAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v127c_commercial_aerospace_continuation_exhaustion_derisk_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
