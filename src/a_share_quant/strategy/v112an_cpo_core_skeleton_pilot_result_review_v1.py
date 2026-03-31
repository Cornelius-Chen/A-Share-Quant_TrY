from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score

from a_share_quant.strategy.v112am_cpo_extremely_small_core_skeleton_training_pilot_v1 import (
    CoreSkeletonSample,
    V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer,
    load_json_report,
)


@dataclass(slots=True)
class V112ANCPOCoreSkeletonPilotResultReviewReport:
    summary: dict[str, Any]
    family_ablation_rows: list[dict[str, Any]]
    role_confusion_rows: list[dict[str, Any]]
    correction_bucket_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "family_ablation_rows": self.family_ablation_rows,
            "role_confusion_rows": self.role_confusion_rows,
            "correction_bucket_rows": self.correction_bucket_rows,
            "interpretation": self.interpretation,
        }


class V112ANCPOCoreSkeletonPilotResultReviewAnalyzer:
    PILOT_FAMILIES = {
        "chronology_price_geometry_family": [
            "ret_5",
            "ret_20",
            "price_vs_ma20",
            "price_vs_ma60",
            "distance_to_high60",
            "distance_to_high120",
        ],
        "liquidity_confirmation_family": [
            "volume_ratio_5_20",
        ],
        "role_prior_family": [
            "cohort_sensitivity",
            "margin_sensitivity",
            "role_beta_proxy",
        ],
        "catalyst_presence_family": [
            "catalyst_presence_proxy",
        ],
    }

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        training_pilot_payload: dict[str, Any],
        dataset_assembly_payload: dict[str, Any],
        cycle_reconstruction_payload: dict[str, Any],
    ) -> V112ANCPOCoreSkeletonPilotResultReviewReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112an_now")):
            raise ValueError("V1.12AN must be open before the result review runs.")

        pilot_summary = dict(training_pilot_payload.get("summary", {}))
        if str(pilot_summary.get("recommended_next_posture")) != "owner_review_of_core_skeleton_pilot_results":
            raise ValueError("V1.12AN requires the completed V1.12AM pilot result payload.")

        pilot_analyzer = V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer()
        stage_map = pilot_analyzer._stage_map(list(cycle_reconstruction_payload.get("reconstructed_stage_rows", [])))  # noqa: SLF001
        truth_rows = [
            row
            for row in list(dataset_assembly_payload.get("dataset_draft_rows", []))
            if bool(row.get("include_in_truth_candidate_rows"))
        ]
        samples = pilot_analyzer._build_samples(truth_rows=truth_rows, stage_map=stage_map)  # noqa: SLF001
        samples.sort(key=lambda item: item.trade_date)
        x = np.array(
            [[sample.feature_values[name] for name in pilot_analyzer.FEATURE_NAMES] for sample in samples],
            dtype=float,
        )
        split_index = max(1, min(len(samples) - 1, int(len(samples) * 0.7)))
        x_train = x[:split_index]
        x_test = x[split_index:]
        test_samples = samples[split_index:]

        targets = {
            "phase_progression_label": [sample.stage_family for sample in samples],
            "role_state_label": [sample.role_family for sample in samples],
            "catalyst_sequence_label": [sample.catalyst_sequence_label for sample in samples],
        }

        family_ablation_rows: list[dict[str, Any]] = []
        role_confusion_rows: list[dict[str, Any]] = []
        correction_bucket_rows: list[dict[str, Any]] = []
        best_family_by_target: dict[str, tuple[str, float]] = {}
        correction_counter = Counter()

        for target_name, label_values in targets.items():
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

            full_accuracy = float(accuracy_score(y_test, gbdt_preds))
            best_drop = -1.0
            best_family = ""

            for family_name, family_features in self.PILOT_FAMILIES.items():
                feature_indexes = [
                    pilot_analyzer.FEATURE_NAMES.index(feature_name)
                    for feature_name in family_features
                    if feature_name in pilot_analyzer.FEATURE_NAMES
                ]
                x_train_masked = x_train.copy()
                x_test_masked = x_test.copy()
                if feature_indexes:
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
                accuracy_drop = round(full_accuracy - masked_accuracy, 4)
                if accuracy_drop > best_drop:
                    best_drop = accuracy_drop
                    best_family = family_name
                family_ablation_rows.append(
                    {
                        "target_name": target_name,
                        "family_name": family_name,
                        "full_accuracy": round(full_accuracy, 4),
                        "masked_accuracy": round(masked_accuracy, 4),
                        "accuracy_drop": accuracy_drop,
                        "reading": (
                            "Larger drop means the current target relies more on this pilot-local family."
                        ),
                    }
                )
            best_family_by_target[target_name] = (best_family, round(best_drop, 4))

            if target_name == "role_state_label":
                confusion_counter: Counter[tuple[str, str]] = Counter()
                corrected_counter: Counter[tuple[str, str]] = Counter()
                for idx, sample in enumerate(test_samples):
                    true_label = classes[int(y_test[idx])]
                    baseline_label = classes[int(baseline_preds[idx])]
                    gbdt_label = classes[int(gbdt_preds[idx])]
                    if gbdt_label != true_label:
                        confusion_counter[(true_label, gbdt_label)] += 1
                    if baseline_label != true_label and gbdt_label == true_label:
                        corrected_counter[(sample.stage_family, true_label)] += 1
                for (true_label, predicted_label), count in confusion_counter.most_common():
                    role_confusion_rows.append(
                        {
                            "true_role": true_label,
                            "predicted_role": predicted_label,
                            "count": count,
                            "reading": "GBDT still confuses these role families on the current tiny pilot.",
                        }
                    )
                for (stage_family, true_label), count in corrected_counter.most_common():
                    correction_counter[(target_name, stage_family, true_label)] += count

            for idx, sample in enumerate(test_samples):
                true_label = classes[int(y_test[idx])]
                baseline_label = classes[int(baseline_preds[idx])]
                gbdt_label = classes[int(gbdt_preds[idx])]
                if baseline_label != true_label and gbdt_label == true_label:
                    correction_counter[(target_name, sample.stage_family, true_label)] += 1

        for (target_name, stage_family, corrected_true_class), count in correction_counter.most_common():
            correction_bucket_rows.append(
                {
                    "target_name": target_name,
                    "stage_family": stage_family,
                    "corrected_true_class": corrected_true_class,
                    "count": count,
                    "reading": "These are the cases where the guardrail missed and GBDT recovered the correct target state.",
                }
            )

        summary = {
            "acceptance_posture": "freeze_v112an_cpo_core_skeleton_pilot_result_review_v1",
            "sample_count": len(samples),
            "test_count": len(test_samples),
            "family_ablation_count": len(family_ablation_rows),
            "role_confusion_count": len(role_confusion_rows),
            "correction_bucket_count": len(correction_bucket_rows),
            "best_family_for_phase": best_family_by_target["phase_progression_label"][0],
            "best_family_drop_for_phase": best_family_by_target["phase_progression_label"][1],
            "best_family_for_catalyst_sequence": best_family_by_target["catalyst_sequence_label"][0],
            "best_family_drop_for_catalyst_sequence": best_family_by_target["catalyst_sequence_label"][1],
            "best_family_for_role_state": best_family_by_target["role_state_label"][0],
            "best_family_drop_for_role_state": best_family_by_target["role_state_label"][1],
            "formal_training_still_forbidden": True,
            "formal_signal_generation_still_forbidden": True,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": "owner_decide_whether_to_widen_pilot_or_patch_role_layer",
        }
        interpretation = [
            "Phase and catalyst-sequence are learned best because the current tiny pilot gives them strong stage-aligned geometry and catalyst-presence support.",
            "Role-state remains harder because the current secondary rows still contain adjacent-role similarity and the pilot-local feature set only partially encodes role handoff.",
            "GBDT adds most value where baseline misses stage-conditioned structure rather than where labels are already trivially separated.",
        ]
        return V112ANCPOCoreSkeletonPilotResultReviewReport(
            summary=summary,
            family_ablation_rows=family_ablation_rows,
            role_confusion_rows=role_confusion_rows,
            correction_bucket_rows=correction_bucket_rows,
            interpretation=interpretation,
        )


def write_v112an_cpo_core_skeleton_pilot_result_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ANCPOCoreSkeletonPilotResultReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
