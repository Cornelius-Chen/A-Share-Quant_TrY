from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V13PhaseClosureCheckReport:
    summary: dict[str, Any]
    evidence_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "evidence_rows": self.evidence_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V13PhaseClosureCheckAnalyzer:
    """Check whether V1.3 has reached a bounded and lawful closure point."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        concept_registry_reclassification_payload: dict[str, Any],
        concept_registry_usage_rules_payload: dict[str, Any],
    ) -> V13PhaseClosureCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        reclass_summary = dict(concept_registry_reclassification_payload.get("summary", {}))
        usage_summary = dict(concept_registry_usage_rules_payload.get("summary", {}))

        success_criteria_met = (
            bool(charter_summary.get("do_open_v13_now"))
            and reclass_summary.get("core_confirmed_count", 0) >= 1
            and usage_summary.get("strategy_integration_allowed_count", 0) == 0
        )

        summary = {
            "acceptance_posture": "close_v13_as_bounded_context_infrastructure_success",
            "v13_success_criteria_met": success_criteria_met,
            "core_confirmed_count": reclass_summary.get("core_confirmed_count", 0),
            "market_confirmed_indirect_count": reclass_summary.get("market_confirmed_indirect_count", 0),
            "bounded_context_primary_count": usage_summary.get("bounded_context_primary_count", 0),
            "bounded_context_secondary_count": usage_summary.get("bounded_context_secondary_count", 0),
            "enter_v13_waiting_state_now": success_criteria_met,
            "do_open_follow_on_v13_branch_now": False,
            "recommended_next_posture": "preserve_v13_bounded_registry_and_wait_for_owner_phase_switch_or_trigger",
        }
        evidence_rows = [
            {
                "evidence_name": "phase_charter",
                "actual": {
                    "acceptance_posture": charter_summary.get("acceptance_posture"),
                    "mission": charter_summary.get("mission"),
                },
                "reading": "V1.3 opened as bounded infrastructure work and should close on infrastructure success rather than drift into signal work.",
            },
            {
                "evidence_name": "concept_registry_reclassification",
                "actual": {
                    "acceptance_posture": reclass_summary.get("acceptance_posture"),
                    "core_confirmed_count": reclass_summary.get("core_confirmed_count"),
                    "market_confirmed_indirect_count": reclass_summary.get("market_confirmed_indirect_count"),
                },
                "reading": "The concept registry now has explicit proof-backed classes instead of a fully provisional structure.",
            },
            {
                "evidence_name": "concept_registry_usage_rules",
                "actual": {
                    "acceptance_posture": usage_summary.get("acceptance_posture"),
                    "bounded_context_primary_count": usage_summary.get("bounded_context_primary_count"),
                    "strategy_integration_allowed_count": usage_summary.get("strategy_integration_allowed_count"),
                },
                "reading": "Usage rules preserve the bounded posture by keeping concept rows out of the strategy mainline.",
            },
        ]
        interpretation = [
            "V1.3 has now delivered a replay-independent, point-in-time-aware, market-confirmed, and usage-bounded concept infrastructure layer.",
            "That satisfies the phase mission without requiring wider ingestion, heavier dependencies, or strategy integration.",
            "Per the autonomy policy, the correct move is to close V1.3 and enter explicit waiting state rather than invent a new branch.",
        ]
        return V13PhaseClosureCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v13_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V13PhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
