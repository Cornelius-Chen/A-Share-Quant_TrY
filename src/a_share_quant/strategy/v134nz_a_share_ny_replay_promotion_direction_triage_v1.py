from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ny_a_share_replay_promotion_latest_status_card_v1 import (
    V134NYAShareReplayPromotionLatestStatusCardV1Analyzer,
)


@dataclass(slots=True)
class V134NZAShareNYReplayPromotionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134NZAShareNYReplayPromotionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134NZAShareNYReplayPromotionDirectionTriageV1Report:
        report = V134NYAShareReplayPromotionLatestStatusCardV1Analyzer(self.repo_root).analyze()
        if report.summary["true_source_gap_count"] == 0:
            summary = {
                "replay_component_count": report.summary["replay_component_count"],
                "true_source_gap_count": report.summary["true_source_gap_count"],
                "authoritative_status": "replay_promotion_should_shift_from_derivation_blocker_narrative_to_internal_build_precondition_recheck",
            }
            triage_rows = [
                {
                    "component": "shadow_execution_journal",
                    "direction": "retain_execution_journal_as_stub_only_until_market_context_closes",
                },
                {
                    "component": "daily_market_promotion",
                    "direction": "use_the_promotable_subset_as_the_new_replay-facing_entry_surface_without_opening_execution",
                },
                {
                    "component": "paired_surfaces",
                    "direction": "retire_limit_halt_as_primary_blocker_and_treat_semantic_pair_materialization_as_done_enough_for_recheck",
                },
                {
                    "component": "index_daily_source_horizon",
                    "direction": "retire_old_freeze_and_continue_with_downstream_reaudit",
                },
            ]
            interpretation = [
                "Replay promotion should now be governed by replay-internal precondition closure rather than source-gap or derivation-gap framing.",
                "The correct next move is execution-stub precondition recheck from the promotable subset, not continued index-source or limit-halt materialization work.",
            ]
        else:
            summary = {
                "replay_component_count": report.summary["replay_component_count"],
                "true_source_gap_count": report.summary["true_source_gap_count"],
                "authoritative_status": "replay_promotion_should_stay_in_blocker_closure_mode",
            }
            triage_rows = [
                {
                    "component": "shadow_execution_journal",
                    "direction": "retain_execution_journal_as_stub_only_until_market_context_closes",
                },
                {
                    "component": "daily_market_promotion",
                    "direction": "keep_daily_market_candidate_surface_read_only_and_nonpromotive",
                },
                {
                    "component": "paired_surfaces",
                    "direction": "treat_index_daily_as_primary_blocker_and_limit_halt_as_secondary_candidate_only",
                },
                {
                    "component": "index_daily_source_horizon",
                    "direction": "freeze_negative_result_and wait_for_new_raw_index_source_before_extension_reopen",
                },
            ]
            interpretation = [
                "Replay promotion should now be governed by a narrow blocker stack, not by new replay-shape experimentation.",
                "The correct next move is source acquisition or prelaunch gating for index-daily, not further daily/limit-halt promotion work.",
            ]
        return V134NZAShareNYReplayPromotionDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134NZAShareNYReplayPromotionDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134NZAShareNYReplayPromotionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134nz_a_share_ny_replay_promotion_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
