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
class V112AXCPOGuardedBranchAdmittedPilotReport:
    summary: dict[str, Any]
    target_rows: list[dict[str, Any]]
    admitted_branch_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "target_rows": self.target_rows,
            "admitted_branch_rows": self.admitted_branch_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112AXCPOGuardedBranchAdmittedPilotAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        branch_admission_payload: dict[str, Any],
        dataset_assembly_payload: dict[str, Any],
        cycle_reconstruction_payload: dict[str, Any],
    ) -> V112AXCPOGuardedBranchAdmittedPilotReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112ax_now")):
            raise ValueError("V1.12AX must be open before the pilot runs.")

        admitted_symbols = {
            str(row.get("symbol"))
            for row in list(branch_admission_payload.get("branch_review_rows", []))
            if bool(row.get("guarded_training_context_admissible"))
        }
        if len(admitted_symbols) != 3:
            raise ValueError("V1.12AX expects exactly three guarded-admissible branch rows from V1.12AW.")

        dataset_rows = list(dataset_assembly_payload.get("dataset_draft_rows", []))
        pilot_rows = [
            row
            for row in dataset_rows
            if bool(row.get("include_in_truth_candidate_rows")) or str(row.get("symbol")) in admitted_symbols
        ]

        base_analyzer = V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer()
        role_patch_analyzer = V112AOCPORoleLayerPatchPilotAnalyzer()
        widen_analyzer = V112AUCPOBoundedRowGeometryWidenPilotAnalyzer()
        branch_patch_analyzer = V112AVCPOBranchRoleGeometryPatchPilotAnalyzer()
        stage_map = base_analyzer._stage_map(list(cycle_reconstruction_payload.get("reconstructed_stage_rows", [])))  # noqa: SLF001
        samples = widen_analyzer._build_samples(  # noqa: SLF001
            widened_rows=pilot_rows,
            stage_map=stage_map,
            pilot_analyzer=base_analyzer,
        )
        samples.sort(key=lambda item: item.trade_date)
        truth_index = {str(row.get("symbol")): row for row in pilot_rows}
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

        target_rows: list[dict[str, Any]] = []
        core_targets = {
            "phase_progression_label": [sample.stage_family for sample in samples],
            "role_state_label": [sample.role_family for sample in samples],
            "catalyst_sequence_label": [sample.catalyst_sequence_label for sample in samples],
        }
        for target_name, labels in core_targets.items():
            baseline_accuracy, gbdt_accuracy = self._run_target(labels=labels, x=x, split_index=split_index)
            target_rows.append(
                {
                    "target_name": target_name,
                    "baseline_accuracy": baseline_accuracy,
                    "gbdt_accuracy": gbdt_accuracy,
                    "gbdt_minus_baseline": round(gbdt_accuracy - baseline_accuracy, 4),
                }
            )

        guarded_defs = {
            "board_condition_label": widen_analyzer._board_condition_label,  # noqa: SLF001
            "role_transition_label": widen_analyzer._role_transition_label,  # noqa: SLF001
            "failed_role_promotion_label": widen_analyzer._failed_role_promotion_label,  # noqa: SLF001
        }
        for target_name, label_fn in guarded_defs.items():
            subset_samples = widen_analyzer._guarded_subset(target_name=target_name, samples=samples)  # noqa: SLF001
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
            labels = [label_fn(sample.role_family, sample.stage_family) for sample in subset_samples]
            baseline_accuracy, gbdt_accuracy = self._run_target(labels=labels, x=subset_x, split_index=subset_split)
            target_rows.append(
                {
                    "target_name": target_name,
                    "baseline_accuracy": baseline_accuracy,
                    "gbdt_accuracy": gbdt_accuracy,
                    "gbdt_minus_baseline": round(gbdt_accuracy - baseline_accuracy, 4),
                }
            )

        admitted_branch_rows = [
            {
                "symbol": str(row.get("symbol")),
                "role_family": str(row.get("role_family")),
                "active_stage_windows": list(row.get("active_stage_windows", [])),
                "pilot_posture": "guarded_training_context_row",
            }
            for row in pilot_rows
            if str(row.get("symbol")) in admitted_symbols
        ]
        core_rows = [row for row in target_rows if row["target_name"] in core_targets]
        guarded_rows = [row for row in target_rows if row["target_name"] not in core_targets]
        summary = {
            "acceptance_posture": "freeze_v112ax_cpo_guarded_branch_admitted_pilot_v1",
            "row_count_after_guarded_branch_admission": len(pilot_rows),
            "admitted_branch_row_count": len(admitted_branch_rows),
            "sample_count": len(samples),
            "core_targets_stable_after_guarded_branch_admission": all(float(row["gbdt_accuracy"]) >= 0.99 for row in core_rows),
            "guarded_targets_stable_after_guarded_branch_admission": all(float(row["gbdt_accuracy"]) >= 0.99 for row in guarded_rows),
            "best_target_after_guarded_branch_admission": max(target_rows, key=lambda row: float(row["gbdt_accuracy"]))["target_name"],
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": (
                "review_if_guarded_branch_rows_can_enter_the_next_bounded_training_layer"
                if all(float(row["gbdt_accuracy"]) >= 0.99 for row in core_rows)
                and all(float(row["gbdt_accuracy"]) >= 0.99 for row in guarded_rows)
                else "keep_guarded_branch_rows_bounded_and_do_not_widen_further"
            ),
        }
        interpretation = [
            "V1.12AX operationalizes the guarded branch admission cut from V1.12AW.",
            "This remains report-only and does not open formal training or signal rights.",
            "A successful result means the admitted branch subset is stable enough for the next bounded layer review.",
        ]
        return V112AXCPOGuardedBranchAdmittedPilotReport(
            summary=summary,
            target_rows=target_rows,
            admitted_branch_rows=admitted_branch_rows,
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
        model = HistGradientBoostingClassifier(max_depth=4, learning_rate=0.05, max_iter=150, random_state=42)
        model.fit(x_train, y_train)
        preds = model.predict(x_test)
        return round(float(accuracy_score(y_test, baseline_preds)), 4), round(float(accuracy_score(y_test, preds)), 4)


def write_v112ax_cpo_guarded_branch_admitted_pilot_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AXCPOGuardedBranchAdmittedPilotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
