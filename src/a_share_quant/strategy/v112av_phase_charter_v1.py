from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AVPhaseCharterReport:
    summary: dict[str, Any]
    charter: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "charter": self.charter,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112AVPhaseCharterAnalyzer:
    def analyze(self, *, v112au_phase_closure_payload: dict[str, Any]) -> V112AVPhaseCharterReport:
        closure_summary = dict(v112au_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("v112au_success_criteria_met")):
            raise ValueError("V1.12AV requires the completed V1.12AU closure check.")

        charter = {
            "phase_name": "V1.12AV CPO Branch Role Geometry Patch Pilot",
            "mission": (
                "Patch the widened branch-role geometry with bounded branch-specific observable features "
                "before any attempt to promote branch rows into a training-facing layer."
            ),
            "in_scope": [
                "reuse the widened row geometry from V1.12AU",
                "keep the same core and guarded target stack",
                "add only bounded branch-role geometry features",
                "compare the branch-patched widened behavior against V1.12AU",
            ],
            "out_of_scope": [
                "spillover row admission",
                "pending row admission",
                "formal training promotion",
                "formal signal generation",
            ],
            "success_criteria": [
                "role_state recovers materially on the widened branch-row geometry",
                "core targets no longer break because of branch-row admission",
                "the next lawful move becomes narrower than generic row-geometry review",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112av_branch_role_geometry_patch_pilot",
            "do_open_v112av_now": True,
            "recommended_first_action": "freeze_v112av_cpo_branch_role_geometry_patch_pilot_v1",
        }
        interpretation = [
            "V1.12AV treats branch-row geometry failure as a patchable structure problem, not as a reason to retreat into generic review.",
            "The boundary remains report-only and non-deployable.",
        ]
        return V112AVPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112av_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AVPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
