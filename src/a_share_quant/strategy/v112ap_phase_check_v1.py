from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112APPhaseCheckReport:
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


class V112APPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        widen_pilot_payload: dict[str, Any],
    ) -> V112APPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        pilot_summary = dict(widen_pilot_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112ap_as_bounded_secondary_widen_pilot",
            "do_open_v112ap_now": charter_summary.get("do_open_v112ap_now"),
            "core_targets_stable_after_widen": pilot_summary.get("core_targets_stable_after_widen"),
            "guarded_targets_learnable_count": pilot_summary.get("guarded_targets_learnable_count"),
            "best_guarded_target": pilot_summary.get("best_guarded_target"),
            "allow_auto_training_now": False,
            "allow_auto_signal_generation_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": pilot_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112ap_widen_pilot",
                "actual": {
                    "core_targets_stable_after_widen": pilot_summary.get("core_targets_stable_after_widen"),
                    "guarded_targets_learnable_count": pilot_summary.get("guarded_targets_learnable_count"),
                    "best_guarded_target": pilot_summary.get("best_guarded_target"),
                },
                "reading": "The widened pilot tells the project whether the current gain survives one lawful secondary step.",
            }
        ]
        interpretation = [
            "V1.12AP is successful if it produces a bounded widen decision, not if it creates pressure for formal training.",
            "The report-only boundary remains intact.",
        ]
        return V112APPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112ap_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112APPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
