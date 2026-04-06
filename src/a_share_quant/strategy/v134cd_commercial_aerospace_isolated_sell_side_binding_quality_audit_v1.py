from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134CDCommercialAerospaceIsolatedSellSideBindingQualityAuditV1Report:
    summary: dict[str, Any]
    symbol_rows: list[dict[str, Any]]
    trigger_tier_rows: list[dict[str, Any]]
    clip_rows: list[dict[str, Any]]
    skip_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "symbol_rows": self.symbol_rows,
            "trigger_tier_rows": self.trigger_tier_rows,
            "clip_rows": self.clip_rows,
            "skip_rows": self.skip_rows,
            "interpretation": self.interpretation,
        }


class V134CDCommercialAerospaceIsolatedSellSideBindingQualityAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.lane_path = (
            repo_root / "reports" / "analysis" / "v134cb_commercial_aerospace_isolated_sell_side_shadow_lane_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_isolated_sell_side_binding_quality_audit_v1.csv"
        )

    @staticmethod
    def _aggregate_symbol_rows(session_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in session_rows:
            buckets[row["symbol"]].append(row)

        aggregated: list[dict[str, Any]] = []
        for symbol, subset in sorted(buckets.items()):
            executed = [row for row in subset if row["lane_status"] == "executed"]
            aggregated.append(
                {
                    "symbol": symbol,
                    "session_count": len(subset),
                    "executed_session_count": len(executed),
                    "skip_no_inventory_count": sum(
                        1 for row in subset if row["skip_reason"] == "no_eligible_start_of_day_inventory"
                    ),
                    "skip_mild_count": sum(1 for row in subset if row["skip_reason"] == "mild_is_governance_only"),
                    "protected_mark_to_close_total": round(
                        sum(float(row["protected_mark_to_close"]) for row in subset),
                        4,
                    ),
                    "protected_mark_to_close_mean_if_executed": round(
                        sum(float(row["protected_mark_to_close"]) for row in executed) / len(executed),
                        4,
                    )
                    if executed
                    else 0.0,
                    "same_day_reduce_close_clipped_total": sum(
                        int(row["same_day_reduce_close_clipped"]) for row in subset
                    ),
                }
            )
        return aggregated

    @staticmethod
    def _aggregate_trigger_tier_rows(order_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in order_rows:
            buckets[row["trigger_tier"]].append(row)

        aggregated: list[dict[str, Any]] = []
        for trigger_tier, subset in sorted(buckets.items()):
            aggregated.append(
                {
                    "trigger_tier": trigger_tier,
                    "order_count": len(subset),
                    "sell_quantity_total": sum(int(row["sell_quantity"]) for row in subset),
                    "protected_mark_to_close_total": round(
                        sum(float(row["protected_mark_to_close"]) for row in subset),
                        4,
                    ),
                    "protected_mark_to_close_mean": round(
                        sum(float(row["protected_mark_to_close"]) for row in subset) / len(subset),
                        4,
                    ),
                }
            )
        return aggregated

    def analyze(self) -> V134CDCommercialAerospaceIsolatedSellSideBindingQualityAuditV1Report:
        lane = json.loads(self.lane_path.read_text(encoding="utf-8"))
        session_rows = lane["session_rows"]
        order_rows = lane["order_rows"]
        reconciliation_rows = lane["reconciliation_rows"]

        symbol_rows = self._aggregate_symbol_rows(session_rows)
        trigger_tier_rows = self._aggregate_trigger_tier_rows(order_rows)
        clip_rows = [
            {
                "trade_date": row["trade_date"],
                "symbol": row["symbol"],
                "same_day_reduce_close_requested": int(row["same_day_reduce_close_requested"]),
                "same_day_reduce_close_effective": int(row["same_day_reduce_close_effective"]),
                "same_day_reduce_close_clipped": int(row["same_day_reduce_close_clipped"]),
                "same_day_new_lots_protected": int(row["same_day_new_lots_protected"]),
            }
            for row in reconciliation_rows
            if int(row["same_day_reduce_close_clipped"]) > 0
        ]
        skip_rows = [
            {
                "trade_date": row["trade_date"],
                "symbol": row["symbol"],
                "skip_reason": row["skip_reason"],
                "same_day_new_lots_quantity": int(row["same_day_new_lots_quantity"]),
                "start_of_day_quantity": int(row["start_of_day_quantity"]),
                "eligible_intraday_sell_quantity": int(row["eligible_intraday_sell_quantity"]),
            }
            for row in session_rows
            if row["lane_status"] == "skipped"
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(symbol_rows[0].keys()))
            writer.writeheader()
            writer.writerows(symbol_rows)

        executed_session_count = sum(1 for row in session_rows if row["lane_status"] == "executed")
        total_protected_mark_to_close = round(sum(float(row["protected_mark_to_close"]) for row in order_rows), 4)
        same_day_new_lots_protected_total = sum(int(row["same_day_new_lots_protected"]) for row in reconciliation_rows)
        clipped_quantity_total = sum(int(row["same_day_reduce_close_clipped"]) for row in reconciliation_rows)
        no_inventory_same_day_new_lots_only_count = sum(
            1
            for row in skip_rows
            if row["skip_reason"] == "no_eligible_start_of_day_inventory" and row["same_day_new_lots_quantity"] > 0
        )
        best_symbol = max(symbol_rows, key=lambda row: float(row["protected_mark_to_close_total"]))
        best_trigger_tier = max(trigger_tier_rows, key=lambda row: float(row["protected_mark_to_close_total"]))

        summary = {
            "acceptance_posture": "freeze_v134cd_commercial_aerospace_isolated_sell_side_binding_quality_audit_v1",
            "broader_hit_session_count": len(session_rows),
            "executed_session_count": executed_session_count,
            "executed_session_share": round(executed_session_count / len(session_rows), 8),
            "total_protected_mark_to_close": total_protected_mark_to_close,
            "protected_mark_to_close_mean_if_executed": round(
                total_protected_mark_to_close / executed_session_count, 4
            )
            if executed_session_count
            else 0.0,
            "best_symbol": best_symbol["symbol"],
            "best_trigger_tier": best_trigger_tier["trigger_tier"],
            "same_day_new_lots_protected_total": same_day_new_lots_protected_total,
            "clipped_reconciliation_count": len(clip_rows),
            "clipped_quantity_total": clipped_quantity_total,
            "skip_no_inventory_count": sum(
                1 for row in skip_rows if row["skip_reason"] == "no_eligible_start_of_day_inventory"
            ),
            "no_inventory_same_day_new_lots_only_count": no_inventory_same_day_new_lots_only_count,
            "quality_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_isolated_sell_side_binding_quality_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34CD converts the first isolated sell-side lane from a runnable surface into a binding-quality audit.",
            "The point is to verify that the lane protects real carried inventory, preserves same-day new lots, and only clips later EOD actions when the carried bucket has already been consumed intraday.",
        ]
        return V134CDCommercialAerospaceIsolatedSellSideBindingQualityAuditV1Report(
            summary=summary,
            symbol_rows=symbol_rows,
            trigger_tier_rows=trigger_tier_rows,
            clip_rows=clip_rows,
            skip_rows=skip_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CDCommercialAerospaceIsolatedSellSideBindingQualityAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CDCommercialAerospaceIsolatedSellSideBindingQualityAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cd_commercial_aerospace_isolated_sell_side_binding_quality_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
