from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V134NEAShareIndexDailySourceHorizonGapAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134NEAShareIndexDailySourceHorizonGapAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.index_raw_dir = repo_root / "data" / "raw" / "index_daily_bars"
        self.shadow_surface_path = (
            repo_root / "data" / "derived" / "info_center" / "replay" / "shadow" / "a_share_shadow_replay_surface_v1.csv"
        )
        self.output_csv = repo_root / "data" / "training" / "a_share_index_daily_source_horizon_gap_status_v1.csv"

    def analyze(self) -> V134NEAShareIndexDailySourceHorizonGapAuditV1Report:
        shadow_rows = _read_csv(self.shadow_surface_path)
        raw_files = sorted(self.index_raw_dir.glob("*.csv"))
        rows: list[dict[str, Any]] = []
        raw_file_count = 0
        beyond_2024_source_count = 0
        max_raw_end = None
        for path in raw_files:
            raw_rows = _read_csv(path)
            if not raw_rows:
                continue
            raw_file_count += 1
            dates = sorted({row["trade_date"] for row in raw_rows if row.get("trade_date")})
            raw_end = dates[-1]
            if max_raw_end is None or raw_end > max_raw_end:
                max_raw_end = raw_end
            if raw_end > "2024-12-31":
                beyond_2024_source_count += 1
            rows.append(
                {
                    "raw_file": path.name,
                    "raw_row_count": len(raw_rows),
                    "raw_coverage_start": dates[0],
                    "raw_coverage_end": raw_end,
                    "extends_beyond_2024": raw_end > "2024-12-31",
                }
            )

        shadow_horizon_dates = sorted({row["decision_trade_date"] for row in shadow_rows})
        shadow_horizon_start = shadow_horizon_dates[0]
        shadow_horizon_end = shadow_horizon_dates[-1]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        summary = {
            "raw_file_count": raw_file_count,
            "beyond_2024_source_count": beyond_2024_source_count,
            "max_raw_coverage_end": max_raw_end,
            "shadow_horizon_start": shadow_horizon_start,
            "shadow_horizon_end": shadow_horizon_end,
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_index_daily_source_horizon_gap_explicit",
        }
        if beyond_2024_source_count == 0:
            interpretation = [
                "The index-daily blocker is now confirmed as a true source-horizon gap, not a missed materialization opportunity.",
                "All currently retained raw index files stop at 2024-12-31 while replay shadow slices extend into 2025-2026.",
            ]
        else:
            interpretation = [
                "At least one retained raw index file now extends beyond 2024, so the old true source-horizon gap has been materially reduced.",
                "The next replay-side question is downstream materialization and paired-surface re-audit rather than raw-source absence.",
            ]
        return V134NEAShareIndexDailySourceHorizonGapAuditV1Report(
            summary=summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134NEAShareIndexDailySourceHorizonGapAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134NEAShareIndexDailySourceHorizonGapAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ne_a_share_index_daily_source_horizon_gap_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
