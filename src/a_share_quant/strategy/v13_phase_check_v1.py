from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V13PhaseCheckReport:
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


class V13PhaseCheckAnalyzer:
    """Check the bounded posture of V1.3 after the first concept-context cycle."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        concept_inventory_payload: dict[str, Any],
        concept_audit_payload: dict[str, Any],
    ) -> V13PhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        inventory_summary = dict(concept_inventory_payload.get("summary", {}))
        audit_summary = dict(concept_audit_payload.get("summary", {}))

        open_v13 = bool(charter_summary.get("do_open_v13_now"))
        concept_separation_present = bool(audit_summary.get("concept_context_separation_present"))
        promote_now = bool(audit_summary.get("promote_concept_branch_now"))

        summary = {
            "acceptance_posture": "keep_v13_active_but_bounded_as_context_infrastructure",
            "v13_open": open_v13,
            "concept_mapping_inventory_frozen": bool(
                inventory_summary.get("acceptance_posture") == "freeze_v13_concept_mapping_inventory_v1"
            ),
            "concept_context_separation_present": concept_separation_present,
            "promote_concept_branch_now": promote_now,
            "do_expand_v13_widely_now": False,
            "do_integrate_into_strategy_now": False,
            "recommended_next_posture": "continue_bounded_v13_infrastructure_only_if_next_artifact_stays_replay_independent",
        }
        evidence_rows = [
            {
                "evidence_name": "phase_charter",
                "actual": {
                    "acceptance_posture": charter_summary.get("acceptance_posture"),
                    "recommended_first_action": charter_summary.get("recommended_first_action"),
                },
                "reading": "V1.3 is a lawful phase only because it opened as infrastructure work, not as direct signal integration.",
            },
            {
                "evidence_name": "concept_inventory",
                "actual": {
                    "acceptance_posture": inventory_summary.get("acceptance_posture"),
                    "requires_point_in_time_mapping": inventory_summary.get("requires_point_in_time_mapping"),
                    "requires_market_confirmation_layer": inventory_summary.get("requires_market_confirmation_layer"),
                },
                "reading": "The concept branch is now grounded in a frozen mapping framework instead of ad hoc labels.",
            },
            {
                "evidence_name": "concept_context_audit",
                "actual": {
                    "acceptance_posture": audit_summary.get("acceptance_posture"),
                    "concept_context_separation_present": concept_separation_present,
                    "promote_concept_branch_now": promote_now,
                },
                "reading": "The first bounded concept audit shows useful separation, but still not enough to promote the branch or integrate it into the strategy.",
            },
        ]
        interpretation = [
            "V1.3 is producing real infrastructure value: concept mapping is now point-in-time aware, market-confirmed, and auditable.",
            "But the branch remains bounded because the current concept context evidence is still report-only and replay-independent.",
            "So V1.3 should continue only through bounded infrastructure artifacts, not through strategy integration or wide ingestion.",
        ]
        return V13PhaseCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v13_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V13PhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
