from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112FRefinementDesignReport:
    summary: dict[str, Any]
    bottleneck_classification: dict[str, Any]
    catalyst_state_refinement_rows: list[dict[str, Any]]
    label_boundary_review_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "bottleneck_classification": self.bottleneck_classification,
            "catalyst_state_refinement_rows": self.catalyst_state_refinement_rows,
            "label_boundary_review_rows": self.label_boundary_review_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112FRefinementDesignAnalyzer:
    """Design the next refinement move from hotspot review plus GBDT attribution."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        hotspot_review_payload: dict[str, Any],
        attribution_review_payload: dict[str, Any],
    ) -> V112FRefinementDesignReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("ready_for_refinement_design_next")):
            raise ValueError("V1.12F refinement design requires an open V1.12F charter.")

        hotspot_summary = dict(hotspot_review_payload.get("summary", {}))
        attribution_summary = dict(attribution_review_payload.get("summary", {}))
        block_rows = list(attribution_review_payload.get("block_ablation_rows", []))
        catalyst_row = next(row for row in block_rows if str(row.get("ablated_block")) == "catalyst_state")

        bottleneck_classification = {
            "primary_bottleneck_type": "feature_definition_or_non_redundancy_gap",
            "why_not_data_gap": (
                "The same-dataset sidecar already improved materially without widening scope, so the immediate blocker "
                "is not lack of samples inside the current pilot."
            ),
            "why_not_weight_only": (
                "The current reading is semantic rather than scalar: removing catalyst_state destroys consolidation control, "
                "which points to missing state meaning instead of a simple coefficient problem."
            ),
            "why_label_is_secondary": (
                "Label review still matters, but attribution says the first high-leverage move should refine catalyst-state "
                "meaning around late-cycle persistence and exhaustion before relabeling the full dataset."
            ),
        }

        catalyst_state_refinement_rows = [
            {
                "new_feature_name": "catalyst_freshness_state",
                "target_stage": "major_markup,high_level_consolidation",
                "semantic_question": "Is the catalyst newly strengthening, still active, or already stale?",
                "reading": "Distinguishes fresh continuation from late-stage carry optimism.",
            },
            {
                "new_feature_name": "cross_day_catalyst_persistence",
                "target_stage": "high_level_consolidation",
                "semantic_question": "Does the catalyst keep receiving cross-day confirmation instead of fading into one-off narrative memory?",
                "reading": "Should help separate healthy high-level bases from overextended stalls.",
            },
            {
                "new_feature_name": "theme_breadth_confirmation_proxy",
                "target_stage": "major_markup,high_level_consolidation",
                "semantic_question": "Is the catalyst still expanding through the cohort, or is only the core name holding up?",
                "reading": "Adds the missing distinction between shared continuation and isolated late-stage overstay.",
            },
        ]

        label_boundary_review_rows = [
            {
                "label_boundary_name": "carry_constructive_in_high_level_consolidation",
                "priority": "secondary",
                "review_question": "Should high-level consolidation require stronger catalyst persistence before staying carry_constructive?",
            },
            {
                "label_boundary_name": "late_major_markup_carry_vs_watch",
                "priority": "secondary",
                "review_question": "Should late major-markup windows downgrade to watch_constructive when catalyst freshness is already decaying?",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v112f_refinement_design_v1",
            "primary_bottleneck_type": bottleneck_classification["primary_bottleneck_type"],
            "top_hotspot_reading": str(hotspot_summary.get("primary_reading", "")),
            "most_useful_block_by_hotspot_impact": str(attribution_summary.get("most_useful_block_by_hotspot_impact", "")),
            "recommend_feature_refinement_first": True,
            "recommend_label_refinement_first": False,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "The next move should not start by tuning weights.",
            "The strongest current evidence says catalyst-state semantics are underdefined in late major-markup and high-level consolidation.",
            "Label-boundary review remains useful, but as a second move after bounded catalyst-state refinement design.",
        ]
        return V112FRefinementDesignReport(
            summary=summary,
            bottleneck_classification=bottleneck_classification,
            catalyst_state_refinement_rows=catalyst_state_refinement_rows,
            label_boundary_review_rows=label_boundary_review_rows,
            interpretation=interpretation,
        )


def write_v112f_refinement_design_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112FRefinementDesignReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
