from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BRPhaseClosureCheckReport:
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


class V112BRPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112BRPhaseClosureCheckReport:
        if not bool(dict(phase_check_payload.get("summary", {})).get("ready_for_phase_closure_next")):
            raise ValueError("V1.12BR closure requires the completed phase check.")

        summary = {
            "acceptance_posture": "close_v112br_as_state_representation_and_resonance_discovery_success",
            "v112br_success_criteria_met": True,
            "enter_v112br_waiting_state_now": True,
            "formal_training_now": False,
            "formal_signal_generation_now": False,
        }
        evidence_rows = [
            {
                "evidence_name": "v112br_phase_check",
                "actual": {
                    "cluster_count": dict(phase_check_payload.get("summary", {})).get("cluster_count"),
                    "offensive_cluster_count": dict(phase_check_payload.get("summary", {})).get("offensive_cluster_count"),
                    "veto_cluster_count": dict(phase_check_payload.get("summary", {})).get("veto_cluster_count"),
                },
                "reading": "The phase closes once state geometry has yielded explicit candidate offensive and veto regions.",
            }
        ]
        interpretation = [
            "V1.12BR closes with the first lawful state-space discovery layer for CPO gate research.",
        ]
        return V112BRPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112br_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BRPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
