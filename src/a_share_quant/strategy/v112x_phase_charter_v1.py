from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112XPhaseCharterReport:
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


class V112XPhaseCharterAnalyzer:
    def analyze(self, *, v112w_phase_closure_payload: dict[str, Any]) -> V112XPhaseCharterReport:
        closure_summary = dict(v112w_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("enter_v112w_waiting_state_now")):
            raise ValueError("V1.12X requires V1.12W to have lawfully closed.")

        charter = {
            "phase_name": "V1.12X CPO Spillover Sidecar Probe",
            "mission": (
                "Use a bounded black-box sidecar posture to score whether the preserved CPO spillover rows show enough "
                "repeatable structure to remain as A-share-specific spillover-factor candidates, without confusing probe "
                "results with formal feature promotion."
            ),
            "in_scope": [
                "probe only the three spillover rows frozen in V1.12T",
                "separate bounded spillover-factor candidates from weaker name-bonus memory rows",
                "freeze review-only sidecar scores and candidacy posture",
            ],
            "out_of_scope": [
                "formal feature promotion",
                "training",
                "signal generation",
                "new spillover discovery",
                "general board-factor modeling",
            ],
            "success_criteria": [
                "the spillover rows are no longer only preserved noise memory",
                "bounded A-share-specific spillover-factor candidacy is probed explicitly",
                "weaker rows remain preserved without being over-promoted",
            ],
            "stop_criteria": [
                "the phase turns review candidacy into formal feature action",
                "the phase silently drops preserved spillover memory",
                "the phase expands beyond the frozen three-row spillover set",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112x_cpo_spillover_sidecar_probe",
            "do_open_v112x_now": True,
            "selected_archetype": "optical_link_price_and_demand_upcycle",
            "recommended_first_action": "freeze_v112x_cpo_spillover_sidecar_probe_v1",
        }
        interpretation = [
            "V1.12X attacks the last unresolved spillover-factor gap from the CPO foundation line.",
            "Its purpose is bounded black-box sidecar probing, not model integration.",
            "The result should keep weak spillover memory and explicit candidate status separate.",
        ]
        return V112XPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112x_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112XPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
