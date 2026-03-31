from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ALPhaseCharterReport:
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


class V112ALPhaseCharterAnalyzer:
    def analyze(self, *, v112ak_phase_closure_payload: dict[str, Any]) -> V112ALPhaseCharterReport:
        closure_summary = dict(v112ak_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("v112ak_success_criteria_met")):
            raise ValueError("V1.12AL requires the completed V1.12AK closure check.")

        charter = {
            "phase_name": "V1.12AL CPO Bounded Training Readiness Review",
            "mission": (
                "Determine whether the current CPO draft dataset can legally support an extremely small bounded "
                "training pilot, and attribute the real bottleneck across row geometry, label binding, and "
                "feature implementation layers."
            ),
            "in_scope": [
                "review row geometry readiness for the current truth-candidate set",
                "review label binding readiness for ready and guarded labels",
                "review feature implementation readiness against current operational gaps",
                "define core-trainable, guarded-trainable, and not-yet-trainable regions",
            ],
            "out_of_scope": [
                "formal training launch",
                "formal label freeze",
                "formal signal generation",
                "pretending that a bounded pilot implies representative readiness",
            ],
            "success_criteria": [
                "the phase produces an action-grade answer rather than another generic review loop",
                "the primary bottleneck layer is explicit",
                "the lawful upper bound of any current pilot is explicit",
                "formal training remains closed unless a later bounded pilot is opened explicitly",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112al_cpo_bounded_training_readiness_review",
            "do_open_v112al_now": True,
            "recommended_first_action": "freeze_v112al_cpo_bounded_training_readiness_review_v1",
        }
        interpretation = [
            "V1.12AL is not a training launch; it is the gate that decides whether any tiny bounded pilot is lawful at all.",
            "The point is to separate bundle readiness, row geometry, and implementation maturity before the project risks over-reading its own progress.",
        ]
        return V112ALPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112al_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ALPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
