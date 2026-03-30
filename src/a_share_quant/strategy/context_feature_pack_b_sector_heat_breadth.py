from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from a_share_quant.common.models import StockSnapshot


@dataclass(slots=True)
class ContextFeaturePackBReport:
    summary: dict[str, Any]
    slice_rows: list[dict[str, Any]]
    candidate_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "slice_rows": self.slice_rows,
            "candidate_rows": self.candidate_rows,
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


class ContextFeaturePackBSectorHeatBreadthAnalyzer:
    """Audit whether near-threshold non-junk misses cluster in sector heat/breadth context."""

    def analyze(
        self,
        *,
        stock_snapshots: list[StockSnapshot],
        slice_specs: list[dict[str, Any]],
        non_junk_threshold: float,
        late_quality_floor: float,
        resonance_floor: float,
        high_sector_heat_threshold: float,
        high_sector_breadth_threshold: float,
        near_threshold_gap: float,
    ) -> ContextFeaturePackBReport:
        slice_rows: list[dict[str, Any]] = []
        candidate_rows: list[dict[str, Any]] = []

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

            candidate_count = 0
            heat_breadth_candidate_count = 0
            heat_only_candidate_count = 0
            breadth_only_candidate_count = 0

            for row in rows:
                non_junk_gap = non_junk_threshold - float(row.non_junk_composite_score)
                structurally_supported = (
                    float(row.late_mover_quality) >= late_quality_floor
                    and float(row.resonance) >= resonance_floor
                )
                sector_heat = float(row.context_sector_heat)
                sector_breadth = float(row.context_sector_breadth)
                heat_high = sector_heat >= high_sector_heat_threshold
                breadth_high = sector_breadth >= high_sector_breadth_threshold
                if heat_high and breadth_high:
                    context_bucket = "heat_breadth_high"
                elif heat_high:
                    context_bucket = "heat_only"
                elif breadth_high:
                    context_bucket = "breadth_only"
                else:
                    context_bucket = "heat_breadth_low"

                conditioning_candidate = (
                    0.0 < non_junk_gap <= near_threshold_gap and structurally_supported
                )
                if conditioning_candidate:
                    candidate_count += 1
                    if context_bucket == "heat_breadth_high":
                        heat_breadth_candidate_count += 1
                    elif context_bucket == "heat_only":
                        heat_only_candidate_count += 1
                    elif context_bucket == "breadth_only":
                        breadth_only_candidate_count += 1

                    candidate_rows.append(
                        {
                            "dataset_name": str(spec["dataset_name"]),
                            "slice_name": str(spec["slice_name"]),
                            "slice_role": str(spec["slice_role"]),
                            "symbol": row.symbol,
                            "trade_date": row.trade_date.isoformat(),
                            "non_junk_composite_score": _round(row.non_junk_composite_score),
                            "non_junk_gap_to_threshold": _round(non_junk_gap),
                            "late_mover_quality": _round(row.late_mover_quality),
                            "resonance": _round(row.resonance),
                            "context_sector_heat": _round(sector_heat),
                            "context_sector_breadth": _round(sector_breadth),
                            "context_bucket": context_bucket,
                        }
                    )

            slice_rows.append(
                {
                    "dataset_name": str(spec["dataset_name"]),
                    "slice_name": str(spec["slice_name"]),
                    "slice_role": str(spec["slice_role"]),
                    "acceptance_posture": summary.get("acceptance_posture"),
                    "top_symbols": top_symbols,
                    "row_count": len(rows),
                    "conditioning_candidate_count": candidate_count,
                    "heat_breadth_high_candidate_count": heat_breadth_candidate_count,
                    "heat_only_candidate_count": heat_only_candidate_count,
                    "breadth_only_candidate_count": breadth_only_candidate_count,
                    "mean_sector_heat": _round(_mean([row.context_sector_heat for row in rows])),
                    "mean_sector_breadth": _round(_mean([row.context_sector_breadth for row in rows])),
                    "mean_non_junk_gap_to_threshold": _round(
                        _mean(
                            [
                                max(0.0, non_junk_threshold - float(row.non_junk_composite_score))
                                for row in rows
                            ]
                        )
                    ),
                }
            )

        candidate_bucket_counts = {
            "heat_breadth_high": sum(
                1 for row in candidate_rows if str(row["context_bucket"]) == "heat_breadth_high"
            ),
            "heat_only": sum(1 for row in candidate_rows if str(row["context_bucket"]) == "heat_only"),
            "breadth_only": sum(
                1 for row in candidate_rows if str(row["context_bucket"]) == "breadth_only"
            ),
            "heat_breadth_low": sum(
                1 for row in candidate_rows if str(row["context_bucket"]) == "heat_breadth_low"
            ),
        }
        candidate_slice_names = sorted({str(row["slice_name"]) for row in candidate_rows})
        ready_for_conditioned_branch = (
            len(candidate_rows) >= 3 and len(candidate_slice_names) >= 2
        )
        summary = {
            "slice_count": len(slice_rows),
            "candidate_row_count": len(candidate_rows),
            "candidate_slice_names": candidate_slice_names,
            "candidate_bucket_counts": candidate_bucket_counts,
            "recommended_next_feature_branch": (
                "conditioned_non_junk_on_sector_heat_breadth_context"
                if ready_for_conditioned_branch
                else "close_sector_heat_breadth_context_branch_as_sparse"
            ),
            "recommended_posture": (
                "continue_sector_heat_breadth_context_branch"
                if ready_for_conditioned_branch
                else "close_sector_heat_breadth_context_branch_as_sparse"
            ),
            "do_continue_context_feature_pack_b": ready_for_conditioned_branch,
        }
        interpretation = [
            "This branch should continue only if near-threshold non-junk misses recur across multiple closed slices while late-quality and resonance remain structurally intact.",
            "If the evidence collapses into one symbol or one slice, sector heat and breadth should remain explanatory context rather than become another retained hierarchy rule.",
            "This is still a conditioned feature audit and does not justify per-sector training.",
        ]
        candidate_rows.sort(key=lambda item: (str(item["slice_name"]), str(item["symbol"]), str(item["trade_date"])))
        slice_rows.sort(key=lambda item: str(item["slice_name"]))
        return ContextFeaturePackBReport(
            summary=summary,
            slice_rows=slice_rows,
            candidate_rows=candidate_rows,
            interpretation=interpretation,
        )


def write_context_feature_pack_b_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: ContextFeaturePackBReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
