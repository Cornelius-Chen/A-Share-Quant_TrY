from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v126m_commercial_aerospace_phase_geometry_label_table_v1 import (
    V126MCommercialAerospacePhaseGeometryLabelTableAnalyzer,
)
from a_share_quant.strategy.v126p_commercial_aerospace_execution_surface_pruning_audit_v1 import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    _VariantConfig,
    _load_csv,
    _mean,
    _quantile,
    _std,
    _trade_costs,
)


@dataclass(slots=True)
class V126QCommercialAerospacePrunedPhaseGeometryShadowReplayReport:
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


class V126QCommercialAerospacePrunedPhaseGeometryShadowReplayAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.daily_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
        self.audit_path = repo_root / "reports" / "analysis" / "v126p_commercial_aerospace_execution_surface_pruning_audit_v1.json"

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

    def _load_best_config(self) -> _VariantConfig:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        best_name = audit["summary"]["best_variant"]
        row = next(item for item in audit["variant_rows"] if item["variant"] == best_name)
        return _VariantConfig(
            name=best_name,
            preheat_cap=int(row["preheat_cap"]),
            impulse_cap=int(row["impulse_cap"]),
            cooldown_days_after_sell=int(row["cooldown_days_after_sell"]),
            min_increment_notional=float(row["min_increment_notional"]),
        )

    def analyze(self) -> V126QCommercialAerospacePrunedPhaseGeometryShadowReplayReport:
        config = self._load_best_config()
        table = V126MCommercialAerospacePhaseGeometryLabelTableAnalyzer(self.repo_root).analyze()
        rows, test_dates, date_to_idx = self._split_rows(table.training_rows)
        ordered_dates = sorted({row["trade_date"] for row in rows})
        by_date: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            by_date.setdefault(row["trade_date"], []).append(row)

        daily_bars = _load_csv(self.daily_path)
        daily_map = {(row["symbol"], row["trade_date"]): row for row in daily_bars}
        next_trade_date_map = {ordered_dates[idx]: ordered_dates[idx + 1] for idx in range(len(ordered_dates) - 1)}

        cash = 1_000_000.0
        peak_equity = 1_000_000.0
        positions: dict[str, int] = {}
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
                    full_scores = [
                        score
                        for row, score in zip(train_rows_z, eligibility_train_scores, strict=False)
                        if row["supervised_action_label_pg"] == "full_eligibility_target"
                    ]
                    probe_scores = [
                        score
                        for row, score in zip(train_rows_z, eligibility_train_scores, strict=False)
                        if row["supervised_action_label_pg"] in {"probe_eligibility_target", "full_eligibility_target"}
                    ]
                    risk_scores = [
                        score
                        for row, score in zip(train_rows_z, de_risk_train_scores, strict=False)
                        if row["regime_proxy_semantic"] in {"risk_off_deterioration_proxy", "sentiment_overdrive_transition_proxy"}
                    ]
                    full_threshold = _quantile(full_scores, 0.6) if full_scores else 0.0
                    probe_threshold = _quantile(probe_scores, 0.7) if probe_scores else 0.0
                    de_risk_threshold = _quantile(risk_scores, 0.8) if risk_scores else 0.0
                    next_trade_date = next_trade_date_map.get(trade_date)
                    if next_trade_date:
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
                                pending_orders.setdefault(next_trade_date, []).append(
                                    {"symbol": symbol, "action": "sell", "reason": "phase_geometry_risk_low_pass", "sell_ratio": 0.5}
                                )
                            cooldown_anchor = last_sell_idx_by_symbol.get(symbol)
                            if cooldown_anchor is not None and current_idx - cooldown_anchor < config.cooldown_days_after_sell:
                                continue
                            if row["phase_window_semantic"] == "preheat_window" and es <= probe_threshold:
                                preheat_candidates.append(
                                    {"symbol": symbol, "score": es, "target_notional": 40_000.0, "reason": "phase_geometry_preheat_probe"}
                                )
                            elif row["phase_window_semantic"] == "impulse_window":
                                if full_scores and es <= full_threshold:
                                    impulse_candidates.append(
                                        {"symbol": symbol, "score": es, "target_notional": 100_000.0, "reason": "phase_geometry_impulse_full"}
                                    )
                                elif es <= probe_threshold:
                                    impulse_candidates.append(
                                        {"symbol": symbol, "score": es, "target_notional": 40_000.0, "reason": "phase_geometry_impulse_probe"}
                                    )
                        preheat_candidates = sorted(preheat_candidates, key=lambda item: (item["score"], item["symbol"]))[: config.preheat_cap]
                        impulse_candidates = sorted(impulse_candidates, key=lambda item: (item["score"], item["symbol"]))[: config.impulse_cap]
                        for candidate in preheat_candidates + impulse_candidates:
                            existing = [p for p in pending_orders.get(next_trade_date, []) if p["symbol"] == candidate["symbol"] and p["action"] == "buy"]
                            if existing:
                                existing[0]["target_notional"] = max(existing[0]["target_notional"], candidate["target_notional"])
                            else:
                                pending_orders.setdefault(next_trade_date, []).append(
                                    {
                                        "symbol": candidate["symbol"],
                                        "action": "buy",
                                        "reason": candidate["reason"],
                                        "target_notional": candidate["target_notional"],
                                    }
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
            "acceptance_posture": "freeze_v126q_commercial_aerospace_pruned_phase_geometry_shadow_replay_v1",
            "selected_variant": config.name,
            "initial_capital": 1_000_000.0,
            "test_date_count": len(test_dates),
            "executed_order_count": len(order_rows),
            "final_equity": round(daily_rows[-1]["equity"], 4) if daily_rows else 1_000_000.0,
            "max_drawdown": round(max((row["drawdown"] for row in daily_rows), default=0.0), 8),
            "authoritative_status": "commercial_aerospace_pruned_phase_geometry_shadow_replay_candidate",
        }
        interpretation = [
            "V1.26Q keeps V1.26O's lawful walk-forward supervised core unchanged and only prunes basket width, top-up size, and post-sell churn.",
            "This isolates whether excessive breadth and daily top-up recycling were the main reason V1.26O looked too noisy.",
        ]
        return V126QCommercialAerospacePrunedPhaseGeometryShadowReplayReport(
            summary=summary,
            daily_rows=daily_rows,
            order_rows=order_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V126QCommercialAerospacePrunedPhaseGeometryShadowReplayReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V126QCommercialAerospacePrunedPhaseGeometryShadowReplayAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v126q_commercial_aerospace_pruned_phase_geometry_shadow_replay_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
