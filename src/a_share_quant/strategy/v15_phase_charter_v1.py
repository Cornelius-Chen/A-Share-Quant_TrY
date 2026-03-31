from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V15PhaseCharterReport:
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


class V15PhaseCharterAnalyzer:
    """Open V1.5 after V1.4 closes and the owner selects retained-feature candidacy review."""

    def analyze(
        self,
        *,
        v14_phase_closure_payload: dict[str, Any],
        v14_context_feature_schema_payload: dict[str, Any],
        v14_bounded_discrimination_payload: dict[str, Any],
    ) -> V15PhaseCharterReport:
        closure_summary = dict(v14_phase_closure_payload.get("summary", {}))
        schema_summary = dict(v14_context_feature_schema_payload.get("summary", {}))
        discrimination_summary = dict(v14_bounded_discrimination_payload.get("summary", {}))

        v14_waiting_ready = bool(closure_summary.get("enter_v14_waiting_state_now"))
        schema_ready = schema_summary.get("report_only_feature_count", 0) > 0
        discrimination_ready = bool(discrimination_summary.get("stable_discrimination_present"))
        open_v15_now = v14_waiting_ready and schema_ready and discrimination_ready

        charter = {
            "mission": "Review whether current report-only context features meet the minimum admissibility threshold for retained-feature candidacy without promoting them into the strategy mainline.",
            "in_scope": [
                "feature admissibility review",
                "evidence sufficiency review",
                "non-redundancy or orthogonality review",
                "safe-containment review",
                "bounded candidacy decisions",
            ],
            "out_of_scope": [
                "retained-feature promotion",
                "strategy integration",
                "formal model work",
                "new wide replay or refresh expansion",
                "local regime segmentation",
            ],
            "success_criteria": [
                "freeze a clear candidacy review protocol",
                "produce admissibility judgments for the current bounded report-only context features",
                "close the phase with a clear retained-candidacy posture or a bounded rejection posture",
            ],
            "stop_criteria": [
                "if current feature definitions are too unstable for candidacy review",
                "if evidence remains too sparse to support bounded admissibility judgments",
                "if the work drifts into direct promotion or strategy integration",
            ],
            "handoff_condition": "After the charter opens, only replay-independent candidacy-review artifacts are allowed until the phase-level posture is explicit.",
        }
        summary = {
            "acceptance_posture": (
                "open_v15_retained_feature_candidacy_review"
                if open_v15_now
                else "hold_v15_charter_until_prerequisites_hold"
            ),
            "v14_waiting_state_present": v14_waiting_ready,
            "context_feature_schema_ready": schema_ready,
            "bounded_discrimination_ready": discrimination_ready,
            "do_open_v15_now": open_v15_now,
            "recommended_first_action": "freeze_v15_feature_candidacy_protocol_v1",
        }
        interpretation = [
            "V1.4 already proved bounded context-consumption value, but stopped below promotion threshold.",
            "That makes retained-feature candidacy review the next lawful question: not whether to promote, but whether current report-only features deserve candidacy consideration at all.",
            "So V1.5 should open as a bounded review phase, not as a promotion, modeling, or segmentation phase.",
        ]
        return V15PhaseCharterReport(
            summary=summary,
            charter=charter,
            interpretation=interpretation,
        )


def write_v15_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V15PhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
