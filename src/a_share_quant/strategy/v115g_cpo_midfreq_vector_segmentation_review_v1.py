from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    text = str(value).strip()
    if text == "":
        return default
    try:
        return float(text)
    except (TypeError, ValueError):
        return default


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _median(values: list[float]) -> float:
    return median(values) if values else 0.0


def write_csv_rows(*, path: Path, rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


@dataclass(slots=True)
class V115GCpoMidfreqVectorSegmentationReviewReport:
    summary: dict[str, Any]
    vector_definition_rows: list[dict[str, Any]]
    context_separation_rows: list[dict[str, Any]]
    sample_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "vector_definition_rows": self.vector_definition_rows,
            "context_separation_rows": self.context_separation_rows,
            "sample_rows": self.sample_rows,
            "interpretation": self.interpretation,
        }


class V115GCpoMidfreqVectorSegmentationReviewAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    @staticmethod
    def _compute_vectors(row: dict[str, Any]) -> dict[str, float]:
        breakout_quality = _mean(
            [
                _to_float(row.get("f30_breakout_efficiency")),
                _to_float(row.get("f60_breakout_efficiency")),
                max(-0.2, _to_float(row.get("f30_close_vs_vwap"))),
                max(-0.2, _to_float(row.get("f60_close_vs_vwap"))),
            ]
        )
        close_quality = _mean(
            [
                _to_float(row.get("f30_close_location")),
                _to_float(row.get("f60_close_location")),
                1.0 + min(0.0, _to_float(row.get("f30_pullback_from_high"))),
                1.0 + min(0.0, _to_float(row.get("f60_pullback_from_high"))),
            ]
        )
        persistence = _mean(
            [
                _to_float(row.get("f30_afternoon_return")),
                _to_float(row.get("f60_afternoon_return")),
                _to_float(row.get("f30_high_time_ratio")),
                _to_float(row.get("f60_high_time_ratio")),
            ]
        )
        failure_risk = _mean(
            [
                _to_float(row.get("f30_failed_push_proxy")),
                _to_float(row.get("f60_failed_push_proxy")),
                max(0.0, -_to_float(row.get("f30_close_vs_vwap"))),
                max(0.0, -_to_float(row.get("f60_close_vs_vwap"))),
            ]
        )
        return {
            "breakout_quality_vector": round(breakout_quality, 6),
            "close_quality_vector": round(close_quality, 6),
            "persistence_vector": round(persistence, 6),
            "failure_risk_vector": round(failure_risk, 6),
        }

    @staticmethod
    def _segment_band(value: float, *, low: float, high: float) -> str:
        if value < low:
            return "low"
        if value > high:
            return "high"
        return "mid"

    def analyze(self, *, enriched_rows: list[dict[str, Any]]) -> tuple[V115GCpoMidfreqVectorSegmentationReviewReport, list[dict[str, Any]]]:
        usable_rows = [
            dict(row)
            for row in enriched_rows
            if str(row.get("action_context")) in {"add_vs_hold", "reduce_vs_hold", "close_vs_hold"}
        ]

        segmented_rows: list[dict[str, Any]] = []
        for row in usable_rows:
            vectors = self._compute_vectors(row)
            merged = {**row, **vectors}
            segmented_rows.append(merged)

        vector_keys = [
            "breakout_quality_vector",
            "close_quality_vector",
            "persistence_vector",
            "failure_risk_vector",
        ]
        thresholds: dict[str, tuple[float, float]] = {}
        for key in vector_keys:
            values = sorted(_to_float(row.get(key)) for row in segmented_rows)
            if not values:
                thresholds[key] = (0.0, 0.0)
                continue
            low = values[max(0, int(len(values) * 0.33) - 1)]
            high = values[min(len(values) - 1, int(len(values) * 0.66))]
            thresholds[key] = (low, high)

        for row in segmented_rows:
            for key in vector_keys:
                low, high = thresholds[key]
                row[f"{key}_band"] = self._segment_band(_to_float(row.get(key)), low=low, high=high)

        context_rows: list[dict[str, Any]] = []
        contexts = sorted({str(row["action_context"]) for row in segmented_rows})
        for context in contexts:
            rows = [row for row in segmented_rows if str(row["action_context"]) == context]
            context_row = {
                "action_context": context,
                "row_count": len(rows),
            }
            for key in vector_keys:
                context_row[f"{key}_mean"] = round(_mean([_to_float(row.get(key)) for row in rows]), 6)
                context_row[f"{key}_median"] = round(_median([_to_float(row.get(key)) for row in rows]), 6)
                context_row[f"{key}_high_band_rate"] = round(
                    _mean([1.0 if str(row.get(f"{key}_band")) == "high" else 0.0 for row in rows]),
                    6,
                )
            context_rows.append(context_row)

        vector_definition_rows = [
            {
                "vector_name": "breakout_quality_vector",
                "fields": [
                    "f30_breakout_efficiency",
                    "f60_breakout_efficiency",
                    "f30_close_vs_vwap",
                    "f60_close_vs_vwap",
                ],
                "why_it_exists": "Compress raw expansion and VWAP reclaim quality into one directional expression score.",
            },
            {
                "vector_name": "close_quality_vector",
                "fields": [
                    "f30_close_location",
                    "f60_close_location",
                    "f30_pullback_from_high",
                    "f60_pullback_from_high",
                ],
                "why_it_exists": "Distinguish healthy close location from weak close and heavy pullback.",
            },
            {
                "vector_name": "persistence_vector",
                "fields": [
                    "f30_afternoon_return",
                    "f60_afternoon_return",
                    "f30_high_time_ratio",
                    "f60_high_time_ratio",
                ],
                "why_it_exists": "Capture whether the move is sustaining into the later bars instead of flashing early and fading.",
            },
            {
                "vector_name": "failure_risk_vector",
                "fields": [
                    "f30_failed_push_proxy",
                    "f60_failed_push_proxy",
                    "negative_close_vs_vwap",
                ],
                "why_it_exists": "Aggregate the noisy failure-side traits into a dedicated risk vector instead of scattering them across raw features.",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v115g_cpo_midfreq_vector_segmentation_review_v1",
            "usable_row_count": len(segmented_rows),
            "context_count": len(contexts),
            "vector_count": len(vector_keys),
            "segmentation_posture": "vector_first_before_balanced_training",
            "recommended_next_posture": "build_balanced_training_view_on_segmented_vectors_not_raw_intraday_fields",
        }
        interpretation = [
            "V115G accepts that raw mid-frequency intraday fields are too noisy to feed directly into training.",
            "The right first move is to compress them into a few semantically heavier vectors before balancing or fitting.",
            "This keeps the intraday line aligned with the project objective: capture more of diffusion-style main uptrend while filtering unnecessary drawdown noise.",
        ]

        report = V115GCpoMidfreqVectorSegmentationReviewReport(
            summary=summary,
            vector_definition_rows=vector_definition_rows,
            context_separation_rows=context_rows,
            sample_rows=segmented_rows[:10],
            interpretation=interpretation,
        )
        return report, segmented_rows


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V115GCpoMidfreqVectorSegmentationReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    with (repo_root / "data" / "training" / "cpo_midfreq_action_outcome_training_rows_enriched_v1.csv").open("r", encoding="utf-8") as handle:
        enriched_rows = list(csv.DictReader(handle))
    analyzer = V115GCpoMidfreqVectorSegmentationReviewAnalyzer(repo_root=repo_root)
    result, segmented_rows = analyzer.analyze(enriched_rows=enriched_rows)
    write_csv_rows(
        path=repo_root / "data" / "training" / "cpo_midfreq_segmented_vectors_v1.csv",
        rows=segmented_rows,
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v115g_cpo_midfreq_vector_segmentation_review_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
