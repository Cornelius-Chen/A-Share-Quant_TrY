from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score

from a_share_quant.strategy.v112ao_cpo_role_layer_patch_pilot_v1 import (
    V112AOCPORoleLayerPatchPilotAnalyzer,
)
from a_share_quant.strategy.v112am_cpo_extremely_small_core_skeleton_training_pilot_v1 import (
    V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer,
)


@dataclass(slots=True)
class V112APCPOBoundedSecondaryWidenPilotReport:
    summary: dict[str, Any]
    target_rows: list[dict[str, Any]]
    guarded_target_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "target_rows": self.target_rows,
            "guarded_target_rows": self.guarded_target_rows,
            "interpretation": self.interpretation,
        }


class V112APCPOBoundedSecondaryWidenPilotAnalyzer:
    GUARDED_TARGETS = (
        "board_condition_label",
        "role_transition_label",
        "failed_role_promotion_label",
    )

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        role_patch_payload: dict[str, Any],
        dataset_assembly_payload: dict[str, Any],
        binding_review_payload: dict[str, Any],
        cycle_reconstruction_payload: dict[str, Any],
    ) -> V112APCPOBoundedSecondaryWidenPilotReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112ap_now")):
            raise ValueError("V1.12AP must be open before the widen pilot runs.")

        ao_analyzer = V112AOCPORoleLayerPatchPilotAnalyzer()
        base_analyzer = V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer()
        stage_map = base_analyzer._stage_map(list(cycle_reconstruction_payload.get("reconstructed_stage_rows", [])))  # noqa: SLF001
        truth_rows = [
            row
            for row in list(dataset_assembly_payload.get("dataset_draft_rows", []))
            if bool(row.get("include_in_truth_candidate_rows"))
        ]
        samples = ao_analyzer._build_samples(  # noqa: SLF001
            truth_rows=truth_rows,
            stage_map=stage_map,
            pilot_analyzer=base_analyzer,
        )
        samples.sort(key=lambda item: item.trade_date)

        feature_names = base_analyzer.FEATURE_NAMES + ao_analyzer.PATCH_FEATURE_NAMES
        x = np.array([[sample.feature_values[name] for name in feature_names] for sample in samples], dtype=float)
        split_index = max(1, min(len(samples) - 1, int(len(samples) * 0.7)))

        prior_role_patch_targets = {
            str(row.get("target_name")): row for row in list(role_patch_payload.get("target_rows", []))
        }
        binding_rows = list(binding_review_payload.get("binding_rows", []))

        target_rows: list[dict[str, Any]] = []
        guarded_target_rows: list[dict[str, Any]] = []

        core_targets = {
            "phase_progression_label": [sample.stage_family for sample in samples],
            "role_state_label": [sample.role_family for sample in samples],
            "catalyst_sequence_label": [sample.catalyst_sequence_label for sample in samples],
        }
        for target_name, labels in core_targets.items():
            baseline_accuracy, gbdt_accuracy = self._run_target(
                labels=labels,
                x=x,
                split_index=split_index,
            )
            prior_row = dict(prior_role_patch_targets[target_name])
            target_rows.append(
                {
                    "target_name": target_name,
                    "gbdt_accuracy_before_widen": prior_row.get("gbdt_accuracy_after_patch"),
                    "gbdt_accuracy_after_widen": gbdt_accuracy,
                    "baseline_accuracy_after_widen": baseline_accuracy,
                    "gbdt_accuracy_change_vs_role_patch": round(
                        gbdt_accuracy - float(prior_row["gbdt_accuracy_after_patch"]),
                        4,
                    ),
                }
            )

        for target_name in self.GUARDED_TARGETS:
            eligible_symbols = {
                str(row.get("symbol"))
                for row in binding_rows
                if str(row.get("label_name")) == target_name
                and str(row.get("binding_posture")) == "guarded_bindable_now"
            }
            subset_samples = [sample for sample in samples if sample.symbol in eligible_symbols]
            subset_samples.sort(key=lambda item: item.trade_date)
            subset_x = np.array(
                [[sample.feature_values[name] for name in feature_names] for sample in subset_samples],
                dtype=float,
            )
            subset_split = max(1, min(len(subset_samples) - 1, int(len(subset_samples) * 0.7)))
            labels = self._guarded_labels(target_name=target_name, samples=subset_samples)
            baseline_accuracy, gbdt_accuracy = self._run_target(
                labels=labels,
                x=subset_x,
                split_index=subset_split,
            )
            guarded_target_rows.append(
                {
                    "target_name": target_name,
                    "eligible_symbol_count": len(eligible_symbols),
                    "sample_count": len(subset_samples),
                    "baseline_accuracy": baseline_accuracy,
                    "gbdt_accuracy": gbdt_accuracy,
                    "gbdt_minus_baseline": round(gbdt_accuracy - baseline_accuracy, 4),
                    "classes": sorted(set(labels)),
                }
            )

        core_targets_stable_after_widen = all(
            float(row["gbdt_accuracy_after_widen"]) >= float(row["gbdt_accuracy_before_widen"])
            for row in target_rows
        )
        guarded_targets_learnable = [row for row in guarded_target_rows if float(row["gbdt_minus_baseline"]) > 0.0]
        best_guarded_target = max(guarded_target_rows, key=lambda row: float(row["gbdt_minus_baseline"]))

        summary = {
            "acceptance_posture": "freeze_v112ap_cpo_bounded_secondary_widen_pilot_v1",
            "truth_candidate_row_count": len(truth_rows),
            "sample_count": len(samples),
            "core_target_count": len(target_rows),
            "guarded_target_count": len(guarded_target_rows),
            "core_targets_stable_after_widen": core_targets_stable_after_widen,
            "guarded_targets_learnable_count": len(guarded_targets_learnable),
            "best_guarded_target": best_guarded_target["target_name"],
            "best_guarded_target_gain": best_guarded_target["gbdt_minus_baseline"],
            "formal_training_still_forbidden": True,
            "formal_signal_generation_still_forbidden": True,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": (
                "review_if_feature_implementation_patch_should_precede_any_row_geometry_widen"
                if core_targets_stable_after_widen and guarded_targets_learnable
                else "do_not_widen_rows_yet_keep_scope_bounded"
            ),
        }
        interpretation = [
            "This pass widens the target stack, not the row geometry.",
            "If the guarded layer is learnable without collapsing the core layer, then the current role patch has survived one lawful widen step.",
            "This still does not authorize formal training or signal generation.",
        ]
        return V112APCPOBoundedSecondaryWidenPilotReport(
            summary=summary,
            target_rows=target_rows,
            guarded_target_rows=guarded_target_rows,
            interpretation=interpretation,
        )

    def _run_target(self, *, labels: list[str], x: np.ndarray, split_index: int) -> tuple[float, float]:
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
        model = HistGradientBoostingClassifier(
            max_depth=4,
            learning_rate=0.05,
            max_iter=150,
            random_state=42,
        )
        model.fit(x_train, y_train)
        preds = model.predict(x_test)
        return round(float(accuracy_score(y_test, baseline_preds)), 4), round(float(accuracy_score(y_test, preds)), 4)

    def _guarded_labels(self, *, target_name: str, samples: list[Any]) -> list[str]:
        if target_name == "board_condition_label":
            return [self._board_condition_label(sample.stage_family) for sample in samples]
        if target_name == "role_transition_label":
            return [self._role_transition_label(sample.role_family, sample.stage_family) for sample in samples]
        if target_name == "failed_role_promotion_label":
            return [self._failed_role_promotion_label(sample.role_family, sample.stage_family) for sample in samples]
        raise ValueError(f"Unsupported guarded target: {target_name}")

    def _board_condition_label(self, stage_family: str) -> str:
        return {
            "pre_ignition_watch": "latent_board",
            "ignition": "supportive_board",
            "main_markup": "supportive_board",
            "diffusion": "widening_board",
            "laggard_catchup": "mature_board",
            "divergence_and_decay": "pressured_board",
        }[stage_family]

    def _role_transition_label(self, role_family: str, stage_family: str) -> str:
        if stage_family == "diffusion":
            if role_family in {
                "domestic_optics_platform_bridge",
                "high_beta_module_extension",
                "high_end_module_extension",
                "smaller_cap_high_beta_module",
            }:
                return "challenger_activation"
            return "role_quality_split"
        if stage_family == "main_markup":
            if role_family == "core_module_leader":
                return "leader_lock_in"
            if role_family in {"high_beta_core_module", "upstream_component_platform"}:
                return "role_requalification"
        if stage_family == "divergence_and_decay":
            return "role_quality_split"
        return "stable_no_transition"

    def _failed_role_promotion_label(self, role_family: str, stage_family: str) -> str:
        if role_family in {
            "high_beta_module_extension",
            "high_end_module_extension",
            "smaller_cap_high_beta_module",
        }:
            if stage_family == "main_markup":
                return "promotion_at_risk"
            return "promotion_attempt_only"
        return "bridge_or_non_failure"


def write_v112ap_cpo_bounded_secondary_widen_pilot_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112APCPOBoundedSecondaryWidenPilotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
