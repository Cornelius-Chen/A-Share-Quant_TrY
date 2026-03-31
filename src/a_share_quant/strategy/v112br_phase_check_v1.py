from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BRPhaseCheckReport:
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


class V112BRPhaseCheckAnalyzer:
    def analyze(self, *, resonance_payload: dict[str, Any]) -> V112BRPhaseCheckReport:
        summary_in = dict(resonance_payload.get("summary", {}))
        if not bool(summary_in.get("ready_for_phase_check_next")):
            raise ValueError("V1.12BR phase check requires the completed resonance discovery report.")

        summary = {
            "acceptance_posture": "keep_v112br_as_state_representation_and_resonance_discovery",
            "cluster_count": int(summary_in.get("cluster_count", 0)),
            "offensive_cluster_count": int(summary_in.get("offensive_cluster_count", 0)),
            "veto_cluster_count": int(summary_in.get("veto_cluster_count", 0)),
            "ready_for_phase_closure_next": True,
        }
        evidence_rows = [
            {
                "evidence_name": "cluster_target_mapping",
                "actual": {
                    "offensive_cluster_count": summary_in.get("offensive_cluster_count"),
                    "veto_cluster_count": summary_in.get("veto_cluster_count"),
                    "candidate_bundle_count": summary_in.get("candidate_bundle_count"),
                },
                "reading": "The phase is only meaningful if the discovered state structure can be mapped back to offensive and veto regions.",
            }
        ]
        interpretation = [
            "V1.12BR phase check confirms that state geometry is now being used to discover candidate decision regions instead of more low-dimensional threshold scans.",
        ]
        return V112BRPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112br_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BRPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
