from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from a_share_quant.common.models import StockSnapshot


@dataclass(slots=True)
class ContextConditionedLateQualityReport:
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


class ContextConditionedLateQualityAnalyzer:
    """Check whether late-quality misses cluster in theme/turnover-heavy context."""

    def analyze(
        self,
        *,
        stock_snapshots: list[StockSnapshot],
        slice_specs: list[dict[str, Any]],
        late_quality_threshold: float,
        non_junk_threshold: float,
        resonance_floor: float,
        high_interaction_threshold: float,
        medium_interaction_threshold: float,
        near_threshold_gap: float,
    ) -> ContextConditionedLateQualityReport:
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

            below_threshold_rows = 0
            structurally_supported_rows = 0
            candidate_count = 0
            high_candidate_count = 0
            medium_candidate_count = 0
            low_candidate_count = 0

            for row in rows:
                late_gap = late_quality_threshold - float(row.late_mover_quality)
                raw_gap = late_quality_threshold - float(row.late_quality_raw_score)
                non_junk_margin = float(row.non_junk_composite_score) - non_junk_threshold
                structurally_supported = non_junk_margin >= 0.0 and float(row.resonance) >= resonance_floor
                if late_gap > 0:
                    below_threshold_rows += 1
                if structurally_supported:
                    structurally_supported_rows += 1

                interaction_value = float(row.context_theme_turnover_interaction)
                if interaction_value >= high_interaction_threshold:
                    context_bucket = "interaction_high"
                elif interaction_value >= medium_interaction_threshold:
                    context_bucket = "interaction_mid"
                else:
                    context_bucket = "interaction_low"

                conditioning_candidate = (
                    0.0 < late_gap <= near_threshold_gap
                    and structurally_supported
                    and context_bucket != "interaction_low"
                )
                if conditioning_candidate:
                    candidate_count += 1
                    if context_bucket == "interaction_high":
                        high_candidate_count += 1
                    elif context_bucket == "interaction_mid":
                        medium_candidate_count += 1
                    else:
                        low_candidate_count += 1
                    candidate_rows.append(
                        {
                            "dataset_name": str(spec["dataset_name"]),
                            "slice_name": str(spec["slice_name"]),
                            "slice_role": str(spec["slice_role"]),
                            "symbol": row.symbol,
                            "trade_date": row.trade_date.isoformat(),
                            "late_mover_quality": _round(row.late_mover_quality),
                            "late_quality_raw_score": _round(row.late_quality_raw_score),
                            "late_gap_to_threshold": _round(late_gap),
                            "raw_gap_to_threshold": _round(raw_gap),
                            "non_junk_margin": _round(non_junk_margin),
                            "resonance": _round(row.resonance),
                            "context_theme_density": _round(row.context_theme_density),
                            "context_turnover_concentration": _round(row.context_turnover_concentration),
                            "context_theme_turnover_interaction": _round(interaction_value),
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
                    "below_late_threshold_count": below_threshold_rows,
                    "structurally_supported_count": structurally_supported_rows,
                    "conditioning_candidate_count": candidate_count,
                    "high_interaction_candidate_count": high_candidate_count,
                    "medium_interaction_candidate_count": medium_candidate_count,
                    "low_interaction_candidate_count": low_candidate_count,
                    "mean_theme_turnover_interaction": _round(
                        _mean([float(row.context_theme_turnover_interaction) for row in rows])
                    ),
                    "mean_late_gap_to_threshold": _round(
                        _mean(
                            [
                                max(0.0, late_quality_threshold - float(row.late_mover_quality))
                                for row in rows
                            ]
                        )
                    ),
                }
            )

        candidate_bucket_counts = {
            "interaction_high": sum(
                1 for row in candidate_rows if str(row["context_bucket"]) == "interaction_high"
            ),
            "interaction_mid": sum(
                1 for row in candidate_rows if str(row["context_bucket"]) == "interaction_mid"
            ),
            "interaction_low": sum(
                1 for row in candidate_rows if str(row["context_bucket"]) == "interaction_low"
            ),
        }
        summary = {
            "slice_count": len(slice_rows),
            "candidate_row_count": len(candidate_rows),
            "candidate_bucket_counts": candidate_bucket_counts,
            "candidate_slice_names": sorted(
                {str(row["slice_name"]) for row in candidate_rows}
            ),
            "recommended_conditioning_branch": self._recommended_branch(candidate_bucket_counts),
            "recommended_conditioning_posture": self._recommended_posture(candidate_bucket_counts),
        }
        interpretation = [
            "This branch should only continue if high- or mid-interaction rows repeatedly produce near-threshold late-quality misses while non-junk and resonance stay structurally intact.",
            "If those rows cluster in the interaction-led buckets, the next useful step is to condition late-quality logic on theme-turnover interaction rather than split the whole model by sector.",
            "If candidate rows are sparse or mostly low-interaction, the context branch should stop before it becomes another descriptive side path.",
        ]
        candidate_rows.sort(key=lambda item: (str(item["slice_name"]), str(item["symbol"]), str(item["trade_date"])))
        slice_rows.sort(key=lambda item: str(item["slice_name"]))
        return ContextConditionedLateQualityReport(
            summary=summary,
            slice_rows=slice_rows,
            candidate_rows=candidate_rows,
            interpretation=interpretation,
        )

    def _recommended_branch(self, candidate_bucket_counts: dict[str, int]) -> str:
        high_count = candidate_bucket_counts.get("interaction_high", 0)
        medium_count = candidate_bucket_counts.get("interaction_mid", 0)
        if high_count + medium_count > 0:
            return "conditioned_late_quality_on_theme_turnover_context"
        return "defer_conditioned_late_quality_branch"

    def _recommended_posture(self, candidate_bucket_counts: dict[str, int]) -> str:
        high_count = candidate_bucket_counts.get("interaction_high", 0)
        medium_count = candidate_bucket_counts.get("interaction_mid", 0)
        low_count = candidate_bucket_counts.get("interaction_low", 0)
        if high_count > 0 and high_count + medium_count > low_count:
            return "continue_context_conditioning_branch"
        if medium_count > 0 and high_count == 0:
            return "continue_context_conditioning_branch_as_mid_interaction_only"
        return "close_context_conditioning_branch_as_not_actionable"


def write_context_conditioned_late_quality_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: ContextConditionedLateQualityReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
