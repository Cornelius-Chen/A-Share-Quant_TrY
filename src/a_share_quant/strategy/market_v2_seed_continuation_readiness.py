from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MarketV2SeedContinuationReadinessReport:
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


class MarketV2SeedContinuationReadinessAnalyzer:
    """Decide whether v2-seed should open another local replay lane."""

    def analyze(
        self,
        *,
        q4_capture_acceptance: dict[str, Any],
        q3_drawdown_acceptance: dict[str, Any],
        audit_payload: dict[str, Any],
        specialist_payload: dict[str, Any],
    ) -> MarketV2SeedContinuationReadinessReport:
        q4_closed = bool(
            q4_capture_acceptance.get("summary", {}).get("do_continue_q4_capture_replay") is False
        )
        q3_closed = bool(
            q3_drawdown_acceptance.get("summary", {}).get("do_continue_q3_drawdown_replay") is False
        )
        baseline_ready = bool(audit_payload.get("summary", {}).get("baseline_ready"))

        specialist_summaries = specialist_payload.get("specialist_summaries", [])
        if not isinstance(specialist_summaries, list):
            raise ValueError("Specialist payload must contain specialist_summaries.")
        contributes_specialist_pockets = any(
            "market_research_v2_seed" in list(item.get("top_datasets", []))
            for item in specialist_summaries
        )

        should_pause = q4_closed and q3_closed and baseline_ready and contributes_specialist_pockets
        recommended_next_phase = (
            "hold_market_v2_seed_as_secondary_substrate_and_wait_for_next_batch_refresh"
            if should_pause
            else "continue_market_v2_seed_narrow_replay"
        )
        summary = {
            "all_open_v2_seed_lanes_closed": q4_closed and q3_closed,
            "v2_seed_baseline_ready": baseline_ready,
            "v2_seed_contributes_specialist_pockets": contributes_specialist_pockets,
            "recommended_next_phase": recommended_next_phase,
            "do_continue_current_v2_seed_replay": not should_pause,
        }
        evidence_rows = [
            {
                "evidence_name": "slice_acceptance_state",
                "actual": {
                    "q4_capture_closed": q4_closed,
                    "q3_drawdown_closed": q3_closed,
                },
                "reading": "If the currently opened v2-seed lanes are already closed, there is no active local replay lane left to justify another symbol by momentum alone.",
            },
            {
                "evidence_name": "pack_status",
                "actual": {
                    "baseline_ready": baseline_ready,
                    "derived_ready_count": audit_payload.get("summary", {}).get("derived_ready_count"),
                },
                "reading": "A closed-lane decision only matters if the pack itself is already stable enough to count as a real substrate.",
            },
            {
                "evidence_name": "specialist_role",
                "actual": {
                    "contributes_specialist_pockets": contributes_specialist_pockets,
                    "top_specialist_by_opportunity_count": specialist_payload.get("summary", {}).get("top_specialist_by_opportunity_count"),
                },
                "reading": "v2-seed is useful only if it already contributes pocket geography, even when it does not yet justify a fresh local replay branch.",
            },
        ]
        interpretation = [
            "This gate is not a promotion comparison. It is a stop-rule for the current v2-seed local replay budget.",
            "If v2-seed is baseline-ready, contributes specialist pockets, and its currently opened lanes are already closed, the correct posture is to keep it as a secondary substrate rather than forcing another replay lane.",
            "Under that condition, the next productive move is either a later batch refresh or a materially different v2-seed suspect lane, not one more local continuation by inertia.",
        ]
        return MarketV2SeedContinuationReadinessReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_market_v2_seed_continuation_readiness_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: MarketV2SeedContinuationReadinessReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
