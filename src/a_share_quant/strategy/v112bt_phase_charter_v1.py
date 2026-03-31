from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BTPhaseCharterReport:
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


class V112BTPhaseCharterAnalyzer:
    def analyze(
        self,
        *,
        v112bs_phase_closure_payload: dict[str, Any],
        v112bp_phase_closure_payload: dict[str, Any],
    ) -> V112BTPhaseCharterReport:
        if not bool(dict(v112bs_phase_closure_payload.get("summary", {})).get("v112bs_success_criteria_met")):
            raise ValueError("V1.12BS must be closed before V1.12BT can open.")
        if not bool(dict(v112bp_phase_closure_payload.get("summary", {})).get("v112bp_success_criteria_met")):
            raise ValueError("V1.12BP must be closed before V1.12BT can open.")

        charter = {
            "phase_name": "V1.12BT Phase-Conditioned Veto And Eligibility Extraction",
            "mission": (
                "Translate the high-dimensional offensive bundles, veto neighborhoods, and transition veto bands "
                "into phase-conditioned control objects: eligibility, entry veto, holding veto, and risk-off override."
            ),
            "in_scope": [
                "extract phase-conditioned eligibility rules from offensive geometry",
                "extract entry-veto rules from veto neighborhoods",
                "extract holding-veto rules from transition bands",
                "extract stage-level risk-off override candidates",
            ],
            "out_of_scope": [
                "formal training opening",
                "formal signal generation",
                "new selector family expansion",
                "returning to low-dimensional hard gate sweeps",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112bt_phase_conditioned_veto_and_eligibility_extraction",
            "do_open_v112bt_now": True,
            "recommended_first_action": "freeze_v112bt_phase_conditioned_veto_and_eligibility_extraction_v1",
        }
        interpretation = [
            "V1.12BT opens because risk structure is now visible as dangerous regions, and the lawful next move is to turn those regions into control objects.",
            "The goal is not another abstract risk memo; it is explicit extraction of eligibility, veto, and override candidates.",
        ]
        return V112BTPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112bt_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BTPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
