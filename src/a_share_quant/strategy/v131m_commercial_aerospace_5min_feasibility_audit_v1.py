from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from a_share_quant.strategy.v115a_cpo_baostock_midfreq_intraday_audit_v1 import (
    _to_baostock_symbol,
)
from a_share_quant.strategy.v131h_commercial_aerospace_intraday_collection_manifest_v1 import (
    V131HCommercialAerospaceIntradayCollectionManifestAnalyzer,
)


def _default_fetch_baostock_5min(symbol: str, trade_date: str) -> dict[str, Any]:
    import baostock as bs

    bs_symbol = _to_baostock_symbol(symbol)
    query_date = datetime.strptime(trade_date, "%Y%m%d").strftime("%Y-%m-%d")
    login_result = bs.login()
    if str(login_result.error_code) != "0":
        raise RuntimeError(f"baostock_login_failed:{login_result.error_code}:{login_result.error_msg}")
    try:
        rs = bs.query_history_k_data_plus(
            bs_symbol,
            "date,time,code,open,high,low,close,volume,amount,adjustflag",
            start_date=query_date,
            end_date=query_date,
            frequency="5",
            adjustflag="2",
        )
        if str(rs.error_code) != "0":
            raise RuntimeError(f"baostock_query_failed:{rs.error_code}:{rs.error_msg}")
        rows = []
        while rs.next():
            rows.append(rs.get_row_data())
        return {
            "row_count": len(rows),
            "nonempty": len(rows) > 0,
            "sample_head": rows[:2],
            "sample_tail": rows[-2:] if rows else [],
        }
    finally:
        try:
            bs.logout()
        except Exception:
            pass


@dataclass(slots=True)
class V131MCommercialAerospace5MinFeasibilityAuditReport:
    summary: dict[str, Any]
    availability_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "availability_rows": self.availability_rows,
            "interpretation": self.interpretation,
        }


class V131MCommercialAerospace5MinFeasibilityAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root / "data" / "raw" / "intraday_requests" / "commercial_aerospace_5min_feasibility_rows_v1.csv"
        )

    def analyze(
        self,
        *,
        fetch_baostock_5min: Callable[[str, str], dict[str, Any]] = _default_fetch_baostock_5min,
    ) -> V131MCommercialAerospace5MinFeasibilityAuditReport:
        manifest = V131HCommercialAerospaceIntradayCollectionManifestAnalyzer(self.repo_root).analyze()
        availability_rows: list[dict[str, Any]] = []
        for row in manifest.manifest_rows:
            symbol = row["symbol"]
            trade_date = row["execution_trade_date"]
            try:
                fetched = fetch_baostock_5min(symbol, trade_date)
                availability_rows.append(
                    {
                        **row,
                        "provider": "baostock",
                        "frequency": "5",
                        "fetch_status": "success_nonempty" if bool(fetched.get("nonempty")) else "success_empty",
                        "row_count": int(fetched.get("row_count", 0)),
                        "sample_head": fetched.get("sample_head", []),
                        "sample_tail": fetched.get("sample_tail", []),
                    }
                )
            except Exception as exc:
                availability_rows.append(
                    {
                        **row,
                        "provider": "baostock",
                        "frequency": "5",
                        "fetch_status": "error",
                        "row_count": 0,
                        "sample_head": [],
                        "sample_tail": [],
                        "error_type": type(exc).__name__,
                        "error_message": str(exc),
                    }
                )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        flattened_rows: list[dict[str, Any]] = []
        for row in availability_rows:
            flat = dict(row)
            flat["sample_head"] = json.dumps(flat.get("sample_head", []), ensure_ascii=False)
            flat["sample_tail"] = json.dumps(flat.get("sample_tail", []), ensure_ascii=False)
            flattened_rows.append(flat)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=sorted({k for row in flattened_rows for k in row.keys()}))
            writer.writeheader()
            for row in flattened_rows:
                writer.writerow(row)

        success_nonempty = sum(1 for row in availability_rows if row["fetch_status"] == "success_nonempty")
        success_empty = sum(1 for row in availability_rows if row["fetch_status"] == "success_empty")
        error_count = sum(1 for row in availability_rows if row["fetch_status"] == "error")

        summary = {
            "acceptance_posture": "freeze_v131m_commercial_aerospace_5min_feasibility_audit_v1",
            "manifest_row_count": len(manifest.manifest_rows),
            "attempt_count": len(availability_rows),
            "success_nonempty_count": success_nonempty,
            "success_empty_count": success_empty,
            "error_count": error_count,
            "five_min_partially_ready": success_nonempty > 0,
            "five_min_fully_ready": success_nonempty == len(availability_rows) and len(availability_rows) > 0,
            "availability_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "use 5min only if the retained override manifest has nonempty local or backfillable support; otherwise keep intraday modeling blocked",
        }
        interpretation = [
            "V1.31M directly tests whether the current commercial-aerospace override manifest can be backfilled with Baostock 5-minute bars.",
            "This is narrower than generic intraday expansion: it only checks the exact high-value failure sessions already retained by governance.",
        ]
        return V131MCommercialAerospace5MinFeasibilityAuditReport(
            summary=summary,
            availability_rows=availability_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131MCommercialAerospace5MinFeasibilityAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V131MCommercialAerospace5MinFeasibilityAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131m_commercial_aerospace_5min_feasibility_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
