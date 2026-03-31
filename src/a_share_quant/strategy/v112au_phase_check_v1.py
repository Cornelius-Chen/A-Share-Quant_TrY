from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AUPhaseCheckReport:
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


class V112AUPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        widen_payload: dict[str, Any],
    ) -> V112AUPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        widen_summary = dict(widen_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112au_as_bounded_row_geometry_widen_pilot",
            "do_open_v112au_now": charter_summary.get("do_open_v112au_now"),
            "core_targets_stable_after_row_widen": widen_summary.get("core_targets_stable_after_row_widen"),
            "guarded_targets_stable_after_row_widen": widen_summary.get("guarded_targets_stable_after_row_widen"),
            "row_count_after_widen": widen_summary.get("row_count_after_widen"),
            "allow_formal_training_now": False,
            "allow_formal_signal_generation_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": widen_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112au_row_widen",
                "actual": {
                    "row_count_after_widen": widen_summary.get("row_count_after_widen"),
                    "added_branch_row_count": widen_summary.get("added_branch_row_count"),
                    "core_targets_stable_after_row_widen": widen_summary.get("core_targets_stable_after_row_widen"),
                    "guarded_targets_stable_after_row_widen": widen_summary.get("guarded_targets_stable_after_row_widen"),
                },
                "reading": "The row-geometry widen is only successful if branch-row admission does not collapse the current post-patch stack.",
            }
        ]
        interpretation = [
            "V1.12AU is a bounded geometry experiment, not a training promotion pass.",
            "Formal training and signal rights remain closed.",
        ]
        return V112AUPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112au_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AUPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
