from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AZPhaseCharterReport:
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


class V112AZPhaseCharterAnalyzer:
    def analyze(self, *, v112ay_phase_closure_payload: dict[str, Any]) -> V112AZPhaseCharterReport:
        closure_summary = dict(v112ay_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("v112ay_success_criteria_met")):
            raise ValueError("V1.12AZ requires the completed V1.12AY closure check.")

        charter = {
            "phase_name": "V1.12AZ CPO Bounded Training Layer Extension",
            "mission": (
                "Extend the bounded training-facing layer from the original 7-row core skeleton to a 10-row "
                "core-plus-guarded-branch layer without opening formal training or signal rights."
            ),
            "in_scope": [
                "preserve the original 7-row truth skeleton",
                "add only the three guarded branch rows admitted by V1.12AY",
                "keep connector/MPO branch out of the training-facing layer",
                "preserve guarded posture on the added branch rows",
            ],
            "out_of_scope": [
                "formal training promotion",
                "formal signal generation",
                "connector/MPO branch admission",
                "spillover or pending row admission",
            ],
            "success_criteria": [
                "a 10-row bounded training-facing layer can be assembled cleanly",
                "the branch addition remains explicitly guarded",
                "the next lawful move becomes a readiness question instead of another admission review",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112az_bounded_training_layer_extension",
            "do_open_v112az_now": True,
            "recommended_first_action": "freeze_v112az_cpo_bounded_training_layer_extension_v1",
        }
        interpretation = [
            "V1.12AZ does not widen beyond the three already-admitted branch rows.",
            "This remains bounded, report-only, and non-deployable.",
        ]
        return V112AZPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112az_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AZPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
