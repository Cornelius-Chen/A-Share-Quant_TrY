from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v120c_cpo_catalyst_event_registry_bootstrap_v1 import load_json_report


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass(slots=True)
class V123ZCpoHeatConditionedRiskoffDrawdownCompareReport:
    summary: dict[str, Any]
    drawdown_compare_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "drawdown_compare_rows": self.drawdown_compare_rows,
            "interpretation": self.interpretation,
        }


class V123ZCpoHeatConditionedRiskoffDrawdownCompareAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V123ZCpoHeatConditionedRiskoffDrawdownCompareReport:
        heat_payload = load_json_report(
            self.repo_root / "reports" / "analysis" / "v123l_cpo_heat_guardrail_drawdown_interval_compare_v1.json"
        )
        conditioned_payload = load_json_report(
            self.repo_root / "reports" / "analysis" / "v123y_cpo_heat_conditioned_riskoff_execution_audit_v1.json"
        )
        variant_rows = {str(row["variant_name"]): row for row in conditioned_payload["variant_rows"]}
        best_name = str(conditioned_payload["summary"]["best_tradeoff_variant_name"])
        best_row = variant_rows[best_name]

        drawdown_compare_rows: list[dict[str, Any]] = []
        for row in list(heat_payload.get("interval_rows", [])):
            drawdown_compare_rows.append(
                {
                    "interval_rank": int(row["rank"]),
                    "peak_date": str(row["peak_date"]),
                    "trough_date": str(row["trough_date"]),
                    "uncapped_drawdown": _to_float(row["uncapped_drawdown"]),
                    "balanced_drawdown": _to_float(row["balanced_heat_guardrail_drawdown"]),
                    "strict_drawdown": _to_float(row["strict_heat_guardrail_drawdown"]),
                    "best_heat_conditioned_variant_name": best_name,
                    "best_heat_conditioned_full_curve_mdd": _to_float(best_row["max_drawdown"]),
                    "heat_conditioned_reduce_count": int(best_row["executed_reduce_count"]),
                    "heat_conditioned_suppressed_reduce_count": int(best_row["suppressed_reduce_count"]),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v123z_cpo_heat_conditioned_riskoff_drawdown_compare_v1",
            "best_heat_conditioned_variant_name": best_name,
            "best_heat_conditioned_final_equity": _to_float(best_row["final_equity"]),
            "best_heat_conditioned_max_drawdown": _to_float(best_row["max_drawdown"]),
            "balanced_heat_reference_final_equity": next(
                _to_float(row["final_equity"])
                for row in conditioned_payload["variant_rows"]
                if str(row["variant_name"]) == "balanced_heat_reference"
            ),
            "balanced_heat_reference_max_drawdown": next(
                _to_float(row["max_drawdown"])
                for row in conditioned_payload["variant_rows"]
                if str(row["variant_name"]) == "balanced_heat_reference"
            ),
            "recommended_next_posture": "triage_heat_conditioned_riskoff_after_tradeoff_and_interval_compare",
        }
        interpretation = [
            "V1.23Z does not claim interval-level causality for the conditioned variants because only full-curve execution results are available here.",
            "Its purpose is to put the best conditioned risk-off execution variant next to the already-frozen top-three heat interval compare.",
            "The key question is practical: does a heat-conditioned risk-off layer preserve enough equity to be worth another governance cycle?",
        ]
        return V123ZCpoHeatConditionedRiskoffDrawdownCompareReport(
            summary=summary,
            drawdown_compare_rows=drawdown_compare_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V123ZCpoHeatConditionedRiskoffDrawdownCompareReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V123ZCpoHeatConditionedRiskoffDrawdownCompareAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123z_cpo_heat_conditioned_riskoff_drawdown_compare_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
