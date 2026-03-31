from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112EPhaseCharterReport:
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


class V112EPhaseCharterAnalyzer:
    """Open the bounded attribution review after the first sidecar result."""

    def analyze(
        self,
        *,
        v112d_phase_closure_payload: dict[str, Any],
    ) -> V112EPhaseCharterReport:
        closure_summary = dict(v112d_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("v112d_success_criteria_met")):
            raise ValueError("V1.12E requires V1.12D closure before opening.")

        charter = {
            "phase_name": "V1.12E GBDT Baseline Attribution Review",
            "mission": (
                "Review why the first GBDT sidecar outperformed the interpretable baseline by using same-dataset "
                "block ablation and hotspot-specific error attribution."
            ),
            "in_scope": [
                "refit the same GBDT sidecar on the frozen pilot dataset",
                "measure hotspot-specific gains against the V1.12B baseline",
                "run block-level ablation across catalyst state, earnings bridge, expectation gap, and price confirmation",
            ],
            "out_of_scope": [
                "strategy deployment",
                "new data acquisition",
                "object widening",
                "intraday execution features",
                "new model families beyond the existing GBDT sidecar",
            ],
            "success_criteria": [
                "the review localizes which feature blocks explain most of the sidecar's hotspot improvement",
                "the result changes the next feature or model decision basis",
                "the review stays same-dataset and report-only",
            ],
            "stop_criteria": [
                "ablation adds no decision value beyond the raw sidecar score",
                "the review requires wider data or weaker validation rules to proceed",
                "the phase drifts into deployment or object expansion",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112e_now_for_gbdt_baseline_attribution_review",
            "do_open_v112e_now": True,
            "ready_for_attribution_review_next": True,
        }
        interpretation = [
            "V1.12E exists to explain the first sidecar gain, not to search for a new winner.",
            "The review remains same-dataset so attribution is about feature blocks and hotspot structure rather than scope drift.",
            "The correct output is a next-step decision basis, not a new deployment branch.",
        ]
        return V112EPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112e_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112EPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
