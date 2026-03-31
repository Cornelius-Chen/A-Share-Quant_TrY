from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V14PhaseCharterReport:
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


class V14PhaseCharterAnalyzer:
    """Open V1.4 after V1.3 closes and the owner requests context-consumption work."""

    def analyze(
        self,
        *,
        v13_phase_closure_payload: dict[str, Any],
        concept_usage_rules_payload: dict[str, Any],
        catalyst_context_audit_payload: dict[str, Any],
    ) -> V14PhaseCharterReport:
        closure_summary = dict(v13_phase_closure_payload.get("summary", {}))
        usage_summary = dict(concept_usage_rules_payload.get("summary", {}))
        audit_summary = dict(catalyst_context_audit_payload.get("summary", {}))

        v13_waiting_ready = bool(closure_summary.get("enter_v13_waiting_state_now"))
        concept_usage_ready = usage_summary.get("row_count", 0) > 0 and (
            usage_summary.get("strategy_integration_allowed_count", 0) == 0
        )
        catalyst_context_ready = bool(audit_summary.get("context_separation_present")) and bool(
            audit_summary.get("keep_branch_report_only")
        )
        open_v14_now = v13_waiting_ready and concept_usage_ready and catalyst_context_ready

        charter = {
            "mission": "Validate whether bounded catalyst and concept context can be consumed as point-in-time, source-aware, market-confirmed report-only features that add stable discrimination across opening, persistence, and carry lanes.",
            "in_scope": [
                "freeze the V1.3-consumable input set",
                "define a context consumption protocol",
                "bind bounded context rows to lane or sample scope",
                "produce report-only context feature candidates",
                "run bounded discrimination checks",
            ],
            "out_of_scope": [
                "strategy integration",
                "retained-feature promotion",
                "formal model work or strategy-level ML",
                "wide replay expansion",
                "new heavy dependencies or paid data",
            ],
            "success_criteria": [
                "bounded context rows can be stably consumed by auditable rules",
                "at least one report-only context feature shows stable discrimination value",
                "the phase can close with a clear next posture: continue report-only, candidate review, or waiting state",
            ],
            "stop_criteria": [
                "if context binding stays too sparse or noisy",
                "if bounded discrimination remains unstable after small-sample review",
                "if the work drifts into strategy integration or retained-feature promotion",
            ],
            "handoff_condition": "After the charter opens, only replay-independent context-consumption artifacts are allowed until a phase-level review says otherwise.",
        }
        summary = {
            "acceptance_posture": (
                "open_v14_context_consumption_pilot"
                if open_v14_now
                else "hold_v14_charter_until_prerequisites_hold"
            ),
            "v13_waiting_state_present": v13_waiting_ready,
            "concept_usage_rules_ready": concept_usage_ready,
            "catalyst_context_ready": catalyst_context_ready,
            "do_open_v14_now": open_v14_now,
            "recommended_first_action": "freeze_v14_context_consumption_protocol_v1",
        }
        interpretation = [
            "V1.3 closed successfully as bounded infrastructure, so the next lawful question is whether that infrastructure can actually be consumed.",
            "The catalyst branch already shows directional separation, but still below promotion threshold; that makes it suitable for a report-only consumption pilot rather than strategy work.",
            "So V1.4 should open as a bounded context-consumption phase, not as a model, refresh, or signal-integration phase.",
        ]
        return V14PhaseCharterReport(
            summary=summary,
            charter=charter,
            interpretation=interpretation,
        )


def write_v14_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V14PhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
