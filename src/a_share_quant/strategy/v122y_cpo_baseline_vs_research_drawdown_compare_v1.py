from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V122YCpoBaselineVsResearchDrawdownCompareReport:
    summary: dict[str, Any]
    interval_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "interval_rows": self.interval_rows,
            "interpretation": self.interpretation,
        }


class V122YCpoBaselineVsResearchDrawdownCompareAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V122YCpoBaselineVsResearchDrawdownCompareReport:
        drawdown_payload = json.loads(
            (self.repo_root / "reports" / "analysis" / "v122w_cpo_research_test_baseline_drawdown_attribution_v1.json").read_text(
                encoding="utf-8"
            )
        )
        baseline_rows = _load_csv_rows(self.repo_root / "data" / "training" / "cpo_baseline_daily_state_v1.csv")
        research_rows = _load_csv_rows(self.repo_root / "data" / "training" / "cpo_research_test_baseline_daily_state_v1.csv")
        baseline_map = {str(row["trade_date"]): row for row in baseline_rows}
        research_map = {str(row["trade_date"]): row for row in research_rows}
        symbols = ["300308", "300502", "300757", "688498"]

        interval_rows: list[dict[str, Any]] = []
        for dd_row in drawdown_payload["drawdown_rows"]:
            peak_date = str(dd_row["peak_date"])
            trough_date = str(dd_row["trough_date"])
            baseline_peak = baseline_map.get(peak_date)
            baseline_trough = baseline_map.get(trough_date)
            research_peak = research_map.get(peak_date)
            research_trough = research_map.get(trough_date)
            if baseline_peak is None or baseline_trough is None or research_peak is None or research_trough is None:
                continue

            symbol_diffs = []
            for symbol in symbols:
                baseline_peak_qty = _to_float(baseline_peak.get(f"{symbol}_qty"))
                research_peak_qty = _to_float(research_peak.get(f"{symbol}_qty"))
                baseline_trough_qty = _to_float(baseline_trough.get(f"{symbol}_qty"))
                research_trough_qty = _to_float(research_trough.get(f"{symbol}_qty"))
                symbol_diffs.append(
                    {
                        "symbol": symbol,
                        "peak_qty_extra_vs_baseline": int(research_peak_qty - baseline_peak_qty),
                        "trough_qty_extra_vs_baseline": int(research_trough_qty - baseline_trough_qty),
                    }
                )

            interval_rows.append(
                {
                    "rank": dd_row["rank"],
                    "peak_date": peak_date,
                    "trough_date": trough_date,
                    "research_drawdown": dd_row["drawdown"],
                    "research_drawdown_amount": dd_row["drawdown_amount"],
                    "baseline_equity_peak": round(_to_float(baseline_peak["equity"]), 4),
                    "baseline_equity_trough": round(_to_float(baseline_trough["equity"]), 4),
                    "research_equity_peak": round(_to_float(research_peak["equity"]), 4),
                    "research_equity_trough": round(_to_float(research_trough["equity"]), 4),
                    "baseline_cash_ratio_peak": round(
                        _to_float(baseline_peak["cash"]) / _to_float(baseline_peak["equity"]), 6
                    ),
                    "research_cash_ratio_peak": round(
                        _to_float(research_peak["cash"]) / _to_float(research_peak["equity"]), 6
                    ),
                    "baseline_cash_ratio_trough": round(
                        _to_float(baseline_trough["cash"]) / _to_float(baseline_trough["equity"]), 6
                    ),
                    "research_cash_ratio_trough": round(
                        _to_float(research_trough["cash"]) / _to_float(research_trough["equity"]), 6
                    ),
                    "baseline_held_symbols_peak": str(baseline_peak["held_symbols"]),
                    "research_held_symbols_peak": str(research_peak["held_symbols"]),
                    "baseline_held_symbols_trough": str(baseline_trough["held_symbols"]),
                    "research_held_symbols_trough": str(research_trough["held_symbols"]),
                    "symbol_qty_diffs": symbol_diffs,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v122y_cpo_baseline_vs_research_drawdown_compare_v1",
            "interval_count": len(interval_rows),
            "recommended_next_posture": "decide_if_priority_should_shift_to_reduce_close_or_position_heat_based_on_direct_baseline_gap",
        }
        interpretation = [
            "V1.22Y compares the same drawdown windows under baseline and research test baseline states.",
            "The point is to answer a practical question: did the research line mainly suffer because it held more of the same names, because it had less cash, or because baseline actually exited earlier?",
        ]
        return V122YCpoBaselineVsResearchDrawdownCompareReport(
            summary=summary,
            interval_rows=interval_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122YCpoBaselineVsResearchDrawdownCompareReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122YCpoBaselineVsResearchDrawdownCompareAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122y_cpo_baseline_vs_research_drawdown_compare_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
