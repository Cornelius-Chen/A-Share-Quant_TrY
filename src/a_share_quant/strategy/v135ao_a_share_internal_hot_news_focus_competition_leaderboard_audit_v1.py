from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_focus_competition_leaderboard_v1 import (
    MaterializeAShareInternalHotNewsFocusCompetitionLeaderboardV1,
)


@dataclass(slots=True)
class V135AOAShareInternalHotNewsFocusCompetitionLeaderboardAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V135AOAShareInternalHotNewsFocusCompetitionLeaderboardAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V135AOAShareInternalHotNewsFocusCompetitionLeaderboardAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsFocusCompetitionLeaderboardV1(
            self.repo_root
        ).materialize()
        rows = [
            {
                "component": "focus_leaderboard",
                "component_state": "materialized",
                "metric": "leaderboard_row_count",
                "value": str(materialized.summary["leaderboard_row_count"]),
            },
            {
                "component": "current_primary",
                "component_state": "materialized",
                "metric": "current_primary_rank",
                "value": str(materialized.summary["current_primary_rank"]),
            },
            {
                "component": "current_primary",
                "component_state": "materialized",
                "metric": "incumbent_is_leader",
                "value": materialized.summary["incumbent_is_leader"],
            },
            {
                "component": "leader_focus",
                "component_state": "materialized",
                "metric": "leader_theme_slug",
                "value": materialized.summary["leader_theme_slug"],
            },
            {
                "component": "leader_focus",
                "component_state": "materialized",
                "metric": "leader_support_row_count",
                "value": str(materialized.summary["leader_support_row_count"]),
            },
            {
                "component": "leader_focus",
                "component_state": "materialized",
                "metric": "leader_focus_total_score",
                "value": f"{materialized.summary['leader_focus_total_score']:.4f}",
            },
        ]
        interpretation = [
            "This leaderboard now ranks the current incumbent beside all challengers by focus score, not just raw support depth.",
            "Focus score blends source authority, policy wording, cycle persistence, second-wave retrigger potential, crowding exhaustion, and tradability.",
            "It makes it explicit whether the incumbent still leads the field or is now merely being held despite trailing scored focus quality.",
        ]
        return V135AOAShareInternalHotNewsFocusCompetitionLeaderboardAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135AOAShareInternalHotNewsFocusCompetitionLeaderboardAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135AOAShareInternalHotNewsFocusCompetitionLeaderboardAuditV1Analyzer(
        repo_root
    ).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135ao_a_share_internal_hot_news_focus_competition_leaderboard_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
