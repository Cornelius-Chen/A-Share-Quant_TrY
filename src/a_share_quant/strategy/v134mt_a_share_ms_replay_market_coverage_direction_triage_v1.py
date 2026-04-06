from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ms_a_share_replay_market_coverage_gap_audit_v1 import (
    V134MSAShareReplayMarketCoverageGapAuditV1Analyzer,
)


@dataclass(slots=True)
class V134MTAShareMSReplayMarketCoverageDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134MTAShareMSReplayMarketCoverageDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134MTAShareMSReplayMarketCoverageDirectionTriageV1Report:
        report = V134MSAShareReplayMarketCoverageGapAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "date_level_bound_count": report.summary["date_level_bound_count"],
            "daily_gap_count": report.summary["daily_gap_count"],
            "intraday_present_daily_missing_count": report.summary["intraday_present_daily_missing_count"],
            "authoritative_status": "replay_market_coverage_gap_narrowed_to_residual_missing_date_contexts",
        }
        triage_rows = [
            {
                "component": "daily_market_coverage",
                "direction": "close_only_the_residual_missing_date_contexts_instead_of_repeating_full_market_extension",
            },
            {
                "component": "replay_tradeable_context",
                "direction": "retain_date_level_binding_and_shift_next_attention_to_symbol_level_or_residual_date_closure",
            },
        ]
        interpretation = [
            "The replay-side blocker is now narrower than before because most shadow slices already have date-level tradeable context.",
            "More bulk market-surface rebuilding would now drift; the next move is residual date closure or controlled symbol-level escalation.",
        ]
        return V134MTAShareMSReplayMarketCoverageDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134MTAShareMSReplayMarketCoverageDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MTAShareMSReplayMarketCoverageDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134mt_a_share_ms_replay_market_coverage_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
