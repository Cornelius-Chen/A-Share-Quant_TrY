from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12FactorizationReviewReport:
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


class V12FactorizationReviewAnalyzer:
    """Review whether V1.2 has already achieved a representative bounded factorization outcome."""

    def analyze(
        self,
        *,
        registry_payload: dict[str, Any],
        protocol_payload: dict[str, Any],
        carry_first_pass_payload: dict[str, Any],
        carry_pilot_payload: dict[str, Any],
    ) -> V12FactorizationReviewReport:
        registry_summary = dict(registry_payload.get("summary", {}))
        protocol_summary = dict(protocol_payload.get("summary", {}))
        carry_first_pass_summary = dict(carry_first_pass_payload.get("summary", {}))
        carry_pilot_summary = dict(carry_pilot_payload.get("summary", {}))

        registry_ready = bool(registry_summary.get("ready_for_factor_evaluation_protocol"))
        protocol_ready = bool(protocol_summary.get("ready_for_first_pass_factor_evaluation"))
        carry_lane_open = bool(carry_first_pass_summary.get("do_open_bounded_carry_factor_lane"))
        carry_pilot_open = bool(carry_pilot_summary.get("allow_report_only_pilot_now"))
        carry_rankable = bool(carry_pilot_summary.get("allow_rankable_pilot_now"))
        penalty_bucket_present = int(protocol_summary.get("evaluate_with_penalty_count", 0)) > 0
        deferred_bucket_present = int(protocol_summary.get("hold_for_more_sample_count", 0)) > 0

        milestone_reached = registry_ready and protocol_ready and carry_lane_open and carry_pilot_open
        acceptance_posture = (
            "close_first_v12_factorization_cycle_as_representative_but_bounded"
            if milestone_reached
            else "continue_v12_factorization_cycle"
        )
        summary = {
            "acceptance_posture": acceptance_posture,
            "v12_factorization_milestone_reached": milestone_reached,
            "registry_ready": registry_ready,
            "protocol_ready": protocol_ready,
            "carry_lane_open": carry_lane_open,
            "carry_pilot_open": carry_pilot_open,
            "carry_pilot_rankable": carry_rankable,
            "penalty_bucket_present": penalty_bucket_present,
            "deferred_bucket_present": deferred_bucket_present,
            "do_open_second_factor_lane_now": False,
            "recommended_next_posture": (
                "hold_second_lane_until_more_diverse_rows_or_new_refresh_batch"
                if milestone_reached
                else "continue_first_factorization_cycle"
            ),
        }
        evidence_rows = [
            {
                "evidence_name": "registry_and_protocol_gate",
                "actual": {
                    "registry_ready": registry_ready,
                    "protocol_ready": protocol_ready,
                    "candidate_factor_count": registry_summary.get("candidate_factor_count"),
                    "evaluate_now_count": protocol_summary.get("evaluate_now_count"),
                },
                "reading": "The first factorization cycle only counts as real when the repo has both a registry layer and a protocol layer.",
            },
            {
                "evidence_name": "carry_lane_status",
                "actual": {
                    "carry_lane_open": carry_lane_open,
                    "carry_pilot_open": carry_pilot_open,
                    "carry_pilot_rankable": carry_rankable,
                    "pilot_mode": carry_pilot_summary.get("pilot_mode"),
                },
                "reading": "The first factor lane should reach pilot state, even if that pilot remains report-only and bounded.",
            },
            {
                "evidence_name": "other_candidate_buckets",
                "actual": {
                    "penalty_bucket_present": penalty_bucket_present,
                    "deferred_bucket_present": deferred_bucket_present,
                    "penalty_shortlist": protocol_summary.get("penalty_shortlist", []),
                    "deferred_shortlist": protocol_summary.get("deferred_shortlist", []),
                },
                "reading": "A representative first cycle does not require opening every factor lane at once; penalty and thin buckets may remain frozen.",
            },
        ]
        interpretation = [
            "V1.2 now has a representative factorization result because one clean factor has progressed from registry to protocol to bounded pilot.",
            "That result is still bounded, not broad: the carry pilot remains report-only and does not justify opening a second lane immediately.",
            "So the correct posture is to close the first factorization cycle as successful-but-bounded, and wait for more row diversity or a later refreshed batch before widening factor work.",
        ]
        return V12FactorizationReviewReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v12_factorization_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12FactorizationReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
