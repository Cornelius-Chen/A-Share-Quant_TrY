from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112PPhaseCharterReport:
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


class V112PPhaseCharterAnalyzer:
    def analyze(
        self,
        *,
        v112o_phase_closure_payload: dict[str, Any],
        owner_requests_full_information_map: bool,
    ) -> V112PPhaseCharterReport:
        closure_summary = dict(v112o_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("enter_v112o_waiting_state_now")):
            raise ValueError("V1.12P requires V1.12O to close into waiting state first.")

        do_open_now = owner_requests_full_information_map
        charter = {
            "phase_name": "V1.12P CPO Full-Cycle Information Registry",
            "mission": (
                "Collect a broad but governed CPO full-cycle information map across catalysts, earnings, technology, "
                "market-state, liquidity, and cohort-expansion objects so later factor/label/training work starts from "
                "a much less incomplete review surface."
            ),
            "in_scope": [
                "freeze multi-layer information dimensions for the CPO cycle",
                "record core leaders, direct related names, extension-concept names, and mixed-relevance drift names",
                "capture review-only catalyst timeline anchors from public sources",
                "capture review-only earnings and business-line anchors from public sources",
                "explicitly record remaining gaps where information is still missing or noisy",
            ],
            "out_of_scope": [
                "automatic label freeze",
                "automatic model feature promotion",
                "automatic training rerun",
                "execution timing",
                "signal generation",
            ],
            "success_criteria": [
                "the CPO line has a broad layered registry rather than a narrow three-name training surface",
                "the registry distinguishes core, adjacent, extension, and mixed-relevance names cleanly",
                "the next discussion can focus on missing information and cohort validation rather than object discovery from scratch",
            ],
            "stop_criteria": [
                "the phase drifts into claiming business relevance that has not been validated",
                "the phase turns review-only information into automatic training candidates",
                "the scope leaks into execution or signal logic",
            ],
        }
        summary = {
            "acceptance_posture": (
                "open_v112p_cpo_full_cycle_information_registry"
                if do_open_now
                else "hold_v112p_until_owner_requests_full_information_map"
            ),
            "do_open_v112p_now": do_open_now,
            "selected_archetype": "optical_link_price_and_demand_upcycle",
            "recommended_first_action": "freeze_v112p_cpo_full_cycle_information_registry_v1",
        }
        interpretation = [
            "V1.12P is intentionally information-heavy and review-first: it exists to reduce omission risk before the next cohort-validation or training decision.",
            "This phase expands the information surface, not the training authorization surface.",
            "The mainline goal is completeness of review memory, including noisy names that may later prove useless.",
        ]
        return V112PPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112p_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112PPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
