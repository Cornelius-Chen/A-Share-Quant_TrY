from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass(slots=True)
class V123UCpoDrawdownRiskLayerAttributionMatrixReport:
    summary: dict[str, Any]
    interval_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "interval_rows": self.interval_rows,
            "interpretation": self.interpretation,
        }


class V123UCpoDrawdownRiskLayerAttributionMatrixAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V123UCpoDrawdownRiskLayerAttributionMatrixReport:
        v122w = json.loads(
            (self.repo_root / "reports" / "analysis" / "v122w_cpo_research_test_baseline_drawdown_attribution_v1.json").read_text(
                encoding="utf-8"
            )
        )
        v122y = json.loads(
            (self.repo_root / "reports" / "analysis" / "v122y_cpo_baseline_vs_research_drawdown_compare_v1.json").read_text(
                encoding="utf-8"
            )
        )
        v123l = json.loads(
            (self.repo_root / "reports" / "analysis" / "v123l_cpo_heat_guardrail_drawdown_interval_compare_v1.json").read_text(
                encoding="utf-8"
            )
        )
        v121l = json.loads(
            (self.repo_root / "reports" / "analysis" / "v121l_cpo_ijk_three_run_adversarial_triage_v1.json").read_text(
                encoding="utf-8"
            )
        )
        v123k = json.loads(
            (self.repo_root / "reports" / "analysis" / "v123k_cpo_hij_market_regime_triage_v1.json").read_text(
                encoding="utf-8"
            )
        )
        v123t = json.loads(
            (self.repo_root / "reports" / "analysis" / "v123t_cpo_qrs_daily_residual_triage_v1.json").read_text(
                encoding="utf-8"
            )
        )

        compare_by_rank = {int(row["rank"]): row for row in v122y["interval_rows"]}
        heat_by_rank = {int(row["rank"]): row for row in v123l["interval_rows"]}
        drawdown_by_rank = {int(row["rank"]): row for row in v122w["drawdown_rows"]}

        interval_rows: list[dict[str, Any]] = []
        for rank in (1, 2, 3):
            compare_row = compare_by_rank[rank]
            heat_row = heat_by_rank[rank]
            drawdown_row = drawdown_by_rank[rank]
            balanced_improvement = _to_float(heat_row["balanced_heat_guardrail_drawdown_improvement"])
            strict_improvement = _to_float(heat_row["strict_heat_guardrail_drawdown_improvement"])
            baseline_cash_gap = _to_float(compare_row["baseline_cash_ratio_peak"]) - _to_float(compare_row["research_cash_ratio_peak"])
            interval_trade_count = int(drawdown_row["interval_trade_count"])

            if max(balanced_improvement, strict_improvement) >= 0.10:
                primary_driver = "position_heat"
            elif max(balanced_improvement, strict_improvement) <= 0.001 and rank == 3:
                primary_driver = "held_pair_residual_deterioration"
            else:
                primary_driver = "mixed_non_heat_downside"

            interval_rows.append(
                {
                    "rank": rank,
                    "peak_date": str(drawdown_row["peak_date"]),
                    "trough_date": str(drawdown_row["trough_date"]),
                    "drawdown": round(_to_float(drawdown_row["drawdown"]), 6),
                    "baseline_cash_gap_at_peak": round(baseline_cash_gap, 6),
                    "interval_trade_count": interval_trade_count,
                    "primary_driver": primary_driver,
                    "heat_balanced_improvement": round(balanced_improvement, 6),
                    "heat_strict_improvement": round(strict_improvement, 6),
                    "broad_risk_off_status": str(v121l["authoritative_conclusion"]["authoritative_status"]),
                    "broad_risk_off_role": "general_reduce_prior",
                    "market_regime_status": str(v123k["summary"]["authoritative_status"]),
                    "market_regime_role": "macro_explanatory_only",
                    "residual_pair_status": (
                        str(v123t["summary"]["authoritative_status"]) if rank == 3 else "not_primary_for_interval"
                    ),
                    "residual_pair_role": (
                        "narrow_residual_soft_penalty" if rank == 3 else "not_primary_for_interval"
                    ),
                    "narrative": (
                        "heat-dominated high-carry drawdown"
                        if primary_driver == "position_heat"
                        else "non-overheated held-pair deterioration dominates after heat caps fail"
                        if primary_driver == "held_pair_residual_deterioration"
                        else "mixed downside with no single dominant layer"
                    ),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v123u_cpo_drawdown_risk_layer_attribution_matrix_v1",
            "interval_count": len(interval_rows),
            "heat_dominated_interval_count": sum(1 for row in interval_rows if row["primary_driver"] == "position_heat"),
            "residual_dominated_interval_count": sum(
                1 for row in interval_rows if row["primary_driver"] == "held_pair_residual_deterioration"
            ),
            "recommended_next_posture": "freeze_risk_layer_priority_order_before_opening_any_new_family",
        }
        interpretation = [
            "V1.23U turns the recent risk work into a drawdown attribution matrix instead of leaving it as separate branch reports.",
            "The goal is to answer which risk layer actually explains each major research-baseline drawdown: heat, broad board risk-off, macro regime, or narrow residual pair deterioration.",
            "This is a prioritization artifact, not a replay rule.",
        ]
        return V123UCpoDrawdownRiskLayerAttributionMatrixReport(
            summary=summary,
            interval_rows=interval_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V123UCpoDrawdownRiskLayerAttributionMatrixReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V123UCpoDrawdownRiskLayerAttributionMatrixAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123u_cpo_drawdown_risk_layer_attribution_matrix_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
