from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AVPhaseCheckReport:
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


class V112AVPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        patch_payload: dict[str, Any],
    ) -> V112AVPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        patch_summary = dict(patch_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112av_as_branch_role_geometry_patch_pilot",
            "do_open_v112av_now": charter_summary.get("do_open_v112av_now"),
            "core_targets_stable_after_branch_patch": patch_summary.get("core_targets_stable_after_branch_patch"),
            "guarded_targets_stable_after_branch_patch": patch_summary.get("guarded_targets_stable_after_branch_patch"),
            "role_state_patch_gain": patch_summary.get("role_state_patch_gain"),
            "branch_patch_family_role_accuracy_drop": patch_summary.get("branch_patch_family_role_accuracy_drop"),
            "allow_formal_training_now": False,
            "allow_formal_signal_generation_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": patch_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112av_branch_patch",
                "actual": {
                    "role_state_gbdt_accuracy_before_patch": patch_summary.get("role_state_gbdt_accuracy_before_patch"),
                    "role_state_gbdt_accuracy_after_patch": patch_summary.get("role_state_gbdt_accuracy_after_patch"),
                    "core_targets_stable_after_branch_patch": patch_summary.get("core_targets_stable_after_branch_patch"),
                    "guarded_targets_stable_after_branch_patch": patch_summary.get("guarded_targets_stable_after_branch_patch"),
                },
                "reading": "The branch patch matters only if widened role-state improves without reopening formal rights.",
            }
        ]
        interpretation = [
            "V1.12AV is a bounded repair pass for branch-row geometry, not a generic training promotion step.",
            "Formal training and signal rights remain closed.",
        ]
        return V112AVPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112av_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AVPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
