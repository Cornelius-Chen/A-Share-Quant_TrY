from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _nonnull_count(rows: list[dict[str, str]], field: str) -> int:
    count = 0
    for row in rows:
        value = str(row.get(field, "")).strip()
        if value and value.lower() != "nan":
            count += 1
    return count


@dataclass(slots=True)
class V119CCpoTushareDatasetCoverageAuditReport:
    summary: dict[str, Any]
    field_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "field_rows": self.field_rows,
            "interpretation": self.interpretation,
        }


class V119CCpoTushareDatasetCoverageAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V119CCpoTushareDatasetCoverageAuditReport:
        daily_basic_rows = _read_csv_rows(
            self.repo_root / "data" / "reference" / "tushare_daily_basic" / "tushare_cpo_daily_basic_v1.csv"
        )
        moneyflow_rows = _read_csv_rows(
            self.repo_root / "data" / "raw" / "moneyflow" / "tushare_cpo_moneyflow_v1.csv"
        )
        stk_limit_rows = _read_csv_rows(
            self.repo_root / "data" / "reference" / "stk_limit" / "tushare_cpo_stk_limit_v1.csv"
        )

        checks = [
            ("daily_basic", daily_basic_rows, "turnover_rate"),
            ("daily_basic", daily_basic_rows, "turnover_rate_f"),
            ("daily_basic", daily_basic_rows, "float_share"),
            ("daily_basic", daily_basic_rows, "free_share"),
            ("daily_basic", daily_basic_rows, "total_mv"),
            ("daily_basic", daily_basic_rows, "circ_mv"),
            ("moneyflow", moneyflow_rows, "net_mf_amount"),
            ("moneyflow", moneyflow_rows, "buy_lg_amount"),
            ("moneyflow", moneyflow_rows, "sell_lg_amount"),
            ("stk_limit", stk_limit_rows, "up_limit"),
            ("stk_limit", stk_limit_rows, "down_limit"),
        ]
        field_rows: list[dict[str, Any]] = []
        for dataset, rows, field in checks:
            nonnull = _nonnull_count(rows, field)
            field_rows.append(
                {
                    "dataset": dataset,
                    "field": field,
                    "row_count": len(rows),
                    "nonnull_count": nonnull,
                    "coverage_ratio": round(nonnull / len(rows), 6) if rows else 0.0,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v119c_cpo_tushare_dataset_coverage_audit_v1",
            "daily_basic_row_count": len(daily_basic_rows),
            "moneyflow_row_count": len(moneyflow_rows),
            "stk_limit_row_count": len(stk_limit_rows),
            "critical_daily_basic_ready": all(
                row["coverage_ratio"] >= 0.99
                for row in field_rows
                if row["dataset"] == "daily_basic" and row["field"] in {"turnover_rate_f", "free_share", "circ_mv"}
            ),
            "critical_moneyflow_ready": all(
                row["coverage_ratio"] >= 0.99
                for row in field_rows
                if row["dataset"] == "moneyflow"
            ),
            "critical_stk_limit_ready": all(
                row["coverage_ratio"] >= 0.99
                for row in field_rows
                if row["dataset"] == "stk_limit"
            ),
            "recommended_next_posture": "replace_proxy_float_turnover_context_with_tushare_daily_basic_and_use_moneyflow_stk_limit_as_auxiliary_inputs",
        }
        interpretation = [
            "V1.19C audits whether the first Tushare-backed CPO datasets are clean enough to replace proxy free-float and turnover context.",
            "The highest-priority purpose is to harden free-float, turnover-rate, and price-limit references before further training or replay work.",
            "Moneyflow is treated as auxiliary context rather than a standalone branch input at this stage.",
        ]
        return V119CCpoTushareDatasetCoverageAuditReport(
            summary=summary,
            field_rows=field_rows,
            interpretation=interpretation,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V119CCpoTushareDatasetCoverageAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = repo_root / "reports" / "analysis" / "v119c_cpo_tushare_dataset_coverage_audit_v1.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
