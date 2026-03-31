from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112DPhaseCharterReport:
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


class V112DPhaseCharterAnalyzer:
    """Open the first same-dataset black-box sidecar pilot."""

    def analyze(
        self,
        *,
        v112c_phase_closure_payload: dict[str, Any],
    ) -> V112DPhaseCharterReport:
        closure_summary = dict(v112c_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("v112c_success_criteria_met")):
            raise ValueError("V1.12D requires V1.12C closure before opening.")

        charter = {
            "phase_name": "V1.12D Same-Dataset Black-Box Sidecar Pilot",
            "mission": (
                "Run the first report-only black-box sidecar comparison on the same optical-link pilot dataset "
                "and measure whether it reduces optimistic false positives in major markup and high-level consolidation."
            ),
            "in_scope": [
                "reuse the exact V1.12B dataset freeze",
                "reuse the exact V1.12 labels and time split",
                "run hist gradient boosting and a small MLP as bounded sidecars",
                "compare sidecars against the existing baseline on hotspot-specific metrics",
            ],
            "out_of_scope": [
                "strategy integration",
                "dataset widening",
                "intraday execution features",
                "model deployment",
                "automatic promotion of any model family",
            ],
            "success_criteria": [
                "at least one sidecar runs successfully on the same dataset and split",
                "hotspot metrics are comparable against the V1.12B baseline",
                "the result changes owner understanding of whether black-box comparison is worthwhile",
            ],
            "stop_criteria": [
                "sidecar models cannot run under current environment constraints",
                "comparison would require changing dataset scope or validation rules",
                "the result cannot be interpreted relative to the known hotspot errors",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112d_now_for_first_same_dataset_sidecar_pilot",
            "do_open_v112d_now": True,
            "ready_for_sidecar_pilot_next": True,
        }
        interpretation = [
            "V1.12D is the first true machine-learning comparison phase on the optical-link pilot, but it stays fully report-only.",
            "The purpose is not to maximize a headline score; it is to test whether black-box models reduce specific known error modes.",
            "The phase should end in owner review, not in deployment or auto-widening.",
        ]
        return V112DPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112d_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112DPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
