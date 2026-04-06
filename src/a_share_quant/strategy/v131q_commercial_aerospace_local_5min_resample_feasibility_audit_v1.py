from __future__ import annotations

import csv
import json
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v131h_commercial_aerospace_intraday_collection_manifest_v1 import (
    V131HCommercialAerospaceIntradayCollectionManifestAnalyzer,
)
from a_share_quant.strategy.v131o_commercial_aerospace_local_1min_archive_readiness_audit_v1 import (
    _symbol_to_archive_member,
)


def _read_member_lines(zip_path: Path, member_name: str) -> list[dict[str, str]]:
    with zipfile.ZipFile(zip_path) as archive:
        with archive.open(member_name, "r") as handle:
            decoded = (line.decode("utf-8-sig", errors="ignore") for line in handle)
            return list(csv.DictReader(decoded))


def _resample_to_5min(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    bars: dict[datetime, dict[str, Any]] = {}
    order: list[datetime] = []
    for row in rows:
        ts = datetime.strptime(row["时间"], "%Y/%m/%d %H:%M")
        bucket = ts.replace(minute=(ts.minute // 5) * 5)
        if bucket not in bars:
            bars[bucket] = {
                "bucket": bucket.strftime("%Y-%m-%d %H:%M"),
                "open": float(row["开盘价"]),
                "high": float(row["最高价"]),
                "low": float(row["最低价"]),
                "close": float(row["收盘价"]),
                "volume": float(row["成交量"]),
                "amount": float(row["成交额"]),
            }
            order.append(bucket)
            continue
        bar = bars[bucket]
        bar["high"] = max(bar["high"], float(row["最高价"]))
        bar["low"] = min(bar["low"], float(row["最低价"]))
        bar["close"] = float(row["收盘价"])
        bar["volume"] += float(row["成交量"])
        bar["amount"] += float(row["成交额"])
    return [bars[key] for key in sorted(order)]


@dataclass(slots=True)
class V131QCommercialAerospaceLocal5MinResampleFeasibilityAuditReport:
    summary: dict[str, Any]
    feasibility_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "feasibility_rows": self.feasibility_rows,
            "interpretation": self.interpretation,
        }


class V131QCommercialAerospaceLocal5MinResampleFeasibilityAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.monthly_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.output_csv = (
            repo_root / "data" / "raw" / "intraday_requests" / "commercial_aerospace_local_5min_resample_rows_v1.csv"
        )

    def analyze(self) -> V131QCommercialAerospaceLocal5MinResampleFeasibilityAuditReport:
        manifest = V131HCommercialAerospaceIntradayCollectionManifestAnalyzer(self.repo_root).analyze()
        feasibility_rows: list[dict[str, Any]] = []
        for row in manifest.manifest_rows:
            trade_date = row["execution_trade_date"]
            month_dir = self.monthly_root / f"{trade_date[:4]}-{trade_date[4:6]}"
            zip_path = month_dir / f"{trade_date}_1min.zip"
            member_name = _symbol_to_archive_member(row["symbol"])
            if not zip_path.exists():
                feasibility_rows.append(
                    {
                        **row,
                        "resample_status": "missing_zip",
                        "one_minute_row_count": 0,
                        "five_minute_row_count": 0,
                        "sample_5min_head": [],
                    }
                )
                continue
            rows_1m = _read_member_lines(zip_path, member_name)
            rows_5m = _resample_to_5min(rows_1m)
            feasibility_rows.append(
                {
                    **row,
                    "resample_status": "ready" if rows_5m else "empty_after_resample",
                    "one_minute_row_count": len(rows_1m),
                    "five_minute_row_count": len(rows_5m),
                    "sample_5min_head": rows_5m[:3],
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        flattened_rows: list[dict[str, Any]] = []
        for row in feasibility_rows:
            flat = dict(row)
            flat["sample_5min_head"] = json.dumps(flat.get("sample_5min_head", []), ensure_ascii=False)
            flattened_rows.append(flat)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=sorted({k for row in flattened_rows for k in row.keys()}))
            writer.writeheader()
            for row in flattened_rows:
                writer.writerow(row)

        ready_count = sum(1 for row in feasibility_rows if row["resample_status"] == "ready")
        summary = {
            "acceptance_posture": "freeze_v131q_commercial_aerospace_local_5min_resample_feasibility_audit_v1",
            "manifest_row_count": len(manifest.manifest_rows),
            "ready_count": ready_count,
            "local_5min_fully_ready": ready_count == len(feasibility_rows) and len(feasibility_rows) > 0,
            "feasibility_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "if the retained override sessions can be resampled from local 1min archives into clean 5min bars, the narrow commercial-aerospace 5min prototype can open without external provider dependence",
        }
        interpretation = [
            "V1.31Q tests whether the newly available local 1-minute archive can be turned into 5-minute bars for the exact retained override sessions.",
            "This bypasses Baostock and turns the commercial-aerospace 5-minute branch into a local-data question.",
        ]
        return V131QCommercialAerospaceLocal5MinResampleFeasibilityAuditReport(
            summary=summary,
            feasibility_rows=feasibility_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131QCommercialAerospaceLocal5MinResampleFeasibilityAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V131QCommercialAerospaceLocal5MinResampleFeasibilityAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131q_commercial_aerospace_local_5min_resample_feasibility_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
