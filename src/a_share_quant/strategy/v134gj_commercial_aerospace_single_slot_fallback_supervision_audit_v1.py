from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134GJCommercialAerospaceSingleSlotFallbackSupervisionAuditV1Report:
    summary: dict[str, Any]
    fallback_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "fallback_rows": self.fallback_rows,
            "interpretation": self.interpretation,
        }


class V134GJCommercialAerospaceSingleSlotFallbackSupervisionAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.capacity_hierarchy_path = (
            repo_root / "reports" / "analysis" / "v134gh_commercial_aerospace_slot_capacity_hierarchy_audit_v1.json"
        )
        self.dual_slot_permission_path = (
            repo_root / "reports" / "analysis" / "v134fz_commercial_aerospace_active_wave_dual_slot_permission_audit_v1.json"
        )
        self.dual_slot_allocation_path = (
            repo_root / "reports" / "analysis" / "v134gb_commercial_aerospace_dual_slot_allocation_supervision_audit_v1.json"
        )

    def analyze(self) -> V134GJCommercialAerospaceSingleSlotFallbackSupervisionAuditV1Report:
        hierarchy = json.loads(self.capacity_hierarchy_path.read_text(encoding="utf-8"))
        permission = json.loads(self.dual_slot_permission_path.read_text(encoding="utf-8"))
        allocation = json.loads(self.dual_slot_allocation_path.read_text(encoding="utf-8"))

        observed_single_slot_day_count = hierarchy["summary"]["single_slot_unobserved_day_count"]
        dual_slot_row = next(
            row for row in hierarchy["hierarchy_rows"] if row["hierarchy_state"] == "tiered_dual_slot_day"
        )
        reset_slot_row = next(row for row in allocation["allocation_rows"] if row["slot_name"] == "reset_slot")
        continuation_slot_row = next(
            row for row in allocation["allocation_rows"] if row["slot_name"] == "continuation_slot"
        )

        fallback_rows = [
            {
                "fallback_state": "observed_single_slot_fallback",
                "status": "unobserved",
                "trade_date": "",
                "slot_name": "",
                "symbol": "",
                "supporting_reading": "no single-slot active-wave day exists on the current strict surface",
            },
            {
                "fallback_state": "forced_local_surrogate",
                "status": "weak_reset_slot_surrogate_only",
                "trade_date": dual_slot_row["trade_date"],
                "slot_name": "reset_slot",
                "symbol": reset_slot_row["symbol"],
                "supporting_reading": (
                    f"weight_ratio={allocation['summary']['reset_to_continuation_weight_ratio']:.8f}|"
                    f"clean_reset_higher_metric_count={permission['summary']['clean_reset_higher_metric_count']}|"
                    f"same_symbol_higher_metric_count={permission['summary']['same_symbol_higher_metric_count']}"
                ),
            },
            {
                "fallback_state": "continuation_slot_counterpart",
                "status": "retain_as_companion_not_fallback",
                "trade_date": dual_slot_row["trade_date"],
                "slot_name": "continuation_slot",
                "symbol": continuation_slot_row["symbol"],
                "supporting_reading": (
                    f"secondary_weight={continuation_slot_row['weight_vs_initial_capital']:.6f}|"
                    f"local_edge=open_to_15m"
                ),
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v134gj_commercial_aerospace_single_slot_fallback_supervision_audit_v1",
            "observed_single_slot_day_count": observed_single_slot_day_count,
            "weak_surrogate_count": 1,
            "surrogate_slot_name": "reset_slot",
            "surrogate_symbol": reset_slot_row["symbol"],
            "dual_slot_reference_trade_date": dual_slot_row["trade_date"],
            "authoritative_rule": (
                "single-slot fallback remains unobserved on the current strict active-wave surface; "
                "at most, the reset slot can be retained as a weak local surrogate when a forced one-slot reading is needed"
            ),
        }
        interpretation = [
            "V1.34GJ asks the next honest question after slot-capacity hierarchy: if the branch cannot yet observe a true single-slot day, is there at least a weak local surrogate?",
            "The answer is narrow. A real single-slot fallback remains unobserved. The reset slot only earns weak surrogate status because the lone dual-slot day already shows reset-primary plus continuation-secondary structure.",
        ]
        return V134GJCommercialAerospaceSingleSlotFallbackSupervisionAuditV1Report(
            summary=summary,
            fallback_rows=fallback_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GJCommercialAerospaceSingleSlotFallbackSupervisionAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GJCommercialAerospaceSingleSlotFallbackSupervisionAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134gj_commercial_aerospace_single_slot_fallback_supervision_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
