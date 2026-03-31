from __future__ import annotations

import json
import math
import os
from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path
from typing import Any

os.environ.setdefault("PANDAS_NO_USE_NUMEXPR", "1")
os.environ.setdefault("PANDAS_NO_USE_BOTTLENECK", "1")

import pandas as pd

from a_share_quant.strategy.v112a_price_cycle_inference_v1 import TencentKlineClient
from a_share_quant.strategy.v112bp_cpo_selector_maturity_fusion_pilot_v1 import (
    V112BPCpoSelectorMaturityFusionPilotAnalyzer,
)


@dataclass(slots=True)
class V112BQCPOGatePrecisionSweepReport:
    summary: dict[str, Any]
    sweep_candidate_rows: list[dict[str, Any]]
    stable_band_rows: list[dict[str, Any]]
    acceptance_profile_rows: list[dict[str, Any]]
    decision_rows: list[dict[str, Any]]
    trade_rows: list[dict[str, Any]]
    equity_curve_rows: list[dict[str, Any]]
    drawdown_curve_rows: list[dict[str, Any]]
    comparison_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "sweep_candidate_rows": self.sweep_candidate_rows,
            "stable_band_rows": self.stable_band_rows,
            "acceptance_profile_rows": self.acceptance_profile_rows,
            "decision_rows": self.decision_rows,
            "trade_rows": self.trade_rows,
            "equity_curve_rows": self.equity_curve_rows,
            "drawdown_curve_rows": self.drawdown_curve_rows,
            "comparison_rows": self.comparison_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BQCPOGatePrecisionSweepAnalyzer:
    HOLDING_DAYS = 20
    FULL_PERCENTILE_LADDER = (0.20, 0.35, 0.50, 0.65, 0.80)
    COARSE_INDEXES = (1, 2, 3)
    STABLE_SCORE_GAP = 0.03
    PARAMETER_SPECS = (
        ("min_ranker_score", "ranker_score", "min"),
        ("min_maturity_balance_score", "maturity_balance_score", "min"),
        ("min_regime_support_score", "regime_support_score", "min"),
        ("max_internal_turnover_concentration_state", "internal_turnover_concentration_state", "max"),
        ("max_spillover_saturation_overlay_state", "spillover_saturation_overlay_state", "max"),
        ("max_turnover_pressure_overlay_state", "turnover_pressure_overlay_state", "max"),
    )

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        fusion_pilot_payload: dict[str, Any],
        neutral_pilot_payload: dict[str, Any],
        teacher_decomposition_payload: dict[str, Any],
        gap_review_payload: dict[str, Any],
        internal_maturity_payload: dict[str, Any],
        regime_gate_payload: dict[str, Any],
        training_layer_payload: dict[str, Any],
        cycle_reconstruction_payload: dict[str, Any],
    ) -> V112BQCPOGatePrecisionSweepReport:
        if not bool(dict(phase_charter_payload.get("summary", {})).get("do_open_v112bq_now")):
            raise ValueError("V1.12BQ must be open before the gate precision sweep runs.")

        fusion_summary = dict(fusion_pilot_payload.get("summary", {}))
        neutral_summary = dict(neutral_pilot_payload.get("summary", {}))
        teacher_summary = dict(teacher_decomposition_payload.get("summary", {}))
        internal_summary = dict(internal_maturity_payload.get("summary", {}))
        regime_summary = dict(regime_gate_payload.get("summary", {}))
        if not bool(fusion_summary.get("ready_for_phase_check_next")):
            raise ValueError("V1.12BQ requires the completed fusion pilot.")
        if int(internal_summary.get("overlay_feature_count", 0)) != 8:
            raise ValueError("V1.12BQ requires the frozen internal maturity overlay family.")
        if int(regime_summary.get("regime_overlay_feature_count", 0)) != 10:
            raise ValueError("V1.12BQ requires the frozen market regime overlay family.")
        if not bool(teacher_summary.get("all_non_cash_failed_proven")):
            raise ValueError("V1.12BQ expects the teacher decomposition negative result to be explicit.")

        training_layer_rows = list(training_layer_payload.get("training_layer_rows", []))
        if len(training_layer_rows) != 10:
            raise ValueError("V1.12BQ expects the frozen 10-row training layer.")

        recommendations = {
            str(row.get("recommendation_name")): row for row in list(gap_review_payload.get("recommendation_rows", []))
        }
        base_gate = {
            "confidence_floor": float(recommendations["minimum_confidence_tier_numeric"]["recommended_value"]),
            "rollforward_floor": float(recommendations["minimum_rollforward_state_numeric"]["recommended_value"]),
            "turnover_cap": float(recommendations["maximum_turnover_state_numeric"]["recommended_value"]),
            "breadth_floor": float(recommendations["minimum_weighted_breadth_ratio"]["recommended_value"]),
            "catalyst_floor": float(recommendations["minimum_catalyst_presence_proxy"]["recommended_value"]),
        }

        bp_analyzer = V112BPCpoSelectorMaturityFusionPilotAnalyzer()
        feature_frame = bp_analyzer._build_feature_frame(  # noqa: SLF001
            training_layer_rows=training_layer_rows,
            cycle_reconstruction_payload=cycle_reconstruction_payload,
        )
        decision_frame = self._build_decision_frame(
            feature_frame=feature_frame,
            fusion_gate_payload=fusion_pilot_payload,
        )
        base_candidate_frame = decision_frame[
            decision_frame.apply(lambda row: self._passes_base_gate(row, base_gate), axis=1)
        ].copy()
        if base_candidate_frame.empty:
            raise ValueError("V1.12BQ base gate produced zero candidate rows.")

        all_dates = sorted(feature_frame["trade_date"].astype(str).unique().tolist())
        bar_cache = self._bar_cache(symbols=sorted(decision_frame["symbol"].astype(str).unique().tolist()))
        decision_map = {str(row["trade_date"]): row for row in decision_frame.to_dict(orient="records")}
        base_negative_rows = base_candidate_frame[base_candidate_frame["forward_return_20d"] < 0.0]
        base_positive_rows = base_candidate_frame[base_candidate_frame["forward_return_20d"] > 0.0]
        base_negative_abs_sum = float(base_negative_rows["forward_return_20d"].abs().sum())

        ladders = self._parameter_ladders(base_candidate_frame)
        coarse_candidates = self._run_sweep(
            decision_map=decision_map,
            all_dates=all_dates,
            bar_cache=bar_cache,
            base_gate=base_gate,
            candidate_grid=self._coarse_grid(ladders),
            fusion_summary=fusion_summary,
            neutral_summary=neutral_summary,
            base_candidate_frame=base_candidate_frame,
            base_negative_rows=base_negative_rows,
            base_positive_rows=base_positive_rows,
            base_negative_abs_sum=base_negative_abs_sum,
            search_stage="coarse",
        )
        best_coarse = max(coarse_candidates, key=lambda row: float(row["objective_score"]))
        refined_candidates = self._run_sweep(
            decision_map=decision_map,
            all_dates=all_dates,
            bar_cache=bar_cache,
            base_gate=base_gate,
            candidate_grid=self._refined_grid(ladders=ladders, anchor_candidate=best_coarse),
            fusion_summary=fusion_summary,
            neutral_summary=neutral_summary,
            base_candidate_frame=base_candidate_frame,
            base_negative_rows=base_negative_rows,
            base_positive_rows=base_positive_rows,
            base_negative_abs_sum=base_negative_abs_sum,
            search_stage="refined",
        )

        deduped_candidates = {
            str(row["candidate_signature"]): row for row in coarse_candidates + refined_candidates
        }
        candidate_rows = sorted(
            deduped_candidates.values(),
            key=lambda row: (float(row["objective_score"]), float(row["total_return"])),
            reverse=True,
        )
        best_candidate = candidate_rows[0]
        best_simulation = self._simulate_candidate(
            decision_map=decision_map,
            all_dates=all_dates,
            bar_cache=bar_cache,
            base_gate=base_gate,
            candidate=best_candidate,
        )

        stable_band_rows = self._stable_band_rows(candidate_rows)
        acceptance_profile_rows = self._acceptance_profile_rows(
            decision_rows=decision_frame,
            base_gate=base_gate,
            candidate=best_candidate,
        )
        public_decision_rows = self._public_decision_rows(
            decision_frame=decision_frame,
            base_gate=base_gate,
            candidate=best_candidate,
        )
        summary = self._summary(
            fusion_summary=fusion_summary,
            neutral_summary=neutral_summary,
            teacher_summary=teacher_summary,
            base_candidate_frame=base_candidate_frame,
            coarse_candidates=coarse_candidates,
            refined_candidates=refined_candidates,
            candidate_rows=candidate_rows,
            best_candidate=best_candidate,
            stable_band_rows=stable_band_rows,
        )
        comparison_rows = self._comparison_rows(
            fusion_summary=fusion_summary,
            neutral_summary=neutral_summary,
            best_candidate=best_candidate,
        )
        interpretation = [
            "V1.12BQ treats the fusion selector as fixed alpha backbone and sweeps gate precision on top of it.",
            "Teacher decomposition remains a condition finder only; its all-cash failure is used as a guard against naive rule worship.",
            "The purpose of this phase is to find stable threshold bands, not a single magic hyperparameter point.",
        ]
        return V112BQCPOGatePrecisionSweepReport(
            summary=summary,
            sweep_candidate_rows=candidate_rows[:40],
            stable_band_rows=stable_band_rows,
            acceptance_profile_rows=acceptance_profile_rows,
            decision_rows=public_decision_rows,
            trade_rows=best_simulation["trade_rows"],
            equity_curve_rows=best_simulation["equity_curve_rows"],
            drawdown_curve_rows=best_simulation["drawdown_curve_rows"],
            comparison_rows=comparison_rows,
            interpretation=interpretation,
        )

    def _build_decision_frame(
        self,
        *,
        feature_frame: pd.DataFrame,
        fusion_gate_payload: dict[str, Any],
    ) -> pd.DataFrame:
        gate_rows = pd.DataFrame(list(fusion_gate_payload.get("gate_decision_rows", [])))
        if gate_rows.empty:
            raise ValueError("V1.12BQ requires the fusion gate decision rows from V1.12BP.")
        merge_cols = [
            "trade_date",
            "symbol",
            "stage_family",
            "role_family",
            "catalyst_sequence_label",
            "forward_return_20d",
            "max_drawdown_20d",
        ]
        merged = gate_rows.merge(feature_frame[merge_cols], on=["trade_date", "symbol"], how="left")
        merged["regime_bucket"] = merged["regime_support_score"].apply(self._regime_bucket)
        merged["maturity_bucket"] = merged["maturity_balance_score"].apply(self._maturity_bucket)
        return merged.sort_values("trade_date").reset_index(drop=True)

    def _parameter_ladders(self, frame: pd.DataFrame) -> dict[str, list[float]]:
        ladders: dict[str, list[float]] = {}
        for param_name, column_name, _mode in self.PARAMETER_SPECS:
            quantiles = [round(float(frame[column_name].quantile(q)), 6) for q in self.FULL_PERCENTILE_LADDER]
            values: list[float] = []
            for value in quantiles:
                if not values or abs(values[-1] - value) > 1e-9:
                    values.append(value)
            if len(values) == 1:
                values = [values[0] - 1e-6, values[0], values[0] + 1e-6]
            ladders[param_name] = values
        return ladders

    def _coarse_grid(self, ladders: dict[str, list[float]]) -> list[dict[str, Any]]:
        coarse_lists = {
            name: [values[idx] for idx in self.COARSE_INDEXES if idx < len(values)] or values
            for name, values in ladders.items()
        }
        rows: list[dict[str, Any]] = []
        for min_ranker_score in coarse_lists["min_ranker_score"]:
            for min_maturity_balance_score in coarse_lists["min_maturity_balance_score"]:
                for min_regime_support_score in coarse_lists["min_regime_support_score"]:
                    for max_internal_turnover in coarse_lists["max_internal_turnover_concentration_state"]:
                        for max_spillover in coarse_lists["max_spillover_saturation_overlay_state"]:
                            for max_turnover_pressure in coarse_lists["max_turnover_pressure_overlay_state"]:
                                rows.append(
                                    {
                                        "min_ranker_score": min_ranker_score,
                                        "min_maturity_balance_score": min_maturity_balance_score,
                                        "min_regime_support_score": min_regime_support_score,
                                        "max_internal_turnover_concentration_state": max_internal_turnover,
                                        "max_spillover_saturation_overlay_state": max_spillover,
                                        "max_turnover_pressure_overlay_state": max_turnover_pressure,
                                    }
                                )
        return rows

    def _refined_grid(
        self,
        *,
        ladders: dict[str, list[float]],
        anchor_candidate: dict[str, Any],
    ) -> list[dict[str, Any]]:
        local_lists: dict[str, list[float]] = {}
        for param_name, _column_name, _mode in self.PARAMETER_SPECS:
            values = ladders[param_name]
            anchor_value = float(anchor_candidate[param_name])
            nearest_idx = min(range(len(values)), key=lambda idx: abs(values[idx] - anchor_value))
            idxs = sorted({max(0, nearest_idx - 1), nearest_idx, min(len(values) - 1, nearest_idx + 1)})
            local_lists[param_name] = [values[idx] for idx in idxs]
        rows: list[dict[str, Any]] = []
        for min_ranker_score in local_lists["min_ranker_score"]:
            for min_maturity_balance_score in local_lists["min_maturity_balance_score"]:
                for min_regime_support_score in local_lists["min_regime_support_score"]:
                    for max_internal_turnover in local_lists["max_internal_turnover_concentration_state"]:
                        for max_spillover in local_lists["max_spillover_saturation_overlay_state"]:
                            for max_turnover_pressure in local_lists["max_turnover_pressure_overlay_state"]:
                                rows.append(
                                    {
                                        "min_ranker_score": min_ranker_score,
                                        "min_maturity_balance_score": min_maturity_balance_score,
                                        "min_regime_support_score": min_regime_support_score,
                                        "max_internal_turnover_concentration_state": max_internal_turnover,
                                        "max_spillover_saturation_overlay_state": max_spillover,
                                        "max_turnover_pressure_overlay_state": max_turnover_pressure,
                                    }
                                )
        return rows

    def _run_sweep(
        self,
        *,
        decision_map: dict[str, dict[str, Any]],
        all_dates: list[str],
        bar_cache: dict[str, pd.DataFrame],
        base_gate: dict[str, float],
        candidate_grid: list[dict[str, Any]],
        fusion_summary: dict[str, Any],
        neutral_summary: dict[str, Any],
        base_candidate_frame: pd.DataFrame,
        base_negative_rows: pd.DataFrame,
        base_positive_rows: pd.DataFrame,
        base_negative_abs_sum: float,
        search_stage: str,
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for candidate in candidate_grid:
            evaluation = self._evaluate_candidate(
                decision_map=decision_map,
                all_dates=all_dates,
                bar_cache=bar_cache,
                base_gate=base_gate,
                candidate={**candidate, "search_stage": search_stage},
                fusion_summary=fusion_summary,
                neutral_summary=neutral_summary,
                base_candidate_frame=base_candidate_frame,
                base_negative_rows=base_negative_rows,
                base_positive_rows=base_positive_rows,
                base_negative_abs_sum=base_negative_abs_sum,
            )
            rows.append(evaluation)
        return rows

    def _evaluate_candidate(
        self,
        *,
        decision_map: dict[str, dict[str, Any]],
        all_dates: list[str],
        bar_cache: dict[str, pd.DataFrame],
        base_gate: dict[str, float],
        candidate: dict[str, Any],
        fusion_summary: dict[str, Any],
        neutral_summary: dict[str, Any],
        base_candidate_frame: pd.DataFrame,
        base_negative_rows: pd.DataFrame,
        base_positive_rows: pd.DataFrame,
        base_negative_abs_sum: float,
    ) -> dict[str, Any]:
        simulation = self._simulate_candidate(
            decision_map=decision_map,
            all_dates=all_dates,
            bar_cache=bar_cache,
            base_gate=base_gate,
            candidate=candidate,
        )
        accepted_dates = {str(row["entry_date"]) for row in simulation["trade_rows"]}
        skipped_frame = base_candidate_frame[~base_candidate_frame["trade_date"].astype(str).isin(accepted_dates)]
        kept_positive = base_positive_rows[base_positive_rows["trade_date"].astype(str).isin(accepted_dates)]
        skipped_negative = base_negative_rows[~base_negative_rows["trade_date"].astype(str).isin(accepted_dates)]

        bad_trade_suppression = float(len(skipped_negative) / len(base_negative_rows)) if len(base_negative_rows) else 0.0
        good_trade_retention = float(len(kept_positive) / len(base_positive_rows)) if len(base_positive_rows) else 0.0
        veto_precision = float(len(skipped_negative) / len(skipped_frame)) if len(skipped_frame) else 0.0
        drawdown_contributor_removal = (
            float(skipped_negative["forward_return_20d"].abs().sum() / base_negative_abs_sum)
            if base_negative_abs_sum > 0.0
            else 0.0
        )

        total_return = float(simulation["summary"]["total_return"])
        max_drawdown = float(simulation["summary"]["max_drawdown"])
        fusion_return = float(fusion_summary.get("total_return", 0.0))
        neutral_trade_count = int(neutral_summary.get("trade_count", 0))
        return_retention = max(0.0, total_return / fusion_return) if fusion_return > 0.0 else 0.0
        fusion_drawdown = abs(float(fusion_summary.get("max_drawdown", 0.0)))
        drawdown_compression = (
            (fusion_drawdown - abs(max_drawdown)) / fusion_drawdown if fusion_drawdown > 0.0 else 0.0
        )
        action_similarity = (
            1.0 - min(abs(int(simulation["summary"]["trade_count"]) - neutral_trade_count) / max(neutral_trade_count, 1), 1.0)
            if neutral_trade_count > 0
            else 0.0
        )
        objective_score = (
            -1.0
            if int(simulation["summary"]["trade_count"]) == 0
            else (
                0.28 * return_retention
                + 0.22 * drawdown_compression
                + 0.18 * bad_trade_suppression
                + 0.12 * good_trade_retention
                + 0.10 * veto_precision
                + 0.10 * action_similarity
            )
        )

        return {
            **candidate,
            "candidate_signature": self._candidate_signature(candidate),
            "trade_count": int(simulation["summary"]["trade_count"]),
            "total_return": round(total_return, 4),
            "max_drawdown": round(max_drawdown, 4),
            "profit_factor": simulation["summary"]["profit_factor"],
            "hit_rate": round(float(simulation["summary"]["hit_rate"]), 4),
            "cash_ratio": round(float(simulation["summary"]["cash_ratio"]), 4),
            "bad_trade_suppression_rate": round(bad_trade_suppression, 4),
            "good_trade_retention_rate": round(good_trade_retention, 4),
            "veto_precision": round(veto_precision, 4),
            "drawdown_contributor_removal": round(drawdown_contributor_removal, 4),
            "fusion_return_delta": round(total_return - fusion_return, 4),
            "neutral_return_delta": round(total_return - float(neutral_summary.get("total_return", 0.0)), 4),
            "neutral_drawdown_delta": round(max_drawdown - float(neutral_summary.get("max_drawdown", 0.0)), 4),
            "objective_score": round(objective_score, 4),
        }

    def _simulate_candidate(
        self,
        *,
        decision_map: dict[str, dict[str, Any]],
        all_dates: list[str],
        bar_cache: dict[str, pd.DataFrame],
        base_gate: dict[str, float],
        candidate: dict[str, Any],
    ) -> dict[str, Any]:
        equity_curve_rows: list[dict[str, Any]] = []
        trade_rows: list[dict[str, Any]] = []
        current_equity = 1.0
        idx = 0
        while idx < len(all_dates):
            trade_date = all_dates[idx]
            decision_row = decision_map.get(trade_date)
            if decision_row is None:
                self._append_equity_point(equity_curve_rows, trade_date, current_equity, "cash", "CASH")
                idx += 1
                continue
            if not self._passes_base_gate(decision_row, base_gate) or not self._passes_candidate_gate(decision_row, candidate):
                self._append_equity_point(equity_curve_rows, trade_date, current_equity, "cash", "CASH")
                idx += 1
                continue

            trade_path = self._trade_path(
                symbol=str(decision_row["symbol"]),
                entry_date=trade_date,
                bars=bar_cache[str(decision_row["symbol"])],
            )
            if not trade_path:
                self._append_equity_point(equity_curve_rows, trade_date, current_equity, "cash", "CASH")
                idx += 1
                continue

            entry_equity = current_equity
            path_peak = entry_equity
            max_path_drawdown = 0.0
            for row in trade_path:
                path_equity = entry_equity * float(row["price_ratio"])
                path_peak = max(path_peak, path_equity)
                if path_peak > 0.0:
                    max_path_drawdown = min(max_path_drawdown, path_equity / path_peak - 1.0)
                self._append_equity_point(
                    equity_curve_rows,
                    str(row["trade_date"]),
                    path_equity,
                    "long",
                    str(decision_row["symbol"]),
                )

            current_equity = float(equity_curve_rows[-1]["equity"])
            exit_date = str(trade_path[-1]["trade_date"])
            trade_rows.append(
                {
                    "entry_date": trade_date,
                    "exit_date": exit_date,
                    "symbol": str(decision_row["symbol"]),
                    "stage_family": str(decision_row["stage_family"]),
                    "role_family": str(decision_row["role_family"]),
                    "catalyst_sequence_label": str(decision_row["catalyst_sequence_label"]),
                    "realized_forward_return_20d": round(current_equity / entry_equity - 1.0, 4),
                    "path_max_drawdown": round(float(max_path_drawdown), 4),
                }
            )
            idx = bisect_right(all_dates, exit_date)

        drawdown_curve_rows = self._drawdown_curve(equity_curve_rows)
        total_return = float(equity_curve_rows[-1]["equity"]) - 1.0 if equity_curve_rows else 0.0
        max_drawdown = min((float(row["drawdown"]) for row in drawdown_curve_rows), default=0.0)
        positive_sum = sum(float(row["realized_forward_return_20d"]) for row in trade_rows if float(row["realized_forward_return_20d"]) > 0.0)
        negative_sum = sum(float(row["realized_forward_return_20d"]) for row in trade_rows if float(row["realized_forward_return_20d"]) < 0.0)
        profit_factor = positive_sum / abs(negative_sum) if negative_sum < 0.0 else math.inf
        hit_rate = sum(1 for row in trade_rows if float(row["realized_forward_return_20d"]) > 0.0) / len(trade_rows) if trade_rows else 0.0
        cash_days = sum(1 for row in equity_curve_rows if str(row["position_state"]) == "cash")
        return {
            "trade_rows": trade_rows,
            "equity_curve_rows": equity_curve_rows,
            "drawdown_curve_rows": drawdown_curve_rows,
            "summary": {
                "trade_count": len(trade_rows),
                "total_return": round(total_return, 4),
                "max_drawdown": round(max_drawdown, 4),
                "profit_factor": round(float(profit_factor), 4) if profit_factor != math.inf else "inf",
                "hit_rate": round(hit_rate, 4),
                "cash_ratio": round(float(cash_days / len(equity_curve_rows)), 4) if equity_curve_rows else 0.0,
            },
        }

    def _passes_base_gate(self, row: pd.Series | dict[str, Any], base_gate: dict[str, float]) -> bool:
        return (
            float(row["confidence_tier_numeric"]) >= base_gate["confidence_floor"]
            and float(row["rollforward_state_numeric"]) >= base_gate["rollforward_floor"]
            and float(row["turnover_state_numeric"]) <= base_gate["turnover_cap"]
            and float(row["weighted_breadth_ratio"]) >= base_gate["breadth_floor"]
            and float(row["catalyst_presence_proxy"]) >= base_gate["catalyst_floor"]
        )

    def _passes_candidate_gate(self, row: pd.Series | dict[str, Any], candidate: dict[str, Any]) -> bool:
        return (
            float(row["ranker_score"]) >= float(candidate["min_ranker_score"])
            and float(row["maturity_balance_score"]) >= float(candidate["min_maturity_balance_score"])
            and float(row["regime_support_score"]) >= float(candidate["min_regime_support_score"])
            and float(row["internal_turnover_concentration_state"]) <= float(candidate["max_internal_turnover_concentration_state"])
            and float(row["spillover_saturation_overlay_state"]) <= float(candidate["max_spillover_saturation_overlay_state"])
            and float(row["turnover_pressure_overlay_state"]) <= float(candidate["max_turnover_pressure_overlay_state"])
        )

    def _stable_band_rows(self, candidate_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        best_score = float(candidate_rows[0]["objective_score"])
        stable = [
            row
            for row in candidate_rows
            if float(row["objective_score"]) >= best_score - self.STABLE_SCORE_GAP and int(row["trade_count"]) > 0
        ]
        rows: list[dict[str, Any]] = []
        for param_name, _column_name, _mode in self.PARAMETER_SPECS:
            values = [float(row[param_name]) for row in stable]
            rows.append(
                {
                    "parameter_name": param_name,
                    "stable_candidate_count": len(stable),
                    "min_value": round(min(values), 6),
                    "max_value": round(max(values), 6),
                }
            )
        return rows

    def _acceptance_profile_rows(
        self,
        *,
        decision_rows: pd.DataFrame,
        base_gate: dict[str, float],
        candidate: dict[str, Any],
    ) -> list[dict[str, Any]]:
        frame = decision_rows.copy()
        frame["base_gate_open"] = frame.apply(lambda row: self._passes_base_gate(row, base_gate), axis=1)
        frame["candidate_open"] = frame.apply(
            lambda row: self._passes_base_gate(row, base_gate) and self._passes_candidate_gate(row, candidate), axis=1
        )
        rows: list[dict[str, Any]] = []
        for stage_family, group in frame.groupby("stage_family"):
            rows.append(
                {
                    "profile_axis": "stage_family",
                    "profile_value": str(stage_family),
                    "decision_row_count": int(len(group)),
                    "base_gate_open_rate": round(float(group["base_gate_open"].mean()), 4),
                    "candidate_open_rate": round(float(group["candidate_open"].mean()), 4),
                }
            )
        for regime_bucket, group in frame.groupby("regime_bucket"):
            rows.append(
                {
                    "profile_axis": "regime_bucket",
                    "profile_value": str(regime_bucket),
                    "decision_row_count": int(len(group)),
                    "base_gate_open_rate": round(float(group["base_gate_open"].mean()), 4),
                    "candidate_open_rate": round(float(group["candidate_open"].mean()), 4),
                }
            )
        return rows

    def _public_decision_rows(
        self,
        *,
        decision_frame: pd.DataFrame,
        base_gate: dict[str, float],
        candidate: dict[str, Any],
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for row in decision_frame.to_dict(orient="records"):
            base_open = self._passes_base_gate(row, base_gate)
            rows.append(
                {
                    "trade_date": str(row["trade_date"]),
                    "symbol": str(row["symbol"]),
                    "stage_family": str(row["stage_family"]),
                    "role_family": str(row["role_family"]),
                    "catalyst_sequence_label": str(row["catalyst_sequence_label"]),
                    "ranker_score": round(float(row["ranker_score"]), 4),
                    "maturity_balance_score": round(float(row["maturity_balance_score"]), 4),
                    "regime_support_score": round(float(row["regime_support_score"]), 4),
                    "base_gate_open": bool(base_open),
                    "candidate_gate_open": bool(base_open and self._passes_candidate_gate(row, candidate)),
                }
            )
        return rows

    def _summary(
        self,
        *,
        fusion_summary: dict[str, Any],
        neutral_summary: dict[str, Any],
        teacher_summary: dict[str, Any],
        base_candidate_frame: pd.DataFrame,
        coarse_candidates: list[dict[str, Any]],
        refined_candidates: list[dict[str, Any]],
        candidate_rows: list[dict[str, Any]],
        best_candidate: dict[str, Any],
        stable_band_rows: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return {
            "acceptance_posture": "freeze_v112bq_cpo_gate_precision_sweep_v1",
            "track_name": "gate_precision_sweep_track",
            "no_leak_enforced": True,
            "base_candidate_row_count": int(len(base_candidate_frame)),
            "coarse_candidate_count": len(coarse_candidates),
            "refined_candidate_count": len(refined_candidates),
            "total_candidate_count": len(candidate_rows),
            "best_candidate_signature": str(best_candidate["candidate_signature"]),
            "best_candidate_stage": str(best_candidate["search_stage"]),
            "best_trade_count": int(best_candidate["trade_count"]),
            "best_total_return": float(best_candidate["total_return"]),
            "best_max_drawdown": float(best_candidate["max_drawdown"]),
            "best_profit_factor": best_candidate["profit_factor"],
            "best_bad_trade_suppression_rate": float(best_candidate["bad_trade_suppression_rate"]),
            "best_good_trade_retention_rate": float(best_candidate["good_trade_retention_rate"]),
            "best_veto_precision": float(best_candidate["veto_precision"]),
            "best_drawdown_contributor_removal": float(best_candidate["drawdown_contributor_removal"]),
            "best_objective_score": float(best_candidate["objective_score"]),
            "stable_band_parameter_count": len(stable_band_rows),
            "fusion_return_delta": round(float(best_candidate["total_return"]) - float(fusion_summary.get("total_return", 0.0)), 4),
            "neutral_return_delta": round(float(best_candidate["total_return"]) - float(neutral_summary.get("total_return", 0.0)), 4),
            "neutral_drawdown_delta": round(float(best_candidate["max_drawdown"]) - float(neutral_summary.get("max_drawdown", 0.0)), 4),
            "teacher_all_non_cash_failed_proven": bool(teacher_summary.get("all_non_cash_failed_proven")),
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": (
                "promote_best_gate_stack_to_selector_gate_follow_up"
                if float(best_candidate["objective_score"]) > 0.6
                else "keep_gate_precision_as_candidate_rule_discovery_only"
            ),
        }

    def _comparison_rows(
        self,
        *,
        fusion_summary: dict[str, Any],
        neutral_summary: dict[str, Any],
        best_candidate: dict[str, Any],
    ) -> list[dict[str, Any]]:
        return [
            {
                "comparison_name": "return_vs_fusion",
                "fusion_value": fusion_summary.get("total_return"),
                "best_gate_value": best_candidate["total_return"],
                "delta": round(float(best_candidate["total_return"]) - float(fusion_summary.get("total_return", 0.0)), 4),
            },
            {
                "comparison_name": "max_drawdown_vs_fusion",
                "fusion_value": fusion_summary.get("max_drawdown"),
                "best_gate_value": best_candidate["max_drawdown"],
                "delta": round(float(best_candidate["max_drawdown"]) - float(fusion_summary.get("max_drawdown", 0.0)), 4),
            },
            {
                "comparison_name": "return_vs_neutral",
                "neutral_value": neutral_summary.get("total_return"),
                "best_gate_value": best_candidate["total_return"],
                "delta": round(float(best_candidate["total_return"]) - float(neutral_summary.get("total_return", 0.0)), 4),
            },
            {
                "comparison_name": "max_drawdown_vs_neutral",
                "neutral_value": neutral_summary.get("max_drawdown"),
                "best_gate_value": best_candidate["max_drawdown"],
                "delta": round(float(best_candidate["max_drawdown"]) - float(neutral_summary.get("max_drawdown", 0.0)), 4),
            },
        ]

    def _regime_bucket(self, value: float) -> str:
        if float(value) >= 0.08:
            return "supportive"
        if float(value) <= -0.08:
            return "risk_off"
        return "mixed"

    def _maturity_bucket(self, value: float) -> str:
        if float(value) >= -0.1:
            return "constructive"
        if float(value) <= -0.3:
            return "crowded_or_late"
        return "transitional"

    def _candidate_signature(self, candidate: dict[str, Any]) -> str:
        return "|".join(
            [
                f"ranker>={float(candidate['min_ranker_score']):.4f}",
                f"maturity>={float(candidate['min_maturity_balance_score']):.4f}",
                f"regime>={float(candidate['min_regime_support_score']):.4f}",
                f"turnover<={float(candidate['max_internal_turnover_concentration_state']):.4f}",
                f"spillover<={float(candidate['max_spillover_saturation_overlay_state']):.4f}",
                f"pressure<={float(candidate['max_turnover_pressure_overlay_state']):.4f}",
            ]
        )

    def _bar_cache(self, *, symbols: list[str]) -> dict[str, pd.DataFrame]:
        client = TencentKlineClient()
        cache: dict[str, pd.DataFrame] = {}
        for symbol in symbols:
            frame = client.fetch_daily_bars(symbol).sort_values("date").reset_index(drop=True).copy()
            frame["trade_date"] = pd.to_datetime(frame["date"]).dt.strftime("%Y-%m-%d")
            cache[symbol] = frame
        return cache

    def _trade_path(self, *, symbol: str, entry_date: str, bars: pd.DataFrame) -> list[dict[str, Any]]:
        matching = bars.index[bars["trade_date"] == entry_date].tolist()
        if not matching:
            return []
        start_idx = int(matching[0])
        end_idx = start_idx + self.HOLDING_DAYS
        if end_idx >= len(bars):
            return []
        entry_close = float(bars.iloc[start_idx]["close"])
        if entry_close == 0.0:
            return []
        rows: list[dict[str, Any]] = []
        for idx in range(start_idx, end_idx + 1):
            close = float(bars.iloc[idx]["close"])
            rows.append({"trade_date": str(bars.iloc[idx]["trade_date"]), "price_ratio": close / entry_close})
        return rows

    def _append_equity_point(
        self,
        equity_curve_rows: list[dict[str, Any]],
        trade_date: str,
        equity: float,
        position_state: str,
        symbol: str,
    ) -> None:
        row = {
            "trade_date": trade_date,
            "equity": round(float(equity), 6),
            "position_state": position_state,
            "symbol": symbol,
        }
        if equity_curve_rows and str(equity_curve_rows[-1]["trade_date"]) == trade_date:
            equity_curve_rows[-1] = row
        else:
            equity_curve_rows.append(row)

    def _drawdown_curve(self, equity_curve_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        peak = 0.0
        rows: list[dict[str, Any]] = []
        for row in equity_curve_rows:
            equity = float(row["equity"])
            peak = max(peak, equity)
            drawdown = equity / peak - 1.0 if peak > 0.0 else 0.0
            rows.append({"trade_date": str(row["trade_date"]), "drawdown": round(float(drawdown), 6)})
        return rows


def write_v112bq_cpo_gate_precision_sweep_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BQCPOGatePrecisionSweepReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
