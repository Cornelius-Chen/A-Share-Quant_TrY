from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ALPhaseCheckReport:
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


class V112ALPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        readiness_review_payload: dict[str, Any],
    ) -> V112ALPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        readiness_summary = dict(readiness_review_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112al_as_bounded_training_readiness_review",
            "do_open_v112al_now": charter_summary.get("do_open_v112al_now"),
            "bounded_training_pilot_lawful_now": readiness_summary.get("bounded_training_pilot_lawful_now"),
            "bounded_training_pilot_scope": readiness_summary.get("bounded_training_pilot_scope"),
            "representative_training_lawful_now": readiness_summary.get("representative_training_lawful_now"),
            "primary_bottleneck_layer": readiness_summary.get("primary_bottleneck_layer"),
            "secondary_bottleneck_layer": readiness_summary.get("secondary_bottleneck_layer"),
            "allow_auto_training_now": False,
            "allow_auto_label_freeze_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": readiness_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112al_training_readiness_review",
                "actual": {
                    "row_geometry_readiness_posture": readiness_summary.get("row_geometry_readiness_posture"),
                    "label_binding_readiness_posture": readiness_summary.get("label_binding_readiness_posture"),
                    "feature_implementation_readiness_posture": readiness_summary.get(
                        "feature_implementation_readiness_posture"
                    ),
                    "primary_bottleneck_layer": readiness_summary.get("primary_bottleneck_layer"),
                },
                "reading": (
                    "The project now has an explicit training-readiness split by layer instead of a vague feeling of being close."
                ),
            }
        ]
        interpretation = [
            "V1.12AL succeeds if it turns training readiness into an action-grade boundary rather than another abstract audit.",
            "Formal training still remains closed.",
        ]
        return V112ALPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112al_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ALPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
