from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import math
import os
from bisect import bisect_right

os.environ.setdefault("PANDAS_NO_USE_NUMEXPR", "1")
os.environ.setdefault("PANDAS_NO_USE_BOTTLENECK", "1")

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

from a_share_quant.strategy.v112a_price_cycle_inference_v1 import TencentKlineClient
from a_share_quant.strategy.v112am_cpo_extremely_small_core_skeleton_training_pilot_v1 import (
    V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer,
)
from a_share_quant.strategy.v112ao_cpo_role_layer_patch_pilot_v1 import (
    V112AOCPORoleLayerPatchPilotAnalyzer,
)
from a_share_quant.strategy.v112au_cpo_bounded_row_geometry_widen_pilot_v1 import (
    V112AUCPOBoundedRowGeometryWidenPilotAnalyzer,
)
from a_share_quant.strategy.v112av_cpo_branch_role_geometry_patch_pilot_v1 import (
    V112AVCPOBranchRoleGeometryPatchPilotAnalyzer,
)

@dataclass(slots=True)
class V112BLCpoRegimeAwareGatePilotReport:
    summary: dict[str, Any]
    trade_rows: list[dict[str, Any]]
    equity_curve_rows: list[dict[str, Any]]
    drawdown_curve_rows: list[dict[str, Any]]
    teacher_decision_rows: list[dict[str, Any]]
    regime_overlay_rows: list[dict[str, Any]]
    comparison_rows: list[dict[str, Any]]
    plot_bundle_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "trade_rows": self.trade_rows,
            "equity_curve_rows": self.equity_curve_rows,
            "drawdown_curve_rows": self.drawdown_curve_rows,
            "teacher_decision_rows": self.teacher_decision_rows,
            "regime_overlay_rows": self.regime_overlay_rows,
            "comparison_rows": self.comparison_rows,
            "plot_bundle_rows": self.plot_bundle_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BLCpoRegimeAwareGatePilotAnalyzer:
    HOLDING_DAYS = 20
    MIN_GATE_SAMPLES = 80
    MIN_GATE_POSITIVES = 3
    REGIME_OVERLAY_FEATURE_NAMES = [
        "broad_index_trend_state",
        "all_market_turnover_liquidity_state",
        "risk_appetite_heat_state",
        "chinext_relative_strength_state",
        "star_board_relative_strength_state",
        "ai_hardware_cross_board_resonance_state",
        "optics_sector_etf_strength_state",
        "turnover_pressure_overlay_state",
        "liquidity_dispersion_state",
        "sector_rotation_conflict_state",
    ]
    GATE_FEATURE_NAMES = [
        "ret_5",
        "ret_20",
        "price_vs_ma20",
        "price_vs_ma60",
        "volume_ratio_5_20",
        "distance_to_high60",
        "distance_to_high120",
        "cohort_sensitivity",
        "margin_sensitivity",
        "role_beta_proxy",
        "catalyst_presence_proxy",
        "listing_board_tier",
        "limit_amplitude_proxy",
        "realized_vol_10",
        "positive_day_ratio_10",
        "range_position_20",
        "drawdown_from_high20",
        "intraday_range_mean_10",
        "volume_cv_10",
        "weighted_breadth_ratio",
        "turnover_percentile_20",
        "turnover_state_numeric",
        "event_disclosure_numeric",
        "window_uncertainty_numeric",
        "confidence_tier_numeric",
        "rollforward_state_numeric",
        "branch_subchain_code",
        "branch_stage_alignment_score",
        "branch_component_depth_score",
        "branch_route_focus_score",
        "teacher_neutral_proxy_score",
        *REGIME_OVERLAY_FEATURE_NAMES,
    ]

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        oracle_benchmark_payload: dict[str, Any],
        aggressive_pilot_payload: dict[str, Any],
        neutral_pilot_payload: dict[str, Any],
        ranker_pilot_payload: dict[str, Any],
        v112bc_protocol_payload: dict[str, Any],
        v112bg_gap_review_payload: dict[str, Any],
        market_regime_overlay_payload: dict[str, Any],
        training_layer_payload: dict[str, Any],
        cycle_reconstruction_payload: dict[str, Any],
    ) -> V112BLCpoRegimeAwareGatePilotReport:
        if not bool(dict(phase_charter_payload.get("summary", {})).get("do_open_v112bl_now")):
            raise ValueError("V1.12BL must be open before the regime-aware gate pilot runs.")

        protocol_summary = dict(v112bc_protocol_payload.get("summary", {}))
        gap_summary = dict(v112bg_gap_review_payload.get("summary", {}))
        overlay_summary = dict(market_regime_overlay_payload.get("summary", {}))
        if int(protocol_summary.get("objective_track_count", 0)) != 3:
            raise ValueError("V1.12BL requires the frozen portfolio objective protocol from V1.12BC.")
        if not bool(gap_summary.get("open_neutral_selective_track_next")):
            raise ValueError("V1.12BL requires the neutral selective gap review from V1.12BG.")
        if int(overlay_summary.get("overlay_feature_count", 0)) != len(self.REGIME_OVERLAY_FEATURE_NAMES):
            raise ValueError("V1.12BL requires the frozen 10-feature market-regime overlay family.")

        oracle_summary = dict(oracle_benchmark_payload.get("summary", {}))
        aggressive_summary = dict(aggressive_pilot_payload.get("summary", {}))
        neutral_summary = dict(neutral_pilot_payload.get("summary", {}))
        ranker_summary = dict(ranker_pilot_payload.get("summary", {}))
        training_layer_rows = list(training_layer_payload.get("training_layer_rows", []))
        if len(training_layer_rows) != 10:
            raise ValueError("V1.12BL expects the frozen 10-row training-facing layer.")

        pilot_analyzer = V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer()
        widen_analyzer = V112AUCPOBoundedRowGeometryWidenPilotAnalyzer()
        role_patch = V112AOCPORoleLayerPatchPilotAnalyzer()
        branch_patch = V112AVCPOBranchRoleGeometryPatchPilotAnalyzer()
        stage_map = pilot_analyzer._stage_map(list(cycle_reconstruction_payload.get("reconstructed_stage_rows", [])))  # noqa: SLF001
        samples = widen_analyzer._build_samples(  # noqa: SLF001
            widened_rows=training_layer_rows,
            stage_map=stage_map,
            pilot_analyzer=pilot_analyzer,
        )
        samples.sort(key=lambda item: item.trade_date)
        truth_index = {str(row.get("symbol")): row for row in training_layer_rows}
        impl_features = widen_analyzer._implementation_feature_map(samples=samples, truth_index=truth_index)  # noqa: SLF001

        sample_rows: list[dict[str, Any]] = []
        for sample in samples:
            truth_row = truth_index.get(str(sample.symbol), {})
            row = {
                "trade_date": sample.trade_date,
                "symbol": sample.symbol,
                "cohort_layer": str(truth_row.get("cohort_layer", "")),
                "stage_family": sample.stage_family,
                "role_family": sample.role_family,
                "catalyst_sequence_label": sample.catalyst_sequence_label,
                "forward_return_20d": float(sample.forward_return_20d),
                "max_drawdown_20d": float(sample.max_drawdown_20d),
            }
            for name in pilot_analyzer.FEATURE_NAMES:
                row[name] = float(sample.feature_values[name])
            for name in role_patch.PATCH_FEATURE_NAMES:
                row[name] = float(sample.feature_values[name])
            for name in widen_analyzer.IMPLEMENTATION_FEATURE_NAMES:
                row[name] = float(impl_features[(sample.trade_date, sample.symbol)][name])
            branch_values = branch_patch._branch_patch_values(sample=sample)  # noqa: SLF001
            for idx, name in enumerate(branch_patch.BRANCH_PATCH_FEATURE_NAMES):
                row[name] = float(branch_values[idx])
            sample_rows.append(row)

        frame = pd.DataFrame(sample_rows).sort_values(["trade_date", "symbol"]).reset_index(drop=True)
        teacher_trade_rows = list(neutral_pilot_payload.get("trade_rows", []))
        teacher_entry_dates = {str(row.get("entry_date")) for row in teacher_trade_rows}
        teacher_entry_symbol_by_date = {str(row.get("entry_date")): str(row.get("symbol")) for row in teacher_trade_rows}

        teacher_decision_rows: list[dict[str, Any]] = []
        regime_overlay_rows: list[dict[str, Any]] = []
        ordered_dates = sorted(frame["trade_date"].unique().tolist())
        for idx, trade_date in enumerate(ordered_dates):
            if idx - self.HOLDING_DAYS < 0:
                continue
            current_frame = frame[frame["trade_date"] == trade_date].copy()
            if current_frame.empty:
                continue
            overlay_values = self._regime_overlay_values(current_frame=current_frame)
            regime_overlay_rows.append(
                {
                    "trade_date": trade_date,
                    "candidate_row_count": int(len(current_frame)),
                    **{name: round(float(overlay_values[name]), 4) for name in self.REGIME_OVERLAY_FEATURE_NAMES},
                }
            )

            current_frame = current_frame.copy()
            for name, value in overlay_values.items():
                current_frame[name] = float(value)
            current_frame["teacher_neutral_proxy_score"] = self._neutral_proxy_score(current_frame)

            teacher_symbol = teacher_entry_symbol_by_date.get(trade_date, "")
            if teacher_symbol and teacher_symbol in set(current_frame["symbol"].astype(str).tolist()):
                chosen_row = current_frame[current_frame["symbol"].astype(str) == teacher_symbol].iloc[0]
            else:
                chosen_row = current_frame.sort_values(
                    ["teacher_neutral_proxy_score", "forward_return_20d", "catalyst_presence_proxy"],
                    ascending=[False, False, False],
                ).iloc[0]

            teacher_decision_rows.append(
                self._decision_row(
                    current_row=chosen_row,
                    trade_date=trade_date,
                    teacher_enter_label=1 if trade_date in teacher_entry_dates else 0,
                    teacher_entry_symbol=teacher_symbol,
                )
            )

        decision_frame = pd.DataFrame(teacher_decision_rows).sort_values("trade_date").reset_index(drop=True)
        if decision_frame.empty:
            raise ValueError("V1.12BL requires non-empty teacher decision rows.")

        decision_dates = set(decision_frame["trade_date"].tolist())
        bar_cache = self._bar_cache(symbols=sorted(frame["symbol"].unique().tolist()))
        equity_curve_rows: list[dict[str, Any]] = []
        trade_rows: list[dict[str, Any]] = []
        current_equity = 1.0
        idx = 0

        while idx < len(ordered_dates):
            trade_date = ordered_dates[idx]
            decision_idx = idx - self.HOLDING_DAYS
            if decision_idx < 0 or trade_date not in decision_dates:
                self._append_equity_point(equity_curve_rows, trade_date, current_equity, "cash", "CASH")
                idx += 1
                continue

            cutoff_date = ordered_dates[decision_idx]
            train_gate_frame = decision_frame[decision_frame["trade_date"] <= cutoff_date].copy()
            positive_count = int(train_gate_frame["teacher_enter_label"].sum()) if not train_gate_frame.empty else 0
            if len(train_gate_frame) < self.MIN_GATE_SAMPLES or positive_count < self.MIN_GATE_POSITIVES:
                self._append_equity_point(equity_curve_rows, trade_date, current_equity, "cash", "CASH")
                idx += 1
                continue

            y_gate_train = train_gate_frame["teacher_enter_label"].to_numpy(dtype=int)
            if len(set(int(v) for v in y_gate_train)) < 2:
                self._append_equity_point(equity_curve_rows, trade_date, current_equity, "cash", "CASH")
                idx += 1
                continue

            x_gate_train = train_gate_frame[self.GATE_FEATURE_NAMES].to_numpy(dtype=float)
            gate_model = HistGradientBoostingClassifier(
                max_depth=3,
                learning_rate=0.05,
                max_iter=140,
                random_state=42,
            )
            pos_weight = len(y_gate_train) / max(positive_count, 1)
            sample_weight = np.where(y_gate_train == 1, pos_weight, 1.0)
            gate_model.fit(x_gate_train, y_gate_train, sample_weight=sample_weight)
            train_probs = gate_model.predict_proba(x_gate_train)[:, 1]
            selected_threshold = self._select_threshold(
                train_probs=train_probs,
                y_train=y_gate_train,
                floor=max(0.10, float(gap_summary.get("recommended_probability_margin_floor", 0.1845)) / 2.0),
            )

            current_row = decision_frame[decision_frame["trade_date"] == trade_date].iloc[0]
            gate_prob = float(gate_model.predict_proba(current_row[self.GATE_FEATURE_NAMES].to_frame().T.to_numpy(dtype=float))[0, 1])
            if gate_prob < selected_threshold:
                self._append_equity_point(equity_curve_rows, trade_date, current_equity, "cash", "CASH")
                idx += 1
                continue

            chosen_symbol = str(current_row["selected_symbol"])
            trade_path = self._trade_path(symbol=chosen_symbol, entry_date=trade_date, bars=bar_cache[chosen_symbol])
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
                self._append_equity_point(equity_curve_rows, str(row["trade_date"]), path_equity, "long", chosen_symbol)

            current_equity = float(equity_curve_rows[-1]["equity"])
            exit_date = str(trade_path[-1]["trade_date"])
            trade_rows.append(
                {
                    "entry_date": trade_date,
                    "exit_date": exit_date,
                    "symbol": chosen_symbol,
                    "stage_family": str(current_row["stage_family"]),
                    "role_family": str(current_row["role_family"]),
                    "catalyst_sequence_label": str(current_row["catalyst_sequence_label"]),
                    "teacher_enter_label": int(current_row["teacher_enter_label"]),
                    "teacher_entry_symbol": str(current_row["teacher_entry_symbol"]),
                    "gate_prob": round(float(gate_prob), 4),
                    "gate_threshold": round(float(selected_threshold), 4),
                    "teacher_neutral_proxy_score": round(float(current_row["teacher_neutral_proxy_score"]), 4),
                    "realized_forward_return_20d": round(current_equity / entry_equity - 1.0, 4),
                    "sample_forward_return_20d": round(float(current_row["forward_return_20d"]), 4),
                    "path_max_drawdown": round(float(max_path_drawdown), 4),
                    "entry_equity": round(entry_equity, 4),
                    "exit_equity": round(current_equity, 4),
                }
            )
            idx = self._next_index_after_exit(ordered_dates=ordered_dates, exit_date=exit_date)

        drawdown_curve_rows = self._drawdown_curve(equity_curve_rows)
        total_return = float(equity_curve_rows[-1]["equity"]) - 1.0 if equity_curve_rows else 0.0
        max_drawdown = min((float(row["drawdown"]) for row in drawdown_curve_rows), default=0.0)
        positive_sum = sum(
            float(row["realized_forward_return_20d"])
            for row in trade_rows
            if float(row["realized_forward_return_20d"]) > 0.0
        )
        negative_sum = sum(
            float(row["realized_forward_return_20d"])
            for row in trade_rows
            if float(row["realized_forward_return_20d"]) < 0.0
        )
        profit_factor = positive_sum / abs(negative_sum) if negative_sum < 0.0 else math.inf
        hit_rate = sum(1 for row in trade_rows if float(row["realized_forward_return_20d"]) > 0.0) / len(trade_rows) if trade_rows else 0.0
        cash_days = sum(1 for row in equity_curve_rows if str(row["position_state"]) == "cash")
        trade_entry_dates = {str(row["entry_date"]) for row in trade_rows}
        teacher_alignment_recall = len(trade_entry_dates & teacher_entry_dates) / len(teacher_entry_dates) if teacher_entry_dates else 0.0
        teacher_alignment_precision = len(trade_entry_dates & teacher_entry_dates) / len(trade_entry_dates) if trade_entry_dates else 0.0

        neutral_total_return = float(neutral_summary.get("total_return", 0.0))
        neutral_max_drawdown = float(neutral_summary.get("max_drawdown", 0.0))
        neutral_profit_factor = float(neutral_summary.get("profit_factor", 0.0)) if str(neutral_summary.get("profit_factor")) != "inf" else math.inf
        regime_features_add_real_incremental_value = (
            total_return > neutral_total_return
            and float(max_drawdown) >= neutral_max_drawdown
            and (profit_factor == math.inf or profit_factor >= neutral_profit_factor)
        )

        selected_thresholds = [float(row["gate_threshold"]) for row in trade_rows]
        comparison_rows = [
            {
                "comparison_name": "return_vs_neutral",
                "neutral_value": neutral_summary.get("total_return"),
                "regime_gate_value": round(total_return, 4),
                "delta": round(total_return - neutral_total_return, 4),
            },
            {
                "comparison_name": "max_drawdown_vs_neutral",
                "neutral_value": neutral_summary.get("max_drawdown"),
                "regime_gate_value": round(float(max_drawdown), 4),
                "delta": round(float(max_drawdown) - neutral_max_drawdown, 4),
            },
            {
                "comparison_name": "profit_factor_vs_neutral",
                "neutral_value": neutral_summary.get("profit_factor"),
                "regime_gate_value": round(float(profit_factor), 4) if profit_factor != math.inf else "inf",
                "delta": (
                    round(float(profit_factor) - neutral_profit_factor, 4)
                    if profit_factor != math.inf and neutral_profit_factor != math.inf
                    else "n/a"
                ),
            },
            {
                "comparison_name": "return_vs_aggressive",
                "aggressive_value": aggressive_summary.get("total_return"),
                "regime_gate_value": round(total_return, 4),
                "delta": round(total_return - float(aggressive_summary.get("total_return", 0.0)), 4),
            },
            {
                "comparison_name": "return_vs_ranker",
                "ranker_value": ranker_summary.get("total_return"),
                "regime_gate_value": round(total_return, 4),
                "delta": round(total_return - float(ranker_summary.get("total_return", 0.0)), 4),
            },
            {
                "comparison_name": "return_gap_vs_oracle",
                "oracle_value": oracle_summary.get("total_return"),
                "regime_gate_value": round(total_return, 4),
                "gap": round(float(oracle_summary.get("total_return", 0.0)) - total_return, 4),
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v112bl_cpo_regime_aware_gate_pilot_v1",
            "track_name": "regime_aware_gate_track",
            "no_leak_enforced": True,
            "training_layer_row_count": len(training_layer_rows),
            "sample_count": len(frame),
            "teacher_decision_row_count": len(decision_frame),
            "teacher_positive_row_count": int(decision_frame["teacher_enter_label"].sum()),
            "regime_overlay_feature_count": len(self.REGIME_OVERLAY_FEATURE_NAMES),
            "trade_count": len(trade_rows),
            "equity_curve_point_count": len(equity_curve_rows),
            "drawdown_curve_point_count": len(drawdown_curve_rows),
            "total_return": round(total_return, 4),
            "max_drawdown": round(float(max_drawdown), 4),
            "profit_factor": round(float(profit_factor), 4) if profit_factor != math.inf else "inf",
            "hit_rate": round(float(hit_rate), 4),
            "cash_ratio": round(float(cash_days / len(equity_curve_rows)), 4) if equity_curve_rows else 0.0,
            "teacher_alignment_recall": round(float(teacher_alignment_recall), 4),
            "teacher_alignment_precision": round(float(teacher_alignment_precision), 4),
            "regime_gate_threshold_median": round(float(np.median(selected_thresholds)), 4) if selected_thresholds else 0.0,
            "regime_gate_threshold_mean": round(float(np.mean(selected_thresholds)), 4) if selected_thresholds else 0.0,
            "neutral_return_delta": round(total_return - neutral_total_return, 4),
            "aggressive_return_delta": round(total_return - float(aggressive_summary.get("total_return", 0.0)), 4),
            "ranker_return_delta": round(total_return - float(ranker_summary.get("total_return", 0.0)), 4),
            "oracle_return_gap": round(float(oracle_summary.get("total_return", 0.0)) - total_return, 4),
            "regime_features_add_real_incremental_value": regime_features_add_real_incremental_value,
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": (
                "compare_regime_gate_vs_neutral_and_only_expand_if_real_incremental_value_is_true"
                if regime_features_add_real_incremental_value
                else "keep_regime_overlay_as_context_only_or_revisit_thresholding_before_any_further_widen"
            ),
        }
        interpretation = [
            "This line is a single-model, no-leak, regime-aware gate attempt built on the same lawful 10-row CPO layer.",
            "The regime overlay family is used explicitly as a context layer; it does not replace the CPO role and catalyst grammar.",
            "Its value is judged only by whether it improves the neutral selective line without opening formal training or signal rights.",
        ]
        return V112BLCpoRegimeAwareGatePilotReport(
            summary=summary,
            trade_rows=trade_rows,
            equity_curve_rows=equity_curve_rows,
            drawdown_curve_rows=drawdown_curve_rows,
            teacher_decision_rows=teacher_decision_rows,
            regime_overlay_rows=regime_overlay_rows,
            comparison_rows=comparison_rows,
            plot_bundle_rows=[
                {"plot_name": "regime_aware_gate_equity_curve", "series_name": "equity", "point_count": len(equity_curve_rows)},
                {"plot_name": "regime_aware_gate_drawdown_curve", "series_name": "drawdown", "point_count": len(drawdown_curve_rows)},
            ],
            interpretation=interpretation,
        )

    def _neutral_proxy_score(self, current_frame: pd.DataFrame) -> pd.Series:
        return (
            0.14 * current_frame["ret_5"].fillna(0.0)
            + 0.10 * current_frame["ret_20"].fillna(0.0)
            + 0.08 * current_frame["price_vs_ma20"].fillna(0.0)
            + 0.05 * current_frame["price_vs_ma60"].fillna(0.0)
            + 0.06 * current_frame["volume_ratio_5_20"].fillna(1.0)
            + 0.06 * current_frame["catalyst_presence_proxy"].fillna(0.0)
            + 0.05 * current_frame["weighted_breadth_ratio"].fillna(0.0)
            + 0.03 * current_frame["confidence_tier_numeric"].fillna(0.0)
            + 0.03 * current_frame["rollforward_state_numeric"].fillna(0.0)
            - 0.05 * current_frame["turnover_state_numeric"].fillna(0.0)
            - 0.04 * current_frame["window_uncertainty_numeric"].fillna(0.0)
            - 0.02 * current_frame["realized_vol_10"].fillna(0.0)
            - 0.02 * current_frame["volume_cv_10"].fillna(0.0)
        )

    def _decision_row(
        self,
        *,
        current_row: pd.Series,
        trade_date: str,
        teacher_enter_label: int,
        teacher_entry_symbol: str,
    ) -> dict[str, Any]:
        row = {
            "trade_date": trade_date,
            "selected_symbol": str(current_row["symbol"]),
            "teacher_entry_symbol": teacher_entry_symbol,
            "teacher_enter_label": int(teacher_enter_label),
            "stage_family": str(current_row["stage_family"]),
            "role_family": str(current_row["role_family"]),
            "catalyst_sequence_label": str(current_row["catalyst_sequence_label"]),
            "forward_return_20d": float(current_row["forward_return_20d"]),
            "max_drawdown_20d": float(current_row["max_drawdown_20d"]),
            "teacher_neutral_proxy_score": round(float(current_row["teacher_neutral_proxy_score"]), 6),
        }
        for name in [
            "ret_5",
            "ret_20",
            "price_vs_ma20",
            "price_vs_ma60",
            "volume_ratio_5_20",
            "distance_to_high60",
            "distance_to_high120",
            "cohort_sensitivity",
            "margin_sensitivity",
            "role_beta_proxy",
            "catalyst_presence_proxy",
            "listing_board_tier",
            "limit_amplitude_proxy",
            "realized_vol_10",
            "positive_day_ratio_10",
            "range_position_20",
            "drawdown_from_high20",
            "intraday_range_mean_10",
            "volume_cv_10",
            "weighted_breadth_ratio",
            "turnover_percentile_20",
            "turnover_state_numeric",
            "event_disclosure_numeric",
            "window_uncertainty_numeric",
            "confidence_tier_numeric",
            "rollforward_state_numeric",
            "branch_subchain_code",
            "branch_stage_alignment_score",
            "branch_component_depth_score",
            "branch_route_focus_score",
        ]:
            row[name] = float(current_row[name])
        for name in self.REGIME_OVERLAY_FEATURE_NAMES:
            row[name] = float(current_row[name])
        return row

    def _regime_overlay_values(self, *, current_frame: pd.DataFrame) -> dict[str, float]:
        frame = current_frame.copy()
        frame["ret_20"] = frame["ret_20"].fillna(0.0)
        frame["ret_5"] = frame["ret_5"].fillna(0.0)
        frame["volume_ratio_5_20"] = frame["volume_ratio_5_20"].fillna(1.0)
        overall_mean_ret20 = float(frame["ret_20"].mean()) if not frame.empty else 0.0
        overall_mean_turnover = float(frame["volume_ratio_5_20"].mean()) if not frame.empty else 0.0
        overall_liquidity_std = float(frame["volume_ratio_5_20"].std(ddof=0)) if len(frame) > 1 else 0.0
        broad_index_trend_state = overall_mean_ret20
        all_market_turnover_liquidity_state = overall_mean_turnover
        risk_appetite_heat_state = float(frame["ret_5"].gt(0.0).mean()) if not frame.empty else 0.0

        chinext_mask = frame["symbol"].astype(str).str.startswith(("300", "301"))
        star_mask = frame["symbol"].astype(str).str.startswith("688")
        chinext_mean = float(frame.loc[chinext_mask, "ret_20"].mean()) if bool(chinext_mask.any()) else overall_mean_ret20
        star_mean = float(frame.loc[star_mask, "ret_20"].mean()) if bool(star_mask.any()) else overall_mean_ret20
        chinext_relative_strength_state = chinext_mean - overall_mean_ret20
        star_board_relative_strength_state = star_mean - overall_mean_ret20
        sector_rotation_conflict_state = abs(chinext_relative_strength_state - star_board_relative_strength_state)

        core_mask = frame["cohort_layer"].isin(
            {"core_anchor", "core_beta", "core_platform_confirmation", "adjacent_bridge", "adjacent_high_beta_extension"}
        )
        branch_mask = frame["cohort_layer"].isin({"branch_extension"})
        core_mean = float(frame.loc[core_mask, "ret_20"].mean()) if bool(core_mask.any()) else overall_mean_ret20
        branch_mean = float(frame.loc[branch_mask, "ret_20"].mean()) if bool(branch_mask.any()) else overall_mean_ret20
        ai_hardware_cross_board_resonance_state = core_mean - branch_mean
        optics_sector_etf_strength_state = core_mean - overall_mean_ret20

        turnover_pressure_overlay_state = 0.0
        if overall_mean_turnover >= 1.35:
            turnover_pressure_overlay_state = 3.0
        elif overall_mean_turnover >= 1.12:
            turnover_pressure_overlay_state = 2.0
        elif overall_mean_turnover >= 0.92:
            turnover_pressure_overlay_state = 1.0

        return {
            "broad_index_trend_state": broad_index_trend_state,
            "all_market_turnover_liquidity_state": all_market_turnover_liquidity_state,
            "risk_appetite_heat_state": risk_appetite_heat_state,
            "chinext_relative_strength_state": chinext_relative_strength_state,
            "star_board_relative_strength_state": star_board_relative_strength_state,
            "ai_hardware_cross_board_resonance_state": ai_hardware_cross_board_resonance_state,
            "optics_sector_etf_strength_state": optics_sector_etf_strength_state,
            "turnover_pressure_overlay_state": turnover_pressure_overlay_state,
            "liquidity_dispersion_state": overall_liquidity_std,
            "sector_rotation_conflict_state": sector_rotation_conflict_state,
        }

    def _select_threshold(self, *, train_probs: np.ndarray, y_train: np.ndarray, floor: float) -> float:
        candidate_thresholds = np.unique(
            np.concatenate(
                [
                    np.linspace(max(0.05, floor / 2.0), 0.95, 37),
                    np.quantile(train_probs, np.linspace(0.05, 0.95, 19)),
                ]
            )
        )
        positive_count = int(np.sum(y_train))
        negative_count = int(len(y_train) - positive_count)
        best_threshold = float(max(0.05, floor / 2.0))
        best_score = -1.0
        for threshold in candidate_thresholds:
            preds = train_probs >= float(threshold)
            pred_positive_count = int(np.sum(preds))
            if pred_positive_count == 0:
                continue
            tp = int(np.sum(preds & (y_train == 1)))
            fp = pred_positive_count - tp
            tn = negative_count - fp
            precision = tp / pred_positive_count if pred_positive_count else 0.0
            recall = tp / positive_count if positive_count else 0.0
            tnr = tn / negative_count if negative_count else 0.0
            score = 0.45 * recall + 0.35 * precision + 0.20 * tnr
            if score > best_score:
                best_score = score
                best_threshold = float(threshold)
        return float(max(best_threshold, max(0.05, floor / 2.0)))

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

    def _next_index_after_exit(self, *, ordered_dates: list[str], exit_date: str) -> int:
        return bisect_right(ordered_dates, exit_date)


def write_v112bl_cpo_regime_aware_gate_pilot_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BLCpoRegimeAwareGatePilotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
