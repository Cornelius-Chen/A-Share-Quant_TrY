from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V13PhaseCharterReport:
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


class V13PhaseCharterAnalyzer:
    """Open V1.3 after V1.2 enters waiting state and owner approves a phase switch."""

    def analyze(
        self,
        *,
        v12_waiting_state_payload: dict[str, Any],
        catalyst_schema_payload: dict[str, Any],
        catalyst_audit_payload: dict[str, Any],
        catalyst_phase_check_payload: dict[str, Any],
    ) -> V13PhaseCharterReport:
        waiting_summary = dict(v12_waiting_state_payload.get("summary", {}))
        schema_summary = dict(catalyst_schema_payload.get("summary", {}))
        audit_summary = dict(catalyst_audit_payload.get("summary", {}))
        branch_summary = dict(catalyst_phase_check_payload.get("summary", {}))

        waiting_ready = bool(waiting_summary.get("enter_explicit_waiting_state_now"))
        catalyst_ready = bool(schema_summary.get("ready_for_bounded_registry_seeding")) and bool(
            audit_summary.get("context_separation_present")
        )
        branch_support_real = bool(branch_summary.get("context_separation_present")) and bool(
            branch_summary.get("keep_branch_report_only")
        )
        open_v13_now = waiting_ready and catalyst_ready and branch_support_real

        charter = {
            "mission": "Build bounded catalyst and concept context infrastructure that can feed later research without directly entering the strategy mainline.",
            "in_scope": [
                "event registry structure",
                "concept mapping inventory",
                "event-to-theme/sector/symbol mapping rules",
                "market-confirmation layer",
                "bounded context-support artifacts",
            ],
            "out_of_scope": [
                "strategy integration",
                "heavy NLP or real-time news systems",
                "paid data sources",
                "promotion of report-only catalyst features into retained features",
            ],
            "success_criteria": [
                "freeze a usable concept/context mapping framework",
                "define bounded source and mapping rules",
                "produce at least one replay-independent infrastructure artifact that future branches can consume",
            ],
            "stop_criteria": [
                "if concept/context infrastructure cannot improve on the existing bounded catalyst branch",
                "if the work would require heavy dependencies or paid sources",
                "if the branch drifts into direct strategy integration before the infrastructure is stable",
            ],
            "handoff_condition": "After the infrastructure entry action completes, continue only with bounded mapping and registry work inside V1.3.",
        }
        summary = {
            "acceptance_posture": (
                "open_v13_catalyst_and_concept_context_infrastructure"
                if open_v13_now
                else "hold_v13_charter_until_phase_switch_conditions_hold"
            ),
            "v12_waiting_state_present": waiting_ready,
            "catalyst_schema_ready": bool(schema_summary.get("ready_for_bounded_registry_seeding")),
            "catalyst_context_separation_present": bool(audit_summary.get("context_separation_present")),
            "catalyst_branch_support_real": branch_support_real,
            "do_open_v13_now": open_v13_now,
            "recommended_first_action": "freeze_v13_concept_mapping_inventory_v1",
        }
        interpretation = [
            "V1.2 has already reached explicit waiting state, so a new phase now requires an owner-directed switch plus a lawful charter.",
            "The catalyst branch is real enough to justify infrastructure work because it has a frozen schema and bounded separation evidence, but it remains below promotion threshold.",
            "So V1.3 should open as infrastructure work, not as direct signal or training work, and concept mapping inventory is the correct first bounded action.",
        ]
        return V13PhaseCharterReport(
            summary=summary,
            charter=charter,
            interpretation=interpretation,
        )


def write_v13_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V13PhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
