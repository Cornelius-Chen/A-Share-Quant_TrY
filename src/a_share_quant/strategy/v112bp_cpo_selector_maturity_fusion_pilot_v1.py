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

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestRegressor

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
from a_share_quant.strategy.v112bl_cpo_regime_aware_gate_pilot_v1 import (
    V112BLCpoRegimeAwareGatePilotAnalyzer,
)


@dataclass(slots=True)
class V112BPCpoSelectorMaturityFusionPilotReport:
    summary: dict[str, Any]
    trade_rows: list[dict[str, Any]]
    equity_curve_rows: list[dict[str, Any]]
    drawdown_curve_rows: list[dict[str, Any]]
    gate_decision_rows: list[dict[str, Any]]
    comparison_rows: list[dict[str, Any]]
    plot_bundle_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "trade_rows": self.trade_rows,
            "equity_curve_rows": self.equity_curve_rows,
            "drawdown_curve_rows": self.drawdown_curve_rows,
            "gate_decision_rows": self.gate_decision_rows,
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


class V112BPCpoSelectorMaturityFusionPilotAnalyzer:
    HOLDING_DAYS = 20
    MIN_SELECTOR_SAMPLES = 120
    MIN_GATE_SAMPLES = 80
    MIN_GATE_POSITIVES = 3

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        oracle_benchmark_payload: dict[str, Any],
        aggressive_pilot_payload: dict[str, Any],
        neutral_pilot_payload: dict[str, Any],
        ranker_search_payload: dict[str, Any],
        market_overlay_payload: dict[str, Any],
        internal_maturity_payload: dict[str, Any],
        training_layer_payload: dict[str, Any],
        cycle_reconstruction_payload: dict[str, Any],
    ) -> V112BPCpoSelectorMaturityFusionPilotReport:
        if not bool(dict(phase_charter_payload.get("summary", {})).get("do_open_v112bp_now")):
            raise ValueError("V1.12BP must be open before the fusion pilot runs.")

        oracle_summary = dict(oracle_benchmark_payload.get("summary", {}))
        aggressive_summary = dict(aggressive_pilot_payload.get("summary", {}))
        neutral_summary = dict(neutral_pilot_payload.get("summary", {}))
        ranker_summary = dict(ranker_search_payload.get("summary", {}))
        market_overlay_summary = dict(market_overlay_payload.get("summary", {}))
        internal_summary = dict(internal_maturity_payload.get("summary", {}))
        if int(market_overlay_summary.get("overlay_feature_count", 0)) <= 0:
            raise ValueError("V1.12BP requires the frozen market overlay family.")
        if int(internal_summary.get("overlay_feature_count", 0)) != 8:
            raise ValueError("V1.12BP requires the frozen internal maturity overlay family.")

        training_layer_rows = list(training_layer_payload.get("training_layer_rows", []))
        if len(training_layer_rows) != 10:
            raise ValueError("V1.12BP expects the frozen 10-row training layer.")

        frame = self._build_feature_frame(
            training_layer_rows=training_layer_rows,
            cycle_reconstruction_payload=cycle_reconstruction_payload,
        )
        ordered_dates = sorted(frame["trade_date"].unique().tolist())
        teacher_entry_dates = {
            str(row.get("entry_date"))
            for row in list(neutral_pilot_payload.get("trade_rows", []))
        }

        bar_cache = self._bar_cache(symbols=sorted(frame["symbol"].unique().tolist()))
        equity_curve_rows: list[dict[str, Any]] = []
        trade_rows: list[dict[str, Any]] = []
        gate_decision_rows: list[dict[str, Any]] = []
        current_equity = 1.0
        idx = 0

        while idx < len(ordered_dates):
            trade_date = ordered_dates[idx]
            decision_idx = idx - self.HOLDING_DAYS
            if decision_idx < 0:
                self._append_equity_point(equity_curve_rows, trade_date, current_equity, "cash", "CASH")
                idx += 1
                continue

            cutoff_date = ordered_dates[decision_idx]
            train_frame = frame[frame["trade_date"] <= cutoff_date]
            if len(train_frame) < self.MIN_SELECTOR_SAMPLES:
                self._append_equity_point(equity_curve_rows, trade_date, current_equity, "cash", "CASH")
                idx += 1
                continue

            selector = RandomForestRegressor(
                n_estimators=120,
                max_depth=5,
                min_samples_leaf=2,
                max_features="sqrt",
                random_state=42,
                n_jobs=1,
            )
            selector.fit(
                train_frame[self._selector_feature_names()].to_numpy(dtype=float),
                train_frame["forward_return_20d"].to_numpy(dtype=float),
            )

            current_frame = frame[frame["trade_date"] == trade_date].copy()
            if current_frame.empty:
                self._append_equity_point(equity_curve_rows, trade_date, current_equity, "cash", "CASH")
                idx += 1
                continue

            current_frame["predicted_return_20d"] = selector.predict(
                current_frame[self._selector_feature_names()].to_numpy(dtype=float)
            )
            current_frame["ranker_score"] = (
                current_frame["predicted_return_20d"]
                + 0.04 * current_frame["weighted_breadth_ratio"]
                + 0.03 * current_frame["catalyst_presence_proxy"]
                + 0.02 * current_frame["confidence_tier_numeric"]
                - 0.02 * current_frame["turnover_state_numeric"]
                - 0.02 * current_frame["window_uncertainty_numeric"]
            )
            current_frame["maturity_balance_score"] = current_frame.apply(self._maturity_balance_score, axis=1)
            current_frame["regime_support_score"] = current_frame.apply(self._regime_support_score, axis=1)
            chosen_row = current_frame.sort_values(
                ["ranker_score", "predicted_return_20d", "forward_return_20d"],
                ascending=[False, False, False],
            ).iloc[0]

            gate_row = self._gate_row(
                chosen_row=chosen_row,
                teacher_enter_label=1 if trade_date in teacher_entry_dates else 0,
            )
            prior_gate_frame = pd.DataFrame(gate_decision_rows)
            gate_prob = 0.0
            gate_threshold = 1.0
            gate_open = False
            if len(prior_gate_frame) >= self.MIN_GATE_SAMPLES and int(prior_gate_frame["teacher_enter_label"].sum()) >= self.MIN_GATE_POSITIVES:
                gate_model = HistGradientBoostingClassifier(
                    max_depth=3,
                    learning_rate=0.05,
                    max_iter=140,
                    random_state=42,
                )
                x_gate_train = prior_gate_frame[self._gate_feature_names()].to_numpy(dtype=float)
                y_gate_train = prior_gate_frame["teacher_enter_label"].to_numpy(dtype=int)
                positive_count = int(y_gate_train.sum())
                sample_weight = np.where(y_gate_train == 1, len(y_gate_train) / max(positive_count, 1), 1.0)
                gate_model.fit(x_gate_train, y_gate_train, sample_weight=sample_weight)
                train_probs = gate_model.predict_proba(x_gate_train)[:, 1]
                gate_threshold = self._select_threshold(train_probs=train_probs, y_train=y_gate_train)
                gate_prob = float(
                    gate_model.predict_proba(
                        pd.DataFrame([gate_row])[self._gate_feature_names()].to_numpy(dtype=float)
                    )[0, 1]
                )
                gate_open = gate_prob >= gate_threshold

            gate_row["gate_prob"] = round(gate_prob, 4)
            gate_row["gate_threshold"] = round(gate_threshold, 4)
            gate_row["gate_open"] = bool(gate_open)
            gate_decision_rows.append(gate_row)

            if not gate_open:
                self._append_equity_point(equity_curve_rows, trade_date, current_equity, "cash", "CASH")
                idx += 1
                continue

            trade_path = self._trade_path(
                symbol=str(chosen_row["symbol"]),
                entry_date=str(chosen_row["trade_date"]),
                bars=bar_cache[str(chosen_row["symbol"])],
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
                self._append_equity_point(equity_curve_rows, str(row["trade_date"]), path_equity, "long", str(chosen_row["symbol"]))

            current_equity = float(equity_curve_rows[-1]["equity"])
            exit_date = str(trade_path[-1]["trade_date"])
            trade_rows.append(
                {
                    "entry_date": str(chosen_row["trade_date"]),
                    "exit_date": exit_date,
                    "symbol": str(chosen_row["symbol"]),
                    "stage_family": str(chosen_row["stage_family"]),
                    "role_family": str(chosen_row["role_family"]),
                    "catalyst_sequence_label": str(chosen_row["catalyst_sequence_label"]),
                    "predicted_return_20d": round(float(chosen_row["predicted_return_20d"]), 4),
                    "ranker_score": round(float(chosen_row["ranker_score"]), 4),
                    "gate_prob": round(gate_prob, 4),
                    "gate_threshold": round(gate_threshold, 4),
                    "maturity_balance_score": round(float(chosen_row["maturity_balance_score"]), 4),
                    "regime_support_score": round(float(chosen_row["regime_support_score"]), 4),
                    "realized_forward_return_20d": round(current_equity / entry_equity - 1.0, 4),
                    "sample_forward_return_20d": round(float(chosen_row["forward_return_20d"]), 4),
                    "path_max_drawdown": round(float(max_path_drawdown), 4),
                    "entry_equity": round(entry_equity, 4),
                    "exit_equity": round(current_equity, 4),
                }
            )
            idx = self._next_index_after_exit(ordered_dates=ordered_dates, exit_date=exit_date)

        return self._finalize_report(
            oracle_summary=oracle_summary,
            aggressive_summary=aggressive_summary,
            neutral_summary=neutral_summary,
            ranker_summary=ranker_summary,
            training_layer_rows=training_layer_rows,
            equity_curve_rows=equity_curve_rows,
            trade_rows=trade_rows,
            gate_decision_rows=gate_decision_rows,
        )

    def _finalize_report(
        self,
        *,
        oracle_summary: dict[str, Any],
        aggressive_summary: dict[str, Any],
        neutral_summary: dict[str, Any],
        ranker_summary: dict[str, Any],
        training_layer_rows: list[dict[str, Any]],
        equity_curve_rows: list[dict[str, Any]],
        trade_rows: list[dict[str, Any]],
        gate_decision_rows: list[dict[str, Any]],
    ) -> V112BPCpoSelectorMaturityFusionPilotReport:
        drawdown_curve_rows = self._drawdown_curve(equity_curve_rows)
        total_return = float(equity_curve_rows[-1]["equity"]) - 1.0 if equity_curve_rows else 0.0
        max_drawdown = min((float(row["drawdown"]) for row in drawdown_curve_rows), default=0.0)
        positive_sum = sum(float(row["realized_forward_return_20d"]) for row in trade_rows if float(row["realized_forward_return_20d"]) > 0.0)
        negative_sum = sum(float(row["realized_forward_return_20d"]) for row in trade_rows if float(row["realized_forward_return_20d"]) < 0.0)
        profit_factor = positive_sum / abs(negative_sum) if negative_sum < 0.0 else math.inf
        hit_rate = sum(1 for row in trade_rows if float(row["realized_forward_return_20d"]) > 0.0) / len(trade_rows) if trade_rows else 0.0
        cash_days = sum(1 for row in equity_curve_rows if str(row["position_state"]) == "cash")

        neutral_return = float(neutral_summary.get("total_return", 0.0))
        neutral_drawdown = float(neutral_summary.get("max_drawdown", 0.0))
        bk_return = float(ranker_summary.get("best_variant_total_return", ranker_summary.get("total_return", 0.0)))
        bk_drawdown = float(ranker_summary.get("best_variant_max_drawdown", ranker_summary.get("max_drawdown", 0.0)))

        comparison_rows = [
            {"comparison_name": "return_vs_neutral", "neutral_value": neutral_summary.get("total_return"), "fusion_value": round(total_return, 4), "delta": round(total_return - neutral_return, 4)},
            {"comparison_name": "max_drawdown_vs_neutral", "neutral_value": neutral_summary.get("max_drawdown"), "fusion_value": round(float(max_drawdown), 4), "delta": round(float(max_drawdown) - neutral_drawdown, 4)},
            {"comparison_name": "return_vs_bk_best_selector", "bk_best_value": bk_return, "fusion_value": round(total_return, 4), "delta": round(total_return - bk_return, 4)},
            {"comparison_name": "max_drawdown_vs_bk_best_selector", "bk_best_value": bk_drawdown, "fusion_value": round(float(max_drawdown), 4), "delta": round(float(max_drawdown) - bk_drawdown, 4)},
            {"comparison_name": "return_vs_aggressive", "aggressive_value": aggressive_summary.get("total_return"), "fusion_value": round(total_return, 4), "delta": round(total_return - float(aggressive_summary.get("total_return", 0.0)), 4)},
            {"comparison_name": "return_gap_vs_oracle", "oracle_value": oracle_summary.get("total_return"), "fusion_value": round(total_return, 4), "gap": round(float(oracle_summary.get("total_return", 0.0)) - total_return, 4)},
        ]

        summary = {
            "acceptance_posture": "freeze_v112bp_cpo_selector_maturity_fusion_pilot_v1",
            "track_name": "selector_maturity_fusion_track",
            "no_leak_enforced": True,
            "training_layer_row_count": len(training_layer_rows),
            "sample_count": len(gate_decision_rows),
            "gate_decision_row_count": len(gate_decision_rows),
            "trade_count": len(trade_rows),
            "equity_curve_point_count": len(equity_curve_rows),
            "drawdown_curve_point_count": len(drawdown_curve_rows),
            "total_return": round(total_return, 4),
            "max_drawdown": round(float(max_drawdown), 4),
            "profit_factor": round(float(profit_factor), 4) if profit_factor != math.inf else "inf",
            "hit_rate": round(float(hit_rate), 4),
            "cash_ratio": round(float(cash_days / len(equity_curve_rows)), 4) if equity_curve_rows else 0.0,
            "neutral_return_delta": round(total_return - neutral_return, 4),
            "neutral_drawdown_delta": round(float(max_drawdown) - neutral_drawdown, 4),
            "bk_return_delta": round(total_return - bk_return, 4),
            "bk_drawdown_delta": round(float(max_drawdown) - bk_drawdown, 4),
            "aggressive_return_delta": round(total_return - float(aggressive_summary.get("total_return", 0.0)), 4),
            "oracle_return_gap": round(float(oracle_summary.get("total_return", 0.0)) - total_return, 4),
            "beats_bk_on_drawdown": float(max_drawdown) > bk_drawdown,
            "beats_neutral_without_material_drawdown_worsening": total_return > neutral_return and float(max_drawdown) >= neutral_drawdown - 0.05,
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": (
                "keep_selector_plus_internal_maturity_fusion_as_the_new_mainline_candidate"
                if total_return > neutral_return and float(max_drawdown) >= neutral_drawdown - 0.05
                else "treat_fusion_as_a_candidate_only_and_continue_condition_discovery"
            ),
        }
        interpretation = [
            "V1.12BP tests whether selector quality becomes more usable once internal maturity and regime context are attached to the gate layer.",
            "The internal maturity overlay is treated as the primary filtering layer; market regime remains auxiliary context only.",
            "This remains no-leak and report-only. It is a fusion experiment, not a production signal.",
        ]
        return V112BPCpoSelectorMaturityFusionPilotReport(
            summary=summary,
            trade_rows=trade_rows,
            equity_curve_rows=equity_curve_rows,
            drawdown_curve_rows=drawdown_curve_rows,
            gate_decision_rows=gate_decision_rows,
            comparison_rows=comparison_rows,
            plot_bundle_rows=[
                {"plot_name": "selector_maturity_fusion_equity_curve", "series_name": "equity", "point_count": len(equity_curve_rows)},
                {"plot_name": "selector_maturity_fusion_drawdown_curve", "series_name": "drawdown", "point_count": len(drawdown_curve_rows)},
            ],
            interpretation=interpretation,
        )

    def _build_feature_frame(
        self,
        *,
        training_layer_rows: list[dict[str, Any]],
        cycle_reconstruction_payload: dict[str, Any],
    ) -> pd.DataFrame:
        pilot_analyzer = V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer()
        widen_analyzer = V112AUCPOBoundedRowGeometryWidenPilotAnalyzer()
        role_patch = V112AOCPORoleLayerPatchPilotAnalyzer()
        branch_patch = V112AVCPOBranchRoleGeometryPatchPilotAnalyzer()
        regime_helper = V112BLCpoRegimeAwareGatePilotAnalyzer()

        stage_map = pilot_analyzer._stage_map(list(cycle_reconstruction_payload.get("reconstructed_stage_rows", [])))  # noqa: SLF001
        samples = widen_analyzer._build_samples(widened_rows=training_layer_rows, stage_map=stage_map, pilot_analyzer=pilot_analyzer)  # noqa: SLF001
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
        overlay_rows: list[dict[str, Any]] = []
        for trade_date, current_frame in frame.groupby("trade_date"):
            regime_values = regime_helper._regime_overlay_values(current_frame=current_frame.copy())  # noqa: SLF001
            maturity_values = self._internal_maturity_overlay_values(current_frame=current_frame.copy())
            overlay_rows.append({"trade_date": str(trade_date), **regime_values, **maturity_values})
        return frame.merge(pd.DataFrame(overlay_rows), on="trade_date", how="left")

    def _internal_maturity_overlay_values(self, *, current_frame: pd.DataFrame) -> dict[str, float]:
        frame = current_frame.copy()
        core_mask = frame["cohort_layer"].isin({"core_anchor", "core_beta", "core_platform_confirmation"})
        branch_mask = frame["cohort_layer"].isin({"branch_extension"})
        extension_mask = frame["cohort_layer"].isin({"adjacent_bridge", "adjacent_high_beta_extension", "branch_extension"})
        leader_mask = frame["role_family"].astype(str).eq("core_module_leader")

        def mean_of(mask: pd.Series, column: str, fallback: float = 0.0) -> float:
            return float(frame.loc[mask, column].mean()) if bool(mask.any()) else fallback

        core_ret20 = mean_of(core_mask, "ret_20")
        branch_ret20 = mean_of(branch_mask, "ret_20", fallback=core_ret20)
        extension_ret20 = mean_of(extension_mask, "ret_20", fallback=core_ret20)
        positive_ratio = float(frame["ret_5"].gt(0.0).mean()) if not frame.empty else 0.0
        top_two_turnover = float(frame["volume_ratio_5_20"].nlargest(min(2, len(frame))).sum()) if not frame.empty else 0.0
        turnover_total = float(frame["volume_ratio_5_20"].sum()) if not frame.empty else 0.0

        leader_fragility = 0.0
        if bool(leader_mask.any()):
            leader_row = frame.loc[leader_mask].iloc[0]
            leader_fragility = max(0.0, -float(leader_row["drawdown_from_high20"])) + max(0.0, float(leader_row["realized_vol_10"]) - 0.08)

        branch_failure = (
            float(
                frame.loc[branch_mask, ["ret_5", "price_vs_ma20"]]
                .apply(lambda row: 1.0 if float(row["ret_5"]) <= 0.0 or float(row["price_vs_ma20"]) < 0.15 else 0.0, axis=1)
                .mean()
            )
            if bool(branch_mask.any())
            else 0.0
        )
        role_deterioration = (
            float(
                frame.loc[extension_mask, ["drawdown_from_high20", "price_vs_ma20"]]
                .apply(lambda row: 1.0 if float(row["drawdown_from_high20"]) < -0.18 or float(row["price_vs_ma20"]) < 0.1 else 0.0, axis=1)
                .mean()
            )
            if bool(extension_mask.any())
            else 0.0
        )

        return {
            "core_branch_relative_strength_spread_state": core_ret20 - branch_ret20,
            "core_spillover_divergence_state": core_ret20 - extension_ret20,
            "internal_breadth_compression_state": 1.0 - positive_ratio,
            "internal_turnover_concentration_state": top_two_turnover / turnover_total if turnover_total > 0.0 else 0.0,
            "leader_absorption_fragility_state": leader_fragility,
            "branch_promotion_failure_rate_state": branch_failure,
            "role_deterioration_spread_state": role_deterioration,
            "spillover_saturation_overlay_state": max(0.0, extension_ret20 - core_ret20),
        }

    def _maturity_balance_score(self, row: pd.Series) -> float:
        good = 0.22 * float(row["core_branch_relative_strength_spread_state"]) + 0.12 * float(row["core_spillover_divergence_state"])
        bad = (
            0.18 * float(row["internal_breadth_compression_state"])
            + 0.16 * float(row["internal_turnover_concentration_state"])
            + 0.12 * float(row["leader_absorption_fragility_state"])
            + 0.12 * float(row["branch_promotion_failure_rate_state"])
            + 0.12 * float(row["role_deterioration_spread_state"])
            + 0.08 * float(row["spillover_saturation_overlay_state"])
        )
        return good - bad

    def _regime_support_score(self, row: pd.Series) -> float:
        return (
            0.25 * float(row["broad_index_trend_state"])
            + 0.18 * float(row["risk_appetite_heat_state"])
            + 0.14 * float(row["ai_hardware_cross_board_resonance_state"])
            + 0.12 * float(row["optics_sector_etf_strength_state"])
            - 0.16 * float(row["turnover_pressure_overlay_state"])
            - 0.08 * float(row["sector_rotation_conflict_state"])
        )

    def _selector_feature_names(self) -> list[str]:
        return [
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
        ]

    def _gate_feature_names(self) -> list[str]:
        return [
            "predicted_return_20d",
            "ranker_score",
            "maturity_balance_score",
            "regime_support_score",
            "weighted_breadth_ratio",
            "catalyst_presence_proxy",
            "confidence_tier_numeric",
            "rollforward_state_numeric",
            "turnover_state_numeric",
            "window_uncertainty_numeric",
            "core_branch_relative_strength_spread_state",
            "core_spillover_divergence_state",
            "internal_breadth_compression_state",
            "internal_turnover_concentration_state",
            "leader_absorption_fragility_state",
            "branch_promotion_failure_rate_state",
            "role_deterioration_spread_state",
            "spillover_saturation_overlay_state",
            "broad_index_trend_state",
            "risk_appetite_heat_state",
            "ai_hardware_cross_board_resonance_state",
            "optics_sector_etf_strength_state",
            "turnover_pressure_overlay_state",
            "sector_rotation_conflict_state",
        ]

    def _gate_row(self, *, chosen_row: pd.Series, teacher_enter_label: int) -> dict[str, Any]:
        row = {
            "trade_date": str(chosen_row["trade_date"]),
            "symbol": str(chosen_row["symbol"]),
            "teacher_enter_label": int(teacher_enter_label),
            "predicted_return_20d": float(chosen_row["predicted_return_20d"]),
            "ranker_score": float(chosen_row["ranker_score"]),
            "maturity_balance_score": float(chosen_row["maturity_balance_score"]),
            "regime_support_score": float(chosen_row["regime_support_score"]),
        }
        for name in self._gate_feature_names():
            row[name] = float(row.get(name, chosen_row[name]))
        return row

    def _select_threshold(self, *, train_probs: np.ndarray, y_train: np.ndarray) -> float:
        candidate_thresholds = np.unique(
            np.concatenate([np.linspace(0.05, 0.9, 35), np.quantile(train_probs, np.linspace(0.05, 0.95, 19))])
        )
        positive_count = int(np.sum(y_train))
        negative_count = int(len(y_train) - positive_count)
        best_threshold = 0.5
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
            score = 0.4 * recall + 0.35 * precision + 0.15 * tnr - 0.1 * (pred_positive_count / max(len(y_train), 1))
            if score > best_score:
                best_score = score
                best_threshold = float(threshold)
        return float(best_threshold)

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


def write_v112bp_cpo_selector_maturity_fusion_pilot_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BPCpoSelectorMaturityFusionPilotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
