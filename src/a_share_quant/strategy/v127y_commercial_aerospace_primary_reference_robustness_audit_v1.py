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
from a_share_quant.strategy.v127m_commercial_aerospace_phase_conditioned_drag_veto_audit_v1 import (
    _VetoPolicy,
    V127MCommercialAerospacePhaseConditionedDragVetoAuditAnalyzer,
)


WINDOW_START = "20260112"
WINDOW_END = "20260212"


@dataclass(slots=True)
class _VariantConfig:
    name: str
    riskoff_sell_ratio: float
    weakdrift_sell_ratio: float
    include_impulse_derisk: bool
    impulse_sell_ratio: float


@dataclass(slots=True)
class V127YCommercialAerospacePrimaryReferenceRobustnessAuditReport:
    summary: dict[str, Any]
    split_rows: list[dict[str, Any]]
    suffix_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "split_rows": self.split_rows,
            "suffix_rows": self.suffix_rows,
            "interpretation": self.interpretation,
        }


class V127YCommercialAerospacePrimaryReferenceRobustnessAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.helper = V127GCommercialAerospacePrimaryReferenceAttributionAnalyzer(repo_root)
        self.policy_analyzer = V127MCommercialAerospacePhaseConditionedDragVetoAuditAnalyzer(repo_root)
        self.daily_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
        self.old_variant = _VariantConfig("veto_drag_trio_impulse_only", 0.5, 0.5, False, 0.5)
        self.new_variant = _VariantConfig("window_riskoff_full_weakdrift_075_impulse_half", 1.0, 0.75, True, 0.5)

    def _prepare_rows(self) -> tuple[list[dict[str, Any]], list[str]]:
        label_table = V126MCommercialAerospacePhaseGeometryLabelTableAnalyzer(self.repo_root).analyze()
        all_rows = label_table.training_rows
        drag_trio = set(self.policy_analyzer._drag_symbols()[:3])
        veto_policy = _VetoPolicy("veto_drag_trio_impulse_only", set(), set(), drag_trio)
        filtered_rows = [row for row in all_rows if not self.policy_analyzer._blocked(row, veto_policy)]
        ordered_dates = sorted({row["trade_date"] for row in filtered_rows})
        return filtered_rows, ordered_dates

    def _safe_score_rows(
        self,
        train_rows: list[dict[str, Any]],
        eval_rows: list[dict[str, Any]],
        positive_labels: set[str],
    ) -> tuple[list[float], bool]:
        positive_count = sum(1 for row in train_rows if row["supervised_action_label_pg"] in positive_labels)
        negative_count = len(train_rows) - positive_count
        if positive_count == 0 or negative_count == 0:
            return [float("inf")] * len(eval_rows), False
        return self.helper._score_rows(train_rows, eval_rows, positive_labels), True

    def _simulate_variant(
        self,
        *,
        rows: list[dict[str, Any]],
        ordered_dates: list[str],
        test_dates: list[str],
        config: _VariantConfig,
    ) -> dict[str, Any]:
        base = self.helper._load_base_config()
        replay_config = _ReplayConfig(
            name=config.name,
            preheat_cap=int(base["preheat_cap"]),
            impulse_cap=int(base["impulse_cap"]),
            cooldown_days_after_sell=int(base["cooldown_days_after_sell"]),
            min_increment_notional=float(base["min_increment_notional"]),
            preheat_full_target_notional=70_000.0,
            family="broad_half_reference",
            sell_ratio=0.5,
        )

        by_date: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            by_date.setdefault(row["trade_date"], []).append(row)
        date_to_idx = {trade_date: idx for idx, trade_date in enumerate(ordered_dates)}
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
                    train_rows_z, eval_rows_z = self.helper._standardize(available_rows, eval_rows)
                    eligibility_train_scores, eligibility_supported = self._safe_score_rows(
                        train_rows_z,
                        train_rows_z,
                        {"probe_eligibility_target", "full_eligibility_target"},
                    )
                    de_risk_train_scores, derisk_supported = self._safe_score_rows(train_rows_z, train_rows_z, {"de_risk_target"})
                    eligibility_eval_scores, _ = self._safe_score_rows(
                        train_rows_z,
                        eval_rows_z,
                        {"probe_eligibility_target", "full_eligibility_target"},
                    )
                    de_risk_eval_scores, _ = self._safe_score_rows(train_rows_z, eval_rows_z, {"de_risk_target"})

                    preheat_full_scores = [
                        score
                        for row, score in zip(train_rows_z, eligibility_train_scores, strict=False)
                        if row["phase_window_semantic"] == "preheat_window" and row["supervised_action_label_pg"] == "full_eligibility_target"
                    ] if eligibility_supported else []
                    preheat_probe_scores = [
                        score
                        for row, score in zip(train_rows_z, eligibility_train_scores, strict=False)
                        if row["phase_window_semantic"] == "preheat_window" and row["supervised_action_label_pg"] in {"probe_eligibility_target", "full_eligibility_target"}
                    ] if eligibility_supported else []
                    impulse_full_scores = [
                        score
                        for row, score in zip(train_rows_z, eligibility_train_scores, strict=False)
                        if row["phase_window_semantic"] == "impulse_window" and row["supervised_action_label_pg"] == "full_eligibility_target"
                    ] if eligibility_supported else []
                    impulse_probe_scores = [
                        score
                        for row, score in zip(train_rows_z, eligibility_train_scores, strict=False)
                        if row["phase_window_semantic"] == "impulse_window" and row["supervised_action_label_pg"] in {"probe_eligibility_target", "full_eligibility_target"}
                    ] if eligibility_supported else []
                    risk_scores = [
                        score
                        for row, score in zip(train_rows_z, de_risk_train_scores, strict=False)
                        if row["regime_proxy_semantic"] in {"risk_off_deterioration_proxy", "sentiment_overdrive_transition_proxy", "weak_drift_chop_proxy"}
                    ] if derisk_supported else []
                    impulse_derisk_scores = [
                        score
                        for row, score in zip(train_rows_z, de_risk_train_scores, strict=False)
                        if row["phase_window_semantic"] == "impulse_window" and row["supervised_action_label_pg"] == "de_risk_target"
                    ] if derisk_supported else []
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
                            in_window = WINDOW_START <= trade_date <= WINDOW_END
                            if (
                                row["regime_proxy_semantic"] in {"risk_off_deterioration_proxy", "sentiment_overdrive_transition_proxy", "weak_drift_chop_proxy"}
                                and ds <= de_risk_threshold
                                and symbol in positions
                                and all(p["symbol"] != symbol or p["action"] != "sell" for p in pending_orders.get(next_trade_date, []))
                            ):
                                sell_ratio = 0.5
                                if in_window and row["regime_proxy_semantic"] == "risk_off_deterioration_proxy":
                                    sell_ratio = config.riskoff_sell_ratio
                                elif in_window and row["regime_proxy_semantic"] == "weak_drift_chop_proxy":
                                    sell_ratio = config.weakdrift_sell_ratio
                                risk_candidates.append(
                                    {
                                        "symbol": symbol,
                                        "sell_ratio": sell_ratio,
                                        "reason": f"window_derisk_{row['regime_proxy_semantic']}",
                                    }
                                )
                            if (
                                config.include_impulse_derisk
                                and in_window
                                and row["phase_window_semantic"] == "impulse_window"
                                and row["supervised_action_label_pg"] == "de_risk_target"
                                and ds <= impulse_derisk_threshold
                                and symbol in positions
                                and all(p["symbol"] != symbol or p["action"] != "sell" for p in pending_orders.get(next_trade_date, []))
                            ):
                                risk_candidates.append(
                                    {
                                        "symbol": symbol,
                                        "sell_ratio": config.impulse_sell_ratio,
                                        "reason": "window_derisk_impulse_target",
                                    }
                                )
                            cooldown_anchor = last_sell_idx_by_symbol.get(symbol)
                            if cooldown_anchor is not None and current_idx - cooldown_anchor < replay_config.cooldown_days_after_sell:
                                continue
                            if row["phase_window_semantic"] == "preheat_window":
                                if preheat_full_scores and es <= preheat_full_threshold:
                                    preheat_candidates.append({"symbol": symbol, "score": es, "target_notional": replay_config.preheat_full_target_notional, "reason": "phase_geometry_preheat_full"})
                                elif es <= preheat_probe_threshold:
                                    preheat_candidates.append({"symbol": symbol, "score": es, "target_notional": 40_000.0, "reason": "phase_geometry_preheat_probe"})
                            elif row["phase_window_semantic"] == "impulse_window":
                                if impulse_full_scores and es <= impulse_full_threshold:
                                    impulse_candidates.append({"symbol": symbol, "score": es, "target_notional": 100_000.0, "reason": "phase_geometry_impulse_full"})
                                elif es <= impulse_probe_threshold:
                                    impulse_candidates.append({"symbol": symbol, "score": es, "target_notional": 40_000.0, "reason": "phase_geometry_impulse_probe"})

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
                                }
                            )

                        preheat_candidates = sorted(preheat_candidates, key=lambda item: (item["score"], item["symbol"]))[: replay_config.preheat_cap]
                        impulse_candidates = sorted(impulse_candidates, key=lambda item: (item["score"], item["symbol"]))[: replay_config.impulse_cap]
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
            for symbol, quantity in positions.items():
                bar = daily_map.get((symbol, trade_date))
                if bar:
                    market_value += quantity * float(bar["close"])
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
                }
            )

        return {
            "variant": config.name,
            "final_equity": round(daily_rows[-1]["equity"], 4) if daily_rows else 1_000_000.0,
            "max_drawdown": round(max((row["drawdown"] for row in daily_rows), default=0.0), 8),
            "executed_order_count": len(order_rows),
            "test_day_count": len(test_dates),
            "daily_rows": daily_rows,
            "order_rows": order_rows,
        }

    @staticmethod
    def _frontier_win(new_row: dict[str, Any], old_row: dict[str, Any]) -> bool:
        return (
            new_row["final_equity"] >= old_row["final_equity"]
            and new_row["max_drawdown"] <= old_row["max_drawdown"]
            and new_row["executed_order_count"] <= old_row["executed_order_count"]
        )

    def analyze(self) -> V127YCommercialAerospacePrimaryReferenceRobustnessAuditReport:
        rows, ordered_dates = self._prepare_rows()

        split_rows: list[dict[str, Any]] = []
        for split_fraction in (0.70, 0.75, 0.80, 0.85):
            split_idx = max(1, round(len(ordered_dates) * split_fraction))
            test_dates = ordered_dates[split_idx:]
            old_payload = self._simulate_variant(rows=rows, ordered_dates=ordered_dates, test_dates=test_dates, config=self.old_variant)
            new_payload = self._simulate_variant(rows=rows, ordered_dates=ordered_dates, test_dates=test_dates, config=self.new_variant)
            split_rows.append(
                {
                    "split_fraction": split_fraction,
                    "test_start": test_dates[0],
                    "test_end": test_dates[-1],
                    "test_day_count": len(test_dates),
                    "old_final_equity": old_payload["final_equity"],
                    "old_max_drawdown": old_payload["max_drawdown"],
                    "old_executed_order_count": old_payload["executed_order_count"],
                    "new_final_equity": new_payload["final_equity"],
                    "new_max_drawdown": new_payload["max_drawdown"],
                    "new_executed_order_count": new_payload["executed_order_count"],
                    "equity_delta_new_minus_old": round(new_payload["final_equity"] - old_payload["final_equity"], 4),
                    "drawdown_delta_new_minus_old": round(new_payload["max_drawdown"] - old_payload["max_drawdown"], 8),
                    "frontier_win": self._frontier_win(new_payload, old_payload),
                }
            )

        default_split_idx = max(1, round(len(ordered_dates) * 0.80))
        base_test_dates = ordered_dates[default_split_idx:]
        suffix_rows: list[dict[str, Any]] = []
        for label, fraction in (
            ("full_test", 0.00),
            ("q25_suffix", 0.25),
            ("q50_suffix", 0.50),
            ("q75_suffix", 0.75),
        ):
            start_idx = min(len(base_test_dates) - 1, round((len(base_test_dates) - 1) * fraction))
            suffix_dates = base_test_dates[start_idx:]
            old_payload = self._simulate_variant(rows=rows, ordered_dates=ordered_dates, test_dates=suffix_dates, config=self.old_variant)
            new_payload = self._simulate_variant(rows=rows, ordered_dates=ordered_dates, test_dates=suffix_dates, config=self.new_variant)
            suffix_rows.append(
                {
                    "suffix_label": label,
                    "suffix_start": suffix_dates[0],
                    "suffix_end": suffix_dates[-1],
                    "test_day_count": len(suffix_dates),
                    "old_final_equity": old_payload["final_equity"],
                    "old_max_drawdown": old_payload["max_drawdown"],
                    "old_executed_order_count": old_payload["executed_order_count"],
                    "new_final_equity": new_payload["final_equity"],
                    "new_max_drawdown": new_payload["max_drawdown"],
                    "new_executed_order_count": new_payload["executed_order_count"],
                    "equity_delta_new_minus_old": round(new_payload["final_equity"] - old_payload["final_equity"], 4),
                    "drawdown_delta_new_minus_old": round(new_payload["max_drawdown"] - old_payload["max_drawdown"], 8),
                    "frontier_win": self._frontier_win(new_payload, old_payload),
                }
            )

        split_frontier_wins = sum(1 for row in split_rows if row["frontier_win"])
        suffix_frontier_wins = sum(1 for row in suffix_rows if row["frontier_win"])
        summary = {
            "acceptance_posture": "freeze_v127y_commercial_aerospace_primary_reference_robustness_audit_v1",
            "old_primary_variant": self.old_variant.name,
            "new_primary_variant": self.new_variant.name,
            "split_frontier_wins": split_frontier_wins,
            "split_total": len(split_rows),
            "suffix_frontier_wins": suffix_frontier_wins,
            "suffix_total": len(suffix_rows),
            "worst_split_equity_delta_new_minus_old": min(row["equity_delta_new_minus_old"] for row in split_rows),
            "worst_split_drawdown_delta_new_minus_old": max(row["drawdown_delta_new_minus_old"] for row in split_rows),
            "worst_suffix_equity_delta_new_minus_old": min(row["equity_delta_new_minus_old"] for row in suffix_rows),
            "worst_suffix_drawdown_delta_new_minus_old": max(row["drawdown_delta_new_minus_old"] for row in suffix_rows),
            "authoritative_status": (
                "robust_enough_to_keep_current_primary"
                if split_frontier_wins >= 3 and suffix_frontier_wins >= 3
                else "needs_subagent_review_before_freeze"
            ),
        }
        interpretation = [
            "V1.27Y stress-tests the current commercial-aerospace primary reference against the prior primary under alternate chronology splits and suffix-anchored replay windows.",
            "The audit is intentionally lawfully replay-bound: it keeps the same EOD/T+1 execution semantics and only changes chronology geometry.",
        ]
        return V127YCommercialAerospacePrimaryReferenceRobustnessAuditReport(
            summary=summary,
            split_rows=split_rows,
            suffix_rows=suffix_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V127YCommercialAerospacePrimaryReferenceRobustnessAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V127YCommercialAerospacePrimaryReferenceRobustnessAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v127y_commercial_aerospace_primary_reference_robustness_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
