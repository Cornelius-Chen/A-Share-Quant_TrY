from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.market.materialize_a_share_daily_market_extension_candidate_v1 import (
    MaterializeAShareDailyMarketExtensionCandidateV1,
)


@dataclass(slots=True)
class V134MWAShareDailyMarketExtensionCandidateAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134MWAShareDailyMarketExtensionCandidateAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_daily_market_extension_candidate_status_v1.csv"

    def analyze(self) -> V134MWAShareDailyMarketExtensionCandidateAuditV1Report:
        materialized = MaterializeAShareDailyMarketExtensionCandidateV1(self.repo_root).materialize()
        summary = materialized.summary
        rows = [
            {
                "component": "daily_market_extension_candidate_surface",
                "component_state": "materialized_candidate_cover_surface",
                "artifact_path": summary["candidate_path"],
                "coverage_note": f"candidate_cover_count = {summary['candidate_cover_count']}",
            },
            {
                "component": "extension_candidate_residual",
                "component_state": "materialized_named_residuals",
                "artifact_path": summary["residual_path"],
                "coverage_note": f"raw_daily_symbol_count = {summary['raw_daily_symbol_count']}",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        report_summary = {
            "shadow_slice_count": summary["shadow_slice_count"],
            "candidate_cover_count": summary["candidate_cover_count"],
            "raw_daily_symbol_count": summary["raw_daily_symbol_count"],
            "raw_daily_coverage_start": summary["raw_daily_coverage_start"],
            "raw_daily_coverage_end": summary["raw_daily_coverage_end"],
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_daily_market_extension_candidate_surface_materialized",
        }
        interpretation = [
            "The replay daily coverage gap is not a raw-source absence problem anymore: a candidate daily extension surface now exists.",
            "The next step is controlled promotion of candidate daily coverage, plus matching index and limit-halt extension.",
        ]
        return V134MWAShareDailyMarketExtensionCandidateAuditV1Report(
            summary=report_summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134MWAShareDailyMarketExtensionCandidateAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MWAShareDailyMarketExtensionCandidateAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134mw_a_share_daily_market_extension_candidate_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
