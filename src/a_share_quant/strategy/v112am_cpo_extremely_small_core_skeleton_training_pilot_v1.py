from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any

os.environ.setdefault("PANDAS_NO_USE_NUMEXPR", "1")
os.environ.setdefault("PANDAS_NO_USE_BOTTLENECK", "1")

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score

from a_share_quant.strategy.v112a_price_cycle_inference_v1 import TencentKlineClient


@dataclass(slots=True)
class CoreSkeletonSample:
    trade_date: str
    symbol: str
    stage_family: str
    role_family: str
    catalyst_sequence_label: str
    feature_values: dict[str, float]
    forward_return_20d: float
    max_drawdown_20d: float


@dataclass(slots=True)
class V112AMCPOExtremelySmallCoreSkeletonTrainingPilotReport:
    summary: dict[str, Any]
    target_rows: list[dict[str, Any]]
    model_rows: list[dict[str, Any]]
    sample_rows_preview: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "target_rows": self.target_rows,
            "model_rows": self.model_rows,
            "sample_rows_preview": self.sample_rows_preview,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer:
    FEATURE_NAMES = [
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
    ]

    ROLE_FEATURES = {
        "core_anchor": (0.90, 0.80, 0.95),
        "core_beta": (1.00, 0.90, 1.00),
        "core_platform_confirmation": (0.78, 0.85, 0.82),
        "adjacent_bridge": (0.66, 0.62, 0.60),
        "adjacent_high_beta_extension": (0.82, 0.72, 0.78),
    }

    STAGE_CATALYST_PROXY = {
        "pre_ignition_watch": 0.25,
        "ignition": 1.0,
        "main_markup": 0.9,
        "diffusion": 0.65,
        "laggard_catchup": 0.35,
        "divergence_and_decay": 0.15,
    }

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        readiness_review_payload: dict[str, Any],
        dataset_assembly_payload: dict[str, Any],
        cycle_reconstruction_payload: dict[str, Any],
    ) -> V112AMCPOExtremelySmallCoreSkeletonTrainingPilotReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        readiness_summary = dict(readiness_review_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112am_now")):
            raise ValueError("V1.12AM must be open before the pilot runs.")
        if str(readiness_summary.get("bounded_training_pilot_scope")) != "extremely_small_core_skeleton_only":
            raise ValueError("V1.12AM only runs on the approved extremely small core-skeleton scope.")

        dataset_rows = list(dataset_assembly_payload.get("dataset_draft_rows", []))
        truth_rows = [row for row in dataset_rows if bool(row.get("include_in_truth_candidate_rows"))]
        stage_rows = list(cycle_reconstruction_payload.get("reconstructed_stage_rows", []))
        if not truth_rows or not stage_rows:
            raise ValueError("V1.12AM requires truth rows and reconstructed stage rows.")

        stage_map = self._stage_map(stage_rows)
        samples = self._build_samples(truth_rows=truth_rows, stage_map=stage_map)
        if len(samples) < 40:
            raise ValueError("V1.12AM requires at least 40 daily samples to make the tiny pilot meaningful.")

        samples.sort(key=lambda item: item.trade_date)
        x = np.array([[sample.feature_values[name] for name in self.FEATURE_NAMES] for sample in samples], dtype=float)
        split_index = max(1, min(len(samples) - 1, int(len(samples) * 0.7)))
        x_train = x[:split_index]
        x_test = x[split_index:]
        test_samples = samples[split_index:]

        target_defs = {
            "phase_progression_label": [sample.stage_family for sample in samples],
            "role_state_label": [sample.role_family for sample in samples],
            "catalyst_sequence_label": [sample.catalyst_sequence_label for sample in samples],
        }

        model_rows: list[dict[str, Any]] = []
        target_rows: list[dict[str, Any]] = []

        for target_name, label_values in target_defs.items():
            classes = sorted(set(label_values))
            label_to_int = {label: idx for idx, label in enumerate(classes)}
            y = np.array([label_to_int[label] for label in label_values], dtype=int)
            y_train = y[:split_index]
            y_test = y[split_index:]

            baseline_preds = self._nearest_centroid_predictions(x_train=x_train, y_train=y_train, x_test=x_test)

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

            target_rows.append(
                {
                    "target_name": target_name,
                    "class_count": len(classes),
                    "class_labels": classes,
                    "baseline_accuracy": baseline_accuracy,
                    "gbdt_accuracy": gbdt_accuracy,
                    "gbdt_minus_baseline": round(gbdt_accuracy - baseline_accuracy, 4),
                }
            )

            model_rows.append(
                self._model_row(
                    model_name="nearest_centroid_guardrail",
                    target_name=target_name,
                    preds=baseline_preds,
                    y_test=y_test,
                    classes=classes,
                    test_samples=test_samples,
                )
            )
            model_rows.append(
                self._model_row(
                    model_name="hist_gradient_boosting_classifier",
                    target_name=target_name,
                    preds=gbdt_preds,
                    y_test=y_test,
                    classes=classes,
                    test_samples=test_samples,
                )
            )

        best_target_gain = max(target_rows, key=lambda row: float(row["gbdt_minus_baseline"]))
        summary = {
            "acceptance_posture": "freeze_v112am_cpo_extremely_small_core_skeleton_training_pilot_v1",
            "sample_count": len(samples),
            "train_count": split_index,
            "test_count": len(samples) - split_index,
            "truth_candidate_row_count": len(truth_rows),
            "target_count": len(target_rows),
            "model_count": len(model_rows),
            "best_target_by_gbdt_gain": best_target_gain["target_name"],
            "best_target_gain": best_target_gain["gbdt_minus_baseline"],
            "bounded_training_pilot_scope": "extremely_small_core_skeleton_only",
            "formal_training_still_forbidden": True,
            "formal_signal_generation_still_forbidden": True,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": "owner_review_of_core_skeleton_pilot_results",
        }
        sample_rows_preview = [
            {
                "trade_date": sample.trade_date,
                "symbol": sample.symbol,
                "stage_family": sample.stage_family,
                "role_family": sample.role_family,
                "catalyst_sequence_label": sample.catalyst_sequence_label,
                "forward_return_20d": round(sample.forward_return_20d, 4),
                "max_drawdown_20d": round(sample.max_drawdown_20d, 4),
                **sample.feature_values,
            }
            for sample in samples[:12]
        ]
        interpretation = [
            "This is a deliberately tiny learnability pilot on the current core skeleton, not a broad production-grade training run.",
            "The experiment exists to expose whether the current skeleton can be learned at all before the project invests in broader implementation work.",
            "GBDT remains the primary black-box probe, while the nearest-centroid baseline acts as a guardrail comparator.",
        ]
        return V112AMCPOExtremelySmallCoreSkeletonTrainingPilotReport(
            summary=summary,
            target_rows=target_rows,
            model_rows=model_rows,
            sample_rows_preview=sample_rows_preview,
            interpretation=interpretation,
        )

    def _stage_map(self, stage_rows: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
        mapping: dict[str, dict[str, str]] = {}
        for row in stage_rows:
            occurrence_name = str(row.get("occurrence_name"))
            window = str(row.get("window"))
            start_month, end_month = [part.strip() for part in window.split("to")]
            mapping[occurrence_name] = {
                "stage_family": str(row.get("stage_family")),
                "start_month": start_month,
                "end_month": end_month,
            }
        return mapping

    def _build_samples(
        self,
        *,
        truth_rows: list[dict[str, Any]],
        stage_map: dict[str, dict[str, str]],
    ) -> list[CoreSkeletonSample]:
        client = TencentKlineClient()
        samples: list[CoreSkeletonSample] = []
        for row in truth_rows:
            symbol = str(row.get("symbol"))
            cohort_layer = str(row.get("cohort_layer"))
            role_family = str(row.get("role_family"))
            active_windows = [str(window) for window in row.get("active_stage_windows", [])]
            bars = client.fetch_daily_bars(symbol).sort_values("date").reset_index(drop=True)
            bars["ret_5"] = bars["close"].pct_change(5)
            bars["ret_20"] = bars["close"].pct_change(20)
            bars["ma20"] = bars["close"].rolling(20, min_periods=5).mean()
            bars["ma60"] = bars["close"].rolling(60, min_periods=20).mean()
            bars["high60"] = bars["high"].rolling(60, min_periods=20).max()
            bars["high120"] = bars["high"].rolling(120, min_periods=20).max()
            bars["vol5"] = bars["volume"].rolling(5, min_periods=3).mean()
            bars["vol20"] = bars["volume"].rolling(20, min_periods=5).mean()
            bars["future_close_20"] = bars["close"].shift(-20)
            bars["future_min_low_20"] = bars["low"][::-1].rolling(20, min_periods=1).min()[::-1].shift(-1)

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
                stage_info = stage_map[chosen_occurrence]
                stage_family = str(stage_info["stage_family"])
                samples.append(
                    CoreSkeletonSample(
                        trade_date=pd.Timestamp(row_data.date).strftime("%Y-%m-%d"),
                        symbol=symbol,
                        stage_family=stage_family,
                        role_family=role_family,
                        catalyst_sequence_label=self._catalyst_sequence_label(stage_family),
                        feature_values=self._feature_row(
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
                        ),
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

    def _catalyst_sequence_label(self, stage_family: str) -> str:
        return {
            "pre_ignition_watch": "preheat_watch",
            "ignition": "fresh_trigger",
            "main_markup": "validated_markup",
            "diffusion": "diffusion_extension",
            "laggard_catchup": "late_echo_maturity",
            "divergence_and_decay": "stale_or_conflicted",
        }[stage_family]

    def _feature_row(
        self,
        *,
        cohort_layer: str,
        stage_family: str,
        close: float,
        ret_5: float,
        ret_20: float,
        ma20: float,
        ma60: float,
        high60: float,
        high120: float,
        vol5: float,
        vol20: float,
    ) -> dict[str, float]:
        cohort_sensitivity, margin_sensitivity, role_beta = self.ROLE_FEATURES[cohort_layer]
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
            "catalyst_presence_proxy": self.STAGE_CATALYST_PROXY[stage_family],
        }

    def _nearest_centroid_predictions(self, *, x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray) -> np.ndarray:
        mean_vec = x_train.mean(axis=0)
        std_vec = x_train.std(axis=0)
        std_vec[std_vec == 0.0] = 1.0
        x_train_scaled = (x_train - mean_vec) / std_vec
        x_test_scaled = (x_test - mean_vec) / std_vec

        centroids = []
        centroid_classes = []
        for class_id in sorted(set(int(value) for value in y_train)):
            centroids.append(x_train_scaled[y_train == class_id].mean(axis=0))
            centroid_classes.append(class_id)
        centroid_matrix = np.vstack(centroids)

        preds: list[int] = []
        for idx in range(len(x_test_scaled)):
            distances = np.linalg.norm(centroid_matrix - x_test_scaled[idx], axis=1)
            preds.append(int(centroid_classes[int(np.argmin(distances))]))
        return np.array(preds, dtype=int)

    def _model_row(
        self,
        *,
        model_name: str,
        target_name: str,
        preds: np.ndarray,
        y_test: np.ndarray,
        classes: list[str],
        test_samples: list[CoreSkeletonSample],
    ) -> dict[str, Any]:
        accuracy = round(float(accuracy_score(y_test, preds)), 4)
        constructive_returns = [
            sample.forward_return_20d
            for idx, sample in enumerate(test_samples)
            if target_name == "phase_progression_label"
            and classes[int(preds[idx])] in {"ignition", "main_markup"}
        ]
        constructive_drawdowns = [
            sample.max_drawdown_20d
            for idx, sample in enumerate(test_samples)
            if target_name == "phase_progression_label"
            and classes[int(preds[idx])] in {"ignition", "main_markup"}
        ]
        return {
            "model_name": model_name,
            "target_name": target_name,
            "test_accuracy": accuracy,
            "constructive_phase_trade_count": len(constructive_returns),
            "constructive_phase_avg_forward_return_20d": round(float(mean(constructive_returns)), 4)
            if constructive_returns
            else 0.0,
            "constructive_phase_avg_max_drawdown_20d": round(float(mean(constructive_drawdowns)), 4)
            if constructive_drawdowns
            else 0.0,
        }


def write_v112am_cpo_extremely_small_core_skeleton_training_pilot_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AMCPOExtremelySmallCoreSkeletonTrainingPilotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
