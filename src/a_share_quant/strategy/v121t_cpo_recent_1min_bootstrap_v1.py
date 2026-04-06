from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import akshare as ak


SYMBOL_MAP = {
    "300308": "sz300308",
    "300502": "sz300502",
    "300757": "sz300757",
    "688498": "sh688498",
}


@dataclass(slots=True)
class V121TCpoRecent1MinBootstrapReport:
    summary: dict[str, Any]
    symbol_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "symbol_rows": self.symbol_rows,
            "interpretation": self.interpretation,
        }


class V121TCpoRecent1MinBootstrapAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V121TCpoRecent1MinBootstrapReport:
        minute_dir = self.repo_root / "data" / "raw" / "minute_bars"
        minute_dir.mkdir(parents=True, exist_ok=True)

        symbol_rows: list[dict[str, Any]] = []
        total_rows = 0
        for symbol, ak_symbol in SYMBOL_MAP.items():
            df = ak.stock_zh_a_minute(symbol=ak_symbol, period="1", adjust="")
            records = df.to_dict("records")
            output_path = minute_dir / f"sina_{symbol}_recent_1min_v1.csv"
            with output_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["day", "open", "high", "low", "close", "volume", "amount"])
                writer.writeheader()
                for record in records:
                    writer.writerow(record)
            total_rows += len(records)
            symbol_rows.append(
                {
                    "symbol": symbol,
                    "source_symbol": ak_symbol,
                    "row_count": len(records),
                    "start_time": records[0]["day"] if records else "",
                    "end_time": records[-1]["day"] if records else "",
                    "output_path": str(output_path.relative_to(self.repo_root)),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v121t_cpo_recent_1min_bootstrap_v1",
            "symbol_count": len(symbol_rows),
            "total_row_count": total_rows,
            "data_plane_status": "recent_1min_live_for_core_cpo_names",
            "recommended_next_posture": "derive_1min_microstructure_features_and_action_timepoint_views",
        }
        interpretation = [
            "V1.21T proves the project can now pull recent rolling 1-minute bars for the core CPO names.",
            "This is not a full historical minute archive, but it is enough to start the 1-minute data plane instead of talking about it abstractly.",
            "The next useful step is to derive microstructure features and align them to action-timepoint views.",
        ]
        return V121TCpoRecent1MinBootstrapReport(
            summary=summary,
            symbol_rows=symbol_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V121TCpoRecent1MinBootstrapReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V121TCpoRecent1MinBootstrapAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v121t_cpo_recent_1min_bootstrap_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
