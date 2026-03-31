from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AKPhaseCharterReport:
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


class V112AKPhaseCharterAnalyzer:
    def analyze(self, *, dataset_assembly_payload: dict[str, Any]) -> V112AKPhaseCharterReport:
        dataset_summary = dict(dataset_assembly_payload.get("summary", {}))
        if not bool(dataset_summary.get("ready_for_phase_check_next")):
            raise ValueError("V1.12AK requires the completed V1.12AJ dataset assembly.")

        charter = {
            "phase_name": "V1.12AK CPO Bounded Feature Binding Review",
            "mission": (
                "Review whether current ready and guarded labels are actually bindable to the current truth-candidate "
                "rows through the existing feature families, and surface any row-label combinations that remain "
                "not-currently-bindable."
            ),
            "in_scope": [
                "review row-label binding for current truth-candidate rows",
                "separate direct bindable, guarded bindable, and row-specific blocked combinations",
                "identify labels that are globally allowed but locally weak on the current truth-candidate set",
            ],
            "out_of_scope": [
                "formal label freeze",
                "formal training",
                "formal feature promotion",
                "rewriting the dataset draft itself",
            ],
            "success_criteria": [
                "the system knows which labels truly bind today and which only exist as future draft capacity",
                "blocked bindings are surfaced explicitly rather than silently ignored",
                "training remains closed",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112ak_cpo_bounded_feature_binding_review",
            "do_open_v112ak_now": True,
            "recommended_first_action": "freeze_v112ak_cpo_bounded_feature_binding_review_v1",
        }
        interpretation = [
            "V1.12AK is the last structural check before anyone can talk seriously about training readiness.",
            "The point is not to prove every label is usable; the point is to identify which labels truly bind on the current row set.",
        ]
        return V112AKPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112ak_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AKPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
