from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12V4RefreshCriteriaReport:
    summary: dict[str, Any]
    criteria_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "criteria_rows": self.criteria_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V12V4RefreshCriteriaAnalyzer:
    """Freeze symbol-selection criteria before opening the V1.2 v4 manifest."""

    def analyze(
        self,
        *,
        next_refresh_entry_payload: dict[str, Any],
        next_refresh_design_payload: dict[str, Any],
        carry_schema_payload: dict[str, Any],
        carry_pilot_payload: dict[str, Any],
    ) -> V12V4RefreshCriteriaReport:
        entry_summary = dict(next_refresh_entry_payload.get("summary", {}))
        design_targets = list(next_refresh_design_payload.get("target_rows", []))
        carry_schema_summary = dict(carry_schema_payload.get("summary", {}))
        carry_pilot_summary = dict(carry_pilot_payload.get("summary", {}))

        if not bool(entry_summary.get("prepare_refresh_entry_now")):
            raise ValueError("V4 refresh criteria only open after the v4 refresh entry is prepared.")

        observable_fields = list(carry_schema_summary.get("required_fields", []))
        distinct_score_count = int(carry_pilot_summary.get("distinct_score_count", 0))

        criteria_rows = [
            {
                "criterion_name": "must_target_one_primary_row_diversity_gap",
                "criterion_type": "inclusion",
                "rule": {
                    "allowed_primary_targets": [
                        "basis_spread_diversity",
                        "carry_duration_diversity",
                        "exit_alignment_diversity",
                        "cross_dataset_carry_reuse",
                    ],
                    "exactly_one_primary_target_per_symbol": True,
                },
                "reading": "Each v4 symbol should enter to solve one carry-row-diversity gap first; generic multi-purpose additions dilute the refresh.",
            },
            {
                "criterion_name": "must_be_observable_under_carry_schema",
                "criterion_type": "inclusion",
                "rule": {
                    "required_observable_fields": observable_fields,
                    "must_support_negative_cycle_basis_reading": True,
                },
                "reading": "A v4 candidate must plausibly generate rows that can populate the bounded carry schema, not just another specialist lane with no carry-like observables.",
            },
            {
                "criterion_name": "must_expand_score_dispersion",
                "criterion_type": "inclusion",
                "rule": {
                    "current_distinct_score_count": distinct_score_count,
                    "expected_effect": "increase_future_carry_score_dispersion",
                },
                "reading": "The refresh should be judged by whether it can create non-isomorphic carry rows and break the current one-score pilot state.",
            },
            {
                "criterion_name": "exclude_opening_led_clone_as_primary_reason",
                "criterion_type": "exclusion",
                "rule": {
                    "exclude_pure_opening_led_clone": True,
                    "exclude_if_no_carry_row_hypothesis": True,
                },
                "reading": "A candidate that only looks like another 002049-style opening lane should not be admitted as a primary v4 target.",
            },
            {
                "criterion_name": "exclude_generic_sample_growth",
                "criterion_type": "exclusion",
                "rule": {
                    "exclude_general_sample_growth": True,
                    "exclude_non_interpretable_symbol_expansion": True,
                },
                "reading": "V4 is a criteria-first carry refresh, not a broad size expansion exercise.",
            },
            {
                "criterion_name": "require_reference_base_novelty",
                "criterion_type": "inclusion",
                "rule": {
                    "must_be_new_vs_combined_reference_base": True,
                    "reference_base": "v1_plus_v2_seed_plus_v2_refresh_plus_v3_seed",
                },
                "reading": "V4 should continue the discipline of adding only genuinely new symbols against the accumulated reference base.",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v12_v4_refresh_symbol_selection_criteria",
            "criteria_count": len(criteria_rows),
            "recommended_next_batch_name": entry_summary.get("recommended_next_batch_name"),
            "prepare_manifest_now": False,
            "ready_to_open_v4_manifest_after_criteria": True,
            "current_distinct_score_count": distinct_score_count,
            "observable_field_count": len(observable_fields),
        }
        interpretation = [
            "The next v4 refresh should be opened only after symbol-selection criteria are frozen, not directly from a phase-level desire for more diversity.",
            "These criteria keep V1.2 focused on carry-row diversity by requiring schema-observable, score-dispersing rows and by excluding pure opening-led clones.",
            "Once these criteria are accepted, the next healthy move is to draft the v4 manifest against them rather than revisit replay on the current v3 map.",
        ]
        return V12V4RefreshCriteriaReport(
            summary=summary,
            criteria_rows=criteria_rows,
            interpretation=interpretation,
        )


def write_v12_v4_refresh_criteria_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12V4RefreshCriteriaReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
