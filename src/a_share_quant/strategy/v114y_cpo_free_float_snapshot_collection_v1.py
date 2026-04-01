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


def _default_fetch_symbol_snapshot(symbol: str) -> dict[str, Any]:
    import akshare as ak

    frame = ak.stock_individual_info_em(symbol=symbol)
    mapping: dict[str, Any] = {}
    for row in frame.to_dict(orient="records"):
        item = str(row.get("item", "")).strip()
        if not item:
            continue
        mapping[item] = row.get("value")
    return mapping


@dataclass(slots=True)
class V114YCpoFreeFloatSnapshotCollectionReport:
    summary: dict[str, Any]
    collected_rows: list[dict[str, Any]]
    failure_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "collected_rows": self.collected_rows,
            "failure_rows": self.failure_rows,
            "interpretation": self.interpretation,
        }


class V114YCpoFreeFloatSnapshotCollectionAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    @staticmethod
    def _extract_symbols(v112aa_payload: dict[str, Any]) -> list[str]:
        rows = list(v112aa_payload.get("object_role_time_rows", []))
        symbols = sorted({str(row.get("symbol", "")).strip() for row in rows if str(row.get("symbol", "")).strip()})
        if not symbols:
            raise ValueError("V114Y requires symbols from V112AA bounded cohort map.")
        return symbols

    @staticmethod
    def _safe_float(value: Any) -> float | None:
        if value in (None, ""):
            return None
        try:
            return float(str(value).replace(",", ""))
        except (TypeError, ValueError):
            return None

    def analyze(
        self,
        *,
        v112aa_payload: dict[str, Any],
        fetch_symbol_snapshot: Callable[[str], dict[str, Any]] = _default_fetch_symbol_snapshot,
    ) -> V114YCpoFreeFloatSnapshotCollectionReport:
        symbols = self._extract_symbols(v112aa_payload)
        collected_rows: list[dict[str, Any]] = []
        failure_rows: list[dict[str, Any]] = []

        for symbol in symbols:
            try:
                snapshot = fetch_symbol_snapshot(symbol)
                total_shares = self._safe_float(snapshot.get("总股本"))
                float_shares = self._safe_float(snapshot.get("流通股"))
                total_market_cap = self._safe_float(snapshot.get("总市值"))
                free_float_market_cap = self._safe_float(snapshot.get("流通市值"))
                collected_rows.append(
                    {
                        "symbol": symbol,
                        "name": snapshot.get("股票简称"),
                        "industry": snapshot.get("行业"),
                        "latest_price": self._safe_float(snapshot.get("最新")),
                        "total_shares": total_shares,
                        "float_shares": float_shares,
                        "total_market_cap": total_market_cap,
                        "free_float_market_cap": free_float_market_cap,
                        "float_ratio": None if total_shares in (None, 0) or float_shares is None else round(float_shares / total_shares, 6),
                        "snapshot_source": "akshare.stock_individual_info_em",
                    }
                )
            except Exception as exc:  # pragma: no cover - exercised in real run
                failure_rows.append(
                    {
                        "symbol": symbol,
                        "error_type": type(exc).__name__,
                        "error_message": str(exc),
                    }
                )

        collected_rows.sort(key=lambda row: str(row["symbol"]))
        failure_rows.sort(key=lambda row: str(row["symbol"]))

        summary = {
            "acceptance_posture": "freeze_v114y_cpo_free_float_snapshot_collection_v1",
            "board_name": "CPO",
            "cohort_symbol_count": len(symbols),
            "collected_symbol_count": len(collected_rows),
            "failed_symbol_count": len(failure_rows),
            "has_current_float_shares_snapshot": len(collected_rows) == len(symbols),
            "has_current_free_float_market_cap_snapshot": all(row.get("free_float_market_cap") is not None for row in collected_rows),
            "historical_float_time_series_ready_now": False,
            "snapshot_use_boundary": "current_snapshot_only_not_historical_truth_surface",
            "recommended_next_posture": "use_snapshot_to_replace_proxy_flags_where_current_only_is_acceptable_but_do_not_treat_it_as_historical_turnover_rate_series",
        }

        interpretation = [
            "V1.14Y converts the old market-cap proxy problem into a narrower truth: current float-share and free-float-market-cap snapshots can be collected for the whole CPO cohort.",
            "This is useful for current state audits and later intraday turnover-rate normalization, but it does not solve historical float-time-series accuracy by itself.",
            "So V1.14Y is a real data upgrade, not a full historical repair. It should replace blind proxy assumptions where snapshot-level truth is acceptable, but not masquerade as point-in-time historical float truth.",
        ]

        return V114YCpoFreeFloatSnapshotCollectionReport(
            summary=summary,
            collected_rows=collected_rows,
            failure_rows=failure_rows,
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


def write_report(*, reports_dir: Path, report_name: str, result: V114YCpoFreeFloatSnapshotCollectionReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V114YCpoFreeFloatSnapshotCollectionAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v112aa_payload=load_json_report(repo_root / "reports/analysis/v112aa_cpo_bounded_cohort_map_v1.json"),
    )
    write_csv_rows(
        path=repo_root / "data/reference/free_float_snapshots/akshare_cpo_free_float_snapshot_v1.csv",
        rows=result.collected_rows,
    )
    write_csv_rows(
        path=repo_root / "data/reference/free_float_snapshots/akshare_cpo_free_float_snapshot_failures_v1.csv",
        rows=result.failure_rows or [{"symbol": "", "error_type": "", "error_message": ""}],
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v114y_cpo_free_float_snapshot_collection_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
