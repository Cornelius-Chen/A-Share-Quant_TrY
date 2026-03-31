from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112APPhaseCharterReport:
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


class V112APPhaseCharterAnalyzer:
    def analyze(self, *, v112ao_phase_closure_payload: dict[str, Any]) -> V112APPhaseCharterReport:
        closure_summary = dict(v112ao_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("v112ao_success_criteria_met")):
            raise ValueError("V1.12AP requires the completed V1.12AO closure check.")

        charter = {
            "phase_name": "V1.12AP CPO Bounded Secondary Widen Pilot",
            "mission": (
                "Test whether the patched role layer survives a bounded widen from core-skeleton-only targets "
                "to a small guarded secondary target set, while keeping the same truth rows and report-only boundary."
            ),
            "in_scope": [
                "reuse the same 7 truth rows and the V1.12AO patched feature set",
                "keep the 3 core targets",
                "add only guarded secondary targets that are currently bindable on a subset",
                "compare guardrail versus GBDT under the widened target stack",
            ],
            "out_of_scope": [
                "new rows outside the current 7 truth rows",
                "quiet-window or spillover truth promotion",
                "formal training promotion",
                "formal signal generation",
            ],
            "success_criteria": [
                "core targets stay stable after widening",
                "at least part of the guarded secondary layer remains learnable above the guardrail baseline",
                "the widened pilot still remains clearly report-only",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112ap_cpo_bounded_secondary_widen_pilot",
            "do_open_v112ap_now": True,
            "recommended_first_action": "freeze_v112ap_cpo_bounded_secondary_widen_pilot_v1",
        }
        interpretation = [
            "V1.12AP is not broad training. It is a bounded stress test of whether the current gain survives one careful widening step.",
            "The phase widens target structure, not row geometry.",
        ]
        return V112APPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112ap_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112APPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
