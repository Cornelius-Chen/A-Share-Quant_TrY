from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113HPhaseCharterReport:
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


class V113HPhaseCharterAnalyzer:
    """Open the transition from structure adjudication into execution adjudication."""

    def analyze(
        self,
        *,
        v112cw_payload: dict[str, Any],
        v112cx_payload: dict[str, Any],
        owner_approves_execution_transition: bool,
    ) -> V113HPhaseCharterReport:
        cw_summary = dict(v112cw_payload.get("summary", {}))
        cx_summary = dict(v112cx_payload.get("summary", {}))

        packaging_surface_ready = bool(cw_summary.get("mainline_extension_count", 0) == 1)
        core_leader_ready = bool(cx_summary.get("promotion_ready", False))
        do_open_now = packaging_surface_ready and core_leader_ready and owner_approves_execution_transition

        charter = {
            "mission": (
                "Convert the current CPO structure-adjudication stack into an execution-adjudication program by "
                "hardening control semantics, introducing explicit cost functions, and subjecting the frozen "
                "mainline surface plus promotable residual controls to dirty-market and out-of-regime judgement."
            ),
            "in_scope": [
                "hard-trigger semantics for entry_veto, de_risk, holding_veto, and admission-extension actions",
                "explicit layered cost function for false promotion, late de-risk, missed mainline, and overstay errors",
                "dirty-market stress design against fake extension, false resonance, and adversarial late-stage traps",
                "out-of-cycle and out-of-regime judgement of the current CPO control surface",
                "preservation of packaging mainline surface and standalone 300308 holding-veto posture during execution-layer hardening",
            ],
            "out_of_scope": [
                "reopening packaging template learning",
                "joint 300308/300502 promotion",
                "automatic training release",
                "automatic signal deployment",
                "broad model-zoo expansion unrelated to execution hardening",
            ],
            "success_criteria": [
                "rewrite current control objects into trigger, action, reversibility, and reset semantics",
                "freeze a first explicit cost-function ledger for the main CPO control families",
                "show which parts of the current stack survive dirty-market stress and which fail",
                "show which parts of the current stack remain valid outside the in-cycle comfort zone",
            ],
            "stop_criteria": [
                "if new exploratory templates are opened before hard-trigger semantics are frozen",
                "if the phase drifts back into unconstrained structure discovery",
                "if stress results are explained away instead of recorded as binding execution costs",
            ],
            "handoff_condition": (
                "After hard-trigger and cost-function freeze, the next legal move is bounded execution replay or "
                "stress-result-driven revision, not automatic deployment."
            ),
            "selected_focus": [
                "hard-trigger semantics",
                "cost-function ledger",
                "dirty-market stress",
                "out-of-regime judgement",
            ],
            "frozen_inputs": [
                "packaging mainline surface",
                "300308 promotable standalone holding-veto candidate",
                "300502 split de-risk sidecar kept outside joint promotion",
            ],
        }
        summary = {
            "acceptance_posture": (
                "open_v113h_execution_decision_layer_phase"
                if do_open_now
                else "hold_v113h_until_packaging_surface_and_core_leader_are_both_frozen_and_owner_approved"
            ),
            "do_open_v113h_now": do_open_now,
            "selected_program": "cpo_execution_decision_layer_transition",
            "packaging_mainline_surface_ready": packaging_surface_ready,
            "core_leader_promotable_ready": core_leader_ready,
            "recommended_first_action": "freeze_v113h_hard_trigger_semantics_and_cost_function_ledger_v1",
        }
        interpretation = [
            "V1.13H exists because the project now has structure selection and promotion discipline, but still needs a unified execution adjudication layer.",
            "The phase does not widen discovery; it hardens already-frozen CPO assets into trigger, cost, and judgement objects.",
            "Dirty-market stress and out-of-regime judgement are now first-class requirements rather than optional later validation.",
        ]
        return V113HPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v113h_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113HPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
