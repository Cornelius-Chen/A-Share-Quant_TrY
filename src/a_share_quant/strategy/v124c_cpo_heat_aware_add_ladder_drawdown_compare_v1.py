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
class V124CCpoHeatAwareAddLadderDrawdownCompareReport:
    summary: dict[str, Any]
    interval_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "interval_rows": self.interval_rows,
            "interpretation": self.interpretation,
        }


class V124CCpoHeatAwareAddLadderDrawdownCompareAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V124CCpoHeatAwareAddLadderDrawdownCompareReport:
        ladder_payload = json.loads(
            (self.repo_root / "reports" / "analysis" / "v124b_cpo_heat_aware_add_ladder_audit_v1.json").read_text(encoding="utf-8")
        )
        interval_payload = json.loads(
            (self.repo_root / "reports" / "analysis" / "v123l_cpo_heat_guardrail_drawdown_interval_compare_v1.json").read_text(encoding="utf-8")
        )
        daily_rows = _load_csv_rows(self.repo_root / "data" / "training" / "cpo_heat_aware_add_ladder_daily_state_v1.csv")

        best_name = str(ladder_payload["summary"]["best_tradeoff_variant_name"])
        daily_map = {
            (str(row["variant_name"]), str(row["trade_date"])): row
            for row in daily_rows
        }

        interval_rows: list[dict[str, Any]] = []
        for row in list(interval_payload.get("interval_rows", [])):
            peak_key = (best_name, str(row["peak_date"]))
            trough_key = (best_name, str(row["trough_date"]))
            peak = daily_map[peak_key]
            trough = daily_map[trough_key]
            peak_equity = _to_float(peak["equity"])
            trough_equity = _to_float(trough["equity"])
            ladder_drawdown = 0.0 if peak_equity <= 0 else (peak_equity - trough_equity) / peak_equity
            interval_rows.append(
                {
                    "rank": int(row["rank"]),
                    "peak_date": str(row["peak_date"]),
                    "trough_date": str(row["trough_date"]),
                    "balanced_heat_guardrail_drawdown": _to_float(row["balanced_heat_guardrail_drawdown"]),
                    "best_ladder_variant_name": best_name,
                    "best_ladder_variant_drawdown": round(ladder_drawdown, 6),
                    "drawdown_improvement_vs_balanced_heat": round(_to_float(row["balanced_heat_guardrail_drawdown"]) - ladder_drawdown, 6),
                    "best_ladder_peak_cash_ratio": _to_float(peak["cash_ratio"]),
                    "best_ladder_trough_cash_ratio": _to_float(trough["cash_ratio"]),
                }
            )

        best_variant = max(
            ladder_payload["variant_rows"],
            key=lambda row: _to_float(row["final_equity"]) - 2_500_000 * _to_float(row["max_drawdown"]),
        )
        summary = {
            "acceptance_posture": "freeze_v124c_cpo_heat_aware_add_ladder_drawdown_compare_v1",
            "best_ladder_variant_name": best_name,
            "best_ladder_final_equity": _to_float(best_variant["final_equity"]),
            "best_ladder_max_drawdown": _to_float(best_variant["max_drawdown"]),
            "recommended_next_posture": "triage_best_ladder_against_balanced_heat_reference",
        }
        interpretation = [
            "V1.24C compares the best heat-aware add ladder against the already-frozen balanced heat reference on the same three major drawdown intervals.",
            "The question is narrow: does smaller add size under the same heat budget improve the real pain points enough to justify replacing the current heat reference?",
        ]
        return V124CCpoHeatAwareAddLadderDrawdownCompareReport(
            summary=summary,
            interval_rows=interval_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V124CCpoHeatAwareAddLadderDrawdownCompareReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V124CCpoHeatAwareAddLadderDrawdownCompareAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124c_cpo_heat_aware_add_ladder_drawdown_compare_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
