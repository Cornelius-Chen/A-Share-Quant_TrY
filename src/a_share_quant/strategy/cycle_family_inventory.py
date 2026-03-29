from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class CycleFamilyInventoryReport:
    summary: dict[str, Any]
    family_rows: list[dict[str, Any]]
    pocket_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "family_rows": self.family_rows,
            "pocket_rows": self.pocket_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class CycleFamilyInventoryAnalyzer:
    """Aggregate drawdown cycle families across analyzed pockets."""

    def analyze(self, *, report_specs: list[dict[str, Any]]) -> CycleFamilyInventoryReport:
        family_map: dict[str, dict[str, Any]] = {}
        pocket_rows: list[dict[str, Any]] = []

        for spec in report_specs:
            report_path = Path(str(spec["report_path"]))
            payload = load_json_report(report_path)
            mechanism_rows = list(payload.get("mechanism_rows", []))

            pocket_negative_total = 0.0
            pocket_positive_cost = 0.0
            pocket_family_counts: dict[str, int] = {}
            for row in mechanism_rows:
                family = str(row["mechanism_type"])
                cycle_sign = str(row["cycle_sign"])
                incumbent_cycle = dict(row["incumbent_cycle"])
                incumbent_pnl = float(incumbent_cycle["pnl"])
                pnl_delta = row.get("pnl_delta_vs_closest")
                if pnl_delta is None:
                    realized_edge = abs(incumbent_pnl)
                else:
                    realized_edge = float(pnl_delta)

                family_row = family_map.setdefault(
                    family,
                    {
                        "family_name": family,
                        "occurrence_count": 0,
                        "negative_row_count": 0,
                        "positive_row_count": 0,
                        "net_negative_improvement": 0.0,
                        "positive_opportunity_cost": 0.0,
                        "report_names": set(),
                        "datasets": set(),
                        "slices": set(),
                        "strategies": set(),
                        "symbols": set(),
                    },
                )
                family_row["occurrence_count"] += 1
                family_row["report_names"].add(str(spec["report_name"]))
                family_row["datasets"].add(str(spec["dataset_name"]))
                family_row["slices"].add(str(spec["slice_name"]))
                family_row["strategies"].add(str(spec["strategy_name"]))
                family_row["symbols"].add(str(spec["symbol"]))

                pocket_family_counts[family] = pocket_family_counts.get(family, 0) + 1
                if cycle_sign == "negative":
                    family_row["negative_row_count"] += 1
                    family_row["net_negative_improvement"] += realized_edge
                    pocket_negative_total += realized_edge
                else:
                    family_row["positive_row_count"] += 1
                    family_row["positive_opportunity_cost"] += abs(realized_edge)
                    pocket_positive_cost += abs(realized_edge)

            pocket_rows.append(
                {
                    "report_name": str(spec["report_name"]),
                    "dataset_name": str(spec["dataset_name"]),
                    "slice_name": str(spec["slice_name"]),
                    "strategy_name": str(spec["strategy_name"]),
                    "symbol": str(spec["symbol"]),
                    "family_counts": pocket_family_counts,
                    "negative_improvement_total": round(pocket_negative_total, 6),
                    "positive_opportunity_cost_total": round(pocket_positive_cost, 6),
                    "net_family_edge": round(pocket_negative_total - pocket_positive_cost, 6),
                }
            )

        family_rows = []
        for row in family_map.values():
            net_negative = float(row["net_negative_improvement"])
            opportunity_cost = float(row["positive_opportunity_cost"])
            family_rows.append(
                {
                    "family_name": str(row["family_name"]),
                    "occurrence_count": int(row["occurrence_count"]),
                    "report_count": len(row["report_names"]),
                    "negative_row_count": int(row["negative_row_count"]),
                    "positive_row_count": int(row["positive_row_count"]),
                    "net_negative_improvement": round(net_negative, 6),
                    "positive_opportunity_cost": round(opportunity_cost, 6),
                    "net_family_edge": round(net_negative - opportunity_cost, 6),
                    "datasets": sorted(str(item) for item in row["datasets"]),
                    "slices": sorted(str(item) for item in row["slices"]),
                    "strategies": sorted(str(item) for item in row["strategies"]),
                    "symbols": sorted(str(item) for item in row["symbols"]),
                }
            )

        family_rows.sort(
            key=lambda item: (
                -float(item["net_family_edge"]),
                -int(item["report_count"]),
                -int(item["occurrence_count"]),
            )
        )
        pocket_rows.sort(key=lambda item: -float(item["net_family_edge"]))

        summary = {
            "family_count": len(family_rows),
            "pocket_count": len(pocket_rows),
            "top_family_by_net_edge": family_rows[0]["family_name"] if family_rows else None,
            "top_pocket_by_net_edge": pocket_rows[0]["report_name"] if pocket_rows else None,
        }
        interpretation = [
            "A cycle family becomes more research-worthy when it repeats across pockets instead of appearing only once.",
            "Negative-cycle improvement should be read together with positive-cycle opportunity cost; clean specialist families preserve more net edge.",
            "Pocket-level net edge helps separate reusable structural families from noisy one-off wins.",
        ]
        return CycleFamilyInventoryReport(
            summary=summary,
            family_rows=family_rows,
            pocket_rows=pocket_rows,
            interpretation=interpretation,
        )


def write_cycle_family_inventory_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: CycleFamilyInventoryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
