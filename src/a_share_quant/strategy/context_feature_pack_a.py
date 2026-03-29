from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from a_share_quant.common.models import StockSnapshot


@dataclass(slots=True)
class ContextFeaturePackAReport:
    summary: dict[str, Any]
    slice_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "slice_rows": self.slice_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


def _quarter_bounds(slice_name: str) -> tuple[date, date]:
    year_str, quarter_str = slice_name.split("_", maxsplit=1)
    year = int(year_str)
    bounds = {
        "q1": (date(year, 1, 1), date(year, 3, 31)),
        "q2": (date(year, 4, 1), date(year, 6, 30)),
        "q3": (date(year, 7, 1), date(year, 9, 30)),
        "q4": (date(year, 10, 1), date(year, 12, 31)),
    }
    key = quarter_str.lower()
    if key not in bounds:
        raise ValueError(f"Unsupported slice name: {slice_name}")
    return bounds[key]


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _round(value: float) -> float:
    return round(float(value), 6)


def _top_symbols(summary: dict[str, Any]) -> list[str]:
    if "top_positive_symbols" in summary:
        return [str(symbol) for symbol in summary["top_positive_symbols"]]
    if "shared_top_driver" in summary:
        return [str(summary["shared_top_driver"])]
    raise ValueError("Acceptance summary must include top_positive_symbols or shared_top_driver.")


class ContextFeaturePackAAnalyzer:
    """Validate the first conditional context branch on already-closed slices."""

    def analyze(
        self,
        *,
        stock_snapshots: list[StockSnapshot],
        slice_specs: list[dict[str, Any]],
    ) -> ContextFeaturePackAReport:
        slice_rows: list[dict[str, Any]] = []
        for spec in slice_specs:
            payload = load_json_report(Path(str(spec["acceptance_report_path"])))
            summary = dict(payload.get("summary", {}))
            top_symbols = _top_symbols(summary)
            start_date, end_date = _quarter_bounds(str(spec["slice_name"]))
            rows = [
                row
                for row in stock_snapshots
                if row.symbol in top_symbols and start_date <= row.trade_date <= end_date
            ]
            if not rows:
                raise ValueError(
                    f"No stock snapshots found for {spec['slice_name']} and symbols {top_symbols}."
                )

            theme_density_mean = _mean([row.context_theme_density for row in rows])
            turnover_concentration_mean = _mean(
                [row.context_turnover_concentration for row in rows]
            )
            interaction_mean = _mean(
                [row.context_theme_turnover_interaction for row in rows]
            )
            sector_heat_mean = _mean([row.context_sector_heat for row in rows])
            sector_breadth_mean = _mean([row.context_sector_breadth for row in rows])

            slice_rows.append(
                {
                    "dataset_name": str(spec["dataset_name"]),
                    "slice_name": str(spec["slice_name"]),
                    "slice_role": str(spec["slice_role"]),
                    "acceptance_posture": summary.get("acceptance_posture"),
                    "top_symbols": top_symbols,
                    "row_count": len(rows),
                    "theme_density_mean": _round(theme_density_mean),
                    "turnover_concentration_mean": _round(turnover_concentration_mean),
                    "theme_turnover_interaction_mean": _round(interaction_mean),
                    "sector_heat_mean": _round(sector_heat_mean),
                    "sector_breadth_mean": _round(sector_breadth_mean),
                }
            )

        max_interaction = max(float(row["theme_turnover_interaction_mean"]) for row in slice_rows)
        min_interaction = min(float(row["theme_turnover_interaction_mean"]) for row in slice_rows)
        max_heat = max(float(row["sector_heat_mean"]) for row in slice_rows)
        interaction_values = [float(row["theme_turnover_interaction_mean"]) for row in slice_rows]
        heat_values = [float(row["sector_heat_mean"]) for row in slice_rows]
        breadth_values = [float(row["sector_breadth_mean"]) for row in slice_rows]
        bucket_counts: dict[str, int] = {}
        for row in slice_rows:
            interaction_value = float(row["theme_turnover_interaction_mean"])
            heat_value = float(row["sector_heat_mean"])
            if interaction_value == max_interaction:
                bucket = "interaction_high"
            elif heat_value == max_heat and interaction_value == min_interaction:
                bucket = "sector_heat_led"
            else:
                bucket = "turnover_led_theme_light"
            row["context_bucket"] = bucket
            bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1

        summary = {
            "slice_count": len(slice_rows),
            "bucket_counts": bucket_counts,
            "interaction_spread": _round(max(interaction_values) - min(interaction_values)),
            "heat_spread": _round(max(heat_values) - min(heat_values)),
            "breadth_spread": _round(max(breadth_values) - min(breadth_values)),
            "recommended_next_feature_branch": "conditioned_late_quality_on_theme_turnover_context",
            "defer_sector_heat_branch": (
                (max(interaction_values) - min(interaction_values))
                >= max(max(heat_values) - min(heat_values), max(breadth_values) - min(breadth_values))
            ),
        }
        interpretation = [
            "Context-feature-pack-a is only useful if explicit context fields still separate already-closed slices strongly enough to guide the next feature branch.",
            "If theme-density plus turnover concentration separates q2/q3/q4 more strongly than sector heat or breadth, the next branch should condition late-quality logic on that interaction first.",
            "This remains a conditioned-global path, not evidence for direct per-sector training.",
        ]
        return ContextFeaturePackAReport(
            summary=summary,
            slice_rows=slice_rows,
            interpretation=interpretation,
        )


def write_context_feature_pack_a_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: ContextFeaturePackAReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
