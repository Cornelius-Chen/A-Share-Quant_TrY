from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ng_a_share_information_center_latest_status_card_v1 import (
    V134NGAShareInformationCenterLatestStatusCardV1Analyzer,
)


@dataclass(slots=True)
class V134NHAShareNGLatestStatusDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134NHAShareNGLatestStatusDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134NHAShareNGLatestStatusDirectionTriageV1Report:
        report = V134NGAShareInformationCenterLatestStatusCardV1Analyzer(self.repo_root).analyze()
        summary = {
            "foundation_complete_count": report.summary["foundation_complete_count"],
            "workstream_count": report.summary["workstream_count"],
            "authoritative_status": "information_center_in_blocker_closure_mode_not_framework_build_mode",
        }
        triage_rows = [
            {
                "component": "framework_core",
                "direction": "freeze_current_framework_and_stop_reopening_scaffold_level_work",
            },
            {
                "component": "source_activation",
                "direction": "treat_allowlist_and_runtime_queues_as_next_real_work_not_more_source_design",
            },
            {
                "component": "replay_daily_market",
                "direction": "retain_daily_market_candidate_surface_but_keep_promotion_closed",
            },
            {
                "component": "paired_surfaces",
                "direction": "treat_index_daily_gap_as_primary_blocker_and_keep_limit_halt_only_candidate_ready",
            },
            {
                "component": "index_daily_source_horizon",
                "direction": "freeze_negative_result_and_wait_for_new_raw_index_source_before_extension_research",
            },
            {
                "component": "live_like_execution",
                "direction": "keep_live_like_and_execution_closed_until_named_source_and_replay_blockers_are_cleared",
            },
        ]
        interpretation = [
            "The project should now be steered as blocker closure, not as open-ended information-center construction.",
            "Daily-market and limit-halt progress should not be mistaken for replay readiness while index-daily remains a true source-horizon gap.",
        ]
        return V134NHAShareNGLatestStatusDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134NHAShareNGLatestStatusDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134NHAShareNGLatestStatusDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134nh_a_share_ng_latest_status_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
