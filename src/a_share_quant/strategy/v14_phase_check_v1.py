from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V14PhaseCheckReport:
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


class V14PhaseCheckAnalyzer:
    """Check the bounded posture of V1.4 after the first discrimination cycle."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        bounded_discrimination_payload: dict[str, Any],
    ) -> V14PhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        discrimination_summary = dict(bounded_discrimination_payload.get("summary", {}))

        summary = {
            "acceptance_posture": "keep_v14_active_but_bounded_as_context_consumption_pilot",
            "v14_open": bool(charter_summary.get("do_open_v14_now")),
            "stable_discrimination_present": bool(discrimination_summary.get("stable_discrimination_present")),
            "promote_context_now": False,
            "do_integrate_into_strategy_now": False,
            "do_open_local_model_branch_now": False,
            "recommended_next_posture": "preserve_v14_as_report_only_context_consumption_and_prepare_phase_closure_or_candidate_review",
        }
        evidence_rows = [
            {
                "evidence_name": "v14_charter",
                "actual": {
                    "acceptance_posture": charter_summary.get("acceptance_posture"),
                    "recommended_first_action": charter_summary.get("recommended_first_action"),
                },
                "reading": "V1.4 opened lawfully as consumption work, not as a modeling or signal phase.",
            },
            {
                "evidence_name": "bounded_discrimination_check",
                "actual": {
                    "acceptance_posture": discrimination_summary.get("acceptance_posture"),
                    "stable_discrimination_present": discrimination_summary.get("stable_discrimination_present"),
                    "promote_context_now": discrimination_summary.get("promote_context_now"),
                },
                "reading": "Bounded report-only discrimination can exist without justifying promotion or strategy integration.",
            },
        ]
        interpretation = [
            "V1.4 has now shown whether bounded context consumption produces directional discrimination beyond protocol and schema design.",
            "Even with positive bounded discrimination, the branch remains below promotion threshold and cannot open local-model or strategy work automatically.",
            "The next legal move is a closure/candidacy decision, not uncontrolled expansion.",
        ]
        return V14PhaseCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v14_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V14PhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
