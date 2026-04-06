from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134mq_a_share_replay_tradeable_context_binding_audit_v1 import (
    V134MQAShareReplayTradeableContextBindingAuditV1Analyzer,
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V134MSAShareReplayMarketCoverageGapAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134MSAShareReplayMarketCoverageGapAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.shadow_surface_path = (
            repo_root / "data" / "derived" / "info_center" / "replay" / "shadow" / "a_share_shadow_replay_surface_v1.csv"
        )
        self.intraday_coverage_path = (
            repo_root / "data" / "reference" / "info_center" / "market_registry" / "a_share_intraday_coverage_registry_v1.csv"
        )
        self.output_csv = repo_root / "data" / "training" / "a_share_replay_market_coverage_gap_status_v1.csv"

    def analyze(self) -> V134MSAShareReplayMarketCoverageGapAuditV1Report:
        shadow_rows = _read_csv(self.shadow_surface_path)
        intraday_rows = _read_csv(self.intraday_coverage_path)
        binding_report = V134MQAShareReplayTradeableContextBindingAuditV1Analyzer(self.repo_root).analyze()
        binding_by_slice = {}
        for row in _read_csv(
            self.repo_root
            / "data"
            / "reference"
            / "info_center"
            / "replay_registry"
            / "a_share_replay_tradeable_context_binding_v1.csv"
        ):
            binding_by_slice[row["slice_id"]] = row

        intraday_dates = {f"{row['trade_date'][:4]}-{row['trade_date'][4:6]}-{row['trade_date'][6:]}" for row in intraday_rows}

        rows: list[dict[str, Any]] = []
        daily_gap_count = 0
        intraday_present_daily_missing_count = 0
        total_intraday_present_count = 0
        for row in shadow_rows:
            decision_trade_date = row["decision_trade_date"]
            intraday_present = row["intraday_zip_available"] == "True"
            binding_state = binding_by_slice[row["slice_id"]]["tradeable_context_state"]
            daily_present = binding_state == "date_level_tradeable_context_bound"
            if intraday_present:
                total_intraday_present_count += 1
            if not daily_present:
                daily_gap_count += 1
            if intraday_present and not daily_present:
                intraday_present_daily_missing_count += 1
            rows.append(
                {
                    "slice_id": row["slice_id"],
                    "decision_trade_date": decision_trade_date,
                    "intraday_present": intraday_present,
                    "daily_present": daily_present,
                    "coverage_gap_state": (
                        "intraday_present_daily_missing"
                        if intraday_present and not daily_present
                        else "full_market_context_missing"
                        if not intraday_present and not daily_present
                        else "covered"
                    ),
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        summary = {
            "shadow_slice_count": len(rows),
            "date_level_bound_count": binding_report.summary["date_level_bound_count"],
            "daily_gap_count": daily_gap_count,
            "total_intraday_present_count": total_intraday_present_count,
            "intraday_present_daily_missing_count": intraday_present_daily_missing_count,
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_replay_market_coverage_gap_explicit",
        }
        interpretation = [
            "Replay's market-context blocker is no longer a blind daily-window mismatch; it is now an explicit residual after date-level tradeable-context binding.",
            "That makes the next replay-side closure target narrower: close the remaining missing date contexts instead of repeating full market-surface bootstrap work.",
        ]
        return V134MSAShareReplayMarketCoverageGapAuditV1Report(
            summary=summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134MSAShareReplayMarketCoverageGapAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MSAShareReplayMarketCoverageGapAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ms_a_share_replay_market_coverage_gap_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
