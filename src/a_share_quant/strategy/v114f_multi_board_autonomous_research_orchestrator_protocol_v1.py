from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V114FMultiBoardAutonomousResearchOrchestratorProtocolReport:
    summary: dict[str, Any]
    phase_stack: list[dict[str, Any]]
    stop_conditions: list[dict[str, Any]]
    promotion_gates: list[dict[str, Any]]
    execution_rules: list[str]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "phase_stack": self.phase_stack,
            "stop_conditions": self.stop_conditions,
            "promotion_gates": self.promotion_gates,
            "execution_rules": self.execution_rules,
            "interpretation": self.interpretation,
        }


class V114FMultiBoardAutonomousResearchOrchestratorProtocolAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        default_phase_version: str,
        board_queue: list[str],
    ) -> V114FMultiBoardAutonomousResearchOrchestratorProtocolReport:
        phase_stack = [
            {
                "phase_name": "board_world_model",
                "purpose": "convert board research into objects/relations/transitions/constraints instead of answer injection",
                "must_output": ["world_model_prior", "board_label_summary"],
            },
            {
                "phase_name": "role_grammar",
                "purpose": "derive internal role structure and relative hierarchy under the board label",
                "must_output": ["role_labels", "relative_structure_labels"],
            },
            {
                "phase_name": "control_extraction",
                "purpose": "translate structure into eligibility/de-risk/veto/admission semantics",
                "must_output": ["control_labels", "candidate_control_surface"],
            },
            {
                "phase_name": "paper_replay",
                "purpose": "bind lawful controls into time-ordered replay with T+1 and no-leverage constraints",
                "must_output": ["replay_curve", "executed_orders", "blocked_intents"],
            },
            {
                "phase_name": "bottleneck_diagnosis",
                "purpose": "locate the main failure mode: selection, timing, sizing, or over-control",
                "must_output": ["primary_bottleneck", "attribution_summary"],
            },
            {
                "phase_name": "sizing_upgrade",
                "purpose": "upgrade expression through probability/expectancy, soft-gate sizing, and constrained add/reduce",
                "must_output": ["stable_zone", "default_sizing_candidate"],
            },
            {
                "phase_name": "unsupervised_candidate_state_audit",
                "purpose": "discover candidate high-dimensional states that may improve add/reduce/sizing without legislating them",
                "must_output": ["candidate_state_families", "audit_results"],
            },
            {
                "phase_name": "promotion_gate",
                "purpose": "decide whether the board exits as mainline asset, candidate, sidecar, or diagnostic-only",
                "must_output": ["terminal_status", "promotion_notes"],
            },
        ]

        stop_conditions = [
            {
                "condition_name": "terminal_status_reached",
                "trigger": "board reaches mainline_asset / candidate / sidecar / diagnostic status",
            },
            {
                "condition_name": "no_incremental_value",
                "trigger": "two consecutive upgrade loops fail to improve replay or audit evidence materially",
            },
            {
                "condition_name": "hard_data_block",
                "trigger": "missing lawful feed, owner label, or no-leak compatible episode inputs",
            },
            {
                "condition_name": "overfit_warning",
                "trigger": "discoveries remain sample-specific and fail stability/action-relevance judgement",
            },
        ]

        promotion_gates = [
            {
                "gate_name": "no_leak_gate",
                "rule": "only point-in-time visible labels, priors, and market context may influence training or replay decisions",
            },
            {
                "gate_name": "replay_gate",
                "rule": "candidate controls must survive time-ordered replay before promotion",
            },
            {
                "gate_name": "stable_zone_gate",
                "rule": "sizing promotion must come from a stable zone, not a single lucky parameter point",
            },
            {
                "gate_name": "unsupervised_audit_gate",
                "rule": "candidate states discovered by vectors must pass stability, action relevance, boundary clarity, and incremental value judgement",
            },
        ]

        execution_rules = [
            "run the full phase stack for each board in queue order without waiting for a new user prompt between phases",
            "do not reopen already-frozen mainline assets unless a hard audit failure appears",
            "allow single-board iteration loops only inside the board until one stop condition is hit",
            "escalate to manual intervention only when a hard data block or promotion ambiguity remains after audit",
            "treat single-symbol case work as mechanism discovery or residual repair, not as the primary training unit",
        ]

        summary = {
            "acceptance_posture": "freeze_v114f_multi_board_autonomous_research_orchestrator_protocol_v1",
            "default_phase_version": default_phase_version,
            "board_queue_count": len(board_queue),
            "phase_count": len(phase_stack),
            "stop_condition_count": len(stop_conditions),
            "promotion_gate_count": len(promotion_gates),
            "autonomous_posture": "run_until_terminal_status_per_board_without_manual_reprompt",
            "recommended_next_posture": "seed_board_queue_and_start_autonomous_research_runner",
        }

        interpretation = [
            "V1.14F turns the board-research method into a one-shot orchestration protocol: once a board enters the queue, it should keep moving through the fixed phase stack until a terminal status or hard stop appears.",
            "This protocol is intentionally not an infinite research machine. It is a bounded board worker with explicit stop conditions, promotion gates, and lawful replay requirements.",
            "The goal is to stop asking the user to reissue the same orchestration command every phase while still preserving auditability and anti-overfitting discipline.",
        ]

        return V114FMultiBoardAutonomousResearchOrchestratorProtocolReport(
            summary=summary,
            phase_stack=phase_stack,
            stop_conditions=stop_conditions,
            promotion_gates=promotion_gates,
            execution_rules=execution_rules,
            interpretation=interpretation,
        )


def write_v114f_multi_board_autonomous_research_orchestrator_protocol_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V114FMultiBoardAutonomousResearchOrchestratorProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path

