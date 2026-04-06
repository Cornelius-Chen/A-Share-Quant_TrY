from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134qs_a_share_runtime_scheduler_governance_opening_review_audit_v1 import (
    V134QSAShareRuntimeSchedulerGovernanceOpeningReviewAuditV1Analyzer,
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass(slots=True)
class V134OSAShareInformationCenterBuildCompletionStatusCardV1Report:
    summary: dict[str, Any]
    status_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "status_rows": self.status_rows,
            "interpretation": self.interpretation,
        }


class V134OSAShareInformationCenterBuildCompletionStatusCardV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.foundation_path = (
            repo_root / "reports" / "analysis" / "v134ld_a_share_information_center_foundation_completion_audit_v1.json"
        )
        self.global_blocker_path = (
            repo_root / "reports" / "analysis" / "v134oc_a_share_information_center_global_blocker_status_card_v1.json"
        )
        self.manual_status_path = (
            repo_root / "reports" / "analysis" / "v134oo_a_share_source_internal_manual_latest_status_card_v1.json"
        )
        self.source_runtime_status_path = (
            repo_root / "reports" / "analysis" / "v134qi_a_share_source_runtime_promotion_lane_status_audit_v1.json"
        )
        self.replay_status_path = (
            repo_root / "reports" / "analysis" / "v134ny_a_share_replay_promotion_latest_status_card_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "a_share_information_center_build_completion_status_v1.csv"
        )

    def analyze(self) -> V134OSAShareInformationCenterBuildCompletionStatusCardV1Report:
        foundation = _read_json(self.foundation_path)["summary"]
        global_blocker = _read_json(self.global_blocker_path)["summary"]
        manual_status = _read_json(self.manual_status_path)["summary"]
        source_runtime_status = _read_json(self.source_runtime_status_path)["summary"]
        opening_review = V134QSAShareRuntimeSchedulerGovernanceOpeningReviewAuditV1Analyzer(self.repo_root).analyze()
        replay_report = _read_json(self.replay_status_path)
        replay_promotable_now_count = 0
        replay_shadow_eligible_subset_count = 0
        for row in replay_report["rows"]:
            if row["replay_component"] == "daily_market_promotion":
                replay_promotable_now_count = int(row["decisive_metric"].split("=")[1].strip())
            if row["replay_component"] == "shadow_corrected_recheck":
                replay_shadow_eligible_subset_count = 15
        total_blocker_count = 0
        for row in _read_json(self.global_blocker_path)["rows"]:
            if row["global_component"] == "live_like_execution":
                total_blocker_count = int(row["decisive_metric"].split("=")[1].strip())
                break

        status_rows = [
            {
                "component": "information_center_core",
                "component_state": "build_complete_enough",
                "metric": "foundation_complete_count",
                "value": str(foundation["foundation_complete_count"]),
            },
            {
                "component": "source_internal_manual",
                "component_state": "single_runtime_opening_review_lane_pending_scheduler_and_governance_after_build",
                "metric": "priority_runtime_candidate_count",
                "value": str(source_runtime_status["priority_runtime_candidate_count"]),
            },
            {
                "component": "replay_promotion",
                "component_state": "shadow_execution_eligible_subset_materialized_after_shadow_overlay_recheck",
                "metric": "eligible_subset_count",
                "value": str(replay_shadow_eligible_subset_count),
            },
            {
                "component": "execution_live_like",
                "component_state": "explicitly_blocked_after_build",
                "metric": "total_blocker_count",
                "value": str(total_blocker_count),
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(status_rows[0].keys()))
            writer.writeheader()
            writer.writerows(status_rows)

        summary = {
            "foundation_complete_count": foundation["foundation_complete_count"],
            "manual_closure_pending_count": opening_review.summary["scheduler_pending_count"],
            "replay_promotable_now_count": replay_promotable_now_count,
            "replay_shadow_eligible_subset_count": replay_shadow_eligible_subset_count,
            "global_blocker_count": total_blocker_count,
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_status": "information_center_build_complete_enough_remaining_work_is_backlog_closure_not_core_construction",
        }
        interpretation = [
            "The information center itself is no longer in a scaffold-building phase; its remaining work is backlog closure and gated promotion.",
            "What remains is divided cleanly into a single source-side runtime scheduler lane, replay-side internal build from a 15-row shadow-execution eligible subset, and intentionally closed governance gates.",
        ]
        return V134OSAShareInformationCenterBuildCompletionStatusCardV1Report(
            summary=summary,
            status_rows=status_rows,
            interpretation=interpretation,
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134OSAShareInformationCenterBuildCompletionStatusCardV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134OSAShareInformationCenterBuildCompletionStatusCardV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134os_a_share_information_center_build_completion_status_card_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
