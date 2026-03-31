from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112CPhaseCharterReport:
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


class V112CPhaseCharterAnalyzer:
    """Open the hotspot-review and black-box sidecar design phase."""

    def analyze(
        self,
        *,
        v112b_phase_closure_payload: dict[str, Any],
    ) -> V112CPhaseCharterReport:
        closure_summary = dict(v112b_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("v112b_success_criteria_met")):
            raise ValueError("V1.12C requires V1.12B baseline closure before opening.")

        charter = {
            "phase_name": "V1.12C Baseline Hotspot Review And Sidecar Protocol",
            "mission": (
                "Turn the first report-only optical-link baseline into a hotspot map and freeze the first "
                "same-dataset black-box sidecar comparison protocol."
            ),
            "in_scope": [
                "review baseline misclassification hotspots by symbol and stage",
                "identify where the current interpretable baseline is structurally too optimistic or too blunt",
                "freeze a report-only black-box sidecar protocol on the same dataset and labels",
            ],
            "out_of_scope": [
                "strategy integration",
                "dataset widening",
                "intraday execution modeling",
                "promotion or retained-feature elevation",
                "unbounded model search",
            ],
            "success_criteria": [
                "baseline error hotspots are explicitly summarized",
                "the first sidecar comparison protocol is frozen on the same sample unit and time split",
                "the phase clarifies what the next model comparison should test before any expansion",
            ],
            "stop_criteria": [
                "the hotspot review adds no new decision value beyond the existing baseline report",
                "the sidecar protocol would require wider data or looser validation to proceed",
                "the phase starts drifting toward deployment instead of bounded comparison",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112c_now_for_hotspot_review_and_sidecar_protocol",
            "do_open_v112c_now": True,
            "ready_for_hotspot_review_next": True,
        }
        interpretation = [
            "V1.12C keeps the same pilot dataset and labels, but changes the task from pipeline construction to error-focused comparison design.",
            "The sidecar remains report-only and same-dataset so the next comparison isolates model choice rather than data drift.",
            "This phase should end with a clear next experiment, not with automatic model deployment.",
        ]
        return V112CPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112c_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
