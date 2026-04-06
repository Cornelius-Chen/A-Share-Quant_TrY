from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V131HCommercialAerospaceIntradayCollectionManifestReport:
    summary: dict[str, Any]
    manifest_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "manifest_rows": self.manifest_rows,
            "interpretation": self.interpretation,
        }


class V131HCommercialAerospaceIntradayCollectionManifestAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.failure_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_failure_library_v1.csv"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_collection_manifest_v1.csv"
        )

    @staticmethod
    def _load_csv(path: Path) -> list[dict[str, Any]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def analyze(self) -> V131HCommercialAerospaceIntradayCollectionManifestReport:
        failure_rows = self._load_csv(self.failure_csv)
        manifest_rows: list[dict[str, Any]] = []
        for row in failure_rows:
            if row["failure_type"] not in {"intraday_collapse_override_required", "intraday_reversal_watch"}:
                continue
            manifest_rows.append(
                {
                    "failure_id": row["failure_id"],
                    "symbol": row["symbol"],
                    "failure_type": row["failure_type"],
                    "signal_trade_date": row["signal_trade_date"],
                    "execution_trade_date": row["execution_trade_date"],
                    "required_session_window": f"{row['execution_trade_date']}_0930_1500",
                    "required_use_case": "intraday_override_supervision",
                    "minimum_fields": "open,high,low,close,volume,amount",
                    "priority": "high" if row["failure_type"] == "intraday_collapse_override_required" else "medium",
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        if manifest_rows:
            with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(manifest_rows[0].keys()))
                writer.writeheader()
                for row in manifest_rows:
                    writer.writerow(row)

        summary = {
            "acceptance_posture": "freeze_v131h_commercial_aerospace_intraday_collection_manifest_v1",
            "manifest_row_count": len(manifest_rows),
            "high_priority_count": sum(1 for row in manifest_rows if row["priority"] == "high"),
            "medium_priority_count": sum(1 for row in manifest_rows if row["priority"] == "medium"),
            "manifest_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "collect minute bars for retained override positives first, then reversal watches, before opening any commercial-aerospace intraday prototype",
        }
        interpretation = [
            "V1.31H turns the current failure library into a concrete minute-data collection manifest.",
            "It deliberately avoids broad universe expansion and instead prioritizes the exact sessions needed to study the retained override seeds.",
        ]
        return V131HCommercialAerospaceIntradayCollectionManifestReport(
            summary=summary,
            manifest_rows=manifest_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131HCommercialAerospaceIntradayCollectionManifestReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V131HCommercialAerospaceIntradayCollectionManifestAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131h_commercial_aerospace_intraday_collection_manifest_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
