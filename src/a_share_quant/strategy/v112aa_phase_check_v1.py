from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AAPhaseCheckReport:
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


class V112AAPhaseCheckAnalyzer:
    def analyze(self, *, phase_charter_payload: dict[str, Any], cohort_map_payload: dict[str, Any]) -> V112AAPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        cohort_summary = dict(cohort_map_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112aa_as_bounded_cohort_map_only",
            "do_open_v112aa_now": charter_summary.get("do_open_v112aa_now"),
            "object_row_count": cohort_summary.get("object_row_count"),
            "primary_core_truth_row_count": cohort_summary.get("primary_core_truth_row_count"),
            "pending_ambiguous_count": cohort_summary.get("pending_ambiguous_count"),
            "allow_auto_labeling_now": False,
            "allow_auto_training_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "owner_review_then_bounded_labeling_review",
        }
        evidence_rows = [
            {
                "evidence_name": "v112aa_bounded_cohort_map",
                "actual": {
                    "object_row_count": cohort_summary.get("object_row_count"),
                    "primary_core_truth_row_count": cohort_summary.get("primary_core_truth_row_count"),
                    "pending_ambiguous_count": cohort_summary.get("pending_ambiguous_count"),
                },
                "reading": "The CPO line now has a usable cohort map with explicit core, extension, spillover, and pending layers.",
            }
        ]
        interpretation = [
            "V1.12AA is a boundary-hardening phase, not a training-opening phase.",
            "Later labeling remains closed until the owner consumes the cohort map.",
        ]
        return V112AAPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112aa_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AAPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
