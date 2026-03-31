from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ABCPOBoundedLabelingReviewReport:
    summary: dict[str, Any]
    labeling_surface_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "labeling_surface_rows": self.labeling_surface_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112ABCPOBoundedLabelingReviewAnalyzer:
    def analyze(self, *, phase_charter_payload: dict[str, Any], cohort_map_payload: dict[str, Any]) -> V112ABCPOBoundedLabelingReviewReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112ab_now")):
            raise ValueError("V1.12AB must be open before bounded labeling review runs.")

        rows = list(cohort_map_payload.get("object_role_time_rows", []))
        if not rows:
            raise ValueError("V1.12AB requires the V1.12AA cohort map.")

        labeling_surface_rows: list[dict[str, Any]] = []
        for row in rows:
            symbol = str(row.get("symbol"))
            cohort_layer = str(row.get("cohort_layer"))
            current_posture = str(row.get("current_posture"))

            if current_posture == "primary_core_truth_row":
                surface = "primary_labeling_surface"
            elif current_posture == "secondary_review_asset":
                surface = "secondary_labeling_surface"
            elif cohort_layer in {"branch_extension", "late_extension"}:
                surface = "review_support_surface"
            elif cohort_layer in {"spillover_candidate", "weak_memory"}:
                surface = "overlay_only_surface"
            else:
                surface = "excluded_pending_surface"

            labeling_surface_rows.append(
                {
                    "symbol": symbol,
                    "cohort_layer": cohort_layer,
                    "role_family": row.get("role_family"),
                    "labeling_surface": surface,
                    "active_stage_windows": row.get("active_stage_windows"),
                    "reading": (
                        "Later label drafting may use this row."
                        if surface in {"primary_labeling_surface", "secondary_labeling_surface"}
                        else "Keep outside formal label truth for now."
                    ),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v112ab_cpo_bounded_labeling_review_v1",
            "primary_labeling_surface_count": sum(1 for row in labeling_surface_rows if row["labeling_surface"] == "primary_labeling_surface"),
            "secondary_labeling_surface_count": sum(1 for row in labeling_surface_rows if row["labeling_surface"] == "secondary_labeling_surface"),
            "review_support_surface_count": sum(1 for row in labeling_surface_rows if row["labeling_surface"] == "review_support_surface"),
            "overlay_only_surface_count": sum(1 for row in labeling_surface_rows if row["labeling_surface"] == "overlay_only_surface"),
            "excluded_pending_surface_count": sum(1 for row in labeling_surface_rows if row["labeling_surface"] == "excluded_pending_surface"),
            "formal_label_freeze_still_forbidden": True,
            "formal_training_still_forbidden": True,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "The labeling review freezes surfaces, not labels.",
            "Core and secondary objects can now be discussed separately from support-only, overlay-only, and pending rows.",
            "This remains a boundary phase; formal labels are still closed.",
        ]
        return V112ABCPOBoundedLabelingReviewReport(
            summary=summary,
            labeling_surface_rows=labeling_surface_rows,
            interpretation=interpretation,
        )


def write_v112ab_cpo_bounded_labeling_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ABCPOBoundedLabelingReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
