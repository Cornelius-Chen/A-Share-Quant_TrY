from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134GHCommercialAerospaceSlotCapacityHierarchyAuditV1Report:
    summary: dict[str, Any]
    hierarchy_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "hierarchy_rows": self.hierarchy_rows,
            "interpretation": self.interpretation,
        }


class V134GHCommercialAerospaceSlotCapacityHierarchyAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.capacity_report_path = (
            repo_root / "reports" / "analysis" / "v134gd_commercial_aerospace_dual_slot_capacity_audit_v1.json"
        )
        self.selection_report_path = (
            repo_root / "reports" / "analysis" / "v134ft_commercial_aerospace_active_wave_selection_supervision_audit_v1.json"
        )
        self.exclusion_report_path = (
            repo_root / "reports" / "analysis" / "v134fv_commercial_aerospace_recent_reduce_residue_exclusion_audit_v1.json"
        )
        self.allocation_report_path = (
            repo_root / "reports" / "analysis" / "v134gb_commercial_aerospace_dual_slot_allocation_supervision_audit_v1.json"
        )

    def analyze(self) -> V134GHCommercialAerospaceSlotCapacityHierarchyAuditV1Report:
        capacity = json.loads(self.capacity_report_path.read_text(encoding="utf-8"))
        selection = json.loads(self.selection_report_path.read_text(encoding="utf-8"))
        exclusion = json.loads(self.exclusion_report_path.read_text(encoding="utf-8"))
        allocation = json.loads(self.allocation_report_path.read_text(encoding="utf-8"))

        selected_rows = {
            row["trade_date"]: row
            for row in selection["candidate_rows"]
            if row["selection_outcome"] == "selected"
        }
        displaced_rows = {
            row["trade_date"]: row
            for row in selection["candidate_rows"]
            if row["selection_outcome"] == "displaced"
        }
        allocation_rows = {}
        for row in allocation["allocation_rows"]:
            allocation_rows.setdefault(row["trade_date"], []).append(row)

        hierarchy_rows: list[dict[str, Any]] = []
        zero_slot_veto_day_count = 0
        tiered_dual_slot_day_count = 0
        single_slot_unobserved_day_count = 0

        for row in capacity["day_rows"]:
            trade_date = row["trade_date"]
            capacity_state = row["capacity_state"]

            if capacity_state == "zero_slot_day":
                displaced = displaced_rows[trade_date]
                hierarchy_state = "zero_slot_veto_day"
                hierarchy_rows.append(
                    {
                        "trade_date": trade_date,
                        "capacity_state": capacity_state,
                        "hierarchy_state": hierarchy_state,
                        "primary_driver": "recent_reduce_residue_exclusion",
                        "symbol": displaced["symbol"],
                        "selection_state": displaced["selection_state"],
                        "supporting_reading": (
                            f"{displaced['last_action_name']}@{displaced['last_action_trade_date']}"
                        ),
                    }
                )
                zero_slot_veto_day_count += 1
                continue

            if capacity_state == "dual_slot_day":
                day_allocations = allocation_rows[trade_date]
                reset_row = next(row for row in day_allocations if row["slot_name"] == "reset_slot")
                continuation_row = next(row for row in day_allocations if row["slot_name"] == "continuation_slot")
                hierarchy_state = "tiered_dual_slot_day"
                hierarchy_rows.append(
                    {
                        "trade_date": trade_date,
                        "capacity_state": capacity_state,
                        "hierarchy_state": hierarchy_state,
                        "primary_driver": "primary_reset_plus_secondary_continuation",
                        "symbol": f"{reset_row['symbol']}|{continuation_row['symbol']}",
                        "selection_state": "clean_reset_candidate|same_symbol_continuation_selected",
                        "supporting_reading": (
                            f"reset_weight={reset_row['weight_vs_initial_capital']:.6f}|"
                            f"continuation_weight={continuation_row['weight_vs_initial_capital']:.6f}"
                        ),
                    }
                )
                tiered_dual_slot_day_count += 1
                continue

            if capacity_state == "single_slot_day":
                selected = selected_rows[trade_date]
                hierarchy_state = "single_slot_unobserved_template"
                hierarchy_rows.append(
                    {
                        "trade_date": trade_date,
                        "capacity_state": capacity_state,
                        "hierarchy_state": hierarchy_state,
                        "primary_driver": "single_slot_fallback_not_yet_observed",
                        "symbol": selected["symbol"],
                        "selection_state": selected["selection_state"],
                        "supporting_reading": "placeholder_only",
                    }
                )
                single_slot_unobserved_day_count += 1

        summary = {
            "acceptance_posture": "freeze_v134gh_commercial_aerospace_slot_capacity_hierarchy_audit_v1",
            "active_wave_day_count": capacity["summary"]["active_wave_day_count"],
            "zero_slot_veto_day_count": zero_slot_veto_day_count,
            "tiered_dual_slot_day_count": tiered_dual_slot_day_count,
            "single_slot_unobserved_day_count": single_slot_unobserved_day_count,
            "exclusion_precision": exclusion["summary"]["displaced_precision"],
            "dual_slot_weight_ratio": allocation["summary"]["reset_to_continuation_weight_ratio"],
            "authoritative_rule": (
                "the current active-wave add branch is best read as an exclusion-first slot-capacity hierarchy: "
                "either recent-reduce residue vetoes the day into zero-slot, or a local tiered dual-slot pattern survives; "
                "single-slot fallback remains unobserved"
            ),
        }
        interpretation = [
            "V1.34GH reframes slot capacity as a hierarchy question rather than a raw count question.",
            "The current strict active-wave surface first applies same-wave exclusion, then resolves into either zero-slot veto or a local tiered dual-slot configuration. A portable single-slot fallback is still unobserved.",
        ]
        return V134GHCommercialAerospaceSlotCapacityHierarchyAuditV1Report(
            summary=summary,
            hierarchy_rows=hierarchy_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GHCommercialAerospaceSlotCapacityHierarchyAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GHCommercialAerospaceSlotCapacityHierarchyAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134gh_commercial_aerospace_slot_capacity_hierarchy_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
