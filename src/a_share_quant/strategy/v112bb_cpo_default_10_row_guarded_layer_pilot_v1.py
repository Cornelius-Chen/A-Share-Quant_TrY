from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

os.environ.setdefault("PANDAS_NO_USE_NUMEXPR", "1")
os.environ.setdefault("PANDAS_NO_USE_BOTTLENECK", "1")

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score

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
class V112BBCPODefault10RowGuardedLayerPilotReport:
    summary: dict[str, Any]
    target_rows: list[dict[str, Any]]
    comparison_rows: list[dict[str, Any]]
    model_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "target_rows": self.target_rows,
            "comparison_rows": self.comparison_rows,
            "model_rows": self.model_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BBCPODefault10RowGuardedLayerPilotAnalyzer:
    CORE_TARGETS = (
        "phase_progression_label",
        "role_state_label",
        "catalyst_sequence_label",
    )
    GUARDED_TARGETS = (
        "board_condition_label",
        "role_transition_label",
        "failed_role_promotion_label",
    )

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        training_layer_extension_payload: dict[str, Any],
        cycle_reconstruction_payload: dict[str, Any],
        v112am_pilot_payload: dict[str, Any],
        v112ap_pilot_payload: dict[str, Any],
        v112ax_pilot_payload: dict[str, Any],
    ) -> V112BBCPODefault10RowGuardedLayerPilotReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112bb_now")):
            raise ValueError("V1.12BB must be open before the default-layer pilot runs.")

        training_layer_rows = list(training_layer_extension_payload.get("training_layer_rows", []))
        if len(training_layer_rows) != 10:
            raise ValueError("V1.12BB expects the frozen 10-row default training-facing layer from V1.12AZ.")

        base_analyzer = V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer()
        role_patch_analyzer = V112AOCPORoleLayerPatchPilotAnalyzer()
        widen_analyzer = V112AUCPOBoundedRowGeometryWidenPilotAnalyzer()
        branch_patch_analyzer = V112AVCPOBranchRoleGeometryPatchPilotAnalyzer()
        stage_map = base_analyzer._stage_map(list(cycle_reconstruction_payload.get("reconstructed_stage_rows", [])))  # noqa: SLF001
        samples = widen_analyzer._build_samples(  # noqa: SLF001
            widened_rows=training_layer_rows,
            stage_map=stage_map,
            pilot_analyzer=base_analyzer,
        )
        samples.sort(key=lambda item: item.trade_date)
        truth_index = {str(row.get("symbol")): row for row in training_layer_rows}
        impl_features = widen_analyzer._implementation_feature_map(samples=samples, truth_index=truth_index)  # noqa: SLF001

        x = np.array(
            [
                [sample.feature_values[name] for name in base_analyzer.FEATURE_NAMES + role_patch_analyzer.PATCH_FEATURE_NAMES]
                + [impl_features[(sample.trade_date, sample.symbol)][name] for name in widen_analyzer.IMPLEMENTATION_FEATURE_NAMES]
                + branch_patch_analyzer._branch_patch_values(sample=sample)  # noqa: SLF001
                for sample in samples
            ],
            dtype=float,
        )
        split_index = max(1, min(len(samples) - 1, int(len(samples) * 0.7)))
        test_samples = samples[split_index:]

        prior_7_core = {str(row.get("target_name")): row for row in list(v112am_pilot_payload.get("target_rows", []))}
        prior_7_guarded = {str(row.get("target_name")): row for row in list(v112ap_pilot_payload.get("guarded_target_rows", []))}
        prior_10_pilot = {str(row.get("target_name")): row for row in list(v112ax_pilot_payload.get("target_rows", []))}

        target_rows: list[dict[str, Any]] = []
        comparison_rows: list[dict[str, Any]] = []
        model_rows: list[dict[str, Any]] = []

        for target_name in self.CORE_TARGETS:
            labels = self._core_labels(target_name=target_name, samples=samples)
            baseline_accuracy, gbdt_accuracy, baseline_preds, gbdt_preds, y_test, classes = self._run_target(
                labels=labels,
                x=x,
                split_index=split_index,
            )
            prior_core_row = dict(prior_7_core[target_name])
            prior_10_row = dict(prior_10_pilot[target_name])
            target_rows.append(
                {
                    "target_name": target_name,
                    "target_posture": "core",
                    "baseline_accuracy_now": baseline_accuracy,
                    "gbdt_accuracy_now": gbdt_accuracy,
                    "gbdt_minus_baseline_now": round(gbdt_accuracy - baseline_accuracy, 4),
                    "gbdt_accuracy_vs_7_row_baseline": round(gbdt_accuracy - float(prior_core_row["gbdt_accuracy"]), 4),
                    "gbdt_accuracy_vs_prior_10_row_guarded_pilot": round(gbdt_accuracy - float(prior_10_row["gbdt_accuracy"]), 4),
                }
            )
            comparison_rows.append(
                {
                    "target_name": target_name,
                    "old_7_row_gbdt_accuracy": prior_core_row["gbdt_accuracy"],
                    "prior_10_row_guarded_pilot_gbdt_accuracy": prior_10_row["gbdt_accuracy"],
                    "current_default_10_row_gbdt_accuracy": gbdt_accuracy,
                    "reading": "Core targets should stay at least as stable as both the old 7-row baseline and the prior guarded-branch pilot.",
                }
            )
            model_rows.append(
                base_analyzer._model_row(  # noqa: SLF001
                    model_name="nearest_centroid_guardrail",
                    target_name=target_name,
                    preds=baseline_preds,
                    y_test=y_test,
                    classes=classes,
                    test_samples=test_samples,
                )
            )
            model_rows.append(
                base_analyzer._model_row(  # noqa: SLF001
                    model_name="hist_gradient_boosting_classifier",
                    target_name=target_name,
                    preds=gbdt_preds,
                    y_test=y_test,
                    classes=classes,
                    test_samples=test_samples,
                )
            )

        for target_name in self.GUARDED_TARGETS:
            subset_samples = self._guarded_subset_for_default_layer(
                target_name=target_name,
                samples=samples,
                truth_index=truth_index,
            )
            subset_x = np.array(
                [
                    [sample.feature_values[name] for name in base_analyzer.FEATURE_NAMES + role_patch_analyzer.PATCH_FEATURE_NAMES]
                    + [impl_features[(sample.trade_date, sample.symbol)][name] for name in widen_analyzer.IMPLEMENTATION_FEATURE_NAMES]
                    + branch_patch_analyzer._branch_patch_values(sample=sample)  # noqa: SLF001
                    for sample in subset_samples
                ],
                dtype=float,
            )
            subset_split = max(1, min(len(subset_samples) - 1, int(len(subset_samples) * 0.7)))
            labels = self._guarded_labels(target_name=target_name, samples=subset_samples, widen_analyzer=widen_analyzer)
            (
                baseline_accuracy,
                gbdt_accuracy,
                _baseline_preds,
                _gbdt_preds,
                _y_test,
                _classes,
            ) = self._run_target(labels=labels, x=subset_x, split_index=subset_split)
            prior_7_row = dict(prior_7_guarded[target_name])
            prior_10_row = dict(prior_10_pilot[target_name])
            target_rows.append(
                {
                    "target_name": target_name,
                    "target_posture": "guarded",
                    "eligible_symbol_count": len({sample.symbol for sample in subset_samples}),
                    "sample_count": len(subset_samples),
                    "baseline_accuracy_now": baseline_accuracy,
                    "gbdt_accuracy_now": gbdt_accuracy,
                    "gbdt_minus_baseline_now": round(gbdt_accuracy - baseline_accuracy, 4),
                    "gbdt_accuracy_vs_7_row_guarded_baseline": round(gbdt_accuracy - float(prior_7_row["gbdt_accuracy"]), 4),
                    "gbdt_accuracy_vs_prior_10_row_guarded_pilot": round(gbdt_accuracy - float(prior_10_row["gbdt_accuracy"]), 4),
                }
            )
            comparison_rows.append(
                {
                    "target_name": target_name,
                    "old_7_row_guarded_gbdt_accuracy": prior_7_row["gbdt_accuracy"],
                    "prior_10_row_guarded_pilot_gbdt_accuracy": prior_10_row["gbdt_accuracy"],
                    "current_default_10_row_gbdt_accuracy": gbdt_accuracy,
                    "reading": "Guarded targets should not degrade when the 10-row layer becomes the formal bounded default.",
                }
            )
            model_rows.append(
                {
                    "model_name": "nearest_centroid_guardrail",
                    "target_name": target_name,
                    "test_accuracy": baseline_accuracy,
                    "sample_count": len(subset_samples),
                }
            )
            model_rows.append(
                {
                    "model_name": "hist_gradient_boosting_classifier",
                    "target_name": target_name,
                    "test_accuracy": gbdt_accuracy,
                    "sample_count": len(subset_samples),
                }
            )

        core_rows = [row for row in target_rows if row["target_posture"] == "core"]
        guarded_rows = [row for row in target_rows if row["target_posture"] == "guarded"]
        phase_model_row = next(
            row
            for row in model_rows
            if row["model_name"] == "hist_gradient_boosting_classifier" and row["target_name"] == "phase_progression_label"
        )
        summary = {
            "acceptance_posture": "freeze_v112bb_cpo_default_10_row_guarded_layer_pilot_v1",
            "default_training_layer_row_count": len(training_layer_rows),
            "sample_count": len(samples),
            "core_target_count": len(core_rows),
            "guarded_target_count": len(guarded_rows),
            "core_targets_stable_vs_7_row_baseline": all(float(row["gbdt_accuracy_vs_7_row_baseline"]) >= 0.0 for row in core_rows),
            "guarded_targets_stable_vs_7_row_guarded_baseline": all(
                float(row["gbdt_accuracy_vs_7_row_guarded_baseline"]) >= 0.0 for row in guarded_rows
            ),
            "core_targets_consistent_vs_prior_10_row_guarded_pilot": all(
                float(row["gbdt_accuracy_vs_prior_10_row_guarded_pilot"]) >= 0.0 for row in core_rows
            ),
            "guarded_targets_consistent_vs_prior_10_row_guarded_pilot": all(
                float(row["gbdt_accuracy_vs_prior_10_row_guarded_pilot"]) >= 0.0 for row in guarded_rows
            ),
            "phase_constructive_phase_avg_forward_return_20d": phase_model_row["constructive_phase_avg_forward_return_20d"],
            "phase_constructive_phase_avg_max_drawdown_20d": phase_model_row["constructive_phase_avg_max_drawdown_20d"],
            "default_10_row_pilot_established": True,
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": (
                "use_10_row_default_layer_as_experimental_baseline_and_only_probe_300570_mixed_branch_if_further_row_widen_is_needed"
            ),
        }
        interpretation = [
            "V1.12BB turns the 10-row guarded layer from an admission decision into the actual default bounded pilot baseline.",
            "The result should be read as an experimental baseline freeze, not as formal training or signal readiness.",
            "Any further row widen should now be judged against this 10-row default layer rather than against the old 7-row skeleton.",
        ]
        return V112BBCPODefault10RowGuardedLayerPilotReport(
            summary=summary,
            target_rows=target_rows,
            comparison_rows=comparison_rows,
            model_rows=model_rows,
            interpretation=interpretation,
        )

    def _run_target(
        self,
        *,
        labels: list[str],
        x: np.ndarray,
        split_index: int,
    ) -> tuple[float, float, np.ndarray, np.ndarray, np.ndarray, list[str]]:
        classes = sorted(set(labels))
        label_to_int = {label: idx for idx, label in enumerate(classes)}
        y = np.array([label_to_int[label] for label in labels], dtype=int)
        x_train = x[:split_index]
        x_test = x[split_index:]
        y_train = y[:split_index]
        y_test = y[split_index:]
        baseline_preds = V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer()._nearest_centroid_predictions(  # noqa: SLF001
            x_train=x_train,
            y_train=y_train,
            x_test=x_test,
        )
        model = HistGradientBoostingClassifier(max_depth=4, learning_rate=0.05, max_iter=150, random_state=42)
        model.fit(x_train, y_train)
        preds = model.predict(x_test)
        return (
            round(float(accuracy_score(y_test, baseline_preds)), 4),
            round(float(accuracy_score(y_test, preds)), 4),
            baseline_preds,
            preds,
            y_test,
            classes,
        )

    def _core_labels(self, *, target_name: str, samples: list[Any]) -> list[str]:
        if target_name == "phase_progression_label":
            return [sample.stage_family for sample in samples]
        if target_name == "role_state_label":
            return [sample.role_family for sample in samples]
        if target_name == "catalyst_sequence_label":
            return [sample.catalyst_sequence_label for sample in samples]
        raise ValueError(target_name)

    def _guarded_subset_for_default_layer(
        self,
        *,
        target_name: str,
        samples: list[Any],
        truth_index: dict[str, dict[str, Any]],
    ) -> list[Any]:
        allowed_samples = [
            sample
            for sample in samples
            if target_name in list(truth_index[sample.symbol].get("allowed_guarded_labels", []))
        ]
        if target_name == "board_condition_label":
            return allowed_samples
        if target_name == "role_transition_label":
            return [sample for sample in allowed_samples if sample.role_family != "core_module_leader"]
        if target_name == "failed_role_promotion_label":
            return [
                sample
                for sample in allowed_samples
                if sample.role_family
                in {
                    "domestic_optics_platform_bridge",
                    "high_beta_module_extension",
                    "high_end_module_extension",
                    "smaller_cap_high_beta_module",
                }
            ]
        raise ValueError(target_name)

    def _guarded_labels(
        self,
        *,
        target_name: str,
        samples: list[Any],
        widen_analyzer: V112AUCPOBoundedRowGeometryWidenPilotAnalyzer,
    ) -> list[str]:
        if target_name == "board_condition_label":
            return [widen_analyzer._board_condition_label(sample.role_family, sample.stage_family) for sample in samples]  # noqa: SLF001
        if target_name == "role_transition_label":
            return [widen_analyzer._role_transition_label(sample.role_family, sample.stage_family) for sample in samples]  # noqa: SLF001
        if target_name == "failed_role_promotion_label":
            return [widen_analyzer._failed_role_promotion_label(sample.role_family, sample.stage_family) for sample in samples]  # noqa: SLF001
        raise ValueError(target_name)


def write_v112bb_cpo_default_10_row_guarded_layer_pilot_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BBCPODefault10RowGuardedLayerPilotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
