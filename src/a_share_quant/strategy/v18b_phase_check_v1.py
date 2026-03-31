from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V18BPhaseCheckReport:
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


class V18BPhaseCheckAnalyzer:
    """Check the bounded posture of V1.8B after admission gate review."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        feature_admission_gate_review_payload: dict[str, Any],
    ) -> V18BPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        review_summary = dict(feature_admission_gate_review_payload.get("summary", {}))

        summary = {
            "acceptance_posture": "keep_v18b_active_but_bounded_as_admission_gate_review",
            "v18b_open": bool(charter_summary.get("do_open_v18b_now")),
            "reviewed_feature_count": review_summary.get("reviewed_feature_count", 0),
            "admission_gate_ready_count": review_summary.get("admission_gate_ready_count", 0),
            "allow_sample_collection_now": False,
            "promote_retained_now": False,
            "recommended_next_posture": "prepare_v18b_phase_closure_or_waiting_state_not_collection",
        }
        evidence_rows = [
            {
                "evidence_name": "v18b_charter",
                "actual": {
                    "acceptance_posture": charter_summary.get("acceptance_posture"),
                    "target_feature_names": charter_summary.get("target_feature_names"),
                },
                "reading": "V1.8B opened lawfully as a bounded breadth admission-gate phase.",
            },
            {
                "evidence_name": "feature_admission_gate_review",
                "actual": {
                    "reviewed_feature_count": review_summary.get("reviewed_feature_count"),
                    "admission_gate_ready_count": review_summary.get("admission_gate_ready_count"),
                    "allow_sample_collection_now": review_summary.get("allow_sample_collection_now"),
                },
                "reading": "The bounded review already states whether the target features have clean admission gates for future screened collection.",
            },
        ]
        interpretation = [
            "V1.8B has produced bounded admission-gate judgments without drifting into actual sample collection.",
            "That means the phase now has a clear gate-readiness posture and does not need forced expansion to justify itself.",
            "The next legal step is a closure check, not sample collection or promotion.",
        ]
        return V18BPhaseCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v18b_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V18BPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
