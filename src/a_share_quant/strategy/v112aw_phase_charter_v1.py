from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AWPhaseCharterReport:
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


class V112AWPhaseCharterAnalyzer:
    def analyze(self, *, v112av_phase_closure_payload: dict[str, Any]) -> V112AWPhaseCharterReport:
        closure_summary = dict(v112av_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("v112av_success_criteria_met")):
            raise ValueError("V1.12AW requires the completed V1.12AV closure check.")

        charter = {
            "phase_name": "V1.12AW CPO Branch Guarded Admission Review",
            "mission": (
                "Review whether the patched branch rows can move from review-only context into a guarded "
                "training-facing context without opening formal training or signal rights."
            ),
            "in_scope": [
                "reuse the four branch rows tested in V1.12AU and patched in V1.12AV",
                "compare review-only versus guarded-context admissibility",
                "allow partial admission instead of forcing all-or-nothing branch promotion",
            ],
            "out_of_scope": [
                "formal training promotion",
                "formal signal generation",
                "spillover admission",
                "pending ambiguous row admission",
            ],
            "success_criteria": [
                "the project can make a bounded branch-row admission decision",
                "at least one branch row can be classified more precisely than review-only",
                "the next lawful move becomes narrower than generic branch review",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112aw_branch_guarded_admission_review",
            "do_open_v112aw_now": True,
            "recommended_first_action": "freeze_v112aw_cpo_branch_guarded_admission_review_v1",
        }
        interpretation = [
            "V1.12AW converts the branch patch result into an admissibility decision instead of reopening generic geometry review.",
            "This remains bounded, report-only, and non-deployable.",
        ]
        return V112AWPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112aw_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AWPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
