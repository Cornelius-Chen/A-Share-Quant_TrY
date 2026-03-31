from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ADPhaseCharterReport:
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


class V112ADPhaseCharterAnalyzer:
    def analyze(
        self,
        *,
        reconstruction_payload: dict[str, Any],
        cohort_map_payload: dict[str, Any],
        unsupervised_probe_payload: dict[str, Any],
    ) -> V112ADPhaseCharterReport:
        reconstruction_summary = dict(reconstruction_payload.get("summary", {}))
        cohort_summary = dict(cohort_map_payload.get("summary", {}))
        probe_summary = dict(unsupervised_probe_payload.get("summary", {}))
        if not bool(reconstruction_summary.get("cycle_absorption_review_success")):
            raise ValueError("V1.12AD requires the V1.12Z reconstruction pass.")
        if int(cohort_summary.get("object_row_count", 0)) <= 0:
            raise ValueError("V1.12AD requires the V1.12AA cohort map.")
        if int(probe_summary.get("cluster_count", 0)) <= 0:
            raise ValueError("V1.12AD requires the V1.12AC unsupervised challenger output.")

        charter = {
            "phase_name": "V1.12AD CPO Dynamic Role-Transition Feature Review",
            "mission": (
                "Turn stage-dependent role migration, leader persistence, challenger activation, "
                "spillover saturation, and late-cycle demotion risk into bounded review-first features "
                "so future modeling is not forced to treat roles as timeless static buckets."
            ),
            "in_scope": [
                "freeze stage-to-stage role transition events",
                "freeze dynamic role-transition feature candidates",
                "capture review-only role replacement and demotion signals",
            ],
            "out_of_scope": [
                "formal label freeze",
                "formal training rights",
                "signal generation",
                "automatic role replacement",
            ],
            "success_criteria": [
                "static role grammar is upgraded into stage-conditioned transition grammar",
                "leader change, spillover saturation, and demotion risk become explicit review features",
                "the result stays bounded and review-first rather than drifting into stealth labeling",
            ],
            "stop_criteria": [
                "role transitions are backfilled with future truth instead of stage-local evidence",
                "dynamic features are treated as deployable signals",
                "the phase tries to replace the existing cohort map rather than augment it",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112ad_dynamic_role_transition_feature_review",
            "do_open_v112ad_now": True,
            "selected_parent_line": "v112z_v112aa_v112ac_cpo_cycle_role_challenge",
            "recommended_first_action": "freeze_v112ad_dynamic_role_transition_feature_review_v1",
        }
        interpretation = [
            "V1.12AD exists because static role labels are not enough once cycles contain re-ignition, demotion, and late spillover.",
            "The goal is to quantify role movement, not to overwrite the current governed cohort map.",
            "Formal labels and training remain closed during this review layer.",
        ]
        return V112ADPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112ad_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ADPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
