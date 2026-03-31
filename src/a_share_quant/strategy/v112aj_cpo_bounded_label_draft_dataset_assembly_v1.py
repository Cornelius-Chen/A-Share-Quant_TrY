from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AJCPOBoundedLabelDraftDatasetAssemblyReport:
    summary: dict[str, Any]
    dataset_draft_rows: list[dict[str, Any]]
    label_bundle_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "dataset_draft_rows": self.dataset_draft_rows,
            "label_bundle_rows": self.label_bundle_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112AJCPOBoundedLabelDraftDatasetAssemblyAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        cohort_map_payload: dict[str, Any],
        labeling_review_payload: dict[str, Any],
        owner_review_payload: dict[str, Any],
    ) -> V112AJCPOBoundedLabelDraftDatasetAssemblyReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112aj_now")):
            raise ValueError("V1.12AJ must be open before dataset assembly runs.")

        cohort_rows = list(cohort_map_payload.get("object_role_time_rows", []))
        surface_rows = list(labeling_review_payload.get("labeling_surface_rows", []))
        owner_rows = list(owner_review_payload.get("review_rows", []))
        if not cohort_rows or not surface_rows or not owner_rows:
            raise ValueError("V1.12AJ requires cohort, surface, and owner-review inputs.")

        cohort_by_symbol = {str(row.get("symbol")): row for row in cohort_rows}
        owner_by_label = {str(row.get("label_name")): row for row in owner_rows}

        draft_ready_labels = [
            row["label_name"]
            for row in owner_rows
            if str(row.get("owner_disposition")) == "preserve_as_draft_ready_label"
        ]
        guarded_labels = [
            row["label_name"]
            for row in owner_rows
            if str(row.get("owner_disposition")) == "preserve_as_guarded_draft_label"
        ]
        review_only_labels = [
            row["label_name"]
            for row in owner_rows
            if str(row.get("owner_disposition")) == "preserve_as_review_only_future_target"
        ]
        confirmed_only_labels = [
            row["label_name"]
            for row in owner_rows
            if str(row.get("owner_disposition")) == "preserve_as_confirmed_only_review_label"
        ]

        dataset_draft_rows: list[dict[str, Any]] = []
        truth_candidate_count = 0
        context_only_count = 0

        for surface_row in surface_rows:
            symbol = str(surface_row.get("symbol"))
            surface = str(surface_row.get("labeling_surface"))
            cohort_row = cohort_by_symbol.get(symbol)
            if cohort_row is None:
                raise ValueError(f"Missing cohort row for symbol {symbol}.")

            if surface == "primary_labeling_surface":
                dataset_posture = "primary_truth_candidate_row"
                include_in_truth_candidate_rows = True
                truth_tier = "primary"
                truth_candidate_count += 1
            elif surface == "secondary_labeling_surface":
                dataset_posture = "secondary_truth_candidate_row"
                include_in_truth_candidate_rows = True
                truth_tier = "secondary"
                truth_candidate_count += 1
            elif surface == "review_support_surface":
                dataset_posture = "review_support_context_row"
                include_in_truth_candidate_rows = False
                truth_tier = "context_only"
                context_only_count += 1
            elif surface == "overlay_only_surface":
                dataset_posture = "overlay_only_context_row"
                include_in_truth_candidate_rows = False
                truth_tier = "context_only"
                context_only_count += 1
            else:
                dataset_posture = "excluded_pending_context_row"
                include_in_truth_candidate_rows = False
                truth_tier = "context_only"
                context_only_count += 1

            dataset_draft_rows.append(
                {
                    "symbol": symbol,
                    "cohort_layer": cohort_row.get("cohort_layer"),
                    "role_family": cohort_row.get("role_family"),
                    "labeling_surface": surface,
                    "dataset_posture": dataset_posture,
                    "truth_tier": truth_tier,
                    "include_in_truth_candidate_rows": include_in_truth_candidate_rows,
                    "active_stage_windows": cohort_row.get("active_stage_windows"),
                    "allowed_ready_labels": draft_ready_labels if include_in_truth_candidate_rows else [],
                    "allowed_guarded_labels": guarded_labels if include_in_truth_candidate_rows else [],
                    "excluded_from_truth_labels": review_only_labels + confirmed_only_labels,
                    "context_reading": (
                        "truth-candidate row"
                        if include_in_truth_candidate_rows
                        else "preserve as context only; do not promote into draft truth"
                    ),
                }
            )

        label_bundle_rows = []
        for label_name in draft_ready_labels + guarded_labels + review_only_labels + confirmed_only_labels:
            owner_row = owner_by_label[label_name]
            owner_disposition = str(owner_row.get("owner_disposition"))
            if owner_disposition == "preserve_as_draft_ready_label":
                dataset_bundle_posture = "allow_into_truth_candidate_bundle"
            elif owner_disposition == "preserve_as_guarded_draft_label":
                dataset_bundle_posture = "allow_into_truth_candidate_bundle_with_guard"
            else:
                dataset_bundle_posture = "exclude_from_truth_candidate_bundle"

            label_bundle_rows.append(
                {
                    "label_name": label_name,
                    "owner_disposition": owner_disposition,
                    "dataset_bundle_posture": dataset_bundle_posture,
                    "reading": owner_row.get("reading"),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v112aj_cpo_bounded_label_draft_dataset_assembly_v1",
            "dataset_row_count": len(dataset_draft_rows),
            "truth_candidate_row_count": truth_candidate_count,
            "context_only_row_count": context_only_count,
            "ready_label_count": len(draft_ready_labels),
            "guarded_label_count": len(guarded_labels),
            "review_only_label_count": len(review_only_labels),
            "confirmed_only_label_count": len(confirmed_only_labels),
            "formal_label_freeze_now": False,
            "formal_training_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": "bounded_feature_binding_review_before_any_training_readiness_claim",
        }
        interpretation = [
            "V1.12AJ assembles the first dataset-shaped CPO label draft without pretending every row or label is truth-ready.",
            "Primary and secondary surfaces become truth-candidate rows; support, overlay, and pending rows remain explicit context.",
            "Only ready and guarded labels enter the truth-candidate bundle.",
        ]
        return V112AJCPOBoundedLabelDraftDatasetAssemblyReport(
            summary=summary,
            dataset_draft_rows=dataset_draft_rows,
            label_bundle_rows=label_bundle_rows,
            interpretation=interpretation,
        )


def write_v112aj_cpo_bounded_label_draft_dataset_assembly_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AJCPOBoundedLabelDraftDatasetAssemblyReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
