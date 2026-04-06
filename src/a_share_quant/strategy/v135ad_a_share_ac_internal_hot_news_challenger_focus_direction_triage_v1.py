from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v135ac_a_share_internal_hot_news_challenger_focus_comparison_audit_v1 import (
    V135ACAShareInternalHotNewsChallengerFocusComparisonAuditV1Analyzer,
)


@dataclass(slots=True)
class V135ADAShareACInternalHotNewsChallengerFocusDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V135ADAShareACInternalHotNewsChallengerFocusDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V135ADAShareACInternalHotNewsChallengerFocusDirectionTriageV1Report:
        report = V135ACAShareInternalHotNewsChallengerFocusComparisonAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "challenger_row_count": report.summary["challenger_row_count"],
            "current_primary_theme_slug": report.summary["current_primary_theme_slug"],
            "current_primary_watch_symbol": report.summary["current_primary_watch_symbol"],
            "top_challenger_theme_slug": report.summary["top_challenger_theme_slug"],
            "top_challenger_symbol": report.summary["top_challenger_symbol"],
            "top_challenger_support_row_count": report.summary["top_challenger_support_row_count"],
            "authoritative_status": "challenger_focus_board_materialized_for_next_rotation_review",
        }
        triage_rows = [
            {
                "component": "current_primary_focus",
                "direction": "keep the accepted primary focus as the live anchor while monitoring the challenger board for any larger multi-row challenger cluster.",
            },
            {
                "component": "challenger_focus_board",
                "direction": "use the top challenger row count and source-family spread as the first quick screen before opening a new accepted-rotation preview.",
            },
            {
                "component": "next_rotation_governance",
                "direction": "only promote a challenger after comparing its replay support board against the current primary-focus replay tracker rather than reacting to a single candidate row.",
            },
        ]
        interpretation = [
            "The current primary focus now has a direct challenger board beside it.",
            "This makes later consumer rotation decisions easier to defend because the incumbent and challenger can be compared on replay support instead of only headline intuition.",
        ]
        return V135ADAShareACInternalHotNewsChallengerFocusDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135ADAShareACInternalHotNewsChallengerFocusDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135ADAShareACInternalHotNewsChallengerFocusDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135ad_a_share_ac_internal_hot_news_challenger_focus_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
