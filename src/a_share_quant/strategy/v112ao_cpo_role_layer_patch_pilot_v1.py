from __future__ import annotations

import json
import os
from collections import Counter
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


@dataclass(slots=True)
class V112AOCPORoleLayerPatchPilotReport:
    summary: dict[str, Any]
    target_rows: list[dict[str, Any]]
    role_patch_family_rows: list[dict[str, Any]]
    role_confusion_comparison_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "target_rows": self.target_rows,
            "role_patch_family_rows": self.role_patch_family_rows,
            "role_confusion_comparison_rows": self.role_confusion_comparison_rows,
            "interpretation": self.interpretation,
        }


class V112AOCPORoleLayerPatchPilotAnalyzer:
    PATCH_FEATURE_NAMES = [
        "listing_board_tier",
        "limit_amplitude_proxy",
        "realized_vol_10",
        "positive_day_ratio_10",
        "range_position_20",
        "drawdown_from_high20",
        "intraday_range_mean_10",
        "volume_cv_10",
    ]

    PATCH_FAMILIES = {
        "original_skeleton_family": V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer.FEATURE_NAMES,
        "role_patch_microstructure_family": [
            "listing_board_tier",
            "limit_amplitude_proxy",
        ],
        "role_patch_behavior_family": [
            "realized_vol_10",
            "positive_day_ratio_10",
            "range_position_20",
            "drawdown_from_high20",
            "intraday_range_mean_10",
            "volume_cv_10",
        ],
    }

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        prior_training_pilot_payload: dict[str, Any],
        prior_result_review_payload: dict[str, Any],
        dataset_assembly_payload: dict[str, Any],
        cycle_reconstruction_payload: dict[str, Any],
    ) -> V112AOCPORoleLayerPatchPilotReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112ao_now")):
            raise ValueError("V1.12AO must be open before the role-layer patch pilot runs.")

        pilot_analyzer = V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer()
        stage_map = pilot_analyzer._stage_map(list(cycle_reconstruction_payload.get("reconstructed_stage_rows", [])))  # noqa: SLF001
        truth_rows = [
            row
            for row in list(dataset_assembly_payload.get("dataset_draft_rows", []))
            if bool(row.get("include_in_truth_candidate_rows"))
        ]
        samples = self._build_samples(
            truth_rows=truth_rows,
            stage_map=stage_map,
            pilot_analyzer=pilot_analyzer,
        )
        samples.sort(key=lambda item: item.trade_date)

        feature_names = pilot_analyzer.FEATURE_NAMES + self.PATCH_FEATURE_NAMES
        x = np.array([[sample.feature_values[name] for name in feature_names] for sample in samples], dtype=float)
        split_index = max(1, min(len(samples) - 1, int(len(samples) * 0.7)))
        x_train = x[:split_index]
        x_test = x[split_index:]
        test_samples = samples[split_index:]

        prior_target_rows = {
            str(row.get("target_name")): row for row in list(prior_training_pilot_payload.get("target_rows", []))
        }
        prior_role_confusion_rows = list(prior_result_review_payload.get("role_confusion_rows", []))

        target_defs = {
            "phase_progression_label": [sample.stage_family for sample in samples],
            "role_state_label": [sample.role_family for sample in samples],
            "catalyst_sequence_label": [sample.catalyst_sequence_label for sample in samples],
        }

        target_rows: list[dict[str, Any]] = []
        role_patch_family_rows: list[dict[str, Any]] = []
        role_confusion_comparison_rows: list[dict[str, Any]] = []
        best_patch_family = ""
        best_patch_drop = -1.0
        role_state_before = float(prior_target_rows["role_state_label"]["gbdt_accuracy"])
        role_state_after = role_state_before
        phase_after = float(prior_target_rows["phase_progression_label"]["gbdt_accuracy"])
        catalyst_after = float(prior_target_rows["catalyst_sequence_label"]["gbdt_accuracy"])
        role_confusion_counter_after: Counter[tuple[str, str]] = Counter()
        constructive_returns: list[float] = []
        constructive_drawdowns: list[float] = []

        for target_name, label_values in target_defs.items():
            classes = sorted(set(label_values))
            label_to_int = {label: idx for idx, label in enumerate(classes)}
            y = np.array([label_to_int[label] for label in label_values], dtype=int)
            y_train = y[:split_index]
            y_test = y[split_index:]

            baseline_preds = pilot_analyzer._nearest_centroid_predictions(  # noqa: SLF001
                x_train=x_train,
                y_train=y_train,
                x_test=x_test,
            )
            gbdt = HistGradientBoostingClassifier(
                max_depth=4,
                learning_rate=0.05,
                max_iter=150,
                random_state=42,
            )
            gbdt.fit(x_train, y_train)
            gbdt_preds = gbdt.predict(x_test)

            baseline_accuracy = round(float(accuracy_score(y_test, baseline_preds)), 4)
            gbdt_accuracy = round(float(accuracy_score(y_test, gbdt_preds)), 4)
            prior_row = dict(prior_target_rows[target_name])

            target_rows.append(
                {
                    "target_name": target_name,
                    "baseline_accuracy_before_patch": prior_row.get("baseline_accuracy"),
                    "baseline_accuracy_after_patch": baseline_accuracy,
                    "gbdt_accuracy_before_patch": prior_row.get("gbdt_accuracy"),
                    "gbdt_accuracy_after_patch": gbdt_accuracy,
                    "gbdt_accuracy_gain_after_patch": round(gbdt_accuracy - float(prior_row["gbdt_accuracy"]), 4),
                    "reading": (
                        "Compare current bounded role-layer patch behavior against the earlier V1.12AM tiny pilot."
                    ),
                }
            )

            if target_name == "phase_progression_label":
                phase_after = gbdt_accuracy
                constructive_returns = [
                    sample.forward_return_20d
                    for idx, sample in enumerate(test_samples)
                    if classes[int(gbdt_preds[idx])] in {"ignition", "main_markup"}
                ]
                constructive_drawdowns = [
                    sample.max_drawdown_20d
                    for idx, sample in enumerate(test_samples)
                    if classes[int(gbdt_preds[idx])] in {"ignition", "main_markup"}
                ]

            if target_name == "catalyst_sequence_label":
                catalyst_after = gbdt_accuracy

            if target_name == "role_state_label":
                role_state_after = gbdt_accuracy
                for idx, sample in enumerate(test_samples):
                    true_label = classes[int(y_test[idx])]
                    predicted_label = classes[int(gbdt_preds[idx])]
                    if true_label != predicted_label:
                        role_confusion_counter_after[(true_label, predicted_label)] += 1

                for family_name, family_features in self.PATCH_FAMILIES.items():
                    x_train_masked = x_train.copy()
                    x_test_masked = x_test.copy()
                    feature_indexes = [feature_names.index(name) for name in family_features]
                    x_train_masked[:, feature_indexes] = 0.0
                    x_test_masked[:, feature_indexes] = 0.0
                    masked_model = HistGradientBoostingClassifier(
                        max_depth=4,
                        learning_rate=0.05,
                        max_iter=150,
                        random_state=42,
                    )
                    masked_model.fit(x_train_masked, y_train)
                    masked_preds = masked_model.predict(x_test_masked)
                    masked_accuracy = float(accuracy_score(y_test, masked_preds))
                    accuracy_drop = round(gbdt_accuracy - masked_accuracy, 4)
                    if family_name != "original_skeleton_family" and accuracy_drop > best_patch_drop:
                        best_patch_drop = accuracy_drop
                        best_patch_family = family_name
                    role_patch_family_rows.append(
                        {
                            "family_name": family_name,
                            "full_accuracy": gbdt_accuracy,
                            "masked_accuracy": round(masked_accuracy, 4),
                            "accuracy_drop": accuracy_drop,
                            "reading": "Larger drop means the patched role-state result relies more on this family.",
                        }
                    )

        prior_confusion_index = {
            (str(row.get("true_role")), str(row.get("predicted_role"))): int(row.get("count", 0))
            for row in prior_role_confusion_rows
        }
        all_confusion_pairs = set(prior_confusion_index) | set(role_confusion_counter_after)
        for true_role, predicted_role in sorted(all_confusion_pairs):
            before_count = int(prior_confusion_index.get((true_role, predicted_role), 0))
            after_count = int(role_confusion_counter_after.get((true_role, predicted_role), 0))
            role_confusion_comparison_rows.append(
                {
                    "true_role": true_role,
                    "predicted_role": predicted_role,
                    "count_before_patch": before_count,
                    "count_after_patch": after_count,
                    "confusion_reduction": before_count - after_count,
                }
            )

        max_confusion_before = max(
            (int(row.get("count_before_patch", 0)) for row in role_confusion_comparison_rows),
            default=0,
        )
        max_confusion_after = max(
            (int(row.get("count_after_patch", 0)) for row in role_confusion_comparison_rows),
            default=0,
        )
        summary = {
            "acceptance_posture": "freeze_v112ao_cpo_role_layer_patch_pilot_v1",
            "sample_count": len(samples),
            "train_count": split_index,
            "test_count": len(test_samples),
            "truth_candidate_row_count": len(truth_rows),
            "patched_feature_count": len(feature_names),
            "patch_feature_count": len(self.PATCH_FEATURE_NAMES),
            "phase_gbdt_accuracy_before_patch": float(prior_target_rows["phase_progression_label"]["gbdt_accuracy"]),
            "phase_gbdt_accuracy_after_patch": phase_after,
            "role_state_gbdt_accuracy_before_patch": role_state_before,
            "role_state_gbdt_accuracy_after_patch": role_state_after,
            "role_state_accuracy_gain_after_patch": round(role_state_after - role_state_before, 4),
            "catalyst_sequence_gbdt_accuracy_before_patch": float(
                prior_target_rows["catalyst_sequence_label"]["gbdt_accuracy"]
            ),
            "catalyst_sequence_gbdt_accuracy_after_patch": catalyst_after,
            "best_role_patch_family": best_patch_family,
            "best_role_patch_family_drop": round(best_patch_drop, 4),
            "max_role_confusion_before_patch": max_confusion_before,
            "max_role_confusion_after_patch": max_confusion_after,
            "constructive_phase_avg_forward_return_20d_after_patch": round(float(np.mean(constructive_returns)), 4)
            if constructive_returns
            else 0.0,
            "constructive_phase_avg_max_drawdown_20d_after_patch": round(float(np.mean(constructive_drawdowns)), 4)
            if constructive_drawdowns
            else 0.0,
            "role_patch_success": role_state_after > role_state_before,
            "formal_training_still_forbidden": True,
            "formal_signal_generation_still_forbidden": True,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": (
                "consider_bounded_secondary_widen_pilot_under_same_report_only_boundary"
                if role_state_after > role_state_before
                else "keep_scope_narrow_and_patch_feature_implementation_before_widen"
            ),
        }
        interpretation = [
            "This patch does not widen geometry; it only tests whether role-state can be improved with bounded market-observable microstructure and behavior inputs.",
            "If the role layer improves, that is evidence for patch-before-widen. It is not evidence for formal training or signal rights.",
            "A strong result here should still be read as A-share-specific role discrimination, not as timeless universal truth.",
        ]
        return V112AOCPORoleLayerPatchPilotReport(
            summary=summary,
            target_rows=target_rows,
            role_patch_family_rows=role_patch_family_rows,
            role_confusion_comparison_rows=role_confusion_comparison_rows,
            interpretation=interpretation,
        )

    def _build_samples(
        self,
        *,
        truth_rows: list[dict[str, Any]],
        stage_map: dict[str, dict[str, str]],
        pilot_analyzer: V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer,
    ) -> list[CoreSkeletonSample]:
        client = TencentKlineClient()
        samples: list[CoreSkeletonSample] = []
        for row in truth_rows:
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
            bars["intraday_range_mean_10"] = (
                ((bars["high"] - bars["low"]) / bars["close"]).rolling(10, min_periods=5).mean()
            )
            bars["volume_cv_10"] = (
                bars["volume"].rolling(10, min_periods=5).std()
                / bars["volume"].rolling(10, min_periods=5).mean()
            )
            bars["future_close_20"] = bars["close"].shift(-20)
            bars["future_min_low_20"] = bars["low"][::-1].rolling(20, min_periods=1).min()[::-1].shift(-1)

            listing_board_tier, limit_amplitude_proxy = self._board_microstructure_values(symbol)

            for row_data in bars.itertuples(index=False):
                if pd.isna(row_data.future_close_20) or pd.isna(row_data.future_min_low_20):
                    continue
                trade_month = pd.Timestamp(row_data.date).strftime("%Y-%m")
                chosen_occurrence = self._resolve_occurrence(
                    trade_month=trade_month,
                    active_windows=active_windows,
                    stage_map=stage_map,
                )
                if chosen_occurrence is None:
                    continue
                stage_family = str(stage_map[chosen_occurrence]["stage_family"])
                feature_values = pilot_analyzer._feature_row(  # noqa: SLF001
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

                range_denom = (
                    float(row_data.high20) - float(row_data.low20)
                    if pd.notna(row_data.high20) and pd.notna(row_data.low20)
                    else 0.0
                )
                feature_values.update(
                    {
                        "listing_board_tier": listing_board_tier,
                        "limit_amplitude_proxy": limit_amplitude_proxy,
                        "realized_vol_10": float(row_data.realized_vol_10)
                        if pd.notna(row_data.realized_vol_10)
                        else 0.0,
                        "positive_day_ratio_10": float(row_data.positive_day_ratio_10)
                        if pd.notna(row_data.positive_day_ratio_10)
                        else 0.5,
                        "range_position_20": (
                            (float(row_data.close) - float(row_data.low20)) / range_denom
                            if range_denom > 0.0
                            else 0.5
                        ),
                        "drawdown_from_high20": (
                            float(row_data.close) / float(row_data.high20) - 1.0
                            if pd.notna(row_data.high20) and float(row_data.high20) != 0.0
                            else 0.0
                        ),
                        "intraday_range_mean_10": float(row_data.intraday_range_mean_10)
                        if pd.notna(row_data.intraday_range_mean_10)
                        else 0.0,
                        "volume_cv_10": float(row_data.volume_cv_10)
                        if pd.notna(row_data.volume_cv_10) and np.isfinite(float(row_data.volume_cv_10))
                        else 0.0,
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

    def _resolve_occurrence(
        self,
        *,
        trade_month: str,
        active_windows: list[str],
        stage_map: dict[str, dict[str, str]],
    ) -> str | None:
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


def write_v112ao_cpo_role_layer_patch_pilot_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AOCPORoleLayerPatchPilotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
