from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134kt_a_share_market_foundation_audit_v1 import (
    V134KTAShareMarketFoundationAuditV1Analyzer,
)


@dataclass(slots=True)
class V134KUAShareKTMarketDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134KUAShareKTMarketDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134KUAShareKTMarketDirectionTriageV1Report:
        audit = V134KTAShareMarketFoundationAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "market_component": "daily_registry",
                "direction": "freeze_as_current_symbol_level_daily_coverage_surface",
            },
            {
                "market_component": "index_registry",
                "direction": "retain_as_market_context_input_for_later_serving_and_replay",
            },
            {
                "market_component": "intraday_coverage_registry",
                "direction": "retain_as_raw_zip_coverage_surface_without_forcing_full_symbol_materialization",
            },
            {
                "market_component": "next_frontier",
                "direction": "shift_into_replay_with_market_foundation_as_input_and_leave_board_state_derivation_explicitly_backlogged",
            },
        ]
        summary = {
            "daily_symbol_count": audit.summary["daily_symbol_count"],
            "intraday_trade_date_count": audit.summary["intraday_trade_date_count"],
            "board_state_still_backlogged": True,
            "authoritative_status": (
                "market_workstream_complete_enough_to_freeze_as_storage_aware_foundation_and_shift_into_replay"
            ),
        }
        interpretation = [
            "The market workstream now has a lawful storage-aware foundation: daily and intraday coverage are explicit, while board-state derivation remains consciously deferred.",
            "This is the correct stopping point for market V1 because it preserves reversibility and avoids premature minute-level expansion before replay and retention policies are fully exercised.",
        ]
        return V134KUAShareKTMarketDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134KUAShareKTMarketDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KUAShareKTMarketDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ku_a_share_kt_market_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
