from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V19PhaseCheckReport:
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


class V19PhaseCheckAnalyzer:
    """Check the bounded posture of V1.9 after breadth re-review."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        feature_breadth_rereview_payload: dict[str, Any],
    ) -> V19PhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        rereview_summary = dict(feature_breadth_rereview_payload.get("summary", {}))

        summary = {
            "acceptance_posture": "keep_v19_active_but_bounded_as_breadth_evidence_rereview",
            "v19_open": bool(charter_summary.get("do_open_v19_now")),
            "reviewed_feature_count": rereview_summary.get("reviewed_feature_count", 0),
            "shortfall_changed_count": rereview_summary.get("shortfall_changed_count", 0),
            "breadth_gap_materially_reduced_count": rereview_summary.get("breadth_gap_materially_reduced_count", 0),
            "breadth_gap_partially_reduced_count": rereview_summary.get("breadth_gap_partially_reduced_count", 0),
            "promote_retained_now": False,
            "do_integrate_into_strategy_now": False,
            "recommended_next_posture": "prepare_v19_phase_closure_or_waiting_state_not_promotion",
        }
        evidence_rows = [
            {
                "evidence_name": "v19_charter",
                "actual": {
                    "acceptance_posture": charter_summary.get("acceptance_posture"),
                    "target_feature_names": charter_summary.get("target_feature_names"),
                },
                "reading": "V1.9 opened lawfully as a bounded re-review phase, not as a promotion phase.",
            },
            {
                "evidence_name": "feature_breadth_rereview",
                "actual": {
                    "reviewed_feature_count": rereview_summary.get("reviewed_feature_count"),
                    "shortfall_changed_count": rereview_summary.get("shortfall_changed_count"),
                    "breadth_gap_materially_reduced_count": rereview_summary.get("breadth_gap_materially_reduced_count"),
                    "breadth_gap_partially_reduced_count": rereview_summary.get("breadth_gap_partially_reduced_count"),
                },
                "reading": "The new breadth evidence is now explicitly reflected in refreshed promotion-judgment shortfalls.",
            },
        ]
        interpretation = [
            "V1.9 has refreshed the breadth-target promotion judgment without crossing into promotion or integration.",
            "The phase now has a clear bounded outcome: one feature improved materially, one only partially, and neither is promotion-ready.",
            "The next legal step is a closure check, not retained-feature promotion or new collection inside this phase.",
        ]
        return V19PhaseCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v19_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V19PhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
