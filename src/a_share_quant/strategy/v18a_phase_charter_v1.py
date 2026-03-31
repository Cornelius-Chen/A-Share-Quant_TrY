from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V18APhaseCharterReport:
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


class V18APhaseCharterAnalyzer:
    """Open V1.8A after V1.7 closes with explicit sample-breadth shortfalls."""

    def analyze(
        self,
        *,
        v17_phase_closure_payload: dict[str, Any],
        v17_feature_promotion_gap_review_payload: dict[str, Any],
    ) -> V18APhaseCharterReport:
        closure_summary = dict(v17_phase_closure_payload.get("summary", {}))
        review_rows = list(v17_feature_promotion_gap_review_payload.get("review_rows", []))

        v17_waiting_ready = bool(closure_summary.get("enter_v17_waiting_state_now"))
        breadth_target_features = [
            str(row.get("feature_name", ""))
            for row in review_rows
            if row.get("primary_shortfall") == "sample_breadth_gap"
        ]
        open_v18a_now = v17_waiting_ready and len(breadth_target_features) > 0

        charter = {
            "mission": "Generate broader but still bounded evidence samples for provisional context features whose primary promotion shortfall is sample breadth, without promoting or integrating any feature now.",
            "in_scope": [
                "sample-breadth target feature freeze",
                "bounded breadth expansion protocol",
                "candidate evidence-sample source selection",
                "minimal lawful breadth-expansion entry design",
            ],
            "out_of_scope": [
                "retained-feature promotion",
                "strategy integration",
                "formal model work",
                "safe-consumption validation work",
                "cross-pocket or cross-regime validation work",
                "wide replay expansion",
            ],
            "success_criteria": [
                "freeze a bounded sample-breadth expansion protocol",
                "lock the initial breadth-expansion target features",
                "define the minimum lawful evidence-sample entry for breadth expansion",
                "close the phase with a clear breadth-expansion readiness posture or bounded hold posture",
            ],
            "stop_criteria": [
                "if breadth expansion drifts into wide replay or generic sample growth",
                "if breadth expansion cannot be bounded to explicit promotion shortfalls",
                "if no lawful evidence-sample entry can be defined without reopening older phases",
            ],
            "handoff_condition": "After the charter opens, only replay-independent sample-breadth expansion artifacts are allowed until a bounded breadth-entry posture is explicit.",
        }
        summary = {
            "acceptance_posture": (
                "open_v18a_sample_breadth_expansion"
                if open_v18a_now
                else "hold_v18a_charter_until_prerequisites_hold"
            ),
            "v17_waiting_state_present": v17_waiting_ready,
            "sample_breadth_target_feature_count": len(breadth_target_features),
            "target_feature_names": breadth_target_features,
            "do_open_v18a_now": open_v18a_now,
            "recommended_first_action": "freeze_v18a_sample_breadth_protocol_v1",
        }
        interpretation = [
            "V1.7 already separated different promotion shortfalls instead of mixing them into one undifferentiated next step.",
            "The highest-leverage next lawful move is to target the shared sample-breadth shortfall first, because it affects more than one provisional candidate.",
            "So V1.8A should open as a bounded sample-breadth expansion phase, not as a promotion or mixed-validation phase.",
        ]
        return V18APhaseCharterReport(
            summary=summary,
            charter=charter,
            interpretation=interpretation,
        )


def write_v18a_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V18APhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
