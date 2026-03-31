from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112PilotCycleSelectionReport:
    summary: dict[str, Any]
    selection: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "selection": self.selection,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112PilotCycleSelectionAnalyzer:
    """Select a single price-cycle archetype for the first experiment."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
    ) -> V112PilotCycleSelectionReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112_now")):
            raise ValueError("V1.12 must be open before pilot cycle selection can be frozen.")

        selection = {
            "selected_primary_family": "earnings_transmission_carry",
            "selected_pilot_cycle": "optical_link_price_and_demand_upcycle",
            "why_selected": [
                "high observable richness across catalyst, transmission, expectation, and price-confirmation layers",
                "multiple listed objects can later be added without changing the core bridge logic",
                "the cycle sits closer to earnings transmission than pure theme diffusion, making it safer for first experimental training",
                "the same template can later expand into other price-sensitive industrial chains",
            ],
            "deferred_for_now": [
                "theme_diffusion_carry",
                "expectation_cycle_carry",
                "intraday_execution_layer",
            ],
            "later_expansion_direction": [
                "add adjacent optical-link objects after the first pilot is frozen",
                "add other price-and-margin transmission cycles only after the first split and label protocol survives",
            ],
        }
        summary = {
            "acceptance_posture": "freeze_v112_pilot_cycle_selection_v1",
            "selected_primary_family": selection["selected_primary_family"],
            "selected_pilot_cycle": selection["selected_pilot_cycle"],
            "later_expansion_object_count_mode": "increase_after_first_clean_cycle_only",
            "ready_for_training_protocol_next": True,
        }
        interpretation = [
            "The first experiment should learn one cleaner earnings-transmission cycle before touching more reflexive theme-diffusion cases.",
            "Optical-link price-and-demand upcycle is chosen because it offers richer observable bridges from catalyst to profit and expectation.",
            "This phase does not deny theme-diffusion importance; it simply avoids mixing families in the very first training experiment.",
        ]
        return V112PilotCycleSelectionReport(summary=summary, selection=selection, interpretation=interpretation)


def write_v112_pilot_cycle_selection_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112PilotCycleSelectionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
