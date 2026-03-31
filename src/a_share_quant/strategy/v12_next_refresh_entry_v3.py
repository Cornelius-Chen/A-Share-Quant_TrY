from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12NextRefreshEntryV3Report:
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


class V12NextRefreshEntryV3Analyzer:
    """Prepare the next refresh entry after v5 exhausts without repairing the training gaps."""

    def analyze(
        self,
        *,
        v5_exhaustion_phase_check_payload: dict[str, Any],
        training_manifest_payload: dict[str, Any],
        catalyst_phase_check_payload: dict[str, Any],
    ) -> V12NextRefreshEntryV3Report:
        phase_summary = dict(v5_exhaustion_phase_check_payload.get("summary", {}))
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

        prepare_refresh_now = bool(phase_summary.get("do_prepare_next_refresh_entry_now"))
        catalyst_support_only = bool(catalyst_summary.get("keep_branch_report_only", True))
        next_batch_name = "market_research_v6_catalyst_supported_carry_persistence_refresh"

        summary = {
            "acceptance_posture": (
                "prepare_v12_next_refresh_entry_for_market_research_v6"
                if prepare_refresh_now
                else "hold_v12_next_refresh_entry_v3_until_v5_exhaustion_allows"
            ),
            "prepare_refresh_entry_now": prepare_refresh_now,
            "prepare_manifest_now": False,
            "recommended_next_batch_name": next_batch_name,
            "recommended_batch_posture": "criteria_first_true_carry_plus_clean_persistence_with_catalyst_context_support",
            "additional_carry_rows_needed": additional_carry_rows_needed,
            "additional_persistence_rows_needed": additional_persistence_rows_needed,
            "catalyst_branch_support_only": catalyst_support_only,
            "reopen_existing_local_substrate_now": False,
            "promote_catalyst_branch_now": False,
        }
        entry_rules = [
            {
                "rule_name": "batch_scope",
                "rule_value": {
                    "next_batch_name": next_batch_name,
                    "prepare_manifest_now": False,
                    "do_not_reopen_v5_local_replay": True,
                    "do_not_widen_existing_substrate_now": True,
                },
                "reading": "The next move should stay criteria-first and start as a new bounded refresh entry instead of reopening exhausted local lanes.",
            },
            {
                "rule_name": "training_gap_targets",
                "rule_value": {
                    "additional_carry_rows_needed": additional_carry_rows_needed,
                    "additional_persistence_rows_needed": additional_persistence_rows_needed,
                    "opening_count_frozen": True,
                },
                "reading": "True carry rows stay the primary target and clean persistence rows stay the secondary target while opening remains frozen.",
            },
            {
                "rule_name": "catalyst_support_role",
                "rule_value": {
                    "catalyst_branch_support_only": catalyst_support_only,
                    "do_not_promote_catalyst_branch_to_mainline": True,
                    "allow_catalyst_context_to_inform_symbol_selection": True,
                },
                "reading": "Catalyst context may support symbol selection, but it still cannot replace the carry-row-diversity objective or become a promoted retained branch.",
            },
        ]
        interpretation = [
            "V5 exhausted cleanly without repairing the remaining training gaps, so the next healthy move is another criteria-first refresh entry.",
            "That next refresh should keep the same primary objective, but it may use catalyst context in a bounded support role when selecting symbols.",
            "So the correct minimal action is to initialize a v6 entry, not to jump directly into a manifest or reopen existing replay zones.",
        ]
        return V12NextRefreshEntryV3Report(
            summary=summary,
            entry_rules=entry_rules,
            interpretation=interpretation,
        )


def write_v12_next_refresh_entry_v3_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12NextRefreshEntryV3Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
