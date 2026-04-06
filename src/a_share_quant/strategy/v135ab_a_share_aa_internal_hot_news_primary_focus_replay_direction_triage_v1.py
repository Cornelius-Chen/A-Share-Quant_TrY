from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v135aa_a_share_internal_hot_news_primary_focus_replay_tracker_audit_v1 import (
    V135AAAShareInternalHotNewsPrimaryFocusReplayTrackerAuditV1Analyzer,
)


@dataclass(slots=True)
class V135ABAShareAAInternalHotNewsPrimaryFocusReplayDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V135ABAShareAAInternalHotNewsPrimaryFocusReplayDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V135ABAShareAAInternalHotNewsPrimaryFocusReplayDirectionTriageV1Report:
        report = V135AAAShareInternalHotNewsPrimaryFocusReplayTrackerAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "focus_match_row_count": report.summary["focus_match_row_count"],
            "focus_source_present_count": report.summary["focus_source_present_count"],
            "theme_match_count": report.summary["theme_match_count"],
            "symbol_match_count": report.summary["symbol_match_count"],
            "current_primary_theme_slug": report.summary["current_primary_theme_slug"],
            "current_primary_watch_symbol": report.summary["current_primary_watch_symbol"],
            "authoritative_status": (
                "accepted_primary_focus_backed_by_real_candidate_lane"
                if report.summary["focus_source_present_count"] >= 1
                else "accepted_primary_focus_needs_revalidation"
            ),
        }
        triage_rows = [
            {
                "component": "accepted_focus_support",
                "direction": "keep monitoring whether the accepted second-source row remains present inside the controlled merge candidate lane before any later consumer rotation.",
            },
            {
                "component": "theme_symbol_replay",
                "direction": "prefer focus-specific replay tracking when a promoted theme/symbol pair becomes the primary consumer anchor instead of relying only on top-level snapshot fields.",
            },
            {
                "component": "multi-source_rotation_governance",
                "direction": "treat any later focus rotation as a replay-backed decision and compare it against the current accepted focus support set before promoting again.",
            },
        ]
        interpretation = [
            "The accepted primary focus is no longer just a shadow proposal; it can now be traced back to concrete rows inside the controlled merge candidate lane.",
            "This gives later rotation decisions a simpler comparison surface: current accepted focus support versus any challenger support set.",
        ]
        return V135ABAShareAAInternalHotNewsPrimaryFocusReplayDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135ABAShareAAInternalHotNewsPrimaryFocusReplayDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135ABAShareAAInternalHotNewsPrimaryFocusReplayDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135ab_a_share_aa_internal_hot_news_primary_focus_replay_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
