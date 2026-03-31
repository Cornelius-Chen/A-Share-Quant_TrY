from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112PhaseCharterReport:
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


class V112PhaseCharterAnalyzer:
    """Open a single price-cycle experimental training pilot."""

    def analyze(
        self,
        *,
        v111a_phase_closure_payload: dict[str, Any],
        owner_phase_switch_approved: bool,
    ) -> V112PhaseCharterReport:
        closure_summary = dict(v111a_phase_closure_payload.get("summary", {}))
        prior_branch_closed = bool(closure_summary.get("enter_v111a_waiting_state_now"))
        do_open_now = prior_branch_closed and owner_phase_switch_approved

        charter = {
            "mission": (
                "Define one high-observability price-cycle experimental training pilot that can later "
                "expand into a broader object set without losing state, label, and validation discipline."
            ),
            "in_scope": [
                "select one pilot carry family and one pilot cycle archetype",
                "freeze training objective and label posture",
                "freeze minimal feature blocks for one cycle experiment",
                "freeze expansion rules for later multi-object scaling",
            ],
            "out_of_scope": [
                "strategy integration",
                "full multi-cycle training",
                "intraday execution modeling",
                "retained-feature promotion",
                "heavy black-box model deployment",
            ],
            "success_criteria": [
                "select one pilot cycle with high observable richness",
                "freeze a minimal training protocol for one-cycle experimentation",
                "state how later object expansion should occur without breaking validation discipline",
            ],
            "stop_criteria": [
                "if no single cycle can be selected without mixing multiple carry families",
                "if training objectives cannot be specified without execution leakage",
                "if the phase drifts into direct signal integration or broad model work",
            ],
            "handoff_condition": (
                "After pilot selection and protocol freeze, the next legal move is bounded pilot data assembly "
                "or another owner-reviewed phase switch."
            ),
            "exploration_layer_phase": True,
        }
        summary = {
            "acceptance_posture": (
                "open_v112_single_price_cycle_experimental_training_pilot"
                if do_open_now
                else "hold_v112_until_owner_switch_after_v111a_waiting_state"
            ),
            "do_open_v112_now": do_open_now,
            "owner_phase_switch_approved": owner_phase_switch_approved,
            "recommended_first_action": "freeze_v112_pilot_cycle_selection_v1",
        }
        interpretation = [
            "V1.12 is not a broad model phase; it is a bounded pilot-design phase for one price cycle.",
            "The point is to learn one high-signal cycle cleanly before scaling to many objects.",
            "The next legal move is to pick the pilot cycle family and archetype rather than train immediately.",
        ]
        return V112PhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112PhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
