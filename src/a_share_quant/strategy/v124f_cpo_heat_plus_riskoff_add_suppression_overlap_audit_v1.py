from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v120c_cpo_catalyst_event_registry_bootstrap_v1 import load_json_report


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_trade_date(value: str) -> datetime.date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    idx = max(0, min(len(ordered) - 1, int(round((len(ordered) - 1) * q))))
    return ordered[idx]


@dataclass(slots=True)
class V124FCpoHeatPlusRiskoffAddSuppressionOverlapAuditReport:
    summary: dict[str, Any]
    overlap_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "overlap_rows": self.overlap_rows,
            "interpretation": self.interpretation,
        }


class V124FCpoHeatPlusRiskoffAddSuppressionOverlapAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _next_trade_date(self, trade_date: str, trade_dates: list[datetime.date]) -> str | None:
        current = parse_trade_date(trade_date)
        for candidate in trade_dates:
            if candidate > current:
                return candidate.strftime("%Y-%m-%d")
        return None

    def analyze(self) -> V124FCpoHeatPlusRiskoffAddSuppressionOverlapAuditReport:
        v114t_payload = load_json_report(self.repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json")
        v120e_payload = load_json_report(self.repo_root / "reports" / "analysis" / "v120e_cpo_research_test_baseline_overlay_replay_v1.json")
        v121j_payload = load_json_report(self.repo_root / "reports" / "analysis" / "v121j_cpo_reduce_side_board_risk_off_external_audit_v1.json")
        v122x_rows = []
        with (self.repo_root / "data" / "training" / "cpo_heat_aware_add_ladder_daily_state_v1.csv").open("r", encoding="utf-8-sig") as handle:
            import csv

            v122x_rows = list(csv.DictReader(handle))

        trade_dates = [parse_trade_date(str(row["trade_date"])) for row in list(v114t_payload.get("replay_day_rows", []))]
        daily_state_map = {
            str(row["trade_date"]): row
            for row in v122x_rows
            if str(row.get("variant_name")) == "balanced_heat_reference"
        }

        risk_rows_by_exec: dict[tuple[str, str], float] = {}
        scored_rows = list(v121j_payload.get("scored_rows", []))
        score_values = [_to_float(row["board_risk_off_reduce_score_candidate"]) for row in scored_rows]
        thresholds = {
            "q75": round(_quantile(score_values, 0.75), 6),
            "q85": round(_quantile(score_values, 0.85), 6),
            "q90": round(_quantile(score_values, 0.90), 6),
        }
        for row in scored_rows:
            execution_trade_date = self._next_trade_date(str(row["signal_trade_date"]), trade_dates)
            if execution_trade_date is None:
                continue
            risk_rows_by_exec[(execution_trade_date, str(row["symbol"]))] = _to_float(row["board_risk_off_reduce_score_candidate"])

        aggregated_rows = list(v120e_payload.get("aggregated_signal_rows", []))
        overlay_exec_rows: list[dict[str, Any]] = []
        for row in aggregated_rows:
            execution_trade_date = self._next_trade_date(str(row["signal_trade_date"]), trade_dates)
            if execution_trade_date is None:
                continue
            state = daily_state_map.get(execution_trade_date)
            cash_ratio = _to_float(state["cash_ratio"]) if state else 0.0
            gross_ratio = _to_float(state["gross_ratio"]) if state else 0.0
            equity = _to_float(state["equity"]) if state else 0.0
            symbol_qty = 0
            if state:
                symbol_qty = int(_to_float(state.get(f"{str(row['symbol'])}_qty"), 0.0))
            symbol_ratio = 0.0
            if state and equity > 0.0 and symbol_qty > 0:
                # close-only approximation is sufficient for overlap audit
                from_price = 0.0
                # No price join needed; ratio gate uses current carried weight proxy from state quantities only when non-zero.
                # If close-level ratio is needed later, a tighter replay join can be added.
                symbol_ratio = 0.0
            overlay_exec_rows.append(
                {
                    "signal_trade_date": str(row["signal_trade_date"]),
                    "execution_trade_date": execution_trade_date,
                    "symbol": str(row["symbol"]),
                    "component_count": int(row["component_count"]),
                    "gross_ratio": gross_ratio,
                    "cash_ratio": cash_ratio,
                    "riskoff_score": risk_rows_by_exec.get((execution_trade_date, str(row["symbol"]))),
                }
            )

        overlap_rows: list[dict[str, Any]] = []
        for quantile_name, threshold in thresholds.items():
            rows_with_signal = [row for row in overlay_exec_rows if row["riskoff_score"] is not None]
            over_threshold = [row for row in rows_with_signal if _to_float(row["riskoff_score"]) >= threshold]
            heat_g55 = [row for row in over_threshold if _to_float(row["gross_ratio"]) >= 0.55]
            heat_g60 = [row for row in over_threshold if _to_float(row["gross_ratio"]) >= 0.60]
            overlap_rows.append(
                {
                    "riskoff_quantile": quantile_name,
                    "threshold": threshold,
                    "overlay_exec_row_count": len(overlay_exec_rows),
                    "rows_with_riskoff_signal": len(rows_with_signal),
                    "rows_over_threshold": len(over_threshold),
                    "rows_over_threshold_and_gross55": len(heat_g55),
                    "rows_over_threshold_and_gross60": len(heat_g60),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v124f_cpo_heat_plus_riskoff_add_suppression_overlap_audit_v1",
            "overlay_exec_row_count": len(overlay_exec_rows),
            "riskoff_thresholds": thresholds,
            "max_overlap_over_threshold_and_gross55": max(row["rows_over_threshold_and_gross55"] for row in overlap_rows) if overlap_rows else 0,
            "recommended_next_posture": "triage_add_suppression_family_if_overlap_is_zero_or_trivial",
        }
        interpretation = [
            "V1.24F explains why the add-suppression execution variants either matter or do nothing.",
            "If there is almost no overlap between overlay add days and high-threshold risk-off states inside already-hot books, then suppression cannot improve the line and should be stopped cleanly.",
        ]
        return V124FCpoHeatPlusRiskoffAddSuppressionOverlapAuditReport(
            summary=summary,
            overlap_rows=overlap_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V124FCpoHeatPlusRiskoffAddSuppressionOverlapAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V124FCpoHeatPlusRiskoffAddSuppressionOverlapAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124f_cpo_heat_plus_riskoff_add_suppression_overlap_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
