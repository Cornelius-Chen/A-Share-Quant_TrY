from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


def _to_baostock_symbol(symbol: str) -> str:
    symbol = str(symbol).strip()
    if symbol.startswith(("600", "601", "603", "605", "688", "689", "900")):
        return f"sh.{symbol}"
    return f"sz.{symbol}"


def _default_fetch_baostock(symbol: str, trade_date: str, frequency: str) -> dict[str, Any]:
    import baostock as bs

    bs_symbol = _to_baostock_symbol(symbol)
    login_result = bs.login()
    if str(login_result.error_code) != "0":
        raise RuntimeError(f"baostock_login_failed:{login_result.error_code}:{login_result.error_msg}")
    try:
        rs = bs.query_history_k_data_plus(
            bs_symbol,
            "date,time,code,open,high,low,close,volume,amount,adjustflag",
            start_date=trade_date,
            end_date=trade_date,
            frequency=frequency,
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
class V115ACpoBaostockMidfreqIntradayAuditReport:
    summary: dict[str, Any]
    availability_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "availability_rows": self.availability_rows,
            "interpretation": self.interpretation,
        }


class V115ACpoBaostockMidfreqIntradayAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v114z_payload: dict[str, Any],
        fetch_baostock: Callable[[str, str, str], dict[str, Any]] = _default_fetch_baostock,
        frequencies: tuple[str, ...] = ("5", "15", "30", "60"),
    ) -> V115ACpoBaostockMidfreqIntradayAuditReport:
        manifest_rows = list(v114z_payload.get("manifest_rows", []))
        if not manifest_rows:
            raise ValueError("V115A requires V114Z manifest rows.")

        availability_rows: list[dict[str, Any]] = []
        for manifest in manifest_rows:
            symbol = str(manifest["symbol"])
            trade_date = str(manifest["trade_date"])
            for frequency in frequencies:
                try:
                    fetched = fetch_baostock(symbol, trade_date, frequency)
                    availability_rows.append(
                        {
                            **manifest,
                            "frequency": frequency,
                            "provider": "baostock",
                            "fetch_status": "success_nonempty" if bool(fetched.get("nonempty")) else "success_empty",
                            "row_count": int(fetched.get("row_count", 0)),
                            "sample_head": fetched.get("sample_head", []),
                            "sample_tail": fetched.get("sample_tail", []),
                        }
                    )
                except Exception as exc:  # pragma: no cover - exercised in real run
                    availability_rows.append(
                        {
                            **manifest,
                            "frequency": frequency,
                            "provider": "baostock",
                            "fetch_status": "error",
                            "row_count": 0,
                            "sample_head": [],
                            "sample_tail": [],
                            "error_type": type(exc).__name__,
                            "error_message": str(exc),
                        }
                    )

        success_nonempty = sum(1 for row in availability_rows if row["fetch_status"] == "success_nonempty")
        success_empty = sum(1 for row in availability_rows if row["fetch_status"] == "success_empty")
        error_count = sum(1 for row in availability_rows if row["fetch_status"] == "error")
        total_count = len(availability_rows)

        summary = {
            "acceptance_posture": "freeze_v115a_cpo_baostock_midfreq_intraday_audit_v1",
            "board_name": "CPO",
            "provider": "baostock",
            "frequency_set": list(frequencies),
            "manifest_window_count": len(manifest_rows),
            "attempt_count": total_count,
            "success_nonempty_count": success_nonempty,
            "success_empty_count": success_empty,
            "error_count": error_count,
            "midfreq_historical_intraday_partially_ready": success_nonempty > 0,
            "midfreq_historical_intraday_fully_ready": success_nonempty == total_count,
            "recommended_next_posture": "use_baostock_as_the_first_historical_midfreq_backfill_source_and_separate_midfreq_success_from_1min_backfill_gap",
        }

        interpretation = [
            "V1.15A upgrades the intraday discussion from 'the current minute provider failed' to a cleaner split: near-term minute collection can use Sina, while historical mid-frequency backfill can be audited against Baostock.",
            "This is exactly the right compromise for the current objective: strengthen add/reduce confirmation for diffusion-style main-uptrend boards without pretending long-history 1-minute replay is already solved.",
            "Baostock mid-frequency success does not eliminate the later need for true 1-minute archives, but it is enough to materially improve confirmation studies before that final layer arrives.",
        ]

        return V115ACpoBaostockMidfreqIntradayAuditReport(
            summary=summary,
            availability_rows=availability_rows,
            interpretation=interpretation,
        )


def write_csv_rows(*, path: Path, rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    flattened_rows: list[dict[str, Any]] = []
    for row in rows:
        flat = dict(row)
        flat["sample_head"] = json.dumps(flat.get("sample_head", []), ensure_ascii=False)
        flat["sample_tail"] = json.dumps(flat.get("sample_tail", []), ensure_ascii=False)
        flattened_rows.append(flat)
    fieldnames = sorted({key for row in flattened_rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in flattened_rows:
            writer.writerow(row)
    return path


def write_report(*, reports_dir: Path, report_name: str, result: V115ACpoBaostockMidfreqIntradayAuditReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V115ACpoBaostockMidfreqIntradayAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v114z_payload=load_json_report(repo_root / "reports/analysis/v114z_cpo_intraday_key_window_availability_audit_v1.json"),
    )
    write_csv_rows(
        path=repo_root / "data/raw/intraday_requests/cpo_baostock_midfreq_availability_v1.csv",
        rows=result.availability_rows,
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v115a_cpo_baostock_midfreq_intraday_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
