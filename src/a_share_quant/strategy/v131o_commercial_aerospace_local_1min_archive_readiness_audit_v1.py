from __future__ import annotations

import csv
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v131h_commercial_aerospace_intraday_collection_manifest_v1 import (
    V131HCommercialAerospaceIntradayCollectionManifestAnalyzer,
)


def _symbol_to_archive_member(symbol: str) -> str:
    if symbol.startswith("6"):
        return f"sh{symbol}.csv"
    if symbol.startswith(("0", "3")):
        return f"sz{symbol}.csv"
    if symbol.startswith(("4", "8")):
        return f"bj{symbol}.csv"
    return f"{symbol}.csv"


@dataclass(slots=True)
class V131OCommercialAerospaceLocal1MinArchiveReadinessAuditReport:
    summary: dict[str, Any]
    readiness_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "readiness_rows": self.readiness_rows,
            "interpretation": self.interpretation,
        }


class V131OCommercialAerospaceLocal1MinArchiveReadinessAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.monthly_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.output_csv = (
            repo_root / "data" / "raw" / "intraday_requests" / "commercial_aerospace_local_1min_readiness_rows_v1.csv"
        )

    def analyze(self) -> V131OCommercialAerospaceLocal1MinArchiveReadinessAuditReport:
        manifest = V131HCommercialAerospaceIntradayCollectionManifestAnalyzer(self.repo_root).analyze()
        readiness_rows: list[dict[str, Any]] = []
        for row in manifest.manifest_rows:
            trade_date = row["execution_trade_date"]
            month_dir = self.monthly_root / f"{trade_date[:4]}-{trade_date[4:6]}"
            zip_name = f"{trade_date}_1min.zip"
            zip_path = month_dir / zip_name
            archive_member = _symbol_to_archive_member(row["symbol"])
            status = "missing_zip"
            sample_head: list[str] = []
            minute_row_count = 0
            if zip_path.exists():
                status = "zip_present_symbol_missing"
                with zipfile.ZipFile(zip_path) as handle:
                    if archive_member in handle.namelist():
                        status = "ready"
                        with handle.open(archive_member, "r") as member:
                            decoded = (
                                line.decode("utf-8-sig", errors="ignore").rstrip("\r\n")
                                for line in member
                            )
                            sample_head = []
                            for idx, line in enumerate(decoded):
                                if idx < 3:
                                    sample_head.append(line)
                                if idx > 0:
                                    minute_row_count += 1
            readiness_rows.append(
                {
                    **row,
                    "month_dir": str(month_dir.relative_to(self.repo_root)),
                    "zip_name": zip_name,
                    "archive_member": archive_member,
                    "zip_exists": zip_path.exists(),
                    "readiness_status": status,
                    "minute_row_count": minute_row_count,
                    "sample_head": sample_head,
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        flattened_rows: list[dict[str, Any]] = []
        for row in readiness_rows:
            flat = dict(row)
            flat["sample_head"] = json.dumps(flat.get("sample_head", []), ensure_ascii=False)
            flattened_rows.append(flat)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=sorted({k for row in flattened_rows for k in row.keys()}))
            writer.writeheader()
            for row in flattened_rows:
                writer.writerow(row)

        ready_count = sum(1 for row in readiness_rows if row["readiness_status"] == "ready")
        summary = {
            "acceptance_posture": "freeze_v131o_commercial_aerospace_local_1min_archive_readiness_audit_v1",
            "manifest_row_count": len(manifest.manifest_rows),
            "ready_count": ready_count,
            "missing_zip_count": sum(1 for row in readiness_rows if row["readiness_status"] == "missing_zip"),
            "symbol_missing_count": sum(
                1 for row in readiness_rows if row["readiness_status"] == "zip_present_symbol_missing"
            ),
            "local_1min_fully_ready": ready_count == len(readiness_rows) and len(readiness_rows) > 0,
            "readiness_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "once the exact retained override sessions are locally present in 1min archives, intraday modeling no longer depends on external providers for those sessions",
        }
        interpretation = [
            "V1.31O checks the new local 1-minute monthly archive against the exact commercial-aerospace retained override manifest.",
            "It is intentionally narrow: the question is not broad intraday completeness, but whether the governance-retained failure sessions are now locally covered end to end.",
        ]
        return V131OCommercialAerospaceLocal1MinArchiveReadinessAuditReport(
            summary=summary,
            readiness_rows=readiness_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131OCommercialAerospaceLocal1MinArchiveReadinessAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V131OCommercialAerospaceLocal1MinArchiveReadinessAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131o_commercial_aerospace_local_1min_archive_readiness_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
