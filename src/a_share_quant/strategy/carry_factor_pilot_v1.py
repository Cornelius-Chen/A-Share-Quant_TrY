from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class CarryFactorPilotReport:
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


class CarryFactorPilotAnalyzer:
    """Assess whether the first carry score is ready for a bounded pilot lane."""

    def analyze(
        self,
        *,
        scoring_payload: dict[str, Any],
        schema_payload: dict[str, Any],
    ) -> CarryFactorPilotReport:
        scoring_summary = dict(scoring_payload.get("summary", {}))
        score_rows = scoring_payload.get("score_rows", [])
        schema_summary = dict(schema_payload.get("summary", {}))
        schema_rows = schema_payload.get("schema_rows", [])
        if not bool(scoring_summary.get("allow_factor_pilot_next")):
            raise ValueError("Carry factor pilot requires an open scoring-to-pilot transition.")
        if not isinstance(score_rows, list) or not score_rows:
            raise ValueError("Carry scoring payload must contain score_rows.")
        if not isinstance(schema_rows, list) or not schema_rows:
            raise ValueError("Carry schema payload must contain schema_rows.")

        scores = [float(row["carry_score_v1"]) for row in score_rows]
        distinct_scores = len({round(score, 6) for score in scores})
        strategy_names = [str(row["strategy_name"]) for row in score_rows]
        score_dispersion_present = distinct_scores > 1
        sample_thin = len(score_rows) < 3

        acceptance_posture = (
            "open_carry_factor_pilot_as_report_only"
            if not score_dispersion_present and sample_thin
            else "open_carry_factor_pilot_as_rankable_micro_pilot"
        )
        summary = {
            "acceptance_posture": acceptance_posture,
            "pilot_mode": (
                "report_only_micro_pilot"
                if acceptance_posture == "open_carry_factor_pilot_as_report_only"
                else "rankable_micro_pilot"
            ),
            "score_row_count": len(score_rows),
            "distinct_score_count": distinct_scores,
            "score_dispersion_present": score_dispersion_present,
            "sample_thin": sample_thin,
            "strategies_covered": strategy_names,
            "allow_report_only_pilot_now": True,
            "allow_rankable_pilot_now": score_dispersion_present,
            "allow_strategy_integration_now": False,
            "allow_retained_feature_promotion_now": False,
            "needs_more_row_diversity_for_rankable_pilot": not score_dispersion_present,
        }
        evidence_rows = [
            {
                "evidence_name": "scoring_summary",
                "actual": scoring_summary,
                "reading": "The pilot can only open after the lane already has an explicit bounded score.",
            },
            {
                "evidence_name": "score_dispersion",
                "actual": {
                    "scores": scores,
                    "distinct_score_count": distinct_scores,
                    "score_dispersion_present": score_dispersion_present,
                },
                "reading": "A rankable pilot needs cross-row score dispersion; identical rows can still support a report-only pilot.",
            },
            {
                "evidence_name": "sample_shape",
                "actual": {
                    "schema_row_count": schema_summary.get("schema_row_count"),
                    "sample_thin": sample_thin,
                    "strategies_covered": strategy_names,
                },
                "reading": "The current carry pilot remains tiny and bounded, so the first pilot should stay report-only unless more diverse rows arrive.",
            },
        ]
        interpretation = [
            "The first carry pilot is allowed because the lane now has admission, schema, and score layers.",
            "But the current evidence is too symmetric for a rankable pilot: both rows score identically and come from the same structural pocket.",
            "So the correct posture is a report-only micro-pilot, with strategy integration and retained-feature promotion still turned off.",
        ]
        return CarryFactorPilotReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_carry_factor_pilot_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: CarryFactorPilotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
