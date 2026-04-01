from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


os.environ.setdefault("PANDAS_NO_USE_NUMEXPR", "1")
os.environ.setdefault("PANDAS_NO_USE_BOTTLENECK", "1")


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


def _default_fetch_intraday(symbol: str, trade_date: str) -> dict[str, Any]:
    import akshare as ak

    start = f"{trade_date} 09:25:00"
    end = f"{trade_date} 15:00:00"
    frame = ak.stock_zh_a_hist_min_em(symbol=symbol, period="1", start_date=start, end_date=end, adjust="qfq")
    return {
        "row_count": int(len(frame)),
        "columns": list(frame.columns.astype(str)),
        "nonempty": int(len(frame)) > 0,
    }


@dataclass(slots=True)
class V114ZCpoIntradayKeyWindowAvailabilityAuditReport:
    summary: dict[str, Any]
    manifest_rows: list[dict[str, Any]]
    availability_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "manifest_rows": self.manifest_rows,
            "availability_rows": self.availability_rows,
            "interpretation": self.interpretation,
        }


class V114ZCpoIntradayKeyWindowAvailabilityAuditAnalyzer:
    ROLE_TO_SYMBOL = {
        "core_module_leader": "300308",
        "high_beta_core_module": "300502",
        "packaging_process_enabler": "300757",
        "laser_chip_component": "688498",
    }

    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _build_manifest(self, v113n_payload: dict[str, Any]) -> list[dict[str, Any]]:
        rows = list(v113n_payload.get("internal_point_rows", []))
        manifest_rows: list[dict[str, Any]] = []
        for row in rows:
            object_id = str(row.get("object_id", "")).strip()
            symbol = self.ROLE_TO_SYMBOL.get(object_id)
            if not symbol:
                continue
            trade_date = str(row.get("trade_date", "")).strip()
            if not trade_date:
                continue
            manifest_rows.append(
                {
                    "symbol": symbol,
                    "trade_date": trade_date,
                    "window_start": f"{trade_date} 09:25:00",
                    "window_end": f"{trade_date} 15:00:00",
                    "role_family": object_id,
                    "control_label": row.get("control_label_assistant"),
                    "board_phase": row.get("board_phase_label_owner"),
                    "reason": f"{object_id}:{row.get('control_label_assistant')}",
                }
            )
        manifest_rows.sort(key=lambda row: (str(row["trade_date"]), str(row["symbol"])))
        return manifest_rows

    def analyze(
        self,
        *,
        v113n_payload: dict[str, Any],
        fetch_intraday: Callable[[str, str], dict[str, Any]] = _default_fetch_intraday,
    ) -> V114ZCpoIntradayKeyWindowAvailabilityAuditReport:
        manifest_rows = self._build_manifest(v113n_payload)
        if not manifest_rows:
            raise ValueError("V114Z requires key windows from V113N internal point rows.")

        availability_rows: list[dict[str, Any]] = []
        for row in manifest_rows:
            symbol = str(row["symbol"])
            trade_date = str(row["trade_date"])
            try:
                fetched = fetch_intraday(symbol, trade_date)
                availability_rows.append(
                    {
                        **row,
                        "fetch_status": "success_nonempty" if bool(fetched.get("nonempty")) else "success_empty",
                        "row_count": int(fetched.get("row_count", 0)),
                        "columns": fetched.get("columns", []),
                    }
                )
            except Exception as exc:  # pragma: no cover - exercised in real run
                availability_rows.append(
                    {
                        **row,
                        "fetch_status": "error",
                        "row_count": 0,
                        "columns": [],
                        "error_type": type(exc).__name__,
                        "error_message": str(exc),
                    }
                )

        success_nonempty = sum(1 for row in availability_rows if row["fetch_status"] == "success_nonempty")
        success_empty = sum(1 for row in availability_rows if row["fetch_status"] == "success_empty")
        error_count = sum(1 for row in availability_rows if row["fetch_status"] == "error")

        summary = {
            "acceptance_posture": "freeze_v114z_cpo_intraday_key_window_availability_audit_v1",
            "board_name": "CPO",
            "focus_symbol_count": len({row["symbol"] for row in manifest_rows}),
            "key_window_count": len(manifest_rows),
            "success_nonempty_count": success_nonempty,
            "success_empty_count": success_empty,
            "error_count": error_count,
            "historical_intraday_provider_ready_now": success_nonempty == len(manifest_rows),
            "recommended_next_posture": "treat_manifest_as_collection_backlog_and_do_not_claim_intraday_replay_ready_until_historical_windows_are_nonempty",
        }

        interpretation = [
            "V1.14Z turns the vague 'we need intraday data' statement into a concrete key-window manifest for the four mature CPO action objects.",
            "The audit is deliberately harsh: a historical provider only counts as ready if the requested key windows return non-empty minute bars for the actual CPO decision dates.",
            "This means V1.14Z can cleanly separate two questions: what windows we need, and whether the current provider can really deliver them.",
        ]

        return V114ZCpoIntradayKeyWindowAvailabilityAuditReport(
            summary=summary,
            manifest_rows=manifest_rows,
            availability_rows=availability_rows,
            interpretation=interpretation,
        )


def write_csv_rows(*, path: Path, rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def write_report(*, reports_dir: Path, report_name: str, result: V114ZCpoIntradayKeyWindowAvailabilityAuditReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V114ZCpoIntradayKeyWindowAvailabilityAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113n_payload=load_json_report(repo_root / "reports/analysis/v113n_cpo_real_board_episode_population_v1.json"),
    )
    write_csv_rows(
        path=repo_root / "data/raw/intraday_requests/cpo_intraday_key_window_manifest_v1.csv",
        rows=result.manifest_rows,
    )
    write_csv_rows(
        path=repo_root / "data/raw/intraday_requests/cpo_intraday_key_window_availability_v1.csv",
        rows=result.availability_rows,
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v114z_cpo_intraday_key_window_availability_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
