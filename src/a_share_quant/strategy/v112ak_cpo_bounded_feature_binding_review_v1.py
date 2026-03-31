from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AKCPOBoundedFeatureBindingReviewReport:
    summary: dict[str, Any]
    binding_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "binding_rows": self.binding_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112AKCPOBoundedFeatureBindingReviewAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        dataset_assembly_payload: dict[str, Any],
        label_draft_payload: dict[str, Any],
    ) -> V112AKCPOBoundedFeatureBindingReviewReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112ak_now")):
            raise ValueError("V1.12AK must be open before feature binding review runs.")

        dataset_rows = list(dataset_assembly_payload.get("dataset_draft_rows", []))
        support_rows = {
            str(row.get("label_name")): row for row in label_draft_payload.get("family_support_matrix_rows", [])
        }
        truth_rows = [row for row in dataset_rows if bool(row.get("include_in_truth_candidate_rows"))]
        if not truth_rows:
            raise ValueError("V1.12AK requires truth-candidate rows from V1.12AJ.")

        ready_labels = []
        guarded_labels = []
        for row in label_draft_payload.get("family_support_matrix_rows", []):
            posture = str(row.get("support_posture"))
            label_name = str(row.get("label_name"))
            if posture == "supported_now":
                ready_labels.append(label_name)
            elif posture in {
                "supported_with_provisional_guard",
                "supported_with_known_operational_gaps",
                "supported_with_overlay_boundary_guard",
            }:
                guarded_labels.append(label_name)

        all_bindable_labels = ready_labels + guarded_labels
        binding_rows: list[dict[str, Any]] = []
        direct_bindable_count = 0
        guarded_bindable_count = 0
        blocked_count = 0

        for row in truth_rows:
            symbol = str(row.get("symbol"))
            cohort_layer = str(row.get("cohort_layer"))
            role_family = str(row.get("role_family"))
            active_windows = list(row.get("active_stage_windows", []))
            has_quiet_window = any("quiet_window" in window for window in active_windows)
            is_secondary = str(row.get("truth_tier")) == "secondary"

            for label_name in all_bindable_labels:
                support = support_rows[label_name]
                support_posture = str(support.get("support_posture"))
                primary_family = str(support.get("primary_support_family"))
                blocking_reason = ""

                if label_name in {"phase_progression_label", "role_state_label", "catalyst_sequence_label"}:
                    binding_posture = "direct_bindable_now"
                    direct_bindable_count += 1
                elif label_name == "board_condition_label":
                    binding_posture = "guarded_bindable_now"
                    guarded_bindable_count += 1
                elif label_name == "role_transition_label":
                    if symbol == "300308":
                        binding_posture = "row_specific_not_currently_bindable"
                        blocking_reason = "stable_core_anchor_has_low_role_variation_on_current_truth_windows"
                        blocked_count += 1
                    else:
                        binding_posture = "guarded_bindable_now"
                        guarded_bindable_count += 1
                elif label_name == "quiet_window_survival_label":
                    if has_quiet_window:
                        binding_posture = "guarded_bindable_now"
                        guarded_bindable_count += 1
                    else:
                        binding_posture = "row_specific_not_currently_bindable"
                        blocking_reason = "current_truth_row_has_no_explicit_quiet_window_attachment"
                        blocked_count += 1
                elif label_name == "failed_role_promotion_label":
                    if is_secondary:
                        binding_posture = "guarded_bindable_now"
                        guarded_bindable_count += 1
                    else:
                        binding_posture = "row_specific_not_currently_bindable"
                        blocking_reason = "current_primary_core_rows_are_not_the_main_failed_promotion_surface"
                        blocked_count += 1
                elif label_name == "spillover_maturity_boundary_label":
                    binding_posture = "row_specific_not_currently_bindable"
                    blocking_reason = "current_truth_candidate_rows_do_not_include_late_extension_or_spillover_surfaces"
                    blocked_count += 1
                else:
                    binding_posture = "row_specific_not_currently_bindable"
                    blocking_reason = "unsupported_by_current_row_geometry"
                    blocked_count += 1

                binding_rows.append(
                    {
                        "symbol": symbol,
                        "cohort_layer": cohort_layer,
                        "role_family": role_family,
                        "label_name": label_name,
                        "support_posture": support_posture,
                        "primary_support_family": primary_family,
                        "binding_posture": binding_posture,
                        "blocking_reason": blocking_reason,
                        "active_stage_windows": active_windows,
                        "reading": (
                            "This label can bind on the current truth row set."
                            if binding_posture != "row_specific_not_currently_bindable"
                            else "This label is globally allowed in principle, but not meaningfully bindable for this row on the current truth set."
                        ),
                    }
                )

        summary = {
            "acceptance_posture": "freeze_v112ak_cpo_bounded_feature_binding_review_v1",
            "truth_candidate_row_count": len(truth_rows),
            "evaluated_binding_count": len(binding_rows),
            "direct_bindable_count": direct_bindable_count,
            "guarded_bindable_count": guarded_bindable_count,
            "row_specific_blocked_count": blocked_count,
            "formal_label_freeze_now": False,
            "formal_training_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": "bounded_training_readiness_review_with_binding_gaps_explicit",
        }
        interpretation = [
            "V1.12AK shows that globally admitted labels are not equally bindable on the current truth row set.",
            "Quiet-window and spillover-boundary labels are especially weak on the present truth-candidate geometry.",
            "This keeps the project from mistaking bundle admission for actual row-level usability.",
        ]
        return V112AKCPOBoundedFeatureBindingReviewReport(
            summary=summary,
            binding_rows=binding_rows,
            interpretation=interpretation,
        )


def write_v112ak_cpo_bounded_feature_binding_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AKCPOBoundedFeatureBindingReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
