from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ZPhaseCharterReport:
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


class V112ZPhaseCharterAnalyzer:
    def analyze(self, *, v112y_phase_closure_payload: dict[str, Any]) -> V112ZPhaseCharterReport:
        closure_summary = dict(v112y_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("enter_v112y_waiting_state_now")):
            raise ValueError("V1.12Z requires V1.12Y to have lawfully closed.")

        charter = {
            "phase_name": "V1.12Z CPO Bounded Cycle Reconstruction",
            "mission": (
                "Run a bounded cycle reconstruction pass over the CPO line so the project can test whether the cleaned "
                "foundation actually reconstructs catalyst ordering, role transitions, spillover behavior, and board-state timing "
                "without prematurely turning that understanding into training or signals."
            ),
            "in_scope": [
                "use the cleaned CPO foundation from V112Q through V112Y",
                "reconstruct one bounded optical-link cycle with stage, role, catalyst, and board-timing overlays",
                "preserve mixed-role and spillover checks instead of over-cleaning them away",
            ],
            "out_of_scope": [
                "formal training",
                "signal generation",
                "execution logic",
                "automatic feature promotion",
                "multi-cycle widening",
            ],
            "success_criteria": [
                "the CPO line can be reconstructed as a coherent bounded cycle",
                "mixed-role and spillover ambiguities are exposed rather than silently erased",
                "the experiment produces a clear judgment on whether the current foundation is robust enough for a later labeling pilot",
            ],
            "stop_criteria": [
                "the phase turns into training-by-stealth",
                "the phase suppresses residual ambiguity to force a clean story",
                "the phase widens beyond the bounded optical-link cycle",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112z_cpo_bounded_cycle_reconstruction",
            "do_open_v112z_now": True,
            "selected_archetype": "optical_link_price_and_demand_upcycle",
            "recommended_first_action": "freeze_v112z_cycle_reconstruction_protocol_v1",
        }
        interpretation = [
            "V1.12Z is the first true downstream experiment after the CPO foundation line was cleaned and challenged.",
            "Its purpose is to expose remaining problems through bounded reconstruction, not to rush into training.",
            "Residual ambiguity should be preserved as evidence if it survives the reconstruction pass.",
        ]
        return V112ZPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112z_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ZPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
