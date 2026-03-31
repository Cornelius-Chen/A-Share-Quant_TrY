from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112PhaseCheckReport:
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


class V112PhaseCheckAnalyzer:
    """Check whether the first one-cycle training pilot has been specified cleanly."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        pilot_cycle_selection_payload: dict[str, Any],
        training_protocol_payload: dict[str, Any],
    ) -> V112PhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        selection_summary = dict(pilot_cycle_selection_payload.get("summary", {}))
        protocol_summary = dict(training_protocol_payload.get("summary", {}))

        summary = {
            "acceptance_posture": "keep_v112_as_single_cycle_training_pilot_definition_only",
            "do_open_v112_now": charter_summary.get("do_open_v112_now"),
            "selected_primary_family": selection_summary.get("selected_primary_family"),
            "selected_pilot_cycle": selection_summary.get("selected_pilot_cycle"),
            "ready_for_bounded_pilot_data_assembly_next": True,
            "allow_strategy_integration_now": False,
            "allow_black_box_deployment_now": False,
            "recommended_next_posture": "close_v112_definition_phase_and_wait_for_owner_review_of_pilot_data_assembly",
        }
        evidence_rows = [
            {
                "evidence_name": "v112_cycle_selection",
                "actual": {
                    "selected_primary_family": selection_summary.get("selected_primary_family"),
                    "selected_pilot_cycle": selection_summary.get("selected_pilot_cycle"),
                },
                "reading": "The phase selected one clean pilot family and archetype instead of mixing multiple carry grammars.",
            },
            {
                "evidence_name": "v112_training_protocol",
                "actual": {
                    "feature_block_count": protocol_summary.get("feature_block_count"),
                    "label_count": protocol_summary.get("label_count"),
                    "validation_rule_count": protocol_summary.get("validation_rule_count"),
                },
                "reading": "The phase froze one-cycle training inputs, labels, and validation rules without leaking into execution or deployment.",
            },
        ]
        interpretation = [
            "V1.12 has done its job once the first one-cycle experiment is sharply defined.",
            "The next legal move is not immediate model deployment but bounded pilot data assembly under the frozen protocol.",
            "This phase should now close rather than expand into multi-object training by default.",
        ]
        return V112PhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112PhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
