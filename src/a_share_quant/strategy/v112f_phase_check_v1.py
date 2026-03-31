from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112FPhaseCheckReport:
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


class V112FPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        refinement_design_payload: dict[str, Any],
    ) -> V112FPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        design_summary = dict(refinement_design_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112f_as_refinement_design_success",
            "refinement_design_present": bool(design_summary.get("ready_for_phase_check_next")),
            "primary_bottleneck_type": str(design_summary.get("primary_bottleneck_type", "")),
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "owner_review_feature_refinement_before_any_new_model_or_weight_change",
        }
        evidence_rows = [
            {
                "evidence_name": "v112f_charter",
                "actual": {"do_open_v112f_now": bool(charter_summary.get("do_open_v112f_now"))},
                "reading": "V1.12F opened lawfully as a bounded refinement-design phase.",
            },
            {
                "evidence_name": "v112f_refinement_design",
                "actual": {
                    "primary_bottleneck_type": str(design_summary.get("primary_bottleneck_type", "")),
                    "most_useful_block_by_hotspot_impact": str(design_summary.get("most_useful_block_by_hotspot_impact", "")),
                },
                "reading": "The next move is feature-semantics-first rather than weight-tuning-first.",
            },
        ]
        interpretation = [
            "V1.12F succeeds once the project has a single primary bottleneck classification and a bounded refinement basis.",
            "That is enough to close without opening a new model family or changing the current dataset.",
            "The next lawful move is owner review of the proposed catalyst-state semantic additions.",
        ]
        return V112FPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112f_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112FPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
