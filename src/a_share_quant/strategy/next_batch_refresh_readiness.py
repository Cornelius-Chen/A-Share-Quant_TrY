from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class NextBatchRefreshReadinessReport:
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


class NextBatchRefreshReadinessAnalyzer:
    """Decide whether the repo should open another suspect-batch refresh now."""

    def analyze(
        self,
        *,
        v11_continuation: dict[str, Any],
        v2_seed_continuation: dict[str, Any],
        specialist_payload: dict[str, Any],
        v2_seed_plan_text: str,
    ) -> NextBatchRefreshReadinessReport:
        v11_paused = bool(
            v11_continuation.get("summary", {}).get("do_continue_current_specialist_loop") is False
        )
        v2_seed_paused = bool(
            v2_seed_continuation.get("summary", {}).get("do_continue_current_v2_seed_replay") is False
        )
        v2_seed_secondary = (
            "secondary substrate" in v2_seed_plan_text.lower()
            or "secondary specialist substrate" in v2_seed_plan_text.lower()
        )

        specialist_summaries = specialist_payload.get("specialist_summaries", [])
        if not isinstance(specialist_summaries, list):
            raise ValueError("Specialist payload must contain specialist_summaries.")
        v2_seed_opportunity_count = 0
        for row in specialist_summaries:
            top_datasets = {str(item) for item in row.get("top_datasets", [])}
            if "market_research_v2_seed" in top_datasets:
                v2_seed_opportunity_count += int(row.get("opportunity_count", 0))

        should_wait = v11_paused and v2_seed_paused and v2_seed_secondary
        recommended_next_phase = (
            "wait_for_new_archetype_gap_signal_before_opening_market_research_v2_refresh"
            if should_wait
            else "open_next_batch_refresh_design"
        )

        summary = {
            "v11_current_loop_paused": v11_paused,
            "v2_seed_local_loop_paused": v2_seed_paused,
            "v2_seed_secondary_substrate_status": v2_seed_secondary,
            "v2_seed_specialist_opportunity_count": v2_seed_opportunity_count,
            "recommended_next_phase": recommended_next_phase,
            "do_open_market_research_v2_refresh_now": not should_wait,
        }
        evidence_rows = [
            {
                "evidence_name": "current_loop_state",
                "actual": {
                    "v11_current_loop_paused": v11_paused,
                    "v2_seed_local_loop_paused": v2_seed_paused,
                },
                "reading": "If both the primary specialist loop and the currently opened v2-seed loop are paused, there is no active replay frontier that forces an immediate refresh.",
            },
            {
                "evidence_name": "v2_seed_role",
                "actual": {
                    "v2_seed_secondary_substrate_status": v2_seed_secondary,
                    "v2_seed_specialist_opportunity_count": v2_seed_opportunity_count,
                },
                "reading": "A secondary substrate can stay useful without immediately triggering another seed-refresh cycle.",
            },
            {
                "evidence_name": "refresh_trigger_posture",
                "actual": {
                    "recommended_next_phase": recommended_next_phase,
                },
                "reading": "The next refresh should open only when a new archetype gap signal or materially different suspect geography appears, not merely because the current packs are productive.",
            },
        ]
        interpretation = [
            "This gate controls when the repo is allowed to open a new suspect-batch refresh after v2-seed.",
            "If the current primary loop is paused and v2-seed is already useful but bounded, the correct default is to wait rather than immediately design another refresh.",
            "The next refresh should be triggered by a new archetype-gap signal, a materially different suspect geography, or a later pack refresh that changes the current bounded reading.",
        ]
        return NextBatchRefreshReadinessReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_next_batch_refresh_readiness_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: NextBatchRefreshReadinessReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
