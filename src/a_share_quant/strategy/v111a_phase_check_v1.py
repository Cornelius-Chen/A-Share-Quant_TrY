from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V111APhaseCheckReport:
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


class V111APhaseCheckAnalyzer:
    """Summarize what the first acquisition pilot did and did not change."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        screened_first_collection_payload: dict[str, Any],
    ) -> V111APhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        collection_summary = dict(screened_first_collection_payload.get("summary", {}))

        admitted_count = int(collection_summary.get("admitted_candidate_count", 0))
        admitted_policy_followthrough_count = int(collection_summary.get("admitted_policy_followthrough_count", 0))
        summary = {
            "acceptance_posture": "keep_v111a_as_bounded_first_acquisition_pilot_only",
            "do_open_v111a_now": charter_summary.get("do_open_v111a_now"),
            "admitted_candidate_count": admitted_count,
            "admitted_policy_followthrough_count": admitted_policy_followthrough_count,
            "direct_policy_followthrough_breadth_gain_present": admitted_policy_followthrough_count > 0,
            "acquisition_path_validated": admitted_count > 0,
            "allow_retained_promotion_now": False,
            "allow_strategy_integration_now": False,
            "recommended_next_posture": "close_v111a_and_preserve_new_candidate_records_for_future_owner_review",
        }
        evidence_rows = [
            {
                "evidence_name": "v111a_charter",
                "actual": {
                    "acceptance_posture": charter_summary.get("acceptance_posture"),
                    "do_open_v111a_now": charter_summary.get("do_open_v111a_now"),
                },
                "reading": "The owner-reviewed first pilot opened lawfully on top of the V1.11 infrastructure.",
            },
            {
                "evidence_name": "screened_first_collection",
                "actual": {
                    "screened_candidate_count": collection_summary.get("screened_candidate_count"),
                    "admitted_candidate_count": collection_summary.get("admitted_candidate_count"),
                    "admitted_policy_followthrough_count": collection_summary.get("admitted_policy_followthrough_count"),
                },
                "reading": "The pilot produced real new candidate admissions, but direct policy-followthrough breadth gain must be read separately from generic acquisition success.",
            },
        ]
        interpretation = [
            "V1.11A validated that the new acquisition basis can admit non-anchor official or high-trust candidates under bounded rules.",
            "The pilot did not automatically convert those admissions into direct policy-followthrough breadth evidence or retained-feature advancement.",
            "The correct next move is closure into waiting state, not auto-expansion.",
        ]
        return V111APhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v111a_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V111APhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
