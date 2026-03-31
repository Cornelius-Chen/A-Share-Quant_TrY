from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V110APhaseCheckReport:
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


class V110APhaseCheckAnalyzer:
    """Check the bounded posture of V1.10A after the single probe runs."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        cross_family_probe_payload: dict[str, Any],
    ) -> V110APhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        probe_summary = dict(cross_family_probe_payload.get("summary", {}))

        summary = {
            "acceptance_posture": "keep_v110a_single_probe_bounded_and_non_expanding",
            "v110a_open": bool(charter_summary.get("do_open_v110a_now")),
            "candidate_count": probe_summary.get("candidate_count", 0),
            "admitted_case_count": probe_summary.get("admitted_case_count", 0),
            "successful_negative_probe": bool(probe_summary.get("successful_negative_probe")),
            "open_follow_on_probe_now": False,
            "promote_retained_now": False,
            "recommended_next_posture": "prepare_v110a_phase_closure_not_v110b",
        }
        evidence_rows = [
            {
                "evidence_name": "v110a_charter",
                "actual": {
                    "acceptance_posture": charter_summary.get("acceptance_posture"),
                    "allow_auto_follow_on_phase": False,
                },
                "reading": "V1.10A opened as a one-off owner-led probe, not as the start of a new chain.",
            },
            {
                "evidence_name": "cross_family_probe",
                "actual": {
                    "candidate_count": probe_summary.get("candidate_count"),
                    "admitted_case_count": probe_summary.get("admitted_case_count"),
                    "successful_negative_probe": probe_summary.get("successful_negative_probe"),
                },
                "reading": "The probe result is bounded and explicit whether positive or negative; it does not justify automatic follow-on expansion.",
            },
        ]
        interpretation = [
            "V1.10A has now produced a single bounded probe result for policy_followthrough cross-family breadth.",
            "The branch stays below promotion and forbids auto-creation of V1.10B or broader replay.",
            "The next legal step is a closure check only.",
        ]
        return V110APhaseCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v110a_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V110APhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
