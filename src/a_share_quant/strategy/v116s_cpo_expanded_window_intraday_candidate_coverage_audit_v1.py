from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_trade_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _baseline_positions_eod(executed_orders: list[dict[str, Any]], trade_dates: list[date]) -> dict[tuple[date, str], int]:
    positions: dict[str, int] = {}
    by_day: dict[tuple[date, str], int] = {}
    rows_by_date: dict[date, list[dict[str, Any]]] = {}
    for row in executed_orders:
        rows_by_date.setdefault(parse_trade_date(str(row["execution_trade_date"])), []).append(row)
    symbols = sorted({str(row["symbol"]) for row in executed_orders})
    for trade_date in trade_dates:
        for row in rows_by_date.get(trade_date, []):
            symbol = str(row["symbol"])
            quantity = int(row["quantity"])
            if str(row["action"]) == "buy":
                positions[symbol] = positions.get(symbol, 0) + quantity
            else:
                positions[symbol] = max(0, positions.get(symbol, 0) - quantity)
        for symbol in symbols:
            by_day[(trade_date, symbol)] = positions.get(symbol, 0)
    return by_day


@dataclass(slots=True)
class V116SCpoExpandedWindowIntradayCandidateCoverageAuditReport:
    summary: dict[str, Any]
    coverage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "coverage_rows": self.coverage_rows,
            "interpretation": self.interpretation,
        }


class V116SCpoExpandedWindowIntradayCandidateCoverageAuditAnalyzer:
    MATURE_SYMBOLS = ("300308", "300502", "300757", "688498")

    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v114t_payload: dict[str, Any],
        v116q_payload: dict[str, Any],
        pca_rows_path: Path,
    ) -> V116SCpoExpandedWindowIntradayCandidateCoverageAuditReport:
        baseline_day_rows = list(v114t_payload.get("replay_day_rows", []))
        trade_dates = sorted(parse_trade_date(str(row["trade_date"])) for row in baseline_day_rows)
        baseline_executed_orders = list(v114t_payload.get("executed_order_rows", []))
        positions_eod = _baseline_positions_eod(baseline_executed_orders, trade_dates)

        pca_rows = _load_csv_rows(pca_rows_path)
        add_rows = [row for row in pca_rows if str(row.get("action_context")) == "add_vs_hold"]
        add_rows_by_day: dict[str, list[dict[str, Any]]] = {}
        for row in add_rows:
            add_rows_by_day.setdefault(str(row["signal_trade_date"]), []).append(row)

        expanded_rows = list(v116q_payload.get("expanded_window_rows", []))
        coverage_rows: list[dict[str, Any]] = []
        missing_new_day_count = 0
        for row in expanded_rows:
            trade_date_str = str(row["trade_date"])
            trade_date = parse_trade_date(trade_date_str)
            add_candidates = add_rows_by_day.get(trade_date_str, [])
            held_mature_symbols = [
                symbol
                for symbol in self.MATURE_SYMBOLS
                if positions_eod.get((trade_date, symbol), 0) > 0
            ]
            has_candidate_rows = len(add_candidates) > 0
            is_original = bool(row.get("is_original_top_miss"))
            if (not is_original) and (not has_candidate_rows):
                missing_new_day_count += 1
            coverage_rows.append(
                {
                    "trade_date": trade_date_str,
                    "is_original_top_miss": is_original,
                    "under_exposure_gap": _to_float(row.get("under_exposure_gap")),
                    "held_mature_symbols": held_mature_symbols,
                    "held_mature_symbol_count": len(held_mature_symbols),
                    "add_candidate_row_count": len(add_candidates),
                    "add_candidate_symbols": sorted({str(candidate["symbol"]) for candidate in add_candidates}),
                    "coverage_gap": (len(held_mature_symbols) > 0 and len(add_candidates) == 0),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v116s_cpo_expanded_window_intraday_candidate_coverage_audit_v1",
            "expanded_window_day_count": len(expanded_rows),
            "days_with_add_candidate_rows": sum(1 for row in coverage_rows if int(row["add_candidate_row_count"]) > 0),
            "days_with_held_mature_symbols": sum(1 for row in coverage_rows if int(row["held_mature_symbol_count"]) > 0),
            "missing_new_day_count": missing_new_day_count,
            "recommended_next_posture": "rebuild_intraday_action_timepoint_table_for_new_expanded_window_days_before_more_visible_only_validation",
        }
        interpretation = [
            "V1.16S audits whether the expanded repaired-window surface is actually represented inside the existing intraday add-vs-hold candidate base table.",
            "This distinguishes a true signal failure from a coverage failure where the widened surface contains held mature names but the intraday action-timepoint table never generated add-candidate rows for those days.",
            "If the new expanded days are mostly missing from the candidate base, the next step is table rebuilding rather than more threshold tuning.",
        ]
        return V116SCpoExpandedWindowIntradayCandidateCoverageAuditReport(
            summary=summary,
            coverage_rows=coverage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V116SCpoExpandedWindowIntradayCandidateCoverageAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116SCpoExpandedWindowIntradayCandidateCoverageAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v114t_payload=json.loads((repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json").read_text(encoding="utf-8")),
        v116q_payload=json.loads((repo_root / "reports" / "analysis" / "v116q_cpo_expanded_repaired_window_manifest_v1.json").read_text(encoding="utf-8")),
        pca_rows_path=repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_v1.csv",
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116s_cpo_expanded_window_intraday_candidate_coverage_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
