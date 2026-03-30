from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ContextConditionedLateQualityAcceptanceReport:
    summary: dict[str, Any]
    strategy_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "strategy_rows": self.strategy_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class ContextConditionedLateQualityAcceptanceAnalyzer:
    """Decide whether the conditioned late-quality branch deserves continued strategy work."""

    def analyze(
        self,
        *,
        control_payload: dict[str, Any],
        conditioned_payload: dict[str, Any],
        min_material_return_improvement: float = 0.0005,
        max_capture_regression: float = 0.001,
    ) -> ContextConditionedLateQualityAcceptanceReport:
        control_rows = {
            str(row["strategy_name"]): row
            for row in control_payload.get("comparisons", [])
        }
        conditioned_rows = {
            str(row["strategy_name"]): row
            for row in conditioned_payload.get("comparisons", [])
        }
        strategy_rows: list[dict[str, Any]] = []
        material_improvement_count = 0
        harmed_strategy_count = 0

        for strategy_name in sorted(set(control_rows) & set(conditioned_rows)):
            control_summary = dict(control_rows[strategy_name].get("summary", {}))
            conditioned_summary = dict(conditioned_rows[strategy_name].get("summary", {}))

            total_return_delta = round(
                float(conditioned_summary.get("total_return", 0.0))
                - float(control_summary.get("total_return", 0.0)),
                6,
            )
            max_drawdown_delta = round(
                float(conditioned_summary.get("max_drawdown", 0.0))
                - float(control_summary.get("max_drawdown", 0.0)),
                6,
            )
            capture_delta = round(
                float(conditioned_summary.get("mainline_capture_ratio", 0.0))
                - float(control_summary.get("mainline_capture_ratio", 0.0)),
                6,
            )
            signal_delta = int(conditioned_summary.get("signal_count", 0)) - int(
                control_summary.get("signal_count", 0)
            )

            material_improvement = (
                total_return_delta >= min_material_return_improvement
                and max_drawdown_delta <= 0.0
                and capture_delta >= -max_capture_regression
            )
            harmed = total_return_delta < 0.0 or max_drawdown_delta > 0.0 or capture_delta < 0.0
            if material_improvement:
                material_improvement_count += 1
            if harmed:
                harmed_strategy_count += 1

            strategy_rows.append(
                {
                    "strategy_name": strategy_name,
                    "total_return_delta": total_return_delta,
                    "max_drawdown_delta": max_drawdown_delta,
                    "capture_delta": capture_delta,
                    "signal_delta": signal_delta,
                    "material_improvement": material_improvement,
                    "harmed": harmed,
                }
            )

        acceptance_posture = (
            "close_conditioned_late_quality_branch_as_non_material"
            if material_improvement_count == 0 and harmed_strategy_count > 0
            else "continue_conditioned_late_quality_branch"
        )
        summary = {
            "acceptance_posture": acceptance_posture,
            "strategy_count": len(strategy_rows),
            "material_improvement_count": material_improvement_count,
            "harmed_strategy_count": harmed_strategy_count,
            "do_promote_conditioned_branch": acceptance_posture
            == "continue_conditioned_late_quality_branch",
        }
        interpretation = [
            "A conditioned late-quality branch only deserves continued strategy work if it changes suite-level outcomes materially rather than just moving a few signals around.",
            "If the branch mostly leaves one strategy unchanged, barely helps another, and harms the third, the correct action is to keep it as explanatory evidence and close the strategy branch.",
            "That still leaves the context axis valuable as analysis, but not yet worthy of a retained hierarchy rule.",
        ]
        return ContextConditionedLateQualityAcceptanceReport(
            summary=summary,
            strategy_rows=strategy_rows,
            interpretation=interpretation,
        )


def write_context_conditioned_late_quality_acceptance_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: ContextConditionedLateQualityAcceptanceReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
