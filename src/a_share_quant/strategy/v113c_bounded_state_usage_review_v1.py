from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113CBoundedStateUsageReviewReport:
    summary: dict[str, Any]
    driver_usage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "driver_usage_rows": self.driver_usage_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V113CBoundedStateUsageReviewAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        driver_review_payload: dict[str, Any],
    ) -> V113CBoundedStateUsageReviewReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("ready_for_state_usage_review_next")):
            raise ValueError("V1.13C requires an open bounded state-usage review charter.")

        review_rows = list(driver_review_payload.get("driver_review_rows", []))
        target_rows = [row for row in review_rows if row.get("review_disposition") == "allow_bounded_state_usage_review_next"]
        if len(target_rows) != 4:
            raise ValueError("V1.13C expects exactly four high-priority candidate drivers from V1.13B.")

        usage_map = {
            "policy_backing_tier": (
                "allow_as_mainline_strength_context_anchor",
                "Use as a top-layer context anchor when judging whether a theme has the right to become a major mainline.",
            ),
            "industrial_advantage_alignment": (
                "allow_as_structural_viability_filter",
                "Use as a structural viability filter to separate real industrial themes from weak story shells.",
            ),
            "market_regime_tailwind": (
                "allow_as_regime_amplifier_context",
                "Use as an amplifier context showing whether the broader tape helps or fights the theme.",
            ),
            "event_resonance_intensity": (
                "allow_as_multi_trigger_confirmation_context",
                "Use as confirmation that the theme is supported by layered events rather than a single one-day impulse.",
            ),
        }

        driver_usage_rows: list[dict[str, Any]] = []
        for row in target_rows:
            name = str(row.get("candidate_driver_name", ""))
            usage_posture, reading = usage_map[name]
            driver_usage_rows.append(
                {
                    "candidate_driver_name": name,
                    "usage_posture": usage_posture,
                    "allowed_layer": "schema_review_only",
                    "disallowed_layers": [
                        "formal_model_feature",
                        "execution_trigger",
                        "strategy_signal",
                    ],
                    "reading": reading,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v113c_bounded_state_usage_review_v1",
            "reviewed_high_priority_driver_count": len(driver_usage_rows),
            "drivers_allowed_for_schema_review_only": len(driver_usage_rows),
            "formal_driver_promotion_now": False,
            "model_usage_now": False,
            "execution_usage_now": False,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "V1.13C keeps the reviewed driver quartet inside the schema-review layer.",
            "The quartet now has lawful review usage, but still no model, execution, or strategy rights.",
            "This turns the high-priority drivers into reusable review grammar rather than premature scoring variables.",
        ]
        return V113CBoundedStateUsageReviewReport(
            summary=summary,
            driver_usage_rows=driver_usage_rows,
            interpretation=interpretation,
        )


def write_v113c_bounded_state_usage_review_report(
    *, reports_dir: Path, report_name: str, result: V113CBoundedStateUsageReviewReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
