from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

os.environ.setdefault("PANDAS_NO_USE_NUMEXPR", "1")
os.environ.setdefault("PANDAS_NO_USE_BOTTLENECK", "1")

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score

from a_share_quant.strategy.v112a_price_cycle_inference_v1 import TencentKlineClient
from a_share_quant.strategy.v112am_cpo_extremely_small_core_skeleton_training_pilot_v1 import (
    CoreSkeletonSample,
    V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer,
)
from a_share_quant.strategy.v112ao_cpo_role_layer_patch_pilot_v1 import (
    V112AOCPORoleLayerPatchPilotAnalyzer,
)
from a_share_quant.strategy.v112at_cpo_post_patch_rerun_v1 import V112ASCohortWeights


@dataclass(slots=True)
class V112AUCPOBoundedRowGeometryWidenPilotReport:
    summary: dict[str, Any]
    target_rows: list[dict[str, Any]]
    widened_row_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "target_rows": self.target_rows,
            "widened_row_rows": self.widened_row_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112AUCPOBoundedRowGeometryWidenPilotAnalyzer:
    BRANCH_SYMBOLS = {"300570", "688498", "688313", "300757"}
    IMPLEMENTATION_FEATURE_NAMES = [
        "weighted_breadth_ratio",
        "turnover_percentile_20",
        "turnover_state_numeric",
        "event_disclosure_numeric",
        "window_uncertainty_numeric",
        "confidence_tier_numeric",
        "rollforward_state_numeric",
    ]
    EXTENDED_ROLE_FEATURES = {
        **V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer.ROLE_FEATURES,
        "branch_extension": (0.55, 0.52, 0.54),
    }

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        post_patch_rerun_payload: dict[str, Any],
        dataset_assembly_payload: dict[str, Any],
        cycle_reconstruction_payload: dict[str, Any],
    ) -> V112AUCPOBoundedRowGeometryWidenPilotReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112au_now")):
            raise ValueError("V1.12AU must be open before the widen pilot runs.")

        prior_rows = {str(row.get("target_name")): row for row in list(post_patch_rerun_payload.get("target_rows", []))}
        dataset_rows = list(dataset_assembly_payload.get("dataset_draft_rows", []))
        widened_rows = [
            row
            for row in dataset_rows
            if bool(row.get("include_in_truth_candidate_rows")) or str(row.get("symbol")) in self.BRANCH_SYMBOLS
        ]
        if len(widened_rows) <= 7:
            raise ValueError("V1.12AU requires a lawful row-geometry widen beyond the original 7 truth rows.")

        pilot_analyzer = V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer()
        role_patch_analyzer = V112AOCPORoleLayerPatchPilotAnalyzer()
        stage_map = pilot_analyzer._stage_map(list(cycle_reconstruction_payload.get("reconstructed_stage_rows", [])))  # noqa: SLF001
        samples = self._build_samples(widened_rows=widened_rows, stage_map=stage_map, pilot_analyzer=pilot_analyzer)
        samples.sort(key=lambda item: item.trade_date)
        truth_index = {str(row.get("symbol")): row for row in widened_rows}
        impl_features = self._implementation_feature_map(samples=samples, truth_index=truth_index)

        x = np.array(
            [
                [sample.feature_values[name] for name in pilot_analyzer.FEATURE_NAMES + role_patch_analyzer.PATCH_FEATURE_NAMES]
                + [impl_features[(sample.trade_date, sample.symbol)][name] for name in self.IMPLEMENTATION_FEATURE_NAMES]
                for sample in samples
            ],
            dtype=float,
        )
        split_index = max(1, min(len(samples) - 1, int(len(samples) * 0.7)))

        target_rows: list[dict[str, Any]] = []
        core_targets = {
            "phase_progression_label": [sample.stage_family for sample in samples],
            "role_state_label": [sample.role_family for sample in samples],
            "catalyst_sequence_label": [sample.catalyst_sequence_label for sample in samples],
        }
        for target_name, labels in core_targets.items():
            baseline_accuracy, gbdt_accuracy = self._run_target(labels=labels, x=x, split_index=split_index)
            prior_row = dict(prior_rows[target_name])
            target_rows.append(
                {
                    "target_name": target_name,
                    "baseline_accuracy_before_widen": prior_row.get("baseline_accuracy_after_impl_patch"),
                    "baseline_accuracy_after_widen": baseline_accuracy,
                    "gbdt_accuracy_before_widen": prior_row.get("gbdt_accuracy_after_impl_patch"),
                    "gbdt_accuracy_after_widen": gbdt_accuracy,
                    "gbdt_accuracy_change_vs_v112at": round(gbdt_accuracy - float(prior_row["gbdt_accuracy_after_impl_patch"]), 4),
                }
            )

        guarded_defs = {
            "board_condition_label": self._board_condition_label,
            "role_transition_label": self._role_transition_label,
            "failed_role_promotion_label": self._failed_role_promotion_label,
        }
        for target_name, label_fn in guarded_defs.items():
            subset_samples = self._guarded_subset(target_name=target_name, samples=samples)
            subset_x = np.array(
                [
                    [sample.feature_values[name] for name in pilot_analyzer.FEATURE_NAMES + role_patch_analyzer.PATCH_FEATURE_NAMES]
                    + [impl_features[(sample.trade_date, sample.symbol)][name] for name in self.IMPLEMENTATION_FEATURE_NAMES]
                    for sample in subset_samples
                ],
                dtype=float,
            )
            subset_split = max(1, min(len(subset_samples) - 1, int(len(subset_samples) * 0.7)))
            labels = [label_fn(sample.role_family, sample.stage_family) for sample in subset_samples]
            baseline_accuracy, gbdt_accuracy = self._run_target(labels=labels, x=subset_x, split_index=subset_split)
            prior_row = dict(prior_rows[target_name])
            target_rows.append(
                {
                    "target_name": target_name,
                    "baseline_accuracy_before_widen": prior_row.get("baseline_accuracy_after_impl_patch"),
                    "baseline_accuracy_after_widen": baseline_accuracy,
                    "gbdt_accuracy_before_widen": prior_row.get("gbdt_accuracy_after_impl_patch"),
                    "gbdt_accuracy_after_widen": gbdt_accuracy,
                    "gbdt_accuracy_change_vs_v112at": round(gbdt_accuracy - float(prior_row["gbdt_accuracy_after_impl_patch"]), 4),
                }
            )

        widened_row_rows = [
            {
                "symbol": str(row.get("symbol")),
                "cohort_layer": str(row.get("cohort_layer")),
                "role_family": str(row.get("role_family")),
                "dataset_posture": str(row.get("dataset_posture")),
                "active_stage_windows": list(row.get("active_stage_windows", [])),
            }
            for row in widened_rows
            if str(row.get("symbol")) in self.BRANCH_SYMBOLS
        ]

        core_rows = [row for row in target_rows if row["target_name"] in core_targets]
        guarded_rows = [row for row in target_rows if row["target_name"] not in core_targets]
        summary = {
            "acceptance_posture": "freeze_v112au_cpo_bounded_row_geometry_widen_pilot_v1",
            "truth_candidate_row_count_before_widen": 7,
            "row_count_after_widen": len(widened_rows),
            "added_branch_row_count": len(widened_row_rows),
            "sample_count": len(samples),
            "core_targets_stable_after_row_widen": all(
                float(row["gbdt_accuracy_after_widen"]) >= float(row["gbdt_accuracy_before_widen"])
                for row in core_rows
            ),
            "guarded_targets_stable_after_row_widen": all(
                float(row["gbdt_accuracy_after_widen"]) >= float(row["gbdt_accuracy_before_widen"])
                for row in guarded_rows
            ),
            "best_target_after_row_widen": max(target_rows, key=lambda row: float(row["gbdt_accuracy_after_widen"]))["target_name"],
            "allow_formal_training_now": False,
            "allow_formal_signal_generation_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": (
                "review_if_branch_row_geometry_can_enter_the_next_bounded_training_pilot"
                if all(float(row["gbdt_accuracy_after_widen"]) >= float(row["gbdt_accuracy_before_widen"]) for row in core_rows)
                and all(float(row["gbdt_accuracy_after_widen"]) >= float(row["gbdt_accuracy_before_widen"]) for row in guarded_rows)
                else "keep_branch_rows_as_review_only_and_patch_branch_role_geometry_before_any_training_widen"
            ),
        }
        interpretation = [
            "This widen admits branch review rows only; it does not open spillover, pending, formal training, or signal rights.",
            "If stability breaks here, the project learns that branch-row geometry is still ahead of the current trainable boundary.",
            "This remains report-only and should be read as geometry evidence, not deployment readiness.",
        ]
        return V112AUCPOBoundedRowGeometryWidenPilotReport(
            summary=summary,
            target_rows=target_rows,
            widened_row_rows=widened_row_rows,
            interpretation=interpretation,
        )

    def _build_samples(
        self,
        *,
        widened_rows: list[dict[str, Any]],
        stage_map: dict[str, dict[str, str]],
        pilot_analyzer: V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer,
    ) -> list[CoreSkeletonSample]:
        client = TencentKlineClient()
        samples: list[CoreSkeletonSample] = []
        for row in widened_rows:
            symbol = str(row.get("symbol"))
            cohort_layer = str(row.get("cohort_layer"))
            role_family = str(row.get("role_family"))
            active_windows = [str(window) for window in row.get("active_stage_windows", [])]

            bars = client.fetch_daily_bars(symbol).sort_values("date").reset_index(drop=True)
            bars["ret_1"] = bars["close"].pct_change()
            bars["ret_5"] = bars["close"].pct_change(5)
            bars["ret_20"] = bars["close"].pct_change(20)
            bars["ma20"] = bars["close"].rolling(20, min_periods=5).mean()
            bars["ma60"] = bars["close"].rolling(60, min_periods=20).mean()
            bars["high20"] = bars["high"].rolling(20, min_periods=5).max()
            bars["low20"] = bars["low"].rolling(20, min_periods=5).min()
            bars["high60"] = bars["high"].rolling(60, min_periods=20).max()
            bars["high120"] = bars["high"].rolling(120, min_periods=20).max()
            bars["vol5"] = bars["volume"].rolling(5, min_periods=3).mean()
            bars["vol20"] = bars["volume"].rolling(20, min_periods=5).mean()
            bars["realized_vol_10"] = bars["ret_1"].rolling(10, min_periods=5).std()
            bars["positive_day_ratio_10"] = bars["ret_1"].gt(0).rolling(10, min_periods=5).mean()
            bars["intraday_range_mean_10"] = (((bars["high"] - bars["low"]) / bars["close"]).rolling(10, min_periods=5).mean())
            bars["volume_cv_10"] = bars["volume"].rolling(10, min_periods=5).std() / bars["volume"].rolling(10, min_periods=5).mean()
            bars["future_close_20"] = bars["close"].shift(-20)
            bars["future_min_low_20"] = bars["low"][::-1].rolling(20, min_periods=1).min()[::-1].shift(-1)
            listing_board_tier, limit_amplitude_proxy = self._board_microstructure_values(symbol)

            for row_data in bars.itertuples(index=False):
                if pd.isna(row_data.future_close_20) or pd.isna(row_data.future_min_low_20):
                    continue
                trade_month = pd.Timestamp(row_data.date).strftime("%Y-%m")
                chosen_occurrence = self._resolve_occurrence(trade_month=trade_month, active_windows=active_windows, stage_map=stage_map)
                if chosen_occurrence is None:
                    continue
                stage_family = str(stage_map[chosen_occurrence]["stage_family"])
                feature_values = self._feature_row(
                    cohort_layer=cohort_layer,
                    stage_family=stage_family,
                    close=float(row_data.close),
                    ret_5=float(row_data.ret_5) if pd.notna(row_data.ret_5) else 0.0,
                    ret_20=float(row_data.ret_20) if pd.notna(row_data.ret_20) else 0.0,
                    ma20=float(row_data.ma20) if pd.notna(row_data.ma20) else float(row_data.close),
                    ma60=float(row_data.ma60) if pd.notna(row_data.ma60) else float(row_data.close),
                    high60=float(row_data.high60) if pd.notna(row_data.high60) else float(row_data.high),
                    high120=float(row_data.high120) if pd.notna(row_data.high120) else float(row_data.high),
                    vol5=float(row_data.vol5) if pd.notna(row_data.vol5) else float(row_data.volume),
                    vol20=float(row_data.vol20) if pd.notna(row_data.vol20) else float(row_data.volume),
                )
                range_denom = float(row_data.high20) - float(row_data.low20) if pd.notna(row_data.high20) and pd.notna(row_data.low20) else 0.0
                feature_values.update(
                    {
                        "listing_board_tier": listing_board_tier,
                        "limit_amplitude_proxy": limit_amplitude_proxy,
                        "realized_vol_10": float(row_data.realized_vol_10) if pd.notna(row_data.realized_vol_10) else 0.0,
                        "positive_day_ratio_10": float(row_data.positive_day_ratio_10) if pd.notna(row_data.positive_day_ratio_10) else 0.5,
                        "range_position_20": ((float(row_data.close) - float(row_data.low20)) / range_denom) if range_denom > 0.0 else 0.5,
                        "drawdown_from_high20": (float(row_data.close) / float(row_data.high20) - 1.0) if pd.notna(row_data.high20) and float(row_data.high20) != 0.0 else 0.0,
                        "intraday_range_mean_10": float(row_data.intraday_range_mean_10) if pd.notna(row_data.intraday_range_mean_10) else 0.0,
                        "volume_cv_10": float(row_data.volume_cv_10) if pd.notna(row_data.volume_cv_10) and np.isfinite(float(row_data.volume_cv_10)) else 0.0,
                    }
                )
                samples.append(
                    CoreSkeletonSample(
                        trade_date=pd.Timestamp(row_data.date).strftime("%Y-%m-%d"),
                        symbol=symbol,
                        stage_family=stage_family,
                        role_family=role_family,
                        catalyst_sequence_label=pilot_analyzer._catalyst_sequence_label(stage_family),  # noqa: SLF001
                        feature_values=feature_values,
                        forward_return_20d=float(row_data.future_close_20 / row_data.close - 1.0),
                        max_drawdown_20d=float(row_data.future_min_low_20 / row_data.close - 1.0),
                    )
                )
        return samples

    def _feature_row(self, *, cohort_layer: str, stage_family: str, close: float, ret_5: float, ret_20: float, ma20: float, ma60: float, high60: float, high120: float, vol5: float, vol20: float) -> dict[str, float]:
        cohort_sensitivity, margin_sensitivity, role_beta = self.EXTENDED_ROLE_FEATURES[cohort_layer]
        return {
            "ret_5": ret_5,
            "ret_20": ret_20,
            "price_vs_ma20": close / ma20 - 1.0 if ma20 else 0.0,
            "price_vs_ma60": close / ma60 - 1.0 if ma60 else 0.0,
            "volume_ratio_5_20": vol5 / vol20 if vol20 else 1.0,
            "distance_to_high60": close / high60 - 1.0 if high60 else 0.0,
            "distance_to_high120": close / high120 - 1.0 if high120 else 0.0,
            "cohort_sensitivity": cohort_sensitivity,
            "margin_sensitivity": margin_sensitivity,
            "role_beta_proxy": role_beta,
            "catalyst_presence_proxy": V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer.STAGE_CATALYST_PROXY[stage_family],
        }

    def _implementation_feature_map(self, *, samples: list[Any], truth_index: dict[str, dict[str, Any]]) -> dict[tuple[str, str], dict[str, float]]:
        frame = pd.DataFrame(
            {
                "trade_date": [sample.trade_date for sample in samples],
                "symbol": [sample.symbol for sample in samples],
                "stage_family": [sample.stage_family for sample in samples],
                "ret_5": [sample.feature_values["ret_5"] for sample in samples],
                "price_vs_ma20": [sample.feature_values["price_vs_ma20"] for sample in samples],
                "volume_ratio_5_20": [sample.feature_values["volume_ratio_5_20"] for sample in samples],
                "cohort_layer": [str(truth_index[sample.symbol]["cohort_layer"]) for sample in samples],
            }
        )
        weights = V112ASCohortWeights.weights()
        frame["weight"] = frame["cohort_layer"].map(weights).astype(float)
        frame["positive_participation"] = ((frame["ret_5"] > 0).astype(float) + (frame["price_vs_ma20"] > 0).astype(float)) / 2.0
        board_daily = frame.groupby("trade_date", as_index=False).apply(self._board_daily_row).reset_index(drop=True).sort_values("trade_date").reset_index(drop=True)
        board_daily["turnover_percentile_20"] = self._trailing_percentile(board_daily["board_proxy"])
        board_daily["turnover_state_numeric"] = board_daily["turnover_percentile_20"].map(self._turnover_numeric)
        frame = frame.merge(board_daily, on="trade_date", how="left")
        frame["event_disclosure_numeric"] = frame["stage_family"].map(self._event_disclosure_numeric)
        frame["window_uncertainty_numeric"] = frame["stage_family"].map(self._window_uncertainty_numeric)
        frame["confidence_tier_numeric"] = frame["stage_family"].map(self._confidence_tier_numeric)
        frame["rollforward_state_numeric"] = frame["stage_family"].map(self._rollforward_state_numeric)
        return {
            (str(row.trade_date), str(row.symbol)): {
                "weighted_breadth_ratio": float(row.weighted_breadth_ratio),
                "turnover_percentile_20": float(row.turnover_percentile_20),
                "turnover_state_numeric": float(row.turnover_state_numeric),
                "event_disclosure_numeric": float(row.event_disclosure_numeric),
                "window_uncertainty_numeric": float(row.window_uncertainty_numeric),
                "confidence_tier_numeric": float(row.confidence_tier_numeric),
                "rollforward_state_numeric": float(row.rollforward_state_numeric),
            }
            for row in frame.itertuples(index=False)
        }

    def _board_daily_row(self, group: pd.DataFrame) -> pd.Series:
        weight_sum = float(group["weight"].sum())
        weighted_breadth_ratio = float((group["weight"] * group["positive_participation"]).sum()) / weight_sum if weight_sum else 0.0
        board_proxy = float((group["weight"] * (group["volume_ratio_5_20"] + group["positive_participation"])).sum()) / weight_sum if weight_sum else 0.0
        return pd.Series({"weighted_breadth_ratio": weighted_breadth_ratio, "board_proxy": board_proxy})

    def _trailing_percentile(self, series: pd.Series) -> pd.Series:
        values = series.astype(float).tolist()
        out: list[float] = []
        for idx, value in enumerate(values):
            start = max(0, idx - 19)
            window = values[start : idx + 1]
            rank = sum(1 for item in window if item <= value)
            out.append(rank / len(window))
        return pd.Series(out, index=series.index)

    def _turnover_numeric(self, percentile: float) -> float:
        if percentile < 0.25:
            return 0.0
        if percentile < 0.60:
            return 1.0
        if percentile < 0.85:
            return 2.0
        return 3.0

    def _event_disclosure_numeric(self, stage_family: str) -> float:
        return {"pre_ignition_watch": 0.0, "ignition": 1.0, "main_markup": 1.0, "diffusion": 0.5, "laggard_catchup": 0.0, "divergence_and_decay": 0.0}[stage_family]

    def _window_uncertainty_numeric(self, stage_family: str) -> float:
        return {"pre_ignition_watch": 1.0, "ignition": 0.5, "main_markup": 0.5, "diffusion": 0.5, "laggard_catchup": 0.0, "divergence_and_decay": 0.0}[stage_family]

    def _confidence_tier_numeric(self, stage_family: str) -> float:
        return {"pre_ignition_watch": 1.0, "ignition": 2.0, "main_markup": 2.0, "diffusion": 1.0, "laggard_catchup": 0.0, "divergence_and_decay": 0.0}[stage_family]

    def _rollforward_state_numeric(self, stage_family: str) -> float:
        return {"pre_ignition_watch": 1.0, "ignition": 0.0, "main_markup": 0.0, "diffusion": 0.5, "laggard_catchup": -1.0, "divergence_and_decay": -1.0}[stage_family]

    def _run_target(self, *, labels: list[str], x: np.ndarray, split_index: int) -> tuple[float, float]:
        classes = sorted(set(labels))
        label_to_int = {label: idx for idx, label in enumerate(classes)}
        y = np.array([label_to_int[label] for label in labels], dtype=int)
        x_train = x[:split_index]
        x_test = x[split_index:]
        y_train = y[:split_index]
        y_test = y[split_index:]
        baseline_preds = V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer()._nearest_centroid_predictions(x_train=x_train, y_train=y_train, x_test=x_test)  # noqa: SLF001
        model = HistGradientBoostingClassifier(max_depth=4, learning_rate=0.05, max_iter=150, random_state=42)
        model.fit(x_train, y_train)
        preds = model.predict(x_test)
        return round(float(accuracy_score(y_test, baseline_preds)), 4), round(float(accuracy_score(y_test, preds)), 4)

    def _guarded_subset(self, *, target_name: str, samples: list[Any]) -> list[Any]:
        if target_name == "board_condition_label":
            return samples
        if target_name == "role_transition_label":
            return [s for s in samples if s.role_family != "core_module_leader"]
        if target_name == "failed_role_promotion_label":
            return [s for s in samples if s.role_family in {"domestic_optics_platform_bridge", "high_beta_module_extension", "high_end_module_extension", "smaller_cap_high_beta_module"}]
        raise ValueError(target_name)

    def _board_condition_label(self, _: str, stage_family: str) -> str:
        return {"pre_ignition_watch": "latent_board", "ignition": "supportive_board", "main_markup": "supportive_board", "diffusion": "widening_board", "laggard_catchup": "mature_board", "divergence_and_decay": "pressured_board"}[stage_family]

    def _role_transition_label(self, role_family: str, stage_family: str) -> str:
        if stage_family == "diffusion":
            if role_family in {"domestic_optics_platform_bridge", "high_beta_module_extension", "high_end_module_extension", "smaller_cap_high_beta_module", "connector_mpo_branch"}:
                return "challenger_activation"
            return "role_quality_split"
        if stage_family == "main_markup":
            if role_family == "core_module_leader":
                return "leader_lock_in"
            if role_family in {"high_beta_core_module", "upstream_component_platform", "laser_chip_component", "silicon_photonics_component", "packaging_process_enabler"}:
                return "role_requalification"
        if stage_family == "divergence_and_decay":
            return "role_quality_split"
        return "stable_no_transition"

    def _failed_role_promotion_label(self, role_family: str, stage_family: str) -> str:
        if role_family in {"high_beta_module_extension", "high_end_module_extension", "smaller_cap_high_beta_module"}:
            if stage_family == "main_markup":
                return "promotion_at_risk"
            return "promotion_attempt_only"
        return "bridge_or_non_failure"

    def _resolve_occurrence(self, *, trade_month: str, active_windows: list[str], stage_map: dict[str, dict[str, str]]) -> str | None:
        matches = []
        for occurrence_name in active_windows:
            stage_info = stage_map.get(occurrence_name)
            if stage_info is None:
                continue
            if str(stage_info["start_month"]) <= trade_month <= str(stage_info["end_month"]):
                matches.append((str(stage_info["start_month"]), occurrence_name))
        if not matches:
            return None
        matches.sort(key=lambda item: item[0])
        return matches[-1][1]

    def _board_microstructure_values(self, symbol: str) -> tuple[float, float]:
        if symbol.startswith("688"):
            return 1.0, 0.20
        if symbol.startswith("300") or symbol.startswith("301"):
            return 0.7, 0.20
        return 0.2, 0.10


def write_v112au_cpo_bounded_row_geometry_widen_pilot_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AUCPOBoundedRowGeometryWidenPilotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
