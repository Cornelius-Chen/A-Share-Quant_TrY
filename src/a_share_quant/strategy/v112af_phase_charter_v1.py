from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AFPhaseCharterReport:
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


class V112AFPhaseCharterAnalyzer:
    def analyze(
        self,
        *,
        registry_schema_payload: dict[str, Any],
        labeling_review_payload: dict[str, Any],
        dynamic_role_payload: dict[str, Any],
        brainstorm_payload: dict[str, Any],
    ) -> V112AFPhaseCharterReport:
        schema_summary = dict(registry_schema_payload.get("summary", {}))
        labeling_summary = dict(labeling_review_payload.get("summary", {}))
        dynamic_summary = dict(dynamic_role_payload.get("summary", {}))
        brainstorm_summary = dict(brainstorm_payload.get("summary", {}))
        if int(schema_summary.get("feature_slot_count", 0)) <= 0:
            raise ValueError("V1.12AF requires the V1.12Q registry schema.")
        if int(labeling_summary.get("primary_labeling_surface_count", 0)) <= 0:
            raise ValueError("V1.12AF requires the V1.12AB bounded labeling review.")
        if int(dynamic_summary.get("dynamic_feature_count", 0)) <= 0:
            raise ValueError("V1.12AF requires the V1.12AD dynamic role-transition review.")
        if int(brainstorm_summary.get("high_value_review_candidate_count", 0)) <= 0:
            raise ValueError("V1.12AF requires the V1.12AE brainstorm integration.")

        charter = {
            "phase_name": "V1.12AF CPO Feature-Family Design Review",
            "mission": (
                "Compress the current CPO brainstorm shortlist plus the dynamic role-transition layer "
                "into bounded feature families with explicit point-in-time definitions, input sources, "
                "surface boundaries, duplicate guards, and anti-leakage rules before any label-draft assembly."
            ),
            "in_scope": [
                "group strong candidates into a small number of feature families",
                "freeze point-in-time definitions and input bundles",
                "freeze duplicate guards against existing schema slots",
                "freeze anti-leakage rules and later admissible surfaces",
            ],
            "out_of_scope": [
                "formal feature promotion",
                "formal label freeze",
                "formal training",
                "signal generation",
                "auto-resolving current operational blind spots",
            ],
            "success_criteria": [
                "the high-value shortlist is reduced to bounded families rather than a flat indicator pile",
                "the strongest candidates have point-in-time definitions and no-leakage guards",
                "review-only overlay candidates remain clearly outside core truth surfaces",
            ],
            "stop_criteria": [
                "a brainstorm candidate is silently promoted into formal feature status",
                "later returns or post-event truth are used to define current-state features",
                "blind spots are hidden instead of preserved as explicit gaps",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112af_cpo_feature_family_design_review",
            "do_open_v112af_now": True,
            "selected_parent_line": "v112q_v112ab_v112ad_v112ae_cpo_schema_to_feature_family",
            "recommended_first_action": "freeze_v112af_cpo_feature_family_design_review_v1",
        }
        interpretation = [
            "V1.12AF exists to stop the current feature shortlist from staying as loose nouns.",
            "The correct output is a bounded family design, not a stealth training feature registry.",
            "The next lawful move after this phase is bounded label-draft assembly, not automatic model expansion.",
        ]
        return V112AFPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112af_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AFPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
