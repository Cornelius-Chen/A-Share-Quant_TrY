from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V111PhaseCheckReport:
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


class V111PhaseCheckAnalyzer:
    """Check the bounded posture of V1.11 after the infrastructure plan is frozen."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        infrastructure_plan_payload: dict[str, Any],
    ) -> V111PhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        plan_summary = dict(infrastructure_plan_payload.get("summary", {}))

        summary = {
            "acceptance_posture": "keep_v111_active_but_exploration_layer_only",
            "v111_open": bool(charter_summary.get("do_open_v111_now")),
            "ready_for_bounded_first_pilot_next": bool(plan_summary.get("ready_for_bounded_first_pilot_next")),
            "allow_strategy_integration_now": False,
            "allow_retained_promotion_now": False,
            "recommended_next_posture": "prepare_v111_closure_or_owner_review_for_first_pilot",
        }
        evidence_rows = [
            {
                "evidence_name": "solution_shift_memo_to_v111",
                "actual": {"phase_open": charter_summary.get("do_open_v111_now")},
                "reading": "V1.11 was opened as the solution-shift response to an exhausted evidence pool.",
            },
            {
                "evidence_name": "acquisition_infrastructure_plan",
                "actual": {
                    "acquisition_scope_count": plan_summary.get("acquisition_scope_count"),
                    "source_hierarchy_count": plan_summary.get("source_hierarchy_count"),
                    "ready_for_bounded_first_pilot_next": plan_summary.get("ready_for_bounded_first_pilot_next"),
                },
                "reading": "The phase now has a reusable upstream acquisition basis instead of another same-pool review loop.",
            },
        ]
        interpretation = [
            "V1.11 has produced an exploration-layer infrastructure result rather than a direct evidence or promotion result.",
            "This is enough to change the future decision basis without relaxing any admission or mainline gates.",
            "The next legal move is an owner-reviewed first pilot, not automatic strategy integration.",
        ]
        return V111PhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v111_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V111PhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
