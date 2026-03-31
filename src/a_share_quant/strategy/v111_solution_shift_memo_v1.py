from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V111SolutionShiftMemoReport:
    summary: dict[str, Any]
    memo: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "memo": self.memo,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V111SolutionShiftMemoAnalyzer:
    """Emit a data-acquisition memo after the current policy-followthrough pool is exhausted."""

    def analyze(
        self,
        *,
        v110a_phase_closure_payload: dict[str, Any],
        v110a_cross_family_probe_payload: dict[str, Any],
    ) -> V111SolutionShiftMemoReport:
        closure_summary = dict(v110a_phase_closure_payload.get("summary", {}))
        probe_summary = dict(v110a_cross_family_probe_payload.get("summary", {}))

        if not bool(closure_summary.get("enter_v110a_waiting_state_now")):
            raise ValueError("V1.10A must be in waiting state before solution-shift memo generation.")

        memo = {
            "memo_type": "Data Acquisition Plan",
            "current_primary_bottleneck_category": "data_or_evidence_gap",
            "why_current_path_no_longer_adds_decision_value": (
                "The current bounded policy-followthrough pool has only two visible candidates and both remain inside the "
                "existing 300750 anchor family, so another same-pool probe would repeat the same negative result."
            ),
            "proposed_shift": (
                "Build sustained catalyst evidence acquisition infrastructure that can generate genuinely new, point-in-time, "
                "source-aware, market-confirmed policy-followthrough candidates beyond the current symbol family."
            ),
            "how_the_shift_changes_the_decision_basis": (
                "It changes the evidence source itself rather than recycling the same bounded pool, allowing future "
                "promotion judgment to rest on new family-level evidence instead of repeated re-review."
            ),
            "why_this_is_not_just_more_artifacts": (
                "The output defines acquisition scope, source hierarchy, admissibility, novelty rules, point-in-time "
                "recording, and refresh cadence that can repeatedly produce new candidates."
            ),
            "freeze_reason_if_no_viable_shift_exists": "",
        }
        summary = {
            "acceptance_posture": "emit_solution_shift_memo_as_data_acquisition_plan",
            "triggered_from_exhausted_pool": bool(probe_summary.get("successful_negative_probe")),
            "recommended_next_phase_name": "V1.11 Sustained Catalyst Evidence Acquisition Infrastructure",
            "do_open_v111_now": True,
        }
        interpretation = [
            "The correct response to the exhausted policy-followthrough pool is to change evidence acquisition, not to continue same-pool probing.",
            "This memo therefore selects Data Acquisition Plan as the single allowed solution-shift type.",
            "The next lawful move is an exploration-layer phase that defines sustained evidence acquisition infrastructure.",
        ]
        return V111SolutionShiftMemoReport(summary=summary, memo=memo, interpretation=interpretation)


def write_v111_solution_shift_memo_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V111SolutionShiftMemoReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
