from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BCPhaseCheckReport:
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


class V112BCPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        protocol_payload: dict[str, Any],
    ) -> V112BCPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        protocol_summary = dict(protocol_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112bc_as_cpo_portfolio_objective_protocol",
            "do_open_v112bc_now": charter_summary.get("do_open_v112bc_now"),
            "objective_track_count": protocol_summary.get("objective_track_count"),
            "marginal_stop_threshold": protocol_summary.get("marginal_stop_threshold"),
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_closure_next": True,
        }
        evidence_rows = [
            {
                "evidence_name": "v112bc_protocol",
                "actual": {
                    "objective_track_count": protocol_summary.get("objective_track_count"),
                    "no_leak_track_count": protocol_summary.get("no_leak_track_count"),
                    "oracle_track_count": protocol_summary.get("oracle_track_count"),
                    "marginal_stop_threshold": protocol_summary.get("marginal_stop_threshold"),
                },
                "reading": "The protocol is only useful if it separates the oracle benchmark from no-leak portfolio experiments and freezes a stopping rule.",
            }
        ]
        interpretation = [
            "V1.12BC keeps black-box exploration bounded by objective separation and a hard stop rule.",
            "Formal training and signal rights remain closed.",
        ]
        return V112BCPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bc_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BCPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
