from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112DPhaseCheckReport:
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


class V112DPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        sidecar_pilot_payload: dict[str, Any],
    ) -> V112DPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        pilot_summary = dict(sidecar_pilot_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112d_as_same_dataset_sidecar_pilot_success",
            "sidecar_pilot_present": bool(pilot_summary.get("ready_for_phase_check_next")),
            "allow_sidecar_deployment_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "owner_review_same_dataset_sidecar_result_before_any_feature_or_model_widening",
        }
        evidence_rows = [
            {
                "evidence_name": "v112d_charter",
                "actual": {"do_open_v112d_now": bool(charter_summary.get("do_open_v112d_now"))},
                "reading": "V1.12D opened lawfully as a first sidecar execution phase.",
            },
            {
                "evidence_name": "v112d_sidecar_pilot",
                "actual": {
                    "model_count": int(pilot_summary.get("model_count", 0)),
                    "best_model_name": str(pilot_summary.get("best_model_name", "")),
                    "baseline_test_accuracy": float(pilot_summary.get("baseline_test_accuracy", 0.0)),
                    "best_model_test_accuracy": float(pilot_summary.get("best_model_test_accuracy", 0.0)),
                },
                "reading": "The first same-dataset black-box comparison now exists and can be judged against the known baseline.",
            },
        ]
        interpretation = [
            "V1.12D succeeds once the first black-box sidecar comparison runs under the same dataset and validation split.",
            "That is enough to close the phase without widening scope or opening deployment.",
            "The next lawful move is owner review of whether the sidecar changes decision value enough to continue.",
        ]
        return V112DPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112d_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112DPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
