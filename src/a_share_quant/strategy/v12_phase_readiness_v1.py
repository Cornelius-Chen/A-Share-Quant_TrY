from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12PhaseReadinessReport:
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


class V12PhaseReadinessAnalyzer:
    """Decide whether V1.2 should close now or remain open awaiting a later refresh batch."""

    def analyze(
        self,
        *,
        data_audit_payload: dict[str, Any],
        registry_payload: dict[str, Any],
        factorization_review_payload: dict[str, Any],
        carry_pilot_payload: dict[str, Any],
    ) -> V12PhaseReadinessReport:
        audit_summary = dict(data_audit_payload.get("summary", {}))
        registry_summary = dict(registry_payload.get("summary", {}))
        factorization_summary = dict(factorization_review_payload.get("summary", {}))
        carry_pilot_summary = dict(carry_pilot_payload.get("summary", {}))

        refresh_pack_ready = bool(audit_summary.get("baseline_ready"))
        registry_ready = bool(registry_summary.get("ready_for_factor_evaluation_protocol"))
        factorization_milestone_reached = bool(
            factorization_summary.get("v12_factorization_milestone_reached")
        )
        second_lane_closed = not bool(factorization_summary.get("do_open_second_factor_lane_now"))
        carry_pilot_report_only = (
            str(carry_pilot_summary.get("pilot_mode")) == "report_only_micro_pilot"
        )
        row_diversity_still_missing = bool(
            carry_pilot_summary.get("needs_more_row_diversity_for_rankable_pilot")
        )

        close_v12_now = (
            refresh_pack_ready
            and registry_ready
            and factorization_milestone_reached
            and second_lane_closed
            and not row_diversity_still_missing
        )
        acceptance_posture = (
            "close_v12_as_first_bounded_data_plus_factorization_phase"
            if close_v12_now
            else "keep_v12_open_and_wait_for_new_refresh_batch_or_row_diversity"
        )
        summary = {
            "acceptance_posture": acceptance_posture,
            "refresh_pack_ready": refresh_pack_ready,
            "registry_ready": registry_ready,
            "factorization_milestone_reached": factorization_milestone_reached,
            "second_lane_closed": second_lane_closed,
            "carry_pilot_report_only": carry_pilot_report_only,
            "row_diversity_still_missing": row_diversity_still_missing,
            "ready_to_close_v12_now": close_v12_now,
            "do_open_new_refresh_batch_now": row_diversity_still_missing,
            "recommended_next_posture": (
                "prepare_later_refresh_batch_to_add_factor_row_diversity"
                if row_diversity_still_missing
                else "close_v12_now"
            ),
        }
        evidence_rows = [
            {
                "evidence_name": "data_expansion_status",
                "actual": {
                    "baseline_ready": audit_summary.get("baseline_ready"),
                    "canonical_ready_count": audit_summary.get("canonical_ready_count"),
                    "derived_ready_count": audit_summary.get("derived_ready_count"),
                },
                "reading": "V1.2 cannot close credibly unless the refreshed pack itself is already runnable and auditable.",
            },
            {
                "evidence_name": "factorization_status",
                "actual": {
                    "registry_ready": registry_ready,
                    "factorization_milestone_reached": factorization_milestone_reached,
                    "second_lane_closed": second_lane_closed,
                },
                "reading": "The phase needs one full bounded factorization cycle before any close-or-refresh decision is meaningful.",
            },
            {
                "evidence_name": "carry_pilot_boundary",
                "actual": {
                    "pilot_mode": carry_pilot_summary.get("pilot_mode"),
                    "row_diversity_still_missing": row_diversity_still_missing,
                    "allow_rankable_pilot_now": carry_pilot_summary.get("allow_rankable_pilot_now"),
                },
                "reading": "If the first pilot is still report-only because row diversity is missing, the correct next move is a later refresh batch rather than immediate phase closure.",
            },
        ]
        interpretation = [
            "V1.2 has already achieved a real data-plus-factorization milestone, so it is no longer in early buildout mode.",
            "But the first factor lane is still report-only, which means the phase has not yet converted its first factor lane into a rankable or broader reusable factor layer.",
            "So the correct current posture is to keep V1.2 open, hold the second lane closed, and wait for a later refresh batch that can add more factor row diversity.",
        ]
        return V12PhaseReadinessReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v12_phase_readiness_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12PhaseReadinessReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
