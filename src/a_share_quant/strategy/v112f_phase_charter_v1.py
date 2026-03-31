from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112FPhaseCharterReport:
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


class V112FPhaseCharterAnalyzer:
    """Open a bounded refinement-design phase after the first sidecar attribution review."""

    def analyze(
        self,
        *,
        v112e_phase_closure_payload: dict[str, Any],
    ) -> V112FPhaseCharterReport:
        closure_summary = dict(v112e_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("v112e_success_criteria_met")):
            raise ValueError("V1.12F requires V1.12E closure before opening.")

        charter = {
            "phase_name": "V1.12F Catalyst-State Semantics And Label Boundary Refinement Design",
            "mission": (
                "Turn the first GBDT attribution result into a bounded design decision: determine whether the next "
                "high-value move is catalyst-state semantic refinement, label-boundary refinement, or both."
            ),
            "in_scope": [
                "review V1.12C hotspot rows and V1.12E block-attribution results together",
                "classify the single primary bottleneck behind the current optimistic errors",
                "propose bounded catalyst-state semantic additions for late major-markup and high-level consolidation",
                "propose bounded label-boundary changes only if they add decision value beyond feature refinement",
            ],
            "out_of_scope": [
                "model retraining",
                "new data acquisition",
                "object widening",
                "strategy deployment",
                "intraday execution features",
            ],
            "success_criteria": [
                "the phase selects one primary bottleneck cause instead of leaving feature and label issues mixed",
                "the output gives a bounded next-step design basis",
                "the phase remains report-only and does not mutate the existing training chain",
            ],
            "stop_criteria": [
                "the review cannot identify a single primary bottleneck",
                "the phase starts changing model scope instead of design basis",
                "the result does not change the next refinement decision",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112f_now_for_refinement_design",
            "do_open_v112f_now": True,
            "ready_for_refinement_design_next": True,
        }
        interpretation = [
            "V1.12F is a design-only phase, not a new training or modeling phase.",
            "The point is to stop treating 'weights', 'features', and 'labels' as one blurred problem.",
            "The correct output is a bounded next-step design basis that increases decision value before any new experiment.",
        ]
        return V112FPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112f_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112FPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
