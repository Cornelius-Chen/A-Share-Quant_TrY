from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134mw_a_share_daily_market_extension_candidate_audit_v1 import (
    V134MWAShareDailyMarketExtensionCandidateAuditV1Analyzer,
)


@dataclass(slots=True)
class V134MXAShareMWDailyMarketExtensionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134MXAShareMWDailyMarketExtensionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134MXAShareMWDailyMarketExtensionDirectionTriageV1Report:
        report = V134MWAShareDailyMarketExtensionCandidateAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "candidate_cover_count": report.summary["candidate_cover_count"],
            "raw_daily_symbol_count": report.summary["raw_daily_symbol_count"],
            "authoritative_status": "daily_market_extension_candidate_ready_for_controlled_promotion_review",
        }
        triage_rows = [
            {
                "component": "daily_market_extension_candidate_surface",
                "direction": "review_and_promote_candidate_daily_rows_before_further_replay_symbol_binding_work",
            },
            {
                "component": "paired_surfaces",
                "direction": "extend_index_daily_and_limit_halt_surfaces_in_lockstep_with_any_daily_market_promotion",
            },
        ]
        interpretation = [
            "Replay coverage work has reached a candidate-promotion stopline rather than a source-discovery stopline.",
            "Further replay binding work should wait until the daily candidate surface is either promoted or explicitly rejected.",
        ]
        return V134MXAShareMWDailyMarketExtensionDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134MXAShareMWDailyMarketExtensionDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MXAShareMWDailyMarketExtensionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134mx_a_share_mw_daily_market_extension_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
