from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ABPhaseCharterReport:
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


class V112ABPhaseCharterAnalyzer:
    def analyze(self, *, v112aa_phase_closure_payload: dict[str, Any]) -> V112ABPhaseCharterReport:
        closure_summary = dict(v112aa_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("enter_v112aa_waiting_state_now")):
            raise ValueError("V1.12AB requires V1.12AA to have lawfully closed.")

        charter = {
            "phase_name": "V1.12AB CPO Bounded Labeling Review",
            "mission": (
                "Use the frozen CPO bounded cohort map to decide which objects may later enter primary or secondary "
                "labeling surfaces, while keeping review-only, spillover, and pending rows outside formal label freeze."
            ),
            "in_scope": [
                "review later labeling surface boundaries",
                "freeze primary versus secondary versus review-only object posture",
                "preserve pending rows as explicit exclusions",
            ],
            "out_of_scope": [
                "formal label freeze",
                "formal training rights",
                "signal logic",
                "execution rules",
            ],
            "success_criteria": [
                "later labeling surfaces are explicit",
                "core truth, secondary candidates, support-only rows, overlays, and exclusions remain separated",
                "the line can move toward a bounded label-draft assembly without leaking ambiguity into truth",
            ],
            "stop_criteria": [
                "the review quietly turns into final truth assignment",
                "spillover or pending rows are promoted without governance",
                "the phase opens training by stealth",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112ab_cpo_bounded_labeling_review",
            "do_open_v112ab_now": True,
            "selected_parent_line": "v112aa_cpo_bounded_cohort_map",
            "recommended_first_action": "freeze_v112ab_cpo_bounded_labeling_review_v1",
        }
        interpretation = [
            "V1.12AB does not label samples yet; it freezes labeling surfaces and exclusions.",
            "This phase exists to keep later label drafting disciplined.",
        ]
        return V112ABPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112ab_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ABPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
