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
class V134PIAShareLimitHaltSideInputAvailabilityAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134PIAShareLimitHaltSideInputAvailabilityAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.security_master_path = (
            repo_root / "data" / "reference" / "info_center" / "identity" / "a_share_security_master_v1.csv"
        )
        self.stk_limit_path = (
            repo_root / "data" / "reference" / "stk_limit" / "tushare_commercial_aerospace_stk_limit_v1.csv"
        )
        self.namechange_path = (
            repo_root / "data" / "reference" / "namechange" / "tushare_commercial_aerospace_namechange_v1.csv"
        )
        self.suspend_path = (
            repo_root / "data" / "reference" / "suspend_d" / "tushare_commercial_aerospace_suspend_d_v1.csv"
        )
        self.output_csv = repo_root / "data" / "training" / "a_share_limit_halt_side_input_availability_status_v1.csv"

    def analyze(self) -> V134PIAShareLimitHaltSideInputAvailabilityAuditV1Report:
        security_rows = _read_csv(self.security_master_path)
        stk_limit_rows = _read_csv(self.stk_limit_path)
        namechange_rows = _read_csv(self.namechange_path)
        suspend_rows = _read_csv(self.suspend_path)

        board_symbol_count = len({row["symbol"] for row in security_rows if row.get("board")})
        stk_limit_symbol_count = len({row["symbol"] for row in stk_limit_rows if row.get("symbol")})
        namechange_symbol_count = len({row["symbol"] for row in namechange_rows if row.get("symbol")})
        suspend_symbol_count = len({row["symbol"] for row in suspend_rows if row.get("symbol")})

        rows = [
            {
                "side_input_family": "board_identity",
                "availability_state": "retained",
                "symbol_count": board_symbol_count,
                "coverage_note": "board comes from security_master identity layer",
            },
            {
                "side_input_family": "stk_limit_price_band",
                "availability_state": "retained",
                "symbol_count": stk_limit_symbol_count,
                "coverage_note": "up_limit/down_limit retained through 2026-04-03",
            },
            {
                "side_input_family": "st_proxy_namechange",
                "availability_state": "retained_sparse",
                "symbol_count": namechange_symbol_count,
                "coverage_note": "namechange retained as first ST proxy family",
            },
            {
                "side_input_family": "suspension_records",
                "availability_state": "retained_sparse",
                "symbol_count": suspend_symbol_count,
                "coverage_note": "suspend_d retained as first suspension family",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        summary = {
            "retained_family_count": 4,
            "board_symbol_count": board_symbol_count,
            "stk_limit_symbol_count": stk_limit_symbol_count,
            "namechange_symbol_count": namechange_symbol_count,
            "suspend_symbol_count": suspend_symbol_count,
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_limit_halt_side_input_availability_surface_materialized",
        }
        interpretation = [
            "Replay-facing limit-halt derivation no longer lacks every side input family.",
            "Board identity and price-band inputs are already retained, while ST and suspension have now been added as sparse but real retained families.",
            "The remaining task is not source hunting; it is semantic materialization from uneven side-input families.",
        ]
        return V134PIAShareLimitHaltSideInputAvailabilityAuditV1Report(
            summary=summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134PIAShareLimitHaltSideInputAvailabilityAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134PIAShareLimitHaltSideInputAvailabilityAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134pi_a_share_limit_halt_side_input_availability_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
