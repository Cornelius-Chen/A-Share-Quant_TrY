from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ss_a_share_trade_calendar_bootstrap_audit_v1 import (
    V134SSAShareTradeCalendarBootstrapAuditV1Analyzer,
)


@dataclass(slots=True)
class V134STAShareSSTradeCalendarDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134STAShareSSTradeCalendarDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134STAShareSSTradeCalendarDirectionTriageV1Report:
        report = V134SSAShareTradeCalendarBootstrapAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "calendar_row_count": report.summary["calendar_row_count"],
            "open_day_count": report.summary["open_day_count"],
            "coverage_start": report.summary["coverage_start"],
            "coverage_end": report.summary["coverage_end"],
            "today_calendar_state": report.summary["today_calendar_state"],
            "authoritative_status": "prefer_trade_calendar_backed_trading_day_state_over_weekday_approximation",
        }
        triage_rows = [
            {
                "component": "status_surface",
                "direction": "promote_real_trade_calendar_into_the_outermost_program_status_surface_before_using_weekday_only_approximation",
            },
            {
                "component": "session_phase_confidence",
                "direction": "mark_session_phase_as_exact_with_trade_calendar_when_the_current_date_is_covered_by_the_registry",
            },
            {
                "component": "fallback_branch",
                "direction": "retain_weekday_only_approximation_only_when_the_trade_calendar_is_missing_or_outside_the_covered_window",
            },
        ]
        interpretation = [
            "The current outermost timing layer can now rely on an actual trade calendar.",
            "Approximate timing is now a fallback branch, not the default branch.",
        ]
        return V134STAShareSSTradeCalendarDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134STAShareSSTradeCalendarDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134STAShareSSTradeCalendarDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134st_a_share_ss_trade_calendar_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
