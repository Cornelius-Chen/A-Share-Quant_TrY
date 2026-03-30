from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12BatchSubstrateDecisionReport:
    summary: dict[str, Any]
    decision_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "decision_rows": self.decision_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V12BatchSubstrateDecisionAnalyzer:
    """Choose the next V1.2 posture after v4 local hunt exhaustion."""

    def analyze(
        self,
        *,
        phase_readiness_payload: dict[str, Any],
        v4_reassessment_payload: dict[str, Any],
        specialist_analysis_payload: dict[str, Any],
    ) -> V12BatchSubstrateDecisionReport:
        phase_summary = dict(phase_readiness_payload.get("summary", {}))
        v4_summary = dict(v4_reassessment_payload.get("summary", {}))
        top_rows = list(specialist_analysis_payload.get("top_opportunities", []))

        row_diversity_still_missing = bool(phase_summary.get("row_diversity_still_missing"))
        later_refresh_batch_needed = bool(phase_summary.get("do_open_new_refresh_batch_now"))
        v4_locally_exhausted = bool(v4_summary.get("checked_region_paused"))
        v4_still_active = bool(v4_summary.get("v4_still_active_substrate"))

        v3_best_row = next(
            (
                row
                for row in top_rows
                if str(row.get("dataset_name", "")) == "market_research_v3_factor_diversity_seed"
            ),
            None,
        )
        v4_best_row = next(
            (
                row
                for row in top_rows
                if str(row.get("dataset_name", "")) == "market_research_v4_carry_row_diversity_refresh"
            ),
            None,
        )

        decision_posture = (
            "prepare_next_refresh_batch_instead_of_reopening_existing_local_substrate"
            if row_diversity_still_missing and later_refresh_batch_needed and v4_locally_exhausted
            else "continue_existing_substrate_checks"
        )

        summary = {
            "acceptance_posture": decision_posture,
            "row_diversity_still_missing": row_diversity_still_missing,
            "later_refresh_batch_needed": later_refresh_batch_needed,
            "v4_still_active_substrate": v4_still_active,
            "v4_locally_exhausted": v4_locally_exhausted,
            "do_reopen_v3_local_lane_now": False,
            "do_reopen_v4_local_lane_now": False,
            "do_prepare_new_refresh_batch_now": (
                row_diversity_still_missing and later_refresh_batch_needed and v4_locally_exhausted
            ),
            "recommended_next_posture": "prepare_next_refresh_batch_for_carry_row_diversity",
        }
        decision_rows = [
            {
                "decision_name": "phase_gate",
                "actual": {
                    "row_diversity_still_missing": row_diversity_still_missing,
                    "do_open_new_refresh_batch_now": later_refresh_batch_needed,
                },
                "reading": "If V1.2 still says row diversity is missing, the default next move should be toward a later refresh batch, not more local replay.",
            },
            {
                "decision_name": "v4_reassessment",
                "actual": {
                    "v4_still_active_substrate": v4_still_active,
                    "v4_locally_exhausted": v4_locally_exhausted,
                },
                "reading": "An active substrate can still be locally exhausted; that combination argues against reopening the same checked local hunt area.",
            },
            {
                "decision_name": "specialist_map_context",
                "actual": {
                    "v3_best_row": v3_best_row,
                    "v4_best_row": v4_best_row,
                },
                "reading": "The broader specialist map shows v3 and v4 are both alive, but that does not override the local exhaustion and row-diversity gate.",
            },
        ]
        interpretation = [
            "The global V1.2 bottleneck remains missing carry row diversity.",
            "V4 should not be discarded, but its checked local hunt area should not be reopened right now.",
            "So the correct next step is to prepare the next refresh batch rather than bounce back into more local substrate replay.",
        ]
        return V12BatchSubstrateDecisionReport(
            summary=summary,
            decision_rows=decision_rows,
            interpretation=interpretation,
        )


def write_v12_batch_substrate_decision_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12BatchSubstrateDecisionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
