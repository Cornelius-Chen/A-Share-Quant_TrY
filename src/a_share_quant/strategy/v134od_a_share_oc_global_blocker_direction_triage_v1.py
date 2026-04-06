from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134oc_a_share_information_center_global_blocker_status_card_v1 import (
    V134OCAShareInformationCenterGlobalBlockerStatusCardV1Analyzer,
)


@dataclass(slots=True)
class V134ODAShareOCGlobalBlockerDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134ODAShareOCGlobalBlockerDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ODAShareOCGlobalBlockerDirectionTriageV1Report:
        report = V134OCAShareInformationCenterGlobalBlockerStatusCardV1Analyzer(self.repo_root).analyze()
        summary = {
            "global_component_count": report.summary["global_component_count"],
            "source_blocker_count": report.summary["source_blocker_count"],
            "replay_true_source_gap_count": report.summary["replay_true_source_gap_count"],
            "authoritative_status": "information_center_should_now_be_steered_by_dual_stopline_governance",
        }
        triage_rows = [
            {
                "component": "framework_core",
                "direction": "keep_framework_frozen_and_stop_scaffold_reopening",
            },
            {
                "component": "source_side",
                "direction": "treat_manual_review_record_closure_as_the_only_meaningful_next_source_side_gain",
            },
            {
                "component": "replay_side",
                "direction": "retain_replay_promotion_as_nonpromotive_until_index_daily_source_boundary_moves",
            },
            {
                "component": "index_daily_frontier",
                "direction": "treat_index_daily_extension_as_deferred_prelaunch_not_active_research",
            },
            {
                "component": "live_like_execution",
                "direction": "keep_live_like_and_execution_closed_while_source_and_replay_stoplines_remain",
            },
        ]
        interpretation = [
            "The project should now be managed as a dual-stopline system rather than as a single open-ended buildout.",
            "That dual stopline is source-side manual closure pending plus replay-side true source gap.",
        ]
        return V134ODAShareOCGlobalBlockerDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134ODAShareOCGlobalBlockerDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ODAShareOCGlobalBlockerDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134od_a_share_oc_global_blocker_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
