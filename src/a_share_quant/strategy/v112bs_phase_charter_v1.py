from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BSPhaseCharterReport:
    summary: dict[str, Any]
    charter: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "charter": self.charter,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BSPhaseCharterAnalyzer:
    def analyze(
        self,
        *,
        v112br_phase_closure_payload: dict[str, Any],
        v112bq_phase_closure_payload: dict[str, Any],
    ) -> V112BSPhaseCharterReport:
        if not bool(dict(v112br_phase_closure_payload.get("summary", {})).get("v112br_success_criteria_met")):
            raise ValueError("V1.12BR must be closed before V1.12BS can open.")
        if not bool(dict(v112bq_phase_closure_payload.get("summary", {})).get("v112bq_success_criteria_met")):
            raise ValueError("V1.12BQ must be closed before V1.12BS can open.")

        charter = {
            "phase_name": "V1.12BS Penalized Target Mapping Refinement",
            "mission": (
                "Refine the high-dimensional state-space mapping so that veto and risk structure can become visible "
                "without collapsing back into a low-dimensional hard gate. The focus is on penalty shaping at the "
                "mapping layer, plus explicit local-neighborhood and transition-band extraction."
            ),
            "in_scope": [
                "reuse the frozen V1.12BR state representation",
                "add outcome penalties for bad-trade density, severity, and drawdown tails",
                "add secondary structure penalties for maturity, crowding, and deterioration",
                "extract candidate veto regions at cluster, neighborhood, and transition-band levels",
            ],
            "out_of_scope": [
                "changing the core clustering method",
                "returning to low-dimensional threshold sweeps",
                "formal training opening",
                "formal signal generation",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112bs_penalized_target_mapping_refinement",
            "do_open_v112bs_now": True,
            "recommended_first_action": "freeze_v112bs_penalized_target_mapping_refinement_v1",
        }
        interpretation = [
            "V1.12BS opens because V1.12BR showed offensive geometry clearly but did not produce a clean veto structure.",
            "The lawful next move is not to re-scan hard thresholds, but to make risk structure more visible at the mapping layer.",
        ]
        return V112BSPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112bs_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BSPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
