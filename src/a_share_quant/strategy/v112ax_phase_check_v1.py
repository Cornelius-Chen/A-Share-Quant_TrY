from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AXPhaseCheckReport:
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


class V112AXPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        pilot_payload: dict[str, Any],
    ) -> V112AXPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        pilot_summary = dict(pilot_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112ax_as_guarded_branch_admitted_pilot",
            "do_open_v112ax_now": charter_summary.get("do_open_v112ax_now"),
            "row_count_after_guarded_branch_admission": pilot_summary.get("row_count_after_guarded_branch_admission"),
            "core_targets_stable_after_guarded_branch_admission": pilot_summary.get("core_targets_stable_after_guarded_branch_admission"),
            "guarded_targets_stable_after_guarded_branch_admission": pilot_summary.get("guarded_targets_stable_after_guarded_branch_admission"),
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": pilot_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112ax_guarded_branch_admitted_pilot",
                "actual": {
                    "row_count_after_guarded_branch_admission": pilot_summary.get("row_count_after_guarded_branch_admission"),
                    "admitted_branch_row_count": pilot_summary.get("admitted_branch_row_count"),
                    "core_targets_stable_after_guarded_branch_admission": pilot_summary.get("core_targets_stable_after_guarded_branch_admission"),
                    "guarded_targets_stable_after_guarded_branch_admission": pilot_summary.get("guarded_targets_stable_after_guarded_branch_admission"),
                },
                "reading": "The guarded branch pilot is only useful if the admitted subset remains stable without reopening generic widen risk.",
            }
        ]
        interpretation = [
            "V1.12AX is a bounded admitted-branch pilot, not a promotion to formal training.",
            "Formal training and signal rights remain closed.",
        ]
        return V112AXPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112ax_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AXPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
