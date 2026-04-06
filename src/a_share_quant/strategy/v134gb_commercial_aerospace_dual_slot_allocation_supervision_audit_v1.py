from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134GBCommercialAerospaceDualSlotAllocationSupervisionAuditV1Report:
    summary: dict[str, Any]
    allocation_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "allocation_rows": self.allocation_rows,
            "interpretation": self.interpretation,
        }


class V134GBCommercialAerospaceDualSlotAllocationSupervisionAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.dual_slot_report_path = (
            repo_root / "reports" / "analysis" / "v134fz_commercial_aerospace_active_wave_dual_slot_permission_audit_v1.json"
        )
        self.orders_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_tail_weakdrift_full_orders_v1.csv"
        )

    def analyze(self) -> V134GBCommercialAerospaceDualSlotAllocationSupervisionAuditV1Report:
        dual_slot_report = json.loads(self.dual_slot_report_path.read_text(encoding="utf-8"))
        slot_by_state = {row["selection_state"]: row["slot_name"] for row in dual_slot_report["slot_rows"]}

        with self.orders_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            order_rows = list(csv.DictReader(handle))

        selected_day = "20251219"
        day_order_rows = [
            row for row in order_rows if row["execution_trade_date"] == selected_day and row["action"] in {"open", "add"}
        ]

        # The current dual-slot surface has one same-symbol continuation selected state and one clean-reset selected state.
        continuation_row = next(row for row in day_order_rows if row["symbol"] == "000738" and row["action"] == "add")
        reset_row = next(row for row in day_order_rows if row["symbol"] == "002085" and row["action"] == "open")

        continuation_weight = float(continuation_row["weight_vs_initial_capital"])
        reset_weight = float(reset_row["weight_vs_initial_capital"])

        allocation_rows = [
            {
                "trade_date": selected_day,
                "slot_name": slot_by_state["same_symbol_continuation_selected"],
                "symbol": continuation_row["symbol"],
                "action": continuation_row["action"],
                "weight_vs_initial_capital": continuation_weight,
                "allocation_role": "secondary_incremental_slot",
            },
            {
                "trade_date": selected_day,
                "slot_name": slot_by_state["clean_reset_candidate"],
                "symbol": reset_row["symbol"],
                "action": reset_row["action"],
                "weight_vs_initial_capital": reset_weight,
                "allocation_role": "primary_reset_slot",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v134gb_commercial_aerospace_dual_slot_allocation_supervision_audit_v1",
            "dual_slot_day_count": 1,
            "allocation_row_count": len(allocation_rows),
            "continuation_slot_weight": round(continuation_weight, 6),
            "reset_slot_weight": round(reset_weight, 6),
            "reset_to_continuation_weight_ratio": round(reset_weight / continuation_weight, 8),
            "authoritative_rule": (
                "the current local dual-slot day supports a primary-reset plus secondary-continuation allocation reading, but only as local supervision"
            ),
        }
        interpretation = [
            "V1.34GB asks the smallest allocation question after dual-slot permission becomes credible: when both slots are actually live on the same day, do they look symmetric or tiered?",
            "The current local answer is tiered. The reset slot carries the larger primary participation, while the continuation slot behaves like a smaller incremental companion slot.",
        ]
        return V134GBCommercialAerospaceDualSlotAllocationSupervisionAuditV1Report(
            summary=summary,
            allocation_rows=allocation_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GBCommercialAerospaceDualSlotAllocationSupervisionAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GBCommercialAerospaceDualSlotAllocationSupervisionAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134gb_commercial_aerospace_dual_slot_allocation_supervision_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
