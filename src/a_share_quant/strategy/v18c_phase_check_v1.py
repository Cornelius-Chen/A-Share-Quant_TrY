from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V18CPhaseCheckReport:
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


class V18CPhaseCheckAnalyzer:
    """Check the bounded posture of V1.8C after screened collection."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        screened_collection_payload: dict[str, Any],
    ) -> V18CPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        collection_summary = dict(screened_collection_payload.get("summary", {}))

        summary = {
            "acceptance_posture": "keep_v18c_active_but_bounded_as_screened_collection",
            "v18c_open": bool(charter_summary.get("do_open_v18c_now")),
            "target_feature_count": collection_summary.get("target_feature_count", 0),
            "admitted_case_count": collection_summary.get("admitted_case_count", 0),
            "targets_with_admitted_cases_count": collection_summary.get("targets_with_admitted_cases_count", 0),
            "promote_retained_now": False,
            "do_integrate_into_strategy_now": False,
            "recommended_next_posture": "prepare_v18c_phase_closure_or_follow_up_review_not_promotion",
        }
        evidence_rows = [
            {
                "evidence_name": "v18c_charter",
                "actual": {
                    "acceptance_posture": charter_summary.get("acceptance_posture"),
                    "target_feature_names": charter_summary.get("target_feature_names"),
                },
                "reading": "V1.8C opened lawfully as a screened bounded collection phase.",
            },
            {
                "evidence_name": "screened_collection",
                "actual": {
                    "admitted_case_count": collection_summary.get("admitted_case_count"),
                    "targets_with_admitted_cases_count": collection_summary.get("targets_with_admitted_cases_count"),
                    "sample_limit_breaches": collection_summary.get("sample_limit_breaches"),
                },
                "reading": "The bounded collection has now produced the first lawful breadth evidence under the frozen rules.",
            },
        ]
        interpretation = [
            "V1.8C has produced real new breadth evidence without crossing into promotion or strategy integration.",
            "That means the phase now has an explicit bounded collection result and does not need wider replay growth to justify itself.",
            "The next legal step is a closure check or later promotion-evidence review, not retained-feature promotion.",
        ]
        return V18CPhaseCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v18c_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V18CPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
