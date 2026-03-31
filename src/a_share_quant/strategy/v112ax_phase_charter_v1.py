from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AXPhaseCharterReport:
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


class V112AXPhaseCharterAnalyzer:
    def analyze(self, *, v112aw_phase_closure_payload: dict[str, Any]) -> V112AXPhaseCharterReport:
        closure_summary = dict(v112aw_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("v112aw_success_criteria_met")):
            raise ValueError("V1.12AX requires the completed V1.12AW closure check.")

        charter = {
            "phase_name": "V1.12AX CPO Guarded Branch-Admitted Pilot",
            "mission": (
                "Run a bounded pilot with the three branch rows admitted into guarded training context "
                "before any broader row-geometry widen."
            ),
            "in_scope": [
                "reuse the current 7 truth rows",
                "admit only the three V1.12AW guarded branch rows",
                "retain the branch patch feature family",
                "test core and guarded targets under this narrower branch admission",
            ],
            "out_of_scope": [
                "formal training promotion",
                "formal signal generation",
                "connector/MPO branch admission",
                "spillover or pending row admission",
            ],
            "success_criteria": [
                "core targets remain stable",
                "guarded targets remain stable",
                "the admitted branch subset does not recreate the V1.12AU role collapse",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112ax_guarded_branch_admitted_pilot",
            "do_open_v112ax_now": True,
            "recommended_first_action": "freeze_v112ax_cpo_guarded_branch_admitted_pilot_v1",
        }
        interpretation = [
            "V1.12AX is the first pilot that uses the V1.12AW admissibility cut operationally.",
            "This remains bounded, report-only, and non-deployable.",
        ]
        return V112AXPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112ax_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AXPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
