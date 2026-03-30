from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12NextRefreshEntryV2Report:
    summary: dict[str, Any]
    entry_rules: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "entry_rules": self.entry_rules,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V12NextRefreshEntryV2Analyzer:
    """Turn the current V1.2 high-level decision into the next criteria-first refresh entry."""

    def analyze(
        self,
        *,
        batch_substrate_decision_payload: dict[str, Any],
        training_manifest_payload: dict[str, Any],
        catalyst_phase_check_payload: dict[str, Any],
    ) -> V12NextRefreshEntryV2Report:
        decision_summary = dict(batch_substrate_decision_payload.get("summary", {}))
        manifest_rows = list(training_manifest_payload.get("manifest_rows", []))
        catalyst_summary = dict(catalyst_phase_check_payload.get("summary", {}))

        additional_carry_rows_needed = 0
        additional_persistence_rows_needed = 0
        for row in manifest_rows:
            class_name = str(row.get("class_name", ""))
            if class_name == "carry_row_present":
                additional_carry_rows_needed = int(row.get("additional_rows_needed", 0))
            elif class_name == "persistence_led":
                additional_persistence_rows_needed = int(row.get("additional_rows_needed", 0))

        prepare_refresh_now = bool(decision_summary.get("do_prepare_new_refresh_batch_now"))
        catalyst_support_only = bool(catalyst_summary.get("keep_branch_report_only", True))
        next_batch_name = "market_research_v5_carry_row_diversity_refresh"

        summary = {
            "acceptance_posture": (
                "prepare_v12_next_refresh_entry_for_market_research_v5"
                if prepare_refresh_now
                else "hold_v12_next_refresh_entry_v2_until_batch_decision_opens"
            ),
            "prepare_refresh_entry_now": prepare_refresh_now,
            "prepare_manifest_now": False,
            "recommended_next_batch_name": next_batch_name,
            "recommended_batch_posture": "criteria_first_true_carry_plus_clean_persistence_refresh",
            "additional_carry_rows_needed": additional_carry_rows_needed,
            "additional_persistence_rows_needed": additional_persistence_rows_needed,
            "catalyst_branch_support_only": catalyst_support_only,
            "reopen_existing_local_substrate_now": False,
        }
        entry_rules = [
            {
                "rule_name": "batch_scope",
                "rule_value": {
                    "next_batch_name": next_batch_name,
                    "prepare_manifest_now": False,
                    "do_not_reopen_v3_local_replay": True,
                    "do_not_reopen_v4_local_replay": True,
                },
                "reading": "The next refresh should open as a new criteria-first batch rather than by reopening already checked local substrate replay.",
            },
            {
                "rule_name": "training_class_targets",
                "rule_value": {
                    "additional_carry_rows_needed": additional_carry_rows_needed,
                    "additional_persistence_rows_needed": additional_persistence_rows_needed,
                    "opening_count_frozen": True,
                },
                "reading": "The new refresh should target true carry rows first and clean persistence rows second, while keeping the opening class frozen.",
            },
            {
                "rule_name": "explicit_exclusions",
                "rule_value": {
                    "exclude_reopening_locally_exhausted_v4_q2_a_region": True,
                    "exclude_relabelled_penalty_or_deferred_basis_rows": True,
                    "exclude_opening_clone_chasing": True,
                },
                "reading": "The refresh should not solve the bottleneck by relabeling or by returning to the already exhausted local q2/A hunt zone.",
            },
            {
                "rule_name": "catalyst_branch_role",
                "rule_value": {
                    "catalyst_branch_support_only": catalyst_support_only,
                    "do_not_promote_catalyst_branch_to_mainline": True,
                },
                "reading": "Catalyst context can support the next refresh design, but it should not replace the main carry-row-diversity objective.",
            },
        ]
        interpretation = [
            "The next V1.2 refresh should start from the current training sample gap, not from whichever local substrate was most recently checked.",
            "That means true carry rows remain the primary target, clean persistence rows remain the secondary target, and opening-led clone expansion remains out of scope.",
            "So the next healthy move is to freeze a new v5 refresh entry before any new manifest drafting begins.",
        ]
        return V12NextRefreshEntryV2Report(
            summary=summary,
            entry_rules=entry_rules,
            interpretation=interpretation,
        )


def write_v12_next_refresh_entry_v2_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12NextRefreshEntryV2Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
