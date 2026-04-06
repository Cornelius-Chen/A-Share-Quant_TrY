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
from a_share_quant.strategy.v126a_commercial_aerospace_regime_conditioned_label_table_v1 import (
    V126ACommercialAerospaceRegimeConditionedLabelTableAnalyzer,
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
class V126ICommercialAerospaceTwoLayerShadowReplayReport:
    summary: dict[str, Any]
    variant_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "variant_rows": self.variant_rows,
            "interpretation": self.interpretation,
        }


class V126ICommercialAerospaceTwoLayerShadowReplayAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.daily_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"

    def _split_rows(self, rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        ordered_dates = sorted({row["trade_date"] for row in rows})
        split_idx = max(1, round(len(ordered_dates) * 0.8))
        train_dates = set(ordered_dates[:split_idx])
        return [row for row in rows if row["trade_date"] in train_dates], [row for row in rows if row["trade_date"] not in train_dates]

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
        positives = [row for row in train_rows if row["supervised_action_label_rc"] in positive_labels]
        negatives = [row for row in train_rows if row["supervised_action_label_rc"] not in positive_labels]
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

    def _run_variant(
        self,
        *,
        scored_rows: list[dict[str, Any]],
        daily_map: dict[tuple[str, str], dict[str, str]],
        test_dates: list[str],
        next_trade_date_map: dict[str, str],
        probe_threshold: float,
        full_threshold: float,
        probe_notional: float,
        full_notional: float,
        de_risk_threshold: float,
    ) -> dict[str, Any]:
        cash = 1_000_000.0
        positions: dict[str, int] = {}
        peak_equity = 1_000_000.0
        pending_orders: dict[str, list[dict[str, Any]]] = {}
        lot_size = 100
        order_count = 0

        by_date: dict[str, list[dict[str, Any]]] = {}
        for row in scored_rows:
            by_date.setdefault(row["trade_date"], []).append(row)

        daily_rows: list[dict[str, Any]] = []
        for trade_date in test_dates:
            for order in pending_orders.pop(trade_date, []):
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
                    order_count += 1
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
                    order_count += 1

            for row in by_date.get(trade_date, []):
                next_trade_date = next_trade_date_map.get(trade_date)
                if not next_trade_date:
                    continue
                if row["regime_proxy_semantic"] == "impulse_expansion_proxy" and row["event_state"] == "continuation_active":
                    target_notional = 0.0
                    if row["eligibility_score"] <= full_threshold:
                        target_notional = full_notional
                    elif row["eligibility_score"] <= probe_threshold:
                        target_notional = probe_notional
                    if target_notional > 0:
                        existing = [p for p in pending_orders.get(next_trade_date, []) if p["symbol"] == row["symbol"] and p["action"] == "buy"]
                        if existing:
                            existing[0]["target_notional"] = max(existing[0]["target_notional"], target_notional)
                        else:
                            pending_orders.setdefault(next_trade_date, []).append(
                                {"symbol": row["symbol"], "action": "buy", "target_notional": target_notional}
                            )
                if (
                    row["regime_proxy_semantic"] in {"risk_off_deterioration_proxy", "sentiment_overdrive_transition_proxy"}
                    and row["de_risk_score"] <= de_risk_threshold
                    and row["symbol"] in positions
                    and all(p["symbol"] != row["symbol"] or p["action"] != "sell" for p in pending_orders.get(next_trade_date, []))
                ):
                    pending_orders.setdefault(next_trade_date, []).append(
                        {"symbol": row["symbol"], "action": "sell", "sell_ratio": 0.5}
                    )

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
            "executed_order_count": order_count,
            "final_equity": round(daily_rows[-1]["equity"], 4) if daily_rows else 1_000_000.0,
            "max_drawdown": round(max((row["drawdown"] for row in daily_rows), default=0.0), 8),
        }

    def analyze(self) -> V126ICommercialAerospaceTwoLayerShadowReplayReport:
        table = V126ACommercialAerospaceRegimeConditionedLabelTableAnalyzer(self.repo_root).analyze()
        rows = table.training_rows
        train_rows, test_rows = self._split_rows(rows)
        train_rows_z, test_rows_z = self._standardize(train_rows, test_rows)
        eligibility_train_scores = self._score_rows(train_rows_z, train_rows_z, {"probe_eligibility_target", "full_eligibility_target"})
        de_risk_train_scores = self._score_rows(train_rows_z, train_rows_z, {"de_risk_target"})
        eligibility_test_scores = self._score_rows(train_rows_z, test_rows_z, {"probe_eligibility_target", "full_eligibility_target"})
        de_risk_test_scores = self._score_rows(train_rows_z, test_rows_z, {"de_risk_target"})

        impulse_train_scores = [
            score for row, score in zip(train_rows_z, eligibility_train_scores, strict=False)
            if row["regime_proxy_semantic"] == "impulse_expansion_proxy" and row["event_state"] == "continuation_active"
        ]
        risk_train_scores = [
            score for row, score in zip(train_rows_z, de_risk_train_scores, strict=False)
            if row["regime_proxy_semantic"] in {"risk_off_deterioration_proxy", "sentiment_overdrive_transition_proxy"}
        ]
        de_risk_threshold = _quantile(risk_train_scores, 0.8)

        scored_rows: list[dict[str, Any]] = []
        for row, es, ds in zip(test_rows_z, eligibility_test_scores, de_risk_test_scores, strict=False):
            enriched = dict(row)
            enriched["eligibility_score"] = es
            enriched["de_risk_score"] = ds
            scored_rows.append(enriched)
        scored_rows.sort(key=lambda row: (row["trade_date"], row["symbol"]))

        daily_bars = _load_csv(self.daily_path)
        daily_map = {(row["symbol"], row["trade_date"]): row for row in daily_bars}
        test_dates = sorted({row["trade_date"] for row in scored_rows})
        next_trade_date_map = {test_dates[idx]: test_dates[idx + 1] for idx in range(len(test_dates) - 1)}

        variants = [
            ("probe50_full100_q80_q60", 0.80, 0.60, 50_000.0, 100_000.0),
            ("probe50_full100_q80_q40", 0.80, 0.40, 50_000.0, 100_000.0),
            ("probe40_full100_q70_q40", 0.70, 0.40, 40_000.0, 100_000.0),
        ]
        variant_rows: list[dict[str, Any]] = []
        for variant_name, probe_q, full_q, probe_notional, full_notional in variants:
            probe_threshold = _quantile(impulse_train_scores, probe_q)
            full_threshold = _quantile(impulse_train_scores, full_q)
            replay = self._run_variant(
                scored_rows=scored_rows,
                daily_map=daily_map,
                test_dates=test_dates,
                next_trade_date_map=next_trade_date_map,
                probe_threshold=probe_threshold,
                full_threshold=full_threshold,
                probe_notional=probe_notional,
                full_notional=full_notional,
                de_risk_threshold=de_risk_threshold,
            )
            variant_rows.append(
                {
                    "variant_name": variant_name,
                    "probe_threshold_quantile": probe_q,
                    "full_threshold_quantile": full_q,
                    "probe_notional": probe_notional,
                    "full_notional": full_notional,
                    "probe_threshold": round(probe_threshold, 8),
                    "full_threshold": round(full_threshold, 8),
                    **replay,
                }
            )

        best_variant = max(variant_rows, key=lambda row: row["final_equity"])
        summary = {
            "acceptance_posture": "freeze_v126i_commercial_aerospace_two_layer_shadow_replay_v1",
            "initial_capital": 1_000_000.0,
            "variant_count": len(variant_rows),
            "best_variant_name": best_variant["variant_name"],
            "best_final_equity": best_variant["final_equity"],
            "best_max_drawdown": best_variant["max_drawdown"],
            "authoritative_status": "commercial_aerospace_two_layer_shadow_replay_non_promotable_audit",
        }
        interpretation = [
            "V1.26I tests whether probe/full score stratification improves economics versus the first regime-local shadow replay.",
            "This remains a shadow audit because the full layer is score-stratified rather than learned from impulse-train full labels.",
        ]
        return V126ICommercialAerospaceTwoLayerShadowReplayReport(summary=summary, variant_rows=variant_rows, interpretation=interpretation)


def write_report(*, reports_dir: Path, report_name: str, result: V126ICommercialAerospaceTwoLayerShadowReplayReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V126ICommercialAerospaceTwoLayerShadowReplayAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v126i_commercial_aerospace_two_layer_shadow_replay_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
