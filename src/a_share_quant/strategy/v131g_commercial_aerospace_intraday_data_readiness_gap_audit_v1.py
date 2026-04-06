from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V131GCommercialAerospaceIntradayDataReadinessGapAuditReport:
    summary: dict[str, Any]
    symbol_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "symbol_rows": self.symbol_rows,
            "interpretation": self.interpretation,
        }


class V131GCommercialAerospaceIntradayDataReadinessGapAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.failure_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_failure_library_v1.csv"
        )
        self.orders_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_tail_weakdrift_full_orders_v1.csv"
        )
        self.minute_dir = repo_root / "data" / "raw" / "minute_bars"

    @staticmethod
    def _load_csv(path: Path) -> list[dict[str, Any]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def analyze(self) -> V131GCommercialAerospaceIntradayDataReadinessGapAuditReport:
        failure_rows = self._load_csv(self.failure_csv)
        order_rows = self._load_csv(self.orders_csv)

        traded_symbols = sorted({row["symbol"] for row in order_rows})
        retained_override_symbols = sorted(
            {
                row["symbol"]
                for row in failure_rows
                if row["failure_type"] == "intraday_collapse_override_required"
            }
        )
        reversal_watch_symbols = sorted(
            {row["symbol"] for row in failure_rows if row["failure_type"] == "intraday_reversal_watch"}
        )
        required_symbols = sorted(set(retained_override_symbols) | set(reversal_watch_symbols))

        minute_files = {path.name: path for path in self.minute_dir.glob("*.csv")} if self.minute_dir.exists() else {}
        symbol_rows: list[dict[str, Any]] = []
        for symbol in required_symbols:
            file_matches = [name for name in minute_files if symbol in name]
            symbol_rows.append(
                {
                    "symbol": symbol,
                    "required_role": (
                        "override_positive"
                        if symbol in retained_override_symbols
                        else "reversal_watch"
                    ),
                    "minute_support_present": bool(file_matches),
                    "minute_file_count": len(file_matches),
                    "minute_files": " | ".join(sorted(file_matches)),
                }
            )

        missing_required_symbols = [row["symbol"] for row in symbol_rows if not row["minute_support_present"]]
        summary = {
            "acceptance_posture": "freeze_v131g_commercial_aerospace_intraday_data_readiness_gap_audit_v1",
            "traded_symbol_count_in_primary": len(traded_symbols),
            "retained_override_symbol_count": len(retained_override_symbols),
            "reversal_watch_symbol_count": len(reversal_watch_symbols),
            "required_intraday_symbol_count": len(required_symbols),
            "required_intraday_symbol_coverage_rate": round(
                sum(1 for row in symbol_rows if row["minute_support_present"]) / len(symbol_rows), 8
            )
            if symbol_rows
            else 0.0,
            "missing_required_symbol_count": len(missing_required_symbols),
            "missing_required_symbols": missing_required_symbols,
            "authoritative_rule": "do_not_start_commercial_aerospace_minute_level_override_modeling_until_required_failure-seed symbols have local minute-bar support",
        }
        interpretation = [
            "V1.31G audits whether the commercial-aerospace intraday-override supervision bundle has the local minute-bar support needed for any lawful next-step intraday work.",
            "The audit is intentionally narrow: it only checks the retained override positives and reversal watches, because those are the current future supervision seeds.",
        ]
        return V131GCommercialAerospaceIntradayDataReadinessGapAuditReport(
            summary=summary,
            symbol_rows=symbol_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131GCommercialAerospaceIntradayDataReadinessGapAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V131GCommercialAerospaceIntradayDataReadinessGapAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131g_commercial_aerospace_intraday_data_readiness_gap_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
