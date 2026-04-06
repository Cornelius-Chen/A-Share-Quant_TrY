from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.market.daily.materialize_a_share_market_foundation_v1 import (
    MaterializeAShareMarketFoundationV1,
)


@dataclass(slots=True)
class V134KTAShareMarketFoundationAuditV1Report:
    summary: dict[str, Any]
    market_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "market_rows": self.market_rows,
            "interpretation": self.interpretation,
        }


class V134KTAShareMarketFoundationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_market_foundation_status_v1.csv"

    def analyze(self) -> V134KTAShareMarketFoundationAuditV1Report:
        materialized = MaterializeAShareMarketFoundationV1(self.repo_root).materialize()
        summary = materialized.summary
        market_rows = [
            {
                "market_component": "daily_registry",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["daily_registry_path"],
                "coverage_note": f"daily_symbol_count = {summary['daily_symbol_count']}",
            },
            {
                "market_component": "index_registry",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["index_registry_path"],
                "coverage_note": f"index_symbol_count = {summary['index_symbol_count']}",
            },
            {
                "market_component": "intraday_coverage_registry",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["intraday_registry_path"],
                "coverage_note": f"intraday_trade_date_count = {summary['intraday_trade_date_count']}",
            },
            {
                "market_component": "board_state_backlog",
                "component_state": "backlog_materialized_not_yet_derived",
                "artifact_path": summary["backlog_path"],
                "coverage_note": f"board_state_backlog_count = {summary['board_state_backlog_count']}",
            },
        ]
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(market_rows[0].keys()))
            writer.writeheader()
            writer.writerows(market_rows)

        report_summary = {
            "acceptance_posture": "build_v134kt_a_share_market_foundation_audit_v1",
            "daily_symbol_count": summary["daily_symbol_count"],
            "daily_identity_overlap_count": summary["daily_identity_overlap_count"],
            "index_symbol_count": summary["index_symbol_count"],
            "intraday_trade_date_count": summary["intraday_trade_date_count"],
            "intraday_first_trade_date": summary["intraday_first_trade_date"],
            "intraday_last_trade_date": summary["intraday_last_trade_date"],
            "market_status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_market_foundation_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34KT completes the first market workstream pass by materializing daily symbol coverage, index coverage, and intraday raw-zip coverage without exploding storage into full minute-level symbol tables.",
            "Board-state, breadth, and limit-halt surfaces remain explicit backlog items, which is consistent with the storage-first information-center design.",
        ]
        return V134KTAShareMarketFoundationAuditV1Report(
            summary=report_summary,
            market_rows=market_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V134KTAShareMarketFoundationAuditV1Report) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KTAShareMarketFoundationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134kt_a_share_market_foundation_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
