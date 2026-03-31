from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112IPhaseCheckReport:
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


class V112IPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        protocol_payload: dict[str, Any],
    ) -> V112IPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        protocol_summary = dict(protocol_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112i_as_review_protocol_success",
            "phase_charter_present": bool(charter_summary),
            "protocol_present": bool(protocol_summary),
            "protocol_ready_for_candidate_structure_review": bool(
                protocol_summary.get("protocol_ready_for_candidate_structure_review")
            ),
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "use_protocol_to_review_bucketization_or_candidate_substate_outputs_before_any_label_split",
        }
        evidence_rows = [
            {
                "evidence_name": "v112i_protocol",
                "actual": {
                    "primary_bottleneck_type": protocol_summary.get("primary_bottleneck_type"),
                    "protocol_ready_for_candidate_structure_review": protocol_summary.get(
                        "protocol_ready_for_candidate_structure_review"
                    ),
                },
                "reading": "V1.12I should end with a stable review rule rather than a relabeling action.",
            }
        ]
        interpretation = [
            "V1.12I is a governance/support phase for the next owner review step.",
            "The lawful next use is to assess structured candidate outputs against this protocol, not to split labels automatically.",
        ]
        return V112IPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112i_phase_check_report(*, reports_dir: Path, report_name: str, result: V112IPhaseCheckReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
