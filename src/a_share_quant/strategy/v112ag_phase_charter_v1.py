from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AGPhaseCharterReport:
    summary: dict[str, Any]
    charter: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "charter": self.charter,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112AGPhaseCharterAnalyzer:
    def analyze(
        self,
        *,
        cohort_map_payload: dict[str, Any],
        labeling_review_payload: dict[str, Any],
        dynamic_role_payload: dict[str, Any],
        feature_family_payload: dict[str, Any],
    ) -> V112AGPhaseCharterReport:
        cohort_summary = dict(cohort_map_payload.get("summary", {}))
        labeling_summary = dict(labeling_review_payload.get("summary", {}))
        dynamic_summary = dict(dynamic_role_payload.get("summary", {}))
        feature_summary = dict(feature_family_payload.get("summary", {}))
        if int(cohort_summary.get("object_row_count", 0)) <= 0:
            raise ValueError("V1.12AG requires the V1.12AA cohort map.")
        if int(labeling_summary.get("primary_labeling_surface_count", 0)) <= 0:
            raise ValueError("V1.12AG requires the V1.12AB labeling review.")
        if int(dynamic_summary.get("dynamic_feature_count", 0)) <= 0:
            raise ValueError("V1.12AG requires the V1.12AD dynamic role review.")
        if int(feature_summary.get("feature_family_count", 0)) <= 0:
            raise ValueError("V1.12AG requires the V1.12AF feature-family design review.")

        charter = {
            "phase_name": "V1.12AG CPO Bounded Label-Draft Assembly",
            "mission": (
                "Assemble a bounded, review-first CPO label draft that checks whether current label language "
                "is consistently supported by cohort, role, chronology, and feature-family structure without "
                "forcing false precision or leaking future information."
            ),
            "in_scope": [
                "freeze a minimal label surface skeleton",
                "freeze family-to-label support mappings",
                "run anti-leakage review against key draft labels",
                "preserve ambiguity through pending, weak-confidence, and review-only draft states",
            ],
            "out_of_scope": [
                "formal label freeze",
                "formal training",
                "formal signal generation",
                "auto-promotion of candidate features into truth",
            ],
            "success_criteria": [
                "important draft labels are supportable by current families rather than narrative intuition alone",
                "labels that need ex-post confirmation are explicitly split or downgraded",
                "spillover, board, role, and phase dimensions are not flattened into one crude strength label",
            ],
            "stop_criteria": [
                "pending rows are silently forced into clean draft labels",
                "draft labels require future outcome information without being marked confirmed-only",
                "overlay-only structures are promoted into core truth labels",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112ag_cpo_bounded_label_draft_assembly",
            "do_open_v112ag_now": True,
            "selected_parent_line": "v112aa_v112ab_v112ad_v112af_cpo_label_feature_cohort_consistency",
            "recommended_first_action": "freeze_v112ag_cpo_bounded_label_draft_assembly_v1",
        }
        interpretation = [
            "V1.12AG is an assembly and integrity check, not a pretraining sprint.",
            "The goal is to see whether labels, families, cohort layers, and dynamic roles fit together without hiding ambiguity.",
            "Formal labels and training remain closed throughout this phase.",
        ]
        return V112AGPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112ag_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AGPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
