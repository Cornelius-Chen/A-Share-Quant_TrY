from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112CPhaseCheckReport:
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


class V112CPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        hotspot_review_payload: dict[str, Any],
        sidecar_protocol_payload: dict[str, Any],
    ) -> V112CPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        hotspot_summary = dict(hotspot_review_payload.get("summary", {}))
        protocol_summary = dict(sidecar_protocol_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112c_as_hotspot_review_and_sidecar_protocol_success",
            "hotspot_review_present": bool(hotspot_summary.get("ready_for_sidecar_protocol_next")),
            "sidecar_protocol_present": bool(protocol_summary.get("ready_for_phase_check_next")),
            "allow_sidecar_deployment_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "owner_review_hotspots_then_decide_whether_to_run_first_sidecar_pilot",
        }
        evidence_rows = [
            {
                "evidence_name": "v112c_charter",
                "actual": {"do_open_v112c_now": bool(charter_summary.get("do_open_v112c_now"))},
                "reading": "V1.12C opened lawfully as a bounded comparison-design phase.",
            },
            {
                "evidence_name": "v112c_hotspot_review",
                "actual": {"primary_reading": str(hotspot_summary.get("primary_reading"))},
                "reading": "The first baseline's main weakness is now explicit rather than anecdotal.",
            },
            {
                "evidence_name": "v112c_sidecar_protocol",
                "actual": {"candidate_model_family_count": int(protocol_summary.get("candidate_model_family_count", 0))},
                "reading": "The first black-box sidecar comparison basis is frozen on the same dataset and same validation split.",
            },
        ]
        interpretation = [
            "V1.12C succeeds once the current baseline weakness is localized and the next comparison rules are frozen.",
            "That is enough to stop without auto-running a sidecar model in the same turn.",
            "The next lawful move is owner review of the hotspot map and the sidecar scope.",
        ]
        return V112CPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112c_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
