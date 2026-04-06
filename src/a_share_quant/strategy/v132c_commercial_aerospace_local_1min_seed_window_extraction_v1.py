from __future__ import annotations

import csv
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _symbol_to_archive_member(symbol: str) -> str:
    if symbol.startswith("6"):
        return f"sh{symbol}.csv"
    if symbol.startswith(("0", "3")):
        return f"sz{symbol}.csv"
    if symbol.startswith(("4", "8")):
        return f"bj{symbol}.csv"
    return f"{symbol}.csv"


@dataclass(slots=True)
class V132CCommercialAerospaceLocal1MinSeedWindowExtractionReport:
    summary: dict[str, Any]
    session_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "session_rows": self.session_rows,
            "interpretation": self.interpretation,
        }


class V132CCommercialAerospaceLocal1MinSeedWindowExtractionAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.registry_report_path = (
            repo_root / "reports" / "analysis" / "v131y_commercial_aerospace_intraday_supervision_registry_v1.json"
        )
        self.monthly_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_local_1min_seed_windows_v1.csv"
        )

    def analyze(self) -> V132CCommercialAerospaceLocal1MinSeedWindowExtractionReport:
        registry = json.loads(self.registry_report_path.read_text(encoding="utf-8"))
        registry_rows = registry["registry_rows"]

        session_rows: list[dict[str, Any]] = []
        for registry_row in registry_rows:
            trade_date = registry_row["execution_trade_date"]
            symbol = registry_row["symbol"]
            zip_path = self.monthly_root / f"{trade_date[:4]}-{trade_date[4:6]}" / f"{trade_date}_1min.zip"
            member_name = _symbol_to_archive_member(symbol)
            with zipfile.ZipFile(zip_path) as archive:
                with archive.open(member_name, "r") as member:
                    minute_rows = list(csv.reader(line.decode("utf-8-sig", errors="ignore") for line in member))[1:]

            first_60 = minute_rows[:60]
            for minute_index, row in enumerate(first_60, start=1):
                session_rows.append(
                    {
                        "signal_trade_date": registry_row["signal_trade_date"],
                        "execution_trade_date": trade_date,
                        "symbol": symbol,
                        "severity_tier": registry_row["severity_tier"],
                        "supervision_label": registry_row["supervision_label"],
                        "minute_index": minute_index,
                        "timestamp": row[0],
                        "open": float(row[3]),
                        "close": float(row[4]),
                        "high": float(row[5]),
                        "low": float(row[6]),
                        "volume": float(row[7]),
                        "amount": float(row[8]),
                    }
                )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(session_rows[0].keys()))
            writer.writeheader()
            writer.writerows(session_rows)

        summary = {
            "acceptance_posture": "freeze_v132c_commercial_aerospace_local_1min_seed_window_extraction_v1",
            "registry_session_count": len(registry_rows),
            "seed_window_row_count": len(session_rows),
            "minutes_per_session": 60,
            "output_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "the commercial-aerospace minute branch should now work off explicit local 1-minute seed windows rather than scattered case anecdotes",
        }
        interpretation = [
            "V1.32C materializes the frozen intraday supervision registry into local one-minute seed windows.",
            "This is the first direct handoff object for later minute-pattern envelope work because every retained seed is now represented as a uniform first-hour 1-minute sequence.",
        ]
        return V132CCommercialAerospaceLocal1MinSeedWindowExtractionReport(
            summary=summary,
            session_rows=session_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132CCommercialAerospaceLocal1MinSeedWindowExtractionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132CCommercialAerospaceLocal1MinSeedWindowExtractionAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132c_commercial_aerospace_local_1min_seed_window_extraction_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
