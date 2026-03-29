from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from a_share_quant.common.models import SectorSnapshot, StockSnapshot


@dataclass(slots=True)
class SectorThemeContextAuditReport:
    summary: dict[str, Any]
    slice_rows: list[dict[str, Any]]
    axis_rankings: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "slice_rows": self.slice_rows,
            "axis_rankings": self.axis_rankings,
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
    quarter_map = {
        "q1": (date(year, 1, 1), date(year, 3, 31)),
        "q2": (date(year, 4, 1), date(year, 6, 30)),
        "q3": (date(year, 7, 1), date(year, 9, 30)),
        "q4": (date(year, 10, 1), date(year, 12, 31)),
    }
    key = quarter_str.lower()
    if key not in quarter_map:
        raise ValueError(f"Unsupported slice name: {slice_name}")
    return quarter_map[key]


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _round(value: float) -> float:
    return round(float(value), 6)


def _extract_top_symbols(summary: dict[str, Any]) -> list[str]:
    if "top_positive_symbols" in summary:
        return [str(symbol) for symbol in summary["top_positive_symbols"]]
    if "shared_top_driver" in summary and summary["shared_top_driver"]:
        return [str(summary["shared_top_driver"])]
    if "top_positive_symbols_by_strategy" in summary:
        seen: list[str] = []
        for symbol in summary["top_positive_symbols_by_strategy"]:
            symbol_str = str(symbol)
            if symbol_str not in seen:
                seen.append(symbol_str)
        return seen
    raise ValueError("Acceptance summary must include top_positive_symbols or shared_top_driver.")


def _context_tags(
    *,
    sector_heat_mean: float,
    sector_breadth_mean: float,
    concept_support_mean: float,
    sector_top_turnover_share_mean: float,
) -> list[str]:
    tags: list[str] = []
    tags.append("hot_sector" if sector_heat_mean >= 0.54 else "cool_sector")
    tags.append("broad_sector" if sector_breadth_mean >= 0.5 else "narrow_sector")
    tags.append("theme_loaded" if concept_support_mean >= 0.45 else "theme_light")
    tags.append(
        "concentrated_turnover"
        if sector_top_turnover_share_mean >= 0.7
        else "balanced_turnover"
    )
    return tags


class SectorThemeContextAuditAnalyzer:
    """Audit whether slice-level specialist pockets separate cleanly by sector/theme state."""

    def analyze(
        self,
        *,
        stock_snapshots: list[StockSnapshot],
        sector_snapshots: list[SectorSnapshot],
        slice_specs: list[dict[str, Any]],
    ) -> SectorThemeContextAuditReport:
        sector_lookup = {
            (snapshot.trade_date, snapshot.sector_id): snapshot
            for snapshot in sector_snapshots
        }

        slice_rows: list[dict[str, Any]] = []
        for spec in slice_specs:
            summary = dict(load_json_report(Path(str(spec["acceptance_report_path"]))).get("summary", {}))
            top_symbols = _extract_top_symbols(summary)
            start_date, end_date = _quarter_bounds(str(spec["slice_name"]))
            relevant_rows = [
                snapshot
                for snapshot in stock_snapshots
                if snapshot.symbol in top_symbols and start_date <= snapshot.trade_date <= end_date
            ]
            if not relevant_rows:
                raise ValueError(
                    f"No stock snapshots found for slice {spec['slice_name']} and symbols {top_symbols}."
                )

            sector_heat_values: list[float] = []
            sector_breadth_values: list[float] = []
            for row in relevant_rows:
                sector_snapshot = sector_lookup.get((row.trade_date, row.sector_id))
                if sector_snapshot is None:
                    continue
                sector_heat_values.append(
                    _mean(
                        [
                            sector_snapshot.activity,
                            sector_snapshot.leader_strength,
                            sector_snapshot.money_making,
                            sector_snapshot.relative_strength,
                        ]
                    )
                )
                sector_breadth_values.append(
                    _mean([sector_snapshot.persistence, sector_snapshot.diffusion])
                )

            concept_support_mean = _mean([row.concept_support for row in relevant_rows])
            concept_count_mean = _mean([float(row.concept_count) for row in relevant_rows])
            theme_density_mean = _mean(
                [
                    row.concept_support * min(float(row.concept_count) / 3.0, 1.0)
                    for row in relevant_rows
                ]
            )
            sector_top_turnover_share_mean = _mean(
                [row.liquidity_sector_top_turnover_share for row in relevant_rows]
            )
            sector_turnover_share_gap_mean = _mean(
                [row.liquidity_sector_turnover_share_gap for row in relevant_rows]
            )
            late_quality_raw_mean = _mean([row.late_quality_raw_score for row in relevant_rows])
            late_quality_margin_mean = _mean(
                [row.late_quality_raw_score - 0.55 for row in relevant_rows]
            )

            slice_row = {
                "dataset_name": str(spec["dataset_name"]),
                "slice_name": str(spec["slice_name"]),
                "slice_role": str(spec["slice_role"]),
                "acceptance_posture": summary.get("acceptance_posture"),
                "top_symbols": top_symbols,
                "row_count": len(relevant_rows),
                "sector_heat_mean": _round(_mean(sector_heat_values)),
                "sector_breadth_mean": _round(_mean(sector_breadth_values)),
                "concept_support_mean": _round(concept_support_mean),
                "concept_count_mean": _round(concept_count_mean),
                "theme_density_mean": _round(theme_density_mean),
                "sector_top_turnover_share_mean": _round(sector_top_turnover_share_mean),
                "sector_turnover_share_gap_mean": _round(sector_turnover_share_gap_mean),
                "late_quality_raw_mean": _round(late_quality_raw_mean),
                "late_quality_margin_mean": _round(late_quality_margin_mean),
                "context_tags": _context_tags(
                    sector_heat_mean=_mean(sector_heat_values),
                    sector_breadth_mean=_mean(sector_breadth_values),
                    concept_support_mean=concept_support_mean,
                    sector_top_turnover_share_mean=sector_top_turnover_share_mean,
                ),
            }
            slice_rows.append(slice_row)

        axis_specs = {
            "sector_heat_mean": "sector_state_heat_breadth_context",
            "sector_breadth_mean": "sector_state_heat_breadth_context",
            "concept_support_mean": "theme_load_plus_turnover_concentration_context",
            "theme_density_mean": "theme_load_plus_turnover_concentration_context",
            "sector_top_turnover_share_mean": "theme_load_plus_turnover_concentration_context",
            "sector_turnover_share_gap_mean": "theme_load_plus_turnover_concentration_context",
            "late_quality_margin_mean": "late_quality_context_follow_on",
        }

        axis_rankings: list[dict[str, Any]] = []
        for axis_name, feature_group in axis_specs.items():
            values = [float(row[axis_name]) for row in slice_rows]
            axis_rankings.append(
                {
                    "axis_name": axis_name,
                    "spread": _round(max(values) - min(values)),
                    "mean_value": _round(_mean(values)),
                    "proposed_feature_group": feature_group,
                }
            )
        axis_rankings.sort(key=lambda item: item["spread"], reverse=True)

        recommended_group = axis_rankings[0]["proposed_feature_group"] if axis_rankings else "none"
        second_group = "none"
        for axis_row in axis_rankings:
            candidate_group = str(axis_row["proposed_feature_group"])
            if candidate_group != recommended_group:
                second_group = candidate_group
                break
        summary = {
            "slice_count": len(slice_rows),
            "dataset_names": sorted({row["dataset_name"] for row in slice_rows}),
            "slice_names": [row["slice_name"] for row in slice_rows],
            "recommended_first_conditional_feature_group": recommended_group,
            "recommended_second_conditional_feature_group": second_group,
            "highest_spread_axis": axis_rankings[0]["axis_name"] if axis_rankings else None,
            "second_spread_axis": axis_rankings[1]["axis_name"] if len(axis_rankings) > 1 else None,
            "sector_conditioning_needed": True,
            "do_sector_specific_training_now": False,
        }
        interpretation = [
            "This audit is a conditioning step, not a mandate to split the strategy into per-sector models.",
            "If slice-level specialist behavior separates first by theme-load and turnover concentration, the correct next step is to add sector/theme state as conditional features rather than train separate board models.",
            "If a later audit shows the same family only survives inside a stable sector-state bucket, then environment grouping becomes a justified next step. This report alone does not justify direct per-sector training.",
        ]
        return SectorThemeContextAuditReport(
            summary=summary,
            slice_rows=slice_rows,
            axis_rankings=axis_rankings,
            interpretation=interpretation,
        )


def write_sector_theme_context_audit_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: SectorThemeContextAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
