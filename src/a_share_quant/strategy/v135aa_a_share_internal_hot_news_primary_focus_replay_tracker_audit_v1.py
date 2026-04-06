from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_primary_focus_replay_tracker_v1 import (
    MaterializeAShareInternalHotNewsPrimaryFocusReplayTrackerV1,
)


@dataclass(slots=True)
class V135AAAShareInternalHotNewsPrimaryFocusReplayTrackerAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V135AAAShareInternalHotNewsPrimaryFocusReplayTrackerAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V135AAAShareInternalHotNewsPrimaryFocusReplayTrackerAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsPrimaryFocusReplayTrackerV1(self.repo_root).materialize()
        rows = [
            {
                "component": "primary_focus_replay_tracker",
                "component_state": "materialized",
                "metric": "focus_match_row_count",
                "value": str(materialized.summary["focus_match_row_count"]),
            },
            {
                "component": "primary_focus_replay_tracker",
                "component_state": "materialized",
                "metric": "focus_source_present_count",
                "value": str(materialized.summary["focus_source_present_count"]),
            },
            {
                "component": "primary_focus_replay_tracker",
                "component_state": "materialized",
                "metric": "theme_match_count",
                "value": str(materialized.summary["theme_match_count"]),
            },
            {
                "component": "primary_focus_replay_tracker",
                "component_state": "materialized",
                "metric": "symbol_match_count",
                "value": str(materialized.summary["symbol_match_count"]),
            },
            {
                "component": "primary_focus_replay_tracker",
                "component_state": "materialized",
                "metric": "dual_match_count",
                "value": str(materialized.summary["dual_match_count"]),
            },
            {
                "component": "primary_focus_replay_tracker",
                "component_state": "materialized",
                "metric": "unique_source_family_count",
                "value": str(materialized.summary["unique_source_family_count"]),
            },
        ]
        interpretation = [
            "This tracker isolates which real candidate rows currently support the accepted primary focus in the consumer chain.",
            "It shows whether the accepted focus is backed by just the accepted second-source row or by a broader set of matching theme/symbol candidates.",
        ]
        return V135AAAShareInternalHotNewsPrimaryFocusReplayTrackerAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135AAAShareInternalHotNewsPrimaryFocusReplayTrackerAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135AAAShareInternalHotNewsPrimaryFocusReplayTrackerAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135aa_a_share_internal_hot_news_primary_focus_replay_tracker_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
