from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from a_share_quant.data.tushare_client import build_tushare_pro


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


def _load_symbols(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return sorted({str(row["symbol"]).strip() for row in rows if str(row.get("symbol", "")).strip()})


@dataclass(slots=True)
class V134PGAShareTushareLimitHaltSemanticSideInputsBootstrapV1Report:
    summary: dict[str, Any]
    output_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "output_rows": self.output_rows,
            "interpretation": self.interpretation,
        }


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134PGAShareTushareLimitHaltSemanticSideInputsBootstrapV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    pro = build_tushare_pro(repo_root=repo_root)

    universe_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
    symbols = _load_symbols(universe_path)
    symbol_set = set(symbols)

    start_date = "20240101"
    end_date = date.today().strftime("%Y%m%d")

    namechange_frame = pro.namechange(start_date=start_date, end_date=end_date)
    suspend_frame = pro.suspend_d(start_date=start_date, end_date=end_date)

    namechange_rows: list[dict[str, Any]] = []
    for record in namechange_frame.to_dict(orient="records") if namechange_frame is not None else []:
        ts_code = str(record.get("ts_code", "")).strip()
        symbol = ts_code.split(".", 1)[0] if ts_code else ""
        if symbol not in symbol_set:
            continue
        namechange_rows.append(
            {
                "symbol": symbol,
                "ts_code": ts_code,
                "name": record.get("name"),
                "start_date": str(record.get("start_date", "")),
                "end_date": str(record.get("end_date", "")),
                "ann_date": str(record.get("ann_date", "")),
                "change_reason": record.get("change_reason"),
            }
        )

    suspend_rows: list[dict[str, Any]] = []
    for record in suspend_frame.to_dict(orient="records") if suspend_frame is not None else []:
        ts_code = str(record.get("ts_code", "")).strip()
        symbol = ts_code.split(".", 1)[0] if ts_code else ""
        if symbol not in symbol_set:
            continue
        suspend_rows.append(
            {
                "symbol": symbol,
                "ts_code": ts_code,
                "trade_date": str(record.get("trade_date", "")),
                "suspend_timing": record.get("suspend_timing"),
                "suspend_type": record.get("suspend_type"),
            }
        )

    namechange_path = _write_csv(
        repo_root / "data" / "reference" / "namechange" / "tushare_commercial_aerospace_namechange_v1.csv",
        ["symbol", "ts_code", "name", "start_date", "end_date", "ann_date", "change_reason"],
        namechange_rows if namechange_rows else [],
    )
    suspend_path = _write_csv(
        repo_root / "data" / "reference" / "suspend_d" / "tushare_commercial_aerospace_suspend_d_v1.csv",
        ["symbol", "ts_code", "trade_date", "suspend_timing", "suspend_type"],
        suspend_rows if suspend_rows else [],
    )

    result = V134PGAShareTushareLimitHaltSemanticSideInputsBootstrapV1Report(
        summary={
            "provider": "tushare",
            "scope": "commercial_aerospace_universe",
            "symbol_count": len(symbols),
            "start_date": start_date,
            "end_date": end_date,
            "namechange_row_count": len(namechange_rows),
            "namechange_symbol_count": len({row["symbol"] for row in namechange_rows}),
            "suspend_row_count": len(suspend_rows),
            "suspend_symbol_count": len({row["symbol"] for row in suspend_rows}),
        },
        output_rows=[
            {"dataset": "namechange", "path": str(namechange_path), "row_count": len(namechange_rows)},
            {"dataset": "suspend_d", "path": str(suspend_path), "row_count": len(suspend_rows)},
        ],
        interpretation=[
            "This bootstrap adds the two semantic side-input families that are most relevant to replay-facing limit-halt derivation: name-change history and suspension records.",
            "These feeds do not by themselves complete replay promotion, but they convert ST/suspension from a vague future need into retained local source families.",
        ],
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134pg_a_share_tushare_limit_halt_semantic_side_inputs_bootstrap_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
