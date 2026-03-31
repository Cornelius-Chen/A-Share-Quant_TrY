from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V17PhaseCharterReport:
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


class V17PhaseCharterAnalyzer:
    """Open V1.7 after V1.6 closes and provisional candidates remain alive but below promotion threshold."""

    def analyze(
        self,
        *,
        v16_phase_closure_payload: dict[str, Any],
        v16_feature_stability_review_payload: dict[str, Any],
    ) -> V17PhaseCharterReport:
        closure_summary = dict(v16_phase_closure_payload.get("summary", {}))
        stability_summary = dict(v16_feature_stability_review_payload.get("summary", {}))

        v16_waiting_ready = bool(closure_summary.get("enter_v16_waiting_state_now"))
        continuing_candidates = int(stability_summary.get("continue_provisional_candidacy_count", 0))
        open_v17_now = v16_waiting_ready and continuing_candidates > 0

        charter = {
            "mission": "Generate bounded promotion-evidence targets for current provisional context features by identifying the minimum new evidence required to change retained-feature promotion judgment without promoting or integrating any feature now.",
            "in_scope": [
                "promotion-evidence gap definition",
                "per-feature promotion shortfall analysis",
                "bounded admissible proof-type design",
                "minimal evidence-generation path design",
            ],
            "out_of_scope": [
                "retained-feature promotion",
                "strategy integration",
                "formal model work",
                "local regime segmentation",
                "new wide replay or refresh expansion",
                "repeating bounded stability review",
            ],
            "success_criteria": [
                "freeze a bounded promotion-evidence protocol",
                "identify explicit promotion shortfalls for current provisional candidates",
                "define the minimum lawful evidence paths that could change promotion judgment",
                "close the phase with a clear continue-waiting or evidence-generation-entry posture",
            ],
            "stop_criteria": [
                "if promotion-evidence design drifts into direct promotion or integration",
                "if current provisional features lack enough bounded definition to state concrete evidence gaps",
                "if no admissible new evidence path can be defined without violating current guardrails",
            ],
            "handoff_condition": "After the charter opens, only replay-independent promotion-evidence artifacts are allowed until a bounded evidence-generation entry is explicit.",
        }
        summary = {
            "acceptance_posture": (
                "open_v17_promotion_evidence_generation"
                if open_v17_now
                else "hold_v17_charter_until_prerequisites_hold"
            ),
            "v16_waiting_state_present": v16_waiting_ready,
            "continuing_provisional_candidate_count": continuing_candidates,
            "do_open_v17_now": open_v17_now,
            "recommended_first_action": "freeze_v17_promotion_evidence_protocol_v1",
        }
        interpretation = [
            "V1.6 already answered whether current provisional candidates remain alive under bounded stability review.",
            "The next lawful question is not another stability loop, but what new evidence would be required to change promotion judgment.",
            "So V1.7 should open as a bounded promotion-evidence generation phase, not as a promotion, integration, or local-model phase.",
        ]
        return V17PhaseCharterReport(
            summary=summary,
            charter=charter,
            interpretation=interpretation,
        )


def write_v17_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V17PhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
