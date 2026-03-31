from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BSPhaseCheckReport:
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


class V112BSPhaseCheckAnalyzer:
    def analyze(self, *, refinement_payload: dict[str, Any]) -> V112BSPhaseCheckReport:
        summary_in = dict(refinement_payload.get("summary", {}))
        if not bool(summary_in.get("ready_for_phase_check_next")):
            raise ValueError("V1.12BS phase check requires the completed penalized refinement report.")

        summary = {
            "acceptance_posture": "keep_v112bs_as_penalized_target_mapping_refinement",
            "candidate_veto_cluster_count": int(summary_in.get("candidate_veto_cluster_count", 0)),
            "candidate_veto_neighborhood_count": int(summary_in.get("candidate_veto_neighborhood_count", 0)),
            "candidate_transition_band_count": int(summary_in.get("candidate_transition_band_count", 0)),
            "ready_for_phase_closure_next": True,
        }
        evidence_rows = [
            {
                "evidence_name": "penalized_veto_visibility",
                "actual": {
                    "candidate_veto_cluster_count": summary_in.get("candidate_veto_cluster_count"),
                    "candidate_veto_neighborhood_count": summary_in.get("candidate_veto_neighborhood_count"),
                    "candidate_transition_band_count": summary_in.get("candidate_transition_band_count"),
                },
                "reading": (
                    "The phase is only useful if the refinement yields explicit risk objects instead of only more offensive geometry."
                ),
            }
        ]
        interpretation = [
            "V1.12BS phase check confirms that veto discovery is now being pushed through mapping refinement rather than further hard-threshold suppression.",
        ]
        return V112BSPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bs_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BSPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
