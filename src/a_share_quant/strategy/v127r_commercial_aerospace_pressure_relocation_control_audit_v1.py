from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v127m_commercial_aerospace_phase_conditioned_drag_veto_audit_v1 import (
    V127MCommercialAerospacePhaseConditionedDragVetoAuditAnalyzer,
    _VetoPolicy,
)


@dataclass(slots=True)
class V127RCommercialAerospacePressureRelocationControlAuditReport:
    summary: dict[str, Any]
    variant_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "variant_rows": self.variant_rows,
            "interpretation": self.interpretation,
        }


class V127RCommercialAerospacePressureRelocationControlAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.base_analyzer = V127MCommercialAerospacePhaseConditionedDragVetoAuditAnalyzer(repo_root)

    def analyze(self) -> V127RCommercialAerospacePressureRelocationControlAuditReport:
        drag_trio = set(self.base_analyzer._drag_symbols()[:3])
        policies = [
            _VetoPolicy("veto_drag_trio_impulse_only", set(), set(), drag_trio),
            _VetoPolicy("veto_drag_trio_impulse_plus_preheat_000738", set(), {"000738"}, drag_trio),
            _VetoPolicy("veto_drag_trio_impulse_plus_preheat_002085", set(), {"002085"}, drag_trio),
            _VetoPolicy("veto_drag_trio_impulse_plus_preheat_000738_002085", set(), {"000738", "002085"}, drag_trio),
            _VetoPolicy("veto_drag_trio_impulse_plus_preheat_000738_002085_and_601698_impulse", set(), {"000738", "002085"}, drag_trio | {"601698"}),
        ]
        variant_payloads = [self.base_analyzer._simulate_with_policy(policy) for policy in policies]
        variant_rows = [
            {
                "variant": payload["variant"],
                "final_equity": payload["summary"]["final_equity"],
                "max_drawdown": payload["summary"]["max_drawdown"],
                "executed_order_count": payload["summary"]["executed_order_count"],
            }
            for payload in variant_payloads
        ]
        reference = variant_rows[0]
        best_variant = min(
            variant_rows,
            key=lambda row: (-row["final_equity"], row["max_drawdown"], row["executed_order_count"]),
        )
        best_cleaner = min(
            [row for row in variant_rows if row["max_drawdown"] < reference["max_drawdown"]],
            key=lambda row: (-row["final_equity"], row["max_drawdown"], row["executed_order_count"]),
            default=reference,
        )
        summary = {
            "acceptance_posture": "freeze_v127r_commercial_aerospace_pressure_relocation_control_audit_v1",
            "reference_variant": reference["variant"],
            "reference_final_equity": reference["final_equity"],
            "reference_max_drawdown": reference["max_drawdown"],
            "best_variant": best_variant["variant"],
            "best_variant_final_equity": best_variant["final_equity"],
            "best_variant_max_drawdown": best_variant["max_drawdown"],
            "best_cleaner_variant": best_cleaner["variant"],
            "best_cleaner_final_equity": best_cleaner["final_equity"],
            "best_cleaner_max_drawdown": best_cleaner["max_drawdown"],
        }
        interpretation = [
            "V1.27R tests whether the new-primary pressure relocation can be reduced by restraining 000738/002085 preheat entries and 601698 impulse entries.",
            "This is a narrow attribution-driven control audit, not a new family search.",
        ]
        return V127RCommercialAerospacePressureRelocationControlAuditReport(
            summary=summary,
            variant_rows=variant_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V127RCommercialAerospacePressureRelocationControlAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V127RCommercialAerospacePressureRelocationControlAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v127r_commercial_aerospace_pressure_relocation_control_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
