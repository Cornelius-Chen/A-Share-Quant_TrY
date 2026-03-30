from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12V5RefreshCriteriaReport:
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


class V12V5RefreshCriteriaAnalyzer:
    """Freeze symbol-selection criteria before opening the V1.2 v5 manifest."""

    def analyze(
        self,
        *,
        next_refresh_entry_payload: dict[str, Any],
        training_manifest_payload: dict[str, Any],
        carry_schema_payload: dict[str, Any],
    ) -> V12V5RefreshCriteriaReport:
        entry_summary = dict(next_refresh_entry_payload.get("summary", {}))
        manifest_rows = list(training_manifest_payload.get("manifest_rows", []))
        carry_schema_summary = dict(carry_schema_payload.get("summary", {}))

        if not bool(entry_summary.get("prepare_refresh_entry_now")):
            raise ValueError("V5 refresh criteria only open after the V5 refresh entry is prepared.")

        observable_fields = list(carry_schema_summary.get("required_fields", []))
        additional_carry_rows_needed = 0
        additional_persistence_rows_needed = 0
        for row in manifest_rows:
            class_name = str(row.get("class_name", ""))
            if class_name == "carry_row_present":
                additional_carry_rows_needed = int(row.get("additional_rows_needed", 0))
            elif class_name == "persistence_led":
                additional_persistence_rows_needed = int(row.get("additional_rows_needed", 0))

        criteria_rows = [
            {
                "criterion_name": "must_target_one_primary_training_gap",
                "criterion_type": "inclusion",
                "rule": {
                    "allowed_primary_targets": [
                        "true_carry_row",
                        "clean_persistence_row",
                    ],
                    "exactly_one_primary_target_per_symbol": True,
                },
                "reading": "Each v5 symbol should enter to solve one training-sample gap first; mixed multi-purpose admissions dilute the refresh.",
            },
            {
                "criterion_name": "must_support_carry_or_persistence_observability",
                "criterion_type": "inclusion",
                "rule": {
                    "carry_required_observable_fields": observable_fields,
                    "persistence_required_signature": "specialist_preserved_window_with_anchor_churn",
                    "must_support_acceptance_grade_row_classification": True,
                },
                "reading": "A v5 candidate must plausibly generate either a true carry row or a clean persistence row that survives the existing acceptance chain.",
            },
            {
                "criterion_name": "must_fill_known_training_gap",
                "criterion_type": "inclusion",
                "rule": {
                    "additional_carry_rows_needed": additional_carry_rows_needed,
                    "additional_persistence_rows_needed": additional_persistence_rows_needed,
                    "opening_count_frozen": True,
                },
                "reading": "The v5 refresh is tied to the current training manifest: it should fill the missing carry and persistence rows while leaving opening rows frozen.",
            },
            {
                "criterion_name": "exclude_opening_led_clone_as_primary_reason",
                "criterion_type": "exclusion",
                "rule": {
                    "exclude_opening_clone_chasing": True,
                    "exclude_if_primary_case_is_only_opening_edge": True,
                },
                "reading": "A candidate that only looks like another opening-led lane should not be admitted as a primary v5 target.",
            },
            {
                "criterion_name": "exclude_relabelled_non_carry_rows",
                "criterion_type": "exclusion",
                "rule": {
                    "exclude_penalty_relabelling_into_carry": True,
                    "exclude_deferred_basis_relabelling_into_carry": True,
                    "exclude_mixed_hold_examples_into_persistence": True,
                },
                "reading": "The new batch should not solve the gap by relabeling adjacent structures into carry or persistence classes.",
            },
            {
                "criterion_name": "exclude_locally_exhausted_replay_zone",
                "criterion_type": "exclusion",
                "rule": {
                    "exclude_v4_q2_a_local_hunt_zone": True,
                    "exclude_reopening_checked_high_priority_symbols": True,
                },
                "reading": "The checked local v4 q2/A hunt zone is already exhausted at high priority and should not be reused as a primary v5 source.",
            },
            {
                "criterion_name": "require_reference_base_novelty",
                "criterion_type": "inclusion",
                "rule": {
                    "must_be_new_vs_combined_reference_base": True,
                    "reference_base": "v1_plus_v2_seed_plus_v2_refresh_plus_v3_seed_plus_v4_refresh",
                },
                "reading": "V5 should continue the discipline of adding only genuinely new symbols against the accumulated reference base.",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v12_v5_refresh_symbol_selection_criteria",
            "criteria_count": len(criteria_rows),
            "recommended_next_batch_name": entry_summary.get("recommended_next_batch_name"),
            "prepare_manifest_now": False,
            "ready_to_open_v5_manifest_after_criteria": True,
            "additional_carry_rows_needed": additional_carry_rows_needed,
            "additional_persistence_rows_needed": additional_persistence_rows_needed,
            "carry_observable_field_count": len(observable_fields),
        }
        interpretation = [
            "The next v5 refresh should open only after its training-gap criteria are frozen, not directly from a generic desire for more samples.",
            "These criteria keep V1.2 focused on true carry rows and clean persistence rows by requiring acceptance-grade observability and by excluding opening-clone chasing.",
            "Once these criteria are accepted, the next healthy move is to draft the v5 manifest against them rather than reopen local replay on existing substrates.",
        ]
        return V12V5RefreshCriteriaReport(
            summary=summary,
            criteria_rows=criteria_rows,
            interpretation=interpretation,
        )


def write_v12_v5_refresh_criteria_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12V5RefreshCriteriaReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
