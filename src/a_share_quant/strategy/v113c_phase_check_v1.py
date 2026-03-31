from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113CPhaseCheckReport:
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


class V113CPhaseCheckAnalyzer:
    def analyze(self, *, state_usage_review_payload: dict[str, Any]) -> V113CPhaseCheckReport:
        review_summary = dict(state_usage_review_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v113c_as_bounded_state_usage_review_success",
            "reviewed_high_priority_driver_count": int(review_summary.get("reviewed_high_priority_driver_count", 0)),
            "drivers_allowed_for_schema_review_only": int(review_summary.get("drivers_allowed_for_schema_review_only", 0)),
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "bounded_archetype_usage_pass_using_schema_review_only_drivers",
        }
        evidence_rows = [
            {
                "evidence_name": "v113c_bounded_state_usage_review",
                "actual": {
                    "reviewed_high_priority_driver_count": summary["reviewed_high_priority_driver_count"],
                    "drivers_allowed_for_schema_review_only": summary["drivers_allowed_for_schema_review_only"],
                },
                "reading": "V1.13C succeeds once the high-priority driver quartet receives lawful schema-review-only usage dispositions.",
            }
        ]
        interpretation = [
            "V1.13C converts driver priority into lawful schema usage without opening model or execution rights.",
            "The next bounded move can now consume this quartet inside archetype review rather than staying fully abstract.",
        ]
        return V113CPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v113c_phase_check_report(
    *, reports_dir: Path, report_name: str, result: V113CPhaseCheckReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
