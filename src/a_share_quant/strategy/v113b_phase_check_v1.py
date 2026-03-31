from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113BPhaseCheckReport:
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


class V113BPhaseCheckAnalyzer:
    def analyze(self, *, driver_review_payload: dict[str, Any]) -> V113BPhaseCheckReport:
        review_summary = dict(driver_review_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v113b_as_candidate_mainline_driver_review_success",
            "candidate_driver_count_reviewed": int(review_summary.get("candidate_driver_count_reviewed", 0)),
            "bounded_state_usage_ready_count": int(review_summary.get("bounded_state_usage_ready_count", 0)),
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "bounded_state_usage_review_on_high_priority_mainline_drivers_only",
        }
        evidence_rows = [
            {
                "evidence_name": "v113b_candidate_mainline_driver_review",
                "actual": {
                    "candidate_driver_count_reviewed": summary["candidate_driver_count_reviewed"],
                    "bounded_state_usage_ready_count": summary["bounded_state_usage_ready_count"],
                },
                "reading": "V1.13B succeeds once the current candidate-driver set is compressed into a narrower next-step review target.",
            }
        ]
        interpretation = [
            "V1.13B narrows the next schema move without promoting any candidate into formal driver law.",
            "The next lawful move should stay small: bounded state-usage review on the highest-priority candidate drivers only.",
        ]
        return V113BPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v113b_phase_check_report(
    *, reports_dir: Path, report_name: str, result: V113BPhaseCheckReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
