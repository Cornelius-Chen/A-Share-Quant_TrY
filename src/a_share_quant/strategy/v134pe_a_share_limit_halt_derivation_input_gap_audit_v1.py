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
class V134PEAShareLimitHaltDerivationInputGapAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134PEAShareLimitHaltDerivationInputGapAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.current_surface_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "market_registry"
            / "a_share_limit_halt_surface_v1.csv"
        )
        self.raw_daily_path = (
            repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
        )
        self.output_csv = repo_root / "data" / "training" / "a_share_limit_halt_derivation_input_gap_status_v1.csv"

    def analyze(self) -> V134PEAShareLimitHaltDerivationInputGapAuditV1Report:
        current_rows = _read_csv(self.current_surface_path)
        raw_rows = _read_csv(self.raw_daily_path)
        current_fields = list(current_rows[0].keys())
        raw_fields = list(raw_rows[0].keys())

        current_required_fields = [
            "trade_date",
            "symbol",
            "board",
            "is_st",
            "is_suspended",
            "limit_ratio",
            "upper_limit_price",
            "lower_limit_price",
            "limit_up_hit",
            "limit_down_hit",
            "halt_or_suspend_flag",
        ]
        directly_present_fields = [field for field in current_required_fields if field in raw_fields]
        missing_direct_fields = [field for field in current_required_fields if field not in raw_fields]

        rows = [
            {
                "input_class": "directly_present_in_raw_daily",
                "field_count": len(directly_present_fields),
                "fields": "|".join(directly_present_fields),
            },
            {
                "input_class": "missing_directly_in_raw_daily",
                "field_count": len(missing_direct_fields),
                "fields": "|".join(missing_direct_fields),
            },
            {
                "input_class": "semantic_dependency_cluster",
                "field_count": 4,
                "fields": "board|is_st|is_suspended|halt_or_suspend_flag",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        summary = {
            "current_surface_field_count": len(current_fields),
            "raw_daily_field_count": len(raw_fields),
            "directly_present_field_count": len(directly_present_fields),
            "missing_direct_field_count": len(missing_direct_fields),
            "semantic_dependency_field_count": 4,
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_limit_halt_derivation_input_gap_explicit",
        }
        interpretation = [
            "Raw daily price/volume data is not the main replay-side gap anymore; it already covers the shadow horizon.",
            "The primary limit-halt derivation gap is semantic: board/ST/suspension inputs are not present in the raw daily file and therefore cannot be silently inferred as if they were ordinary price fields.",
        ]
        return V134PEAShareLimitHaltDerivationInputGapAuditV1Report(
            summary=summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134PEAShareLimitHaltDerivationInputGapAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134PEAShareLimitHaltDerivationInputGapAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134pe_a_share_limit_halt_derivation_input_gap_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
