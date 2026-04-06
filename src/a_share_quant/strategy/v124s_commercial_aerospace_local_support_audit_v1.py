from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V124SCommercialAerospaceLocalSupportAuditReport:
    summary: dict[str, Any]
    supported_rows: list[dict[str, Any]]
    unsupported_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "supported_rows": self.supported_rows,
            "unsupported_rows": self.unsupported_rows,
            "interpretation": self.interpretation,
        }


class V124SCommercialAerospaceLocalSupportAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.universe_path = repo_root / "data" / "training" / "commercial_aerospace_merged_universe_v1.csv"
        self.daily_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
        self.daily_basic_path = repo_root / "data" / "reference" / "tushare_daily_basic" / "tushare_commercial_aerospace_daily_basic_v1.csv"
        self.moneyflow_path = repo_root / "data" / "raw" / "moneyflow" / "tushare_commercial_aerospace_moneyflow_v1.csv"
        self.stk_limit_path = repo_root / "data" / "reference" / "stk_limit" / "tushare_commercial_aerospace_stk_limit_v1.csv"

    def analyze(self) -> V124SCommercialAerospaceLocalSupportAuditReport:
        universe_rows = _load_csv(self.universe_path)
        daily_rows = _load_csv(self.daily_path)
        daily_basic_rows = _load_csv(self.daily_basic_path)
        moneyflow_rows = _load_csv(self.moneyflow_path)
        stk_limit_rows = _load_csv(self.stk_limit_path)

        support = {row["symbol"]: {"daily": 0, "daily_basic": 0, "moneyflow": 0, "stk_limit": 0} for row in universe_rows}
        for row in daily_rows:
            if row["symbol"] in support:
                support[row["symbol"]]["daily"] += 1
        for row in daily_basic_rows:
            if row["symbol"] in support:
                support[row["symbol"]]["daily_basic"] += 1
        for row in moneyflow_rows:
            if row["symbol"] in support:
                support[row["symbol"]]["moneyflow"] += 1
        for row in stk_limit_rows:
            if row["symbol"] in support:
                support[row["symbol"]]["stk_limit"] += 1

        supported_rows: list[dict[str, Any]] = []
        unsupported_rows: list[dict[str, Any]] = []
        for row in universe_rows:
            counts = support[row["symbol"]]
            result_row = {
                "symbol": row["symbol"],
                "name": row["name"],
                "group": row["group"],
                "subgroup": row["subgroup"],
                "confidence": row["confidence"],
                "daily_rows": counts["daily"],
                "daily_basic_rows": counts["daily_basic"],
                "moneyflow_rows": counts["moneyflow"],
                "stk_limit_rows": counts["stk_limit"],
                "fully_supported": all(counts[k] > 0 for k in counts),
            }
            if result_row["fully_supported"]:
                supported_rows.append(result_row)
            else:
                unsupported_rows.append(result_row)

        supported_rows.sort(key=lambda r: (r["group"], r["symbol"]))
        unsupported_rows.sort(key=lambda r: (r["group"], r["symbol"]))

        summary = {
            "acceptance_posture": "freeze_v124s_commercial_aerospace_local_support_audit_v1",
            "merged_universe_count": len(universe_rows),
            "fully_supported_count": len(supported_rows),
            "unsupported_count": len(unsupported_rows),
            "support_ratio": round(len(supported_rows) / max(len(universe_rows), 1), 6),
            "authoritative_rule": "only_fully_supported_symbols_may_enter_refreshed_machine_triage",
        }
        interpretation = [
            "V1.24S audits whether the merged commercial aerospace universe has actually crossed from web concept membership into local machine-readable support.",
            "The goal is to stop confusing a wide universe list with a lawful research surface.",
            "Symbols lacking any one of daily bars, daily_basic, moneyflow, or stk_limit remain outside refreshed machine triage.",
        ]
        return V124SCommercialAerospaceLocalSupportAuditReport(
            summary=summary,
            supported_rows=supported_rows,
            unsupported_rows=unsupported_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V124SCommercialAerospaceLocalSupportAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V124SCommercialAerospaceLocalSupportAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124s_commercial_aerospace_local_support_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
