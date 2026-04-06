from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v126m_commercial_aerospace_phase_geometry_label_table_v1 import (
    V126MCommercialAerospacePhaseGeometryLabelTableAnalyzer,
)
from a_share_quant.strategy.v127g_commercial_aerospace_primary_reference_attribution_v1 import (
    V127GCommercialAerospacePrimaryReferenceAttributionAnalyzer,
    _ReplayConfig,
)


@dataclass(slots=True)
class _VetoPolicy:
    name: str
    global_symbols: set[str]
    preheat_symbols: set[str]
    impulse_symbols: set[str]


@dataclass(slots=True)
class V127MCommercialAerospacePhaseConditionedDragVetoAuditReport:
    summary: dict[str, Any]
    variant_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "variant_rows": self.variant_rows,
            "interpretation": self.interpretation,
        }


class V127MCommercialAerospacePhaseConditionedDragVetoAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.helper = V127GCommercialAerospacePrimaryReferenceAttributionAnalyzer(repo_root)
        self.v127k_path = repo_root / "reports" / "analysis" / "v127k_commercial_aerospace_chronic_drag_symbol_veto_audit_v1.json"

    def _drag_symbols(self) -> list[str]:
        payload = json.loads(self.v127k_path.read_text(encoding="utf-8"))
        return payload["summary"]["drag_symbols_ranked"]

    @staticmethod
    def _blocked(row: dict[str, Any], policy: _VetoPolicy) -> bool:
        symbol = row["symbol"]
        phase = row["phase_window_semantic"]
        if symbol in policy.global_symbols:
            return True
        if phase == "preheat_window" and symbol in policy.preheat_symbols:
            return True
        if phase == "impulse_window" and symbol in policy.impulse_symbols:
            return True
        return False

    def _simulate_with_policy(self, policy: _VetoPolicy) -> dict[str, Any]:
        base = self.helper._load_base_config()
        label_table = V126MCommercialAerospacePhaseGeometryLabelTableAnalyzer(self.repo_root).analyze()
        rows, test_dates, date_to_idx = self.helper._split_rows(label_table.training_rows)
        config = _ReplayConfig(
            name=policy.name,
            preheat_cap=int(base["preheat_cap"]),
            impulse_cap=int(base["impulse_cap"]),
            cooldown_days_after_sell=int(base["cooldown_days_after_sell"]),
            min_increment_notional=float(base["min_increment_notional"]),
            preheat_full_target_notional=70_000.0,
            family="broad_half_reference",
            sell_ratio=0.5,
        )

        filtered_rows = [row for row in rows if not self._blocked(row, policy)]
        return self.helper._simulate_variant_detailed(filtered_rows, test_dates, date_to_idx, config)

    def analyze(self) -> V127MCommercialAerospacePhaseConditionedDragVetoAuditReport:
        drag_symbols = self._drag_symbols()
        trio = set(drag_symbols[:3])
        remainder = set(drag_symbols[1:3])

        policies = [
            _VetoPolicy("broad_half_reference", set(), set(), set()),
            _VetoPolicy("veto_drag_trio_preheat_only", set(), trio, set()),
            _VetoPolicy("veto_drag_trio_impulse_only", set(), set(), trio),
            _VetoPolicy("veto_688066_global_others_preheat", {drag_symbols[0]}, remainder, set()),
            _VetoPolicy("veto_688066_global_others_impulse", {drag_symbols[0]}, set(), remainder),
        ]
        variant_payloads = [self._simulate_with_policy(policy) for policy in policies]
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
        candidates = [row for row in variant_rows[1:] if row["max_drawdown"] < reference["max_drawdown"]]
        best_variant = max(candidates, key=lambda row: row["final_equity"]) if candidates else reference
        summary = {
            "acceptance_posture": "freeze_v127m_commercial_aerospace_phase_conditioned_drag_veto_audit_v1",
            "reference_variant": reference["variant"],
            "reference_final_equity": reference["final_equity"],
            "reference_max_drawdown": reference["max_drawdown"],
            "drag_symbols_ranked": drag_symbols,
            "best_variant": best_variant["variant"],
            "best_variant_final_equity": best_variant["final_equity"],
            "best_variant_max_drawdown": best_variant["max_drawdown"],
        }
        interpretation = [
            "V1.27M tests whether the chronic-drag symbols should be blocked only in specific entry phases instead of globally.",
            "This branch keeps the v127e broad-half control family intact and only changes where chronic drag symbols are allowed to enter.",
        ]
        return V127MCommercialAerospacePhaseConditionedDragVetoAuditReport(
            summary=summary,
            variant_rows=variant_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V127MCommercialAerospacePhaseConditionedDragVetoAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V127MCommercialAerospacePhaseConditionedDragVetoAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v127m_commercial_aerospace_phase_conditioned_drag_veto_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
