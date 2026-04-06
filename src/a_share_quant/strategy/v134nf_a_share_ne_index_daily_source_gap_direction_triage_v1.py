from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ne_a_share_index_daily_source_horizon_gap_audit_v1 import (
    V134NEAShareIndexDailySourceHorizonGapAuditV1Analyzer,
)


@dataclass(slots=True)
class V134NFAShareNEIndexDailySourceGapDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134NFAShareNEIndexDailySourceGapDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134NFAShareNEIndexDailySourceGapDirectionTriageV1Report:
        report = V134NEAShareIndexDailySourceHorizonGapAuditV1Analyzer(self.repo_root).analyze()
        if report.summary["beyond_2024_source_count"] == 0:
            summary = {
                "raw_file_count": report.summary["raw_file_count"],
                "beyond_2024_source_count": report.summary["beyond_2024_source_count"],
                "authoritative_status": "index_daily_extension_blocked_by_true_source_horizon_gap",
            }
            triage_rows = [
                {
                    "component": "index_daily_source_horizon",
                    "direction": "freeze_current_negative_result_and require_new_raw_index_source_before_extension_review",
                },
                {
                    "component": "paired_surface_promotion",
                    "direction": "keep_daily_market_promotion_blocked_until_index_daily_source_horizon_moves",
                },
            ]
            interpretation = [
                "The dominant blocker has moved from uncertain coverage to explicit source insufficiency.",
                "Further index-daily promotion work would drift until a longer raw index feed enters the repository.",
            ]
        else:
            summary = {
                "raw_file_count": report.summary["raw_file_count"],
                "beyond_2024_source_count": report.summary["beyond_2024_source_count"],
                "authoritative_status": "index_daily_true_source_gap_closed_reaudit_required",
            }
            triage_rows = [
                {
                    "component": "index_daily_source_horizon",
                    "direction": "retire_old_true_source_gap_narrative_and_reopen_downstream_reaudit",
                },
                {
                    "component": "paired_surface_promotion",
                    "direction": "move_focus_from_source_absence_to_paired_surface_and_limit_halt_recheck",
                },
            ]
            interpretation = [
                "The dominant replay-side blocker is no longer raw-source absence once a beyond-2024 index file is retained.",
                "The correct next move is downstream re-audit, not continued source-gap framing.",
            ]
        return V134NFAShareNEIndexDailySourceGapDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134NFAShareNEIndexDailySourceGapDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134NFAShareNEIndexDailySourceGapDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134nf_a_share_ne_index_daily_source_gap_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
