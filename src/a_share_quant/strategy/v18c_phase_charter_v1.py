from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V18CPhaseCharterReport:
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


class V18CPhaseCharterAnalyzer:
    """Open V1.8C after V1.8B closes with explicit admission-gate readiness."""

    def analyze(
        self,
        *,
        v18b_phase_closure_payload: dict[str, Any],
        v18b_feature_admission_gate_review_payload: dict[str, Any],
    ) -> V18CPhaseCharterReport:
        closure_summary = dict(v18b_phase_closure_payload.get("summary", {}))
        review_summary = dict(v18b_feature_admission_gate_review_payload.get("summary", {}))
        review_rows = list(v18b_feature_admission_gate_review_payload.get("review_rows", []))

        v18b_waiting_ready = bool(closure_summary.get("enter_v18b_waiting_state_now"))
        ready_feature_names = [
            str(row.get("feature_name", ""))
            for row in review_rows
            if bool(row.get("admission_gate_ready"))
        ]
        open_v18c_now = v18b_waiting_ready and review_summary.get("admission_gate_ready_count", 0) > 0

        charter = {
            "mission": "Execute screened bounded collection for current breadth-target features under the frozen V1.8A entry design and V1.8B admission gate, generating the first lawful breadth evidence without promoting or integrating any feature now.",
            "in_scope": [
                "screened candidate review under frozen admission gates",
                "bounded collection records for admitted cases",
                "per-feature collection summary under sample limits",
                "bounded evidence artifact generation",
            ],
            "out_of_scope": [
                "retained-feature promotion",
                "strategy integration",
                "new refresh or replay widening",
                "sample collection beyond current limits",
                "safe-consumption validation work",
                "cross-pocket or cross-regime validation work",
            ],
            "success_criteria": [
                "execute a lawful screened bounded collection cycle",
                "admit at least one clean additional breadth case for at least one target feature or exhaust the candidate pools cleanly",
                "produce collection records and a bounded collection summary",
                "close the phase with a clear follow-up posture for later promotion-evidence review",
            ],
            "stop_criteria": [
                "if collection drifts beyond frozen sample limits",
                "if screened candidates fail admission gates and no lawful case remains",
                "if collection requires widening replay queues or weakening evidence standards",
            ],
            "handoff_condition": "After the charter opens, only screened bounded collection artifacts are allowed until a bounded collection summary is explicit.",
        }
        summary = {
            "acceptance_posture": (
                "open_v18c_screened_bounded_collection"
                if open_v18c_now
                else "hold_v18c_charter_until_prerequisites_hold"
            ),
            "v18b_waiting_state_present": v18b_waiting_ready,
            "admission_gate_ready_count": review_summary.get("admission_gate_ready_count", 0),
            "target_feature_names": ready_feature_names,
            "do_open_v18c_now": open_v18c_now,
            "recommended_first_action": "freeze_v18c_screened_collection_protocol_v1",
        }
        interpretation = [
            "V1.8A and V1.8B already answered where breadth evidence may come from and which candidates are admissible.",
            "The next lawful move is therefore screened bounded collection itself, not another design-only or review-only phase.",
            "So V1.8C should open as a tightly bounded collection phase, not as a promotion or integration phase.",
        ]
        return V18CPhaseCharterReport(
            summary=summary,
            charter=charter,
            interpretation=interpretation,
        )


def write_v18c_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V18CPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
