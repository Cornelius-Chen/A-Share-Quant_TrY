from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ACPhaseCharterReport:
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


class V112ACPhaseCharterAnalyzer:
    def analyze(
        self,
        *,
        cohort_map_payload: dict[str, Any],
        labeling_review_payload: dict[str, Any],
    ) -> V112ACPhaseCharterReport:
        cohort_summary = dict(cohort_map_payload.get("summary", {}))
        labeling_summary = dict(labeling_review_payload.get("summary", {}))
        if int(cohort_summary.get("object_row_count", 0)) <= 0:
            raise ValueError("V1.12AC requires the V1.12AA cohort map.")
        if int(labeling_summary.get("primary_labeling_surface_count", 0)) <= 0:
            raise ValueError("V1.12AC requires the V1.12AB bounded labeling review.")

        charter = {
            "phase_name": "V1.12AC CPO Unsupervised Role-Challenge Probe",
            "mission": (
                "Use a bounded unsupervised probe to challenge the current manual core/adjacent/branch/"
                "spillover/pending layering using only contemporaneously visible cohort-stage evidence, "
                "without opening formal label freeze, training, or automatic role legislation."
            ),
            "in_scope": [
                "cluster cohort rows using active stage windows and evidence-axis features only",
                "compare latent clusters against the current manual cohort map",
                "preserve supportive and challenging findings as review-only candidate structures",
            ],
            "out_of_scope": [
                "formal role replacement",
                "formal label freeze",
                "training rights",
                "signal generation",
                "execution implications",
            ],
            "success_criteria": [
                "the probe reveals whether the current manual role grammar is supported or challenged by data-side structure",
                "late-cycle spillover and pending ambiguity remain explicit rather than cleaned away",
                "any new latent structure stays review-only and does not legislate labels",
            ],
            "stop_criteria": [
                "future returns or other post-event truth leak into clustering inputs",
                "cluster names are turned into automatic formal roles",
                "the probe is used to silently override pending or spillover boundaries",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112ac_unsupervised_role_challenge_probe",
            "do_open_v112ac_now": True,
            "selected_parent_line": "v112aa_v112ab_cpo_cohort_and_label_surface",
            "recommended_first_action": "freeze_v112ac_unsupervised_role_challenge_probe_v1",
        }
        interpretation = [
            "V1.12AC does not replace the manual cohort map; it challenges it.",
            "The correct posture is hypothesis stress-testing, not automatic role legislation.",
            "Training and formal labeling remain closed throughout this probe.",
        ]
        return V112ACPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112ac_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ACPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
