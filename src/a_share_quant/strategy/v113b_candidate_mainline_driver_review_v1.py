from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113BCandidateMainlineDriverReviewReport:
    summary: dict[str, Any]
    driver_review_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "driver_review_rows": self.driver_review_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V113BCandidateMainlineDriverReviewAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        state_schema_payload: dict[str, Any],
    ) -> V113BCandidateMainlineDriverReviewReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("ready_for_driver_review_next")):
            raise ValueError("V1.13B requires an open candidate-driver review charter.")

        candidate_rows = list(state_schema_payload.get("review_only_candidate_driver_rows", []))
        if not candidate_rows:
            raise ValueError("V1.13B requires review-only candidate drivers from V1.13A.")

        high_priority = {
            "policy_backing_tier",
            "industrial_advantage_alignment",
            "market_regime_tailwind",
            "event_resonance_intensity",
        }
        medium_priority = {
            "leader_height_establishment",
            "mid_core_confirmation",
            "cross_day_breadth_diffusion",
            "absorption_quality_or_a_kill_suppression",
            "catalyst_freshness_and_reinforcement",
        }
        deferred_priority = {"mapping_clarity_and_tradeable_story"}

        driver_review_rows: list[dict[str, Any]] = []
        bounded_usage_ready_count = 0
        for row in candidate_rows:
            name = str(row.get("candidate_driver_name", ""))
            bucket = str(row.get("candidate_bucket", ""))

            if name in high_priority:
                disposition = "allow_bounded_state_usage_review_next"
                reading = "High-leverage candidate; stable enough to guide the next bounded state-usage review."
                bounded_usage_ready_count += 1
            elif name in medium_priority:
                disposition = "keep_review_only_candidate_for_now"
                reading = "Useful and plausible, but still better kept as review-only support rather than immediate next-step focus."
            elif name in deferred_priority:
                disposition = "defer_as_noisy_borderline_candidate"
                reading = "Keep preserved in review memory, but too noisy to prioritize for the next bounded follow-up."
            else:
                disposition = "unclassified_review_only_candidate"
                reading = "Preserve in review memory until a later bounded review clarifies its role."

            driver_review_rows.append(
                {
                    "candidate_driver_name": name,
                    "candidate_bucket": bucket,
                    "incoming_priority_tier": row.get("candidate_priority_tier"),
                    "review_disposition": disposition,
                    "reading": reading,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v113b_candidate_mainline_driver_review_v1",
            "candidate_driver_count_reviewed": len(driver_review_rows),
            "bounded_state_usage_ready_count": bounded_usage_ready_count,
            "formal_driver_promotion_now": False,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "V1.13B does not decide formal driver law; it only ranks review-only candidates for bounded follow-up.",
            "The next lawful state-usage review should stay focused on the small high-priority set rather than all ten candidates.",
            "Lower-priority candidates remain useful review memory, but they should not consume the next bounded schema budget.",
        ]
        return V113BCandidateMainlineDriverReviewReport(
            summary=summary,
            driver_review_rows=driver_review_rows,
            interpretation=interpretation,
        )


def write_v113b_candidate_mainline_driver_review_report(
    *, reports_dir: Path, report_name: str, result: V113BCandidateMainlineDriverReviewReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
