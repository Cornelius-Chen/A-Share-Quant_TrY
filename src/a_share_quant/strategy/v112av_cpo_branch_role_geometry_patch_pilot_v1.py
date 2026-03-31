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


@dataclass(slots=True)
class V112AVCPOBranchRoleGeometryPatchPilotReport:
    summary: dict[str, Any]
    target_rows: list[dict[str, Any]]
    branch_patch_family_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "target_rows": self.target_rows,
            "branch_patch_family_rows": self.branch_patch_family_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112AVCPOBranchRoleGeometryPatchPilotAnalyzer:
    BRANCH_PATCH_FEATURE_NAMES = [
        "branch_subchain_code",
        "branch_stage_alignment_score",
        "branch_component_depth_score",
        "branch_route_focus_score",
    ]

    BRANCH_PATCH_FAMILIES = {
        "widened_pre_patch_family": None,
        "branch_role_geometry_patch_family": BRANCH_PATCH_FEATURE_NAMES,
    }

    BRANCH_CODE = {
        "connector_mpo_branch": 1.0,
        "laser_chip_component": 2.0,
        "silicon_photonics_component": 3.0,
        "packaging_process_enabler": 4.0,
    }
    BRANCH_ALIGNMENT = {
        "connector_mpo_branch": {"diffusion", "laggard_catchup"},
        "laser_chip_component": {"main_markup"},
        "silicon_photonics_component": {"main_markup"},
        "packaging_process_enabler": {"main_markup"},
    }
    BRANCH_DEPTH = {
        "connector_mpo_branch": 0.35,
        "laser_chip_component": 0.90,
        "silicon_photonics_component": 0.82,
        "packaging_process_enabler": 0.68,
    }
    BRANCH_FOCUS = {
        "connector_mpo_branch": 0.45,
        "laser_chip_component": 0.95,
        "silicon_photonics_component": 0.88,
        "packaging_process_enabler": 0.72,
    }

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        widen_pilot_payload: dict[str, Any],
        dataset_assembly_payload: dict[str, Any],
        cycle_reconstruction_payload: dict[str, Any],
    ) -> V112AVCPOBranchRoleGeometryPatchPilotReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112av_now")):
            raise ValueError("V1.12AV must be open before the patch pilot runs.")

        prior_rows = {str(row.get("target_name")): row for row in list(widen_pilot_payload.get("target_rows", []))}
        widen_analyzer = V112AUCPOBoundedRowGeometryWidenPilotAnalyzer()
        dataset_rows = list(dataset_assembly_payload.get("dataset_draft_rows", []))
        widened_rows = [
            row
            for row in dataset_rows
            if bool(row.get("include_in_truth_candidate_rows")) or str(row.get("symbol")) in widen_analyzer.BRANCH_SYMBOLS
        ]

        inner_pilot_analyzer = V112AUCPOBoundedRowGeometryWidenPilotAnalyzer()
        skeleton = V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer()
        stage_map = skeleton._stage_map(list(cycle_reconstruction_payload.get("reconstructed_stage_rows", [])))  # noqa: SLF001
        samples = inner_pilot_analyzer._build_samples(  # noqa: SLF001
            widened_rows=widened_rows,
            stage_map=stage_map,
            pilot_analyzer=skeleton,
        )
        samples.sort(key=lambda item: item.trade_date)
        truth_index = {str(row.get("symbol")): row for row in widened_rows}
        impl_features = inner_pilot_analyzer._implementation_feature_map(samples=samples, truth_index=truth_index)  # noqa: SLF001

        role_patch_names = list(V112AOCPORoleLayerPatchPilotAnalyzer.PATCH_FEATURE_NAMES)
        base_feature_names = V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer.FEATURE_NAMES + role_patch_names

        x = np.array(
            [
                [sample.feature_values[name] for name in base_feature_names]
                + [impl_features[(sample.trade_date, sample.symbol)][name] for name in inner_pilot_analyzer.IMPLEMENTATION_FEATURE_NAMES]
                + self._branch_patch_values(sample=sample)
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
                    "baseline_accuracy_before_patch": prior_row.get("baseline_accuracy_after_widen"),
                    "baseline_accuracy_after_patch": baseline_accuracy,
                    "gbdt_accuracy_before_patch": prior_row.get("gbdt_accuracy_after_widen"),
                    "gbdt_accuracy_after_patch": gbdt_accuracy,
                    "gbdt_accuracy_change_vs_v112au": round(gbdt_accuracy - float(prior_row["gbdt_accuracy_after_widen"]), 4),
                }
            )

        guarded_defs = {
            "board_condition_label": inner_pilot_analyzer._board_condition_label,  # noqa: SLF001
            "role_transition_label": inner_pilot_analyzer._role_transition_label,  # noqa: SLF001
            "failed_role_promotion_label": inner_pilot_analyzer._failed_role_promotion_label,  # noqa: SLF001
        }
        for target_name, label_fn in guarded_defs.items():
            subset_samples = inner_pilot_analyzer._guarded_subset(target_name=target_name, samples=samples)  # noqa: SLF001
            subset_x = np.array(
                [
                    [sample.feature_values[name] for name in base_feature_names]
                    + [impl_features[(sample.trade_date, sample.symbol)][name] for name in inner_pilot_analyzer.IMPLEMENTATION_FEATURE_NAMES]
                    + self._branch_patch_values(sample=sample)
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
                    "baseline_accuracy_before_patch": prior_row.get("baseline_accuracy_after_widen"),
                    "baseline_accuracy_after_patch": baseline_accuracy,
                    "gbdt_accuracy_before_patch": prior_row.get("gbdt_accuracy_after_widen"),
                    "gbdt_accuracy_after_patch": gbdt_accuracy,
                    "gbdt_accuracy_change_vs_v112au": round(gbdt_accuracy - float(prior_row["gbdt_accuracy_after_widen"]), 4),
                }
            )

        # role ablation only
        role_labels = [sample.role_family for sample in samples]
        full_role_accuracy = self._run_target(labels=role_labels, x=x, split_index=split_index)[1]
        masked_x = x.copy()
        start_idx = x.shape[1] - len(self.BRANCH_PATCH_FEATURE_NAMES)
        masked_x[:, start_idx:] = 0.0
        masked_role_accuracy = self._run_target(labels=role_labels, x=masked_x, split_index=split_index)[1]
        branch_patch_family_rows = [
            {
                "family_name": "branch_role_geometry_patch_family",
                "full_accuracy": full_role_accuracy,
                "masked_accuracy": masked_role_accuracy,
                "accuracy_drop": round(full_role_accuracy - masked_role_accuracy, 4),
                "reading": "Accuracy drop shows how much widened role-state relies on branch-role geometry features.",
            }
        ]

        core_rows = [row for row in target_rows if row["target_name"] in core_targets]
        guarded_rows = [row for row in target_rows if row["target_name"] not in core_targets]
        role_row = next(row for row in target_rows if row["target_name"] == "role_state_label")
        summary = {
            "acceptance_posture": "freeze_v112av_cpo_branch_role_geometry_patch_pilot_v1",
            "row_count_after_branch_patch": len(widened_rows),
            "sample_count": len(samples),
            "branch_patch_feature_count": len(self.BRANCH_PATCH_FEATURE_NAMES),
            "core_targets_stable_after_branch_patch": all(
                float(row["gbdt_accuracy_after_patch"]) >= float(row["gbdt_accuracy_before_patch"])
                for row in core_rows
            ),
            "guarded_targets_stable_after_branch_patch": all(
                float(row["gbdt_accuracy_after_patch"]) >= float(row["gbdt_accuracy_before_patch"])
                for row in guarded_rows
            ),
            "role_state_gbdt_accuracy_before_patch": role_row["gbdt_accuracy_before_patch"],
            "role_state_gbdt_accuracy_after_patch": role_row["gbdt_accuracy_after_patch"],
            "role_state_patch_gain": round(float(role_row["gbdt_accuracy_after_patch"]) - float(role_row["gbdt_accuracy_before_patch"]), 4),
            "branch_patch_family_role_accuracy_drop": branch_patch_family_rows[0]["accuracy_drop"],
            "allow_formal_training_now": False,
            "allow_formal_signal_generation_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": (
                "review_if_branch_rows_can_move_from_review_only_to_guarded_training_context"
                if all(float(row["gbdt_accuracy_after_patch"]) >= float(row["gbdt_accuracy_before_patch"]) for row in core_rows)
                and all(float(row["gbdt_accuracy_after_patch"]) >= float(row["gbdt_accuracy_before_patch"]) for row in guarded_rows)
                else "keep_branch_rows_as_review_only_even_after_patch"
            ),
        }
        interpretation = [
            "This patch tests whether widened branch-row failure was specifically a branch-role geometry problem.",
            "A successful result would justify guarded branch-row discussion, not formal training or signal rights.",
            "This remains report-only and localized to the widened branch geometry.",
        ]
        return V112AVCPOBranchRoleGeometryPatchPilotReport(
            summary=summary,
            target_rows=target_rows,
            branch_patch_family_rows=branch_patch_family_rows,
            interpretation=interpretation,
        )

    def _branch_patch_values(self, *, sample: Any) -> list[float]:
        role_family = str(sample.role_family)
        branch_subchain_code = self.BRANCH_CODE.get(role_family, 0.0)
        stage_family = str(sample.stage_family)
        stage_alignment_score = 1.0 if stage_family in self.BRANCH_ALIGNMENT.get(role_family, set()) else 0.0
        branch_depth_score = self.BRANCH_DEPTH.get(role_family, 0.0)
        branch_focus_score = self.BRANCH_FOCUS.get(role_family, 0.0)
        return [
            branch_subchain_code,
            stage_alignment_score,
            branch_depth_score,
            branch_focus_score,
        ]

    def _run_target(self, *, labels: list[str], x: np.ndarray, split_index: int) -> tuple[float, float]:
        classes = sorted(set(labels))
        label_to_int = {label: idx for idx, label in enumerate(classes)}
        y = np.array([label_to_int[label] for label in labels], dtype=int)
        x_train = x[:split_index]
        x_test = x[split_index:]
        y_train = y[:split_index]
        y_test = y[split_index:]
        nearest = V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer()._nearest_centroid_predictions(  # noqa: SLF001
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
        return round(float(accuracy_score(y_test, nearest)), 4), round(float(accuracy_score(y_test, preds)), 4)


def write_v112av_cpo_branch_role_geometry_patch_pilot_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AVCPOBranchRoleGeometryPatchPilotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
