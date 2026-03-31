from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V15PhaseCheckReport:
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


class V15PhaseCheckAnalyzer:
    """Check the bounded posture of V1.5 after the first admissibility cycle."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        feature_admissibility_review_payload: dict[str, Any],
    ) -> V15PhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        review_summary = dict(feature_admissibility_review_payload.get("summary", {}))

        summary = {
            "acceptance_posture": "keep_v15_active_but_bounded_as_candidacy_review",
            "v15_open": bool(charter_summary.get("do_open_v15_now")),
            "allow_provisional_candidacy_review_count": review_summary.get("allow_provisional_candidacy_review_count", 0),
            "hold_for_more_evidence_count": review_summary.get("hold_for_more_evidence_count", 0),
            "promote_retained_now": False,
            "do_integrate_into_strategy_now": False,
            "recommended_next_posture": "prepare_v15_phase_closure_or_waiting_state_not_promotion",
        }
        evidence_rows = [
            {
                "evidence_name": "v15_charter",
                "actual": {
                    "acceptance_posture": charter_summary.get("acceptance_posture"),
                    "recommended_first_action": charter_summary.get("recommended_first_action"),
                },
                "reading": "V1.5 opened as candidacy review only, not as retained-feature promotion.",
            },
            {
                "evidence_name": "feature_admissibility_review",
                "actual": {
                    "allow_provisional_candidacy_review_count": review_summary.get("allow_provisional_candidacy_review_count"),
                    "hold_for_more_evidence_count": review_summary.get("hold_for_more_evidence_count"),
                    "reject_candidacy_count": review_summary.get("reject_candidacy_count"),
                },
                "reading": "The bounded review already answers which features may stay in candidacy review and which still need more evidence.",
            },
        ]
        interpretation = [
            "V1.5 has produced bounded admissibility judgments without crossing into promotion.",
            "That means the phase now has a clear candidacy posture and does not need wider expansion to justify its existence.",
            "The next legal step is a closure check, not an integration or model branch.",
        ]
        return V15PhaseCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v15_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V15PhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
