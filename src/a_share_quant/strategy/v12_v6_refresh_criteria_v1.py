from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12V6RefreshCriteriaReport:
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


class V12V6RefreshCriteriaAnalyzer:
    """Freeze symbol-selection criteria for the catalyst-supported v6 refresh."""

    def analyze(
        self,
        *,
        next_refresh_entry_payload: dict[str, Any],
        training_manifest_payload: dict[str, Any],
        carry_schema_payload: dict[str, Any],
        catalyst_phase_check_payload: dict[str, Any],
    ) -> V12V6RefreshCriteriaReport:
        entry_summary = dict(next_refresh_entry_payload.get("summary", {}))
        manifest_rows = list(training_manifest_payload.get("manifest_rows", []))
        carry_schema_summary = dict(carry_schema_payload.get("summary", {}))
        catalyst_summary = dict(catalyst_phase_check_payload.get("summary", {}))

        if not bool(entry_summary.get("prepare_refresh_entry_now")):
            raise ValueError("V6 refresh criteria only open after the V6 refresh entry is prepared.")

        observable_fields = list(carry_schema_summary.get("summary", carry_schema_summary).get("required_fields", []))
        if not observable_fields:
            observable_fields = list(carry_schema_summary.get("required_fields", []))

        additional_carry_rows_needed = 0
        additional_persistence_rows_needed = 0
        for row in manifest_rows:
            class_name = str(row.get("class_name", ""))
            if class_name == "carry_row_present":
                additional_carry_rows_needed = int(row.get("additional_rows_needed", 0))
            elif class_name == "persistence_led":
                additional_persistence_rows_needed = int(row.get("additional_rows_needed", 0))

        catalyst_support_only = bool(catalyst_summary.get("keep_branch_report_only", True))
        context_separation_present = bool(catalyst_summary.get("context_separation_present", False))

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
                "reading": "Each v6 symbol still enters to solve one training gap first; the catalyst branch does not justify mixed multi-purpose admissions.",
            },
            {
                "criterion_name": "must_support_carry_or_persistence_observability",
                "criterion_type": "inclusion",
                "rule": {
                    "carry_required_observable_fields": observable_fields,
                    "persistence_required_signature": "specialist_preserved_window_with_anchor_churn",
                    "must_support_acceptance_grade_row_classification": True,
                },
                "reading": "A v6 candidate must still plausibly generate either a true carry row or a clean persistence row that survives the existing acceptance chain.",
            },
            {
                "criterion_name": "must_fill_known_training_gap",
                "criterion_type": "inclusion",
                "rule": {
                    "additional_carry_rows_needed": additional_carry_rows_needed,
                    "additional_persistence_rows_needed": additional_persistence_rows_needed,
                    "opening_count_frozen": True,
                },
                "reading": "V6 remains tied to the frozen training manifest: true carry rows first, clean persistence rows second, opening still frozen.",
            },
            {
                "criterion_name": "must_support_catalyst_context_observability",
                "criterion_type": "inclusion",
                "rule": {
                    "require_theme_or_sector_scope": True,
                    "require_market_context_fillable": True,
                    "catalyst_support_only": catalyst_support_only,
                },
                "reading": "Catalyst context stays support-only, but v6 symbols should allow bounded catalyst-context recording rather than living in a context blind spot.",
            },
            {
                "criterion_name": "exclude_single_pulse_only_as_primary_carry_reason",
                "criterion_type": "exclusion",
                "rule": {
                    "exclude_opening_clone_chasing": True,
                    "exclude_single_pulse_only_for_true_carry_primary_target": True,
                    "context_separation_present": context_separation_present,
                },
                "reading": "Because the bounded catalyst audit separated opening from persistence and carry, a single-pulse-only story should not be used as the main admission reason for a true-carry target.",
            },
            {
                "criterion_name": "prefer_multi_day_or_followthrough_context_for_supported_targets",
                "criterion_type": "preference",
                "rule": {
                    "prefer_multi_day_reinforcement_for_clean_persistence": True,
                    "prefer_policy_or_followthrough_context_for_true_carry": True,
                    "do_not_promote_catalyst_branch_to_mainline": True,
                },
                "reading": "Catalyst context can sharpen symbol selection by preferring multi-day reinforcement for persistence and followthrough-style context for carry without becoming the new mainline.",
            },
            {
                "criterion_name": "exclude_relabelled_non_carry_rows",
                "criterion_type": "exclusion",
                "rule": {
                    "exclude_penalty_relabelling_into_carry": True,
                    "exclude_deferred_basis_relabelling_into_carry": True,
                    "exclude_mixed_hold_examples_into_persistence": True,
                },
                "reading": "The new batch still cannot solve the gap by relabeling adjacent structures into carry or persistence classes.",
            },
            {
                "criterion_name": "exclude_reopening_existing_locally_exhausted_replay_zones",
                "criterion_type": "exclusion",
                "rule": {
                    "exclude_v4_q2_a_local_hunt_zone": True,
                    "exclude_v5_local_replay": True,
                },
                "reading": "V6 should not be built by reopening already exhausted local replay zones from v4 or v5.",
            },
            {
                "criterion_name": "require_reference_base_novelty",
                "criterion_type": "inclusion",
                "rule": {
                    "must_be_new_vs_combined_reference_base": True,
                    "reference_base": "v1_plus_v2_seed_plus_v2_refresh_plus_v3_seed_plus_v4_refresh_plus_v5_refresh",
                },
                "reading": "V6 should continue the discipline of adding only genuinely new symbols against the accumulated reference base.",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v12_v6_refresh_symbol_selection_criteria",
            "criteria_count": len(criteria_rows),
            "recommended_next_batch_name": entry_summary.get("recommended_next_batch_name"),
            "prepare_manifest_now": False,
            "ready_to_open_v6_manifest_after_criteria": True,
            "additional_carry_rows_needed": additional_carry_rows_needed,
            "additional_persistence_rows_needed": additional_persistence_rows_needed,
            "carry_observable_field_count": len(observable_fields),
            "catalyst_branch_support_only": catalyst_support_only,
        }
        interpretation = [
            "V6 should remain a training-gap-driven refresh rather than turning into a generic catalyst-news expansion.",
            "The catalyst branch now earns a bounded support role inside symbol selection, but it still cannot override the carry-row-diversity mission or reopen opening clone chasing.",
            "Once these criteria are frozen, the next healthy move is to draft the v6 manifest against them rather than replay old local substrates.",
        ]
        return V12V6RefreshCriteriaReport(
            summary=summary,
            criteria_rows=criteria_rows,
            interpretation=interpretation,
        )


def write_v12_v6_refresh_criteria_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12V6RefreshCriteriaReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
