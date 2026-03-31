from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V18APhaseCheckReport:
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


class V18APhaseCheckAnalyzer:
    """Check the bounded posture of V1.8A after breadth-entry design."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        breadth_entry_design_payload: dict[str, Any],
    ) -> V18APhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        design_summary = dict(breadth_entry_design_payload.get("summary", {}))

        summary = {
            "acceptance_posture": "keep_v18a_active_but_bounded_as_sample_breadth_expansion_design",
            "v18a_open": bool(charter_summary.get("do_open_v18a_now")),
            "target_feature_count": charter_summary.get("sample_breadth_target_feature_count", 0),
            "entry_row_count": design_summary.get("entry_row_count", 0),
            "collect_samples_now": False,
            "promote_retained_now": False,
            "do_integrate_into_strategy_now": False,
            "recommended_next_posture": "prepare_v18a_phase_closure_or_waiting_state_not_sample_collection",
        }
        evidence_rows = [
            {
                "evidence_name": "v18a_charter",
                "actual": {
                    "acceptance_posture": charter_summary.get("acceptance_posture"),
                    "target_feature_names": charter_summary.get("target_feature_names"),
                },
                "reading": "V1.8A opened lawfully as a bounded sample-breadth expansion phase for two explicit targets.",
            },
            {
                "evidence_name": "breadth_entry_design",
                "actual": {
                    "entry_row_count": design_summary.get("entry_row_count"),
                    "allow_unbounded_sample_collection_now": design_summary.get("allow_unbounded_sample_collection_now"),
                },
                "reading": "The bounded review already defines the minimum lawful entry design without authorizing broad sample collection.",
            },
        ]
        interpretation = [
            "V1.8A has produced bounded breadth-entry design without widening into generic sample growth.",
            "That means the phase now has a clear readiness posture and does not need forced collection inside the same cycle.",
            "The next legal step is a closure check, not sample collection or promotion.",
        ]
        return V18APhaseCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v18a_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V18APhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
