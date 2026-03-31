from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AYPhaseCharterReport:
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


class V112AYPhaseCharterAnalyzer:
    def analyze(self, *, v112ax_phase_closure_payload: dict[str, Any]) -> V112AYPhaseCharterReport:
        closure_summary = dict(v112ax_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("v112ax_success_criteria_met")):
            raise ValueError("V1.12AY requires the completed V1.12AX closure check.")

        charter = {
            "phase_name": "V1.12AY CPO Guarded Branch Training-Layer Review",
            "mission": (
                "Decide whether the three guarded-admitted branch rows can enter the next bounded "
                "training-facing layer without opening formal training or broader row-geometry widen."
            ),
            "in_scope": [
                "review the three guarded-admitted branch rows from V1.12AW/V1.12AX",
                "determine bounded training-layer admissibility",
                "preserve connector/MPO branch as out-of-layer if still mixed",
            ],
            "out_of_scope": [
                "formal training promotion",
                "formal signal generation",
                "connector/MPO branch admission",
                "spillover or pending row admission",
            ],
            "success_criteria": [
                "a bounded training-layer admissibility decision exists",
                "the guarded branch rows can be split from broader unresolved branch space",
                "the next lawful move becomes narrower than generic branch expansion",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112ay_guarded_branch_training_layer_review",
            "do_open_v112ay_now": True,
            "recommended_first_action": "freeze_v112ay_cpo_guarded_branch_training_layer_review_v1",
        }
        interpretation = [
            "V1.12AY turns the successful guarded branch-admitted pilot into a training-layer admissibility judgment.",
            "This remains bounded, report-only, and non-deployable.",
        ]
        return V112AYPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112ay_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AYPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
