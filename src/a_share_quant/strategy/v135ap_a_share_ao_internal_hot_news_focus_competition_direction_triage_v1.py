from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v135ao_a_share_internal_hot_news_focus_competition_leaderboard_audit_v1 import (
    V135AOAShareInternalHotNewsFocusCompetitionLeaderboardAuditV1Analyzer,
)


@dataclass(slots=True)
class V135APAShareAOInternalHotNewsFocusCompetitionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V135APAShareAOInternalHotNewsFocusCompetitionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V135APAShareAOInternalHotNewsFocusCompetitionDirectionTriageV1Report:
        report = V135AOAShareInternalHotNewsFocusCompetitionLeaderboardAuditV1Analyzer(
            self.repo_root
        ).analyze()
        summary = {
            "current_primary_theme_slug": report.summary["current_primary_theme_slug"],
            "current_primary_rank": report.summary["current_primary_rank"],
            "leader_theme_slug": report.summary["leader_theme_slug"],
            "leader_watch_symbol": report.summary["leader_watch_symbol"],
            "incumbent_is_leader": report.summary["incumbent_is_leader"],
            "challenger_count": report.summary["challenger_count"],
            "authoritative_status": "focus_competition_leaderboard_materialized",
        }
        triage_rows = [
            {
                "component": "ranking_visibility",
                "direction": "use the leaderboard to see whether current incumbent strength is still first, tied, or trailing without reopening challenger surfaces one by one.",
            },
            {
                "component": "rotation_context",
                "direction": "combine leaderboard rank with challenger review attention so a single noisy challenger does not silently become the narrative anchor.",
            },
            {
                "component": "next_review_trigger",
                "direction": "only promote a challenger when it both climbs the leaderboard and clears the separate review threshold.",
            },
        ]
        interpretation = [
            "The leaderboard adds competition context around the incumbent instead of reducing the system to a single challenger-only view.",
            "It is useful when several themes are near each other and the top challenger alone is not enough to judge focus stability.",
        ]
        return V135APAShareAOInternalHotNewsFocusCompetitionDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135APAShareAOInternalHotNewsFocusCompetitionDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135APAShareAOInternalHotNewsFocusCompetitionDirectionTriageV1Analyzer(
        repo_root
    ).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135ap_a_share_ao_internal_hot_news_focus_competition_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
