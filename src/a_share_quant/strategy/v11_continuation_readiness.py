from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V11ContinuationReadinessReport:
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


class V11ContinuationReadinessAnalyzer:
    """Decide whether specialist refinement should continue locally or pause for a new suspect batch."""

    def analyze(
        self,
        *,
        q2_acceptance: dict[str, Any],
        q3_acceptance: dict[str, Any],
        q4_acceptance: dict[str, Any],
        context_a_acceptance: dict[str, Any],
        context_b_report: dict[str, Any],
        u2_readiness: dict[str, Any],
        specialist_alpha: dict[str, Any],
    ) -> V11ContinuationReadinessReport:
        q2_closed = bool(
            q2_acceptance.get("summary", {}).get("do_continue_q2_capture_replay") is False
        )
        q3_closed = bool(
            q3_acceptance.get("summary", {}).get("do_continue_q3_drawdown_replay") is False
        )
        q4_closed = bool(
            q4_acceptance.get("summary", {}).get("do_continue_q4_drawdown_replay") is False
        )
        context_a_closed = (
            str(
                context_a_acceptance.get("summary", {}).get("acceptance_posture", "")
            )
            == "close_conditioned_late_quality_branch_as_non_material"
        )
        context_b_closed = (
            bool(
                context_b_report.get("summary", {}).get("do_continue_context_feature_pack_b")
                is False
            )
            and str(
                context_b_report.get("summary", {}).get("recommended_posture", "")
            )
            == "close_sector_heat_breadth_context_branch_as_sparse"
        )
        u2_ready = bool(u2_readiness.get("summary", {}).get("u2_ready"))
        specialist_opportunity_count = int(
            sum(
                int(row.get("opportunity_count", 0))
                for row in specialist_alpha.get("specialist_summaries", [])
            )
        )

        should_pause = (
            q2_closed
            and q3_closed
            and q4_closed
            and context_a_closed
            and context_b_closed
            and not u2_ready
        )
        recommended_next_phase = (
            "pause_specialist_refinement_and_prepare_new_suspect_batch"
            if should_pause
            else "continue_narrow_specialist_refinement"
        )

        evidence_rows = [
            {
                "evidence_name": "closed_market_v1_slices",
                "actual": {
                    "q2_closed": q2_closed,
                    "q3_closed": q3_closed,
                    "q4_closed": q4_closed,
                },
                "reading": "If all current market-v1 slice lanes are already closed, there is no open continuation lane left inside the current suspect batch.",
            },
            {
                "evidence_name": "closed_context_branches",
                "actual": {
                    "context_a_closed": context_a_closed,
                    "context_b_closed": context_b_closed,
                    "context_b_candidate_row_count": context_b_report.get("summary", {}).get("candidate_row_count"),
                },
                "reading": "If both conditional context branches are already closed, the current stage has no active context-led refinement branch left either.",
            },
            {
                "evidence_name": "unsupervised_gate",
                "actual": {
                    "u2_ready": u2_ready,
                    "recommended_next_phase": u2_readiness.get("summary", {}).get("recommended_next_phase"),
                },
                "reading": "If U2 is not ready, unsupervised sidecar work is also not the next continuation path.",
            },
            {
                "evidence_name": "specialist_frontier_state",
                "actual": {
                    "specialist_opportunity_count": specialist_opportunity_count,
                    "top_specialist_by_opportunity_count": specialist_alpha.get("summary", {}).get("top_specialist_by_opportunity_count"),
                },
                "reading": "Opportunity pockets still exist, but the current question is whether they justify more local replay under the existing batch or require a new suspect substrate.",
            },
        ]
        interpretation = [
            "This readiness gate is a stop-rule check, not a new strategy comparison.",
            "If all currently active slices and context branches are already closed, and unsupervised clustering is still not ready, the specialist line should pause rather than invent another continuation lane.",
            "Under that condition, the next productive move is to prepare a new suspect batch or a new data expansion phase, not to keep replaying inside the same closed geography.",
        ]
        summary = {
            "all_market_v1_slices_closed": q2_closed and q3_closed and q4_closed,
            "all_context_branches_closed": context_a_closed and context_b_closed,
            "u2_ready": u2_ready,
            "specialist_opportunity_count": specialist_opportunity_count,
            "recommended_next_phase": recommended_next_phase,
            "do_continue_current_specialist_loop": not should_pause,
        }
        return V11ContinuationReadinessReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v11_continuation_readiness_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V11ContinuationReadinessReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
