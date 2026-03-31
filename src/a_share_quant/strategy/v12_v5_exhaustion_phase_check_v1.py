from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12V5ExhaustionPhaseCheckReport:
    summary: dict[str, Any]
    evidence_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "evidence_rows": self.evidence_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V12V5ExhaustionPhaseCheckAnalyzer:
    """Judge the phase posture after v5 exhausts its bounded lanes."""

    def analyze(
        self,
        *,
        v5_reassessment_payload: dict[str, Any],
        last_true_carry_probe_payload: dict[str, Any],
        training_manifest_payload: dict[str, Any],
        catalyst_phase_check_payload: dict[str, Any],
    ) -> V12V5ExhaustionPhaseCheckReport:
        reassessment_summary = dict(v5_reassessment_payload.get("summary", {}))
        last_probe_summary = dict(last_true_carry_probe_payload.get("summary", {}))
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

        v5_manifest_exhausted = (
            bool(reassessment_summary.get("do_open_last_true_carry_probe_now"))
            and not bool(last_probe_summary.get("do_continue_current_symbol_now"))
            and not bool(last_probe_summary.get("do_continue_v5_now"))
        )
        last_probe_opening_only = bool(last_probe_summary.get("opening_present")) and not bool(
            last_probe_summary.get("persistence_present")
        )
        v5_repaired_carry_gap = bool(last_probe_summary.get("lane_changes_training_reading"))
        prepare_next_refresh_entry = (
            v5_manifest_exhausted
            and additional_carry_rows_needed > 0
            and additional_persistence_rows_needed > 0
            and not v5_repaired_carry_gap
        )

        summary = {
            "acceptance_posture": (
                "close_v5_as_bounded_but_non_repairing_refresh"
                if prepare_next_refresh_entry
                else "hold_v5_exhaustion_phase_check_until_manifest_exhausts"
            ),
            "v5_manifest_exhausted": v5_manifest_exhausted,
            "last_probe_opening_led": last_probe_opening_only,
            "v5_repaired_carry_gap": v5_repaired_carry_gap,
            "primary_bottleneck_still_carry_row_diversity": additional_carry_rows_needed > 0,
            "remaining_clean_persistence_gap": additional_persistence_rows_needed,
            "remaining_true_carry_gap": additional_carry_rows_needed,
            "catalyst_branch_support_only": bool(catalyst_summary.get("keep_branch_report_only", True)),
            "do_reopen_v5_now": False,
            "do_prepare_next_refresh_entry_now": prepare_next_refresh_entry,
            "recommended_next_posture": (
                "prepare_v12_next_refresh_entry_for_market_research_v6"
                if prepare_next_refresh_entry
                else "hold_until_v5_manifest_exhaustion_is_complete"
            ),
        }
        evidence_rows = [
            {
                "evidence_name": "v5_reassessment_gate",
                "actual": {
                    "clean_persistence_track_exhausted": reassessment_summary.get(
                        "clean_persistence_track_exhausted"
                    ),
                    "do_open_last_true_carry_probe_now": reassessment_summary.get(
                        "do_open_last_true_carry_probe_now"
                    ),
                },
                "reading": "The v5 manifest only reaches exhaustion after the clean-persistence track fails and the last true-carry probe is consumed.",
            },
            {
                "evidence_name": "last_true_carry_probe",
                "actual": {
                    "acceptance_posture": last_probe_summary.get("acceptance_posture"),
                    "opening_present": last_probe_summary.get("opening_present"),
                    "persistence_present": last_probe_summary.get("persistence_present"),
                    "lane_changes_training_reading": last_probe_summary.get("lane_changes_training_reading"),
                },
                "reading": "The last true-carry probe can exhaust the current manifest without repairing the carry-row-diversity gap.",
            },
            {
                "evidence_name": "remaining_training_gap",
                "actual": {
                    "remaining_clean_persistence_gap": additional_persistence_rows_needed,
                    "remaining_true_carry_gap": additional_carry_rows_needed,
                    "catalyst_branch_support_only": catalyst_summary.get("keep_branch_report_only"),
                },
                "reading": "Once v5 exhausts without new acceptance-grade rows, the remaining training gaps still justify another criteria-first refresh, with catalyst context staying in a support-only role.",
            },
        ]
        interpretation = [
            "V5 has now used up its bounded lanes without repairing the carry-row-diversity gap.",
            "That is a valid negative result, not a reason to widen replay inside v5.",
            "The correct next move is to prepare the next criteria-first refresh entry rather than reopening v5 locally or promoting the catalyst branch.",
        ]
        return V12V5ExhaustionPhaseCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v12_v5_exhaustion_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12V5ExhaustionPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
