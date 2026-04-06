from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


FEATURE_COLUMNS = [
    "minute_return",
    "range_pct",
    "body_pct",
    "upper_shadow_pct",
    "lower_shadow_pct",
    "close_location",
    "close_vs_vwap",
    "pullback_from_high",
    "push_efficiency",
    "micro_pullback_depth",
    "volume_ratio_5",
    "value_ratio_5",
    "prev_close_gap",
    "reclaim_after_break_score",
    "burst_then_fade_score",
    "late_session_integrity_score",
]
HORIZON = 5


def _band(value: float, q_low: float, q_high: float) -> str:
    if value <= q_low:
        return "low"
    if value >= q_high:
        return "high"
    return "mid"


@dataclass(slots=True)
class V122BCpo1MinFamilyShortHorizonExpectancyAuditReport:
    summary: dict[str, Any]
    family_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "family_rows": self.family_rows,
            "interpretation": self.interpretation,
        }


class V122BCpo1MinFamilyShortHorizonExpectancyAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _candidate_bands(self) -> tuple[set[str], set[str]]:
        reports_dir = self.repo_root / "reports" / "analysis"
        with (reports_dir / "v121y_cpo_recent_1min_supportive_continuation_candidate_discovery_v1.json").open(
            "r",
            encoding="utf-8",
        ) as handle:
            supportive = json.load(handle)
        with (reports_dir / "v121z_cpo_recent_1min_burst_fade_trap_candidate_discovery_v1.json").open(
            "r",
            encoding="utf-8",
        ) as handle:
            trap = json.load(handle)
        supportive_bands = set(supportive["summary"]["candidate_band_names"])
        trap_bands = set(trap["summary"]["candidate_band_names"])
        return supportive_bands, trap_bands

    def analyze(self) -> V122BCpo1MinFamilyShortHorizonExpectancyAuditReport:
        table_path = self.repo_root / "data" / "training" / "cpo_recent_1min_microstructure_feature_table_v1.csv"
        with table_path.open("r", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

        matrix = np.array([[float(row[column]) for column in FEATURE_COLUMNS] for row in rows], dtype=float)
        means = matrix.mean(axis=0)
        stds = matrix.std(axis=0)
        stds[stds == 0.0] = 1.0
        standardized = (matrix - means) / stds
        covariance = np.cov(standardized, rowvar=False)
        eigenvalues, eigenvectors = np.linalg.eigh(covariance)
        order = np.argsort(eigenvalues)[::-1]
        eigenvectors = eigenvectors[:, order]
        projection = standardized @ eigenvectors[:, :2]
        pc1_values = projection[:, 0]
        pc2_values = projection[:, 1]
        pc1_q_low, pc1_q_high = np.quantile(pc1_values, [1 / 3, 2 / 3])
        pc2_q_low, pc2_q_high = np.quantile(pc2_values, [1 / 3, 2 / 3])

        supportive_bands, trap_bands = self._candidate_bands()
        grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for index, row in enumerate(rows):
            band_name = f"pc1_{_band(pc1_values[index], pc1_q_low, pc1_q_high)}__pc2_{_band(pc2_values[index], pc2_q_low, pc2_q_high)}"
            family = ""
            if band_name in supportive_bands:
                family = "supportive_continuation"
            elif band_name in trap_bands:
                family = "burst_fade_trap"
            if not family:
                continue
            grouped.setdefault((family, row["symbol"]), []).append(
                {
                    "close": float(row["close"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                }
            )

        family_metrics: dict[str, dict[str, float]] = {
            "supportive_continuation": {
                "sample_count": 0.0,
                "mean_forward_return_5": 0.0,
                "mean_max_favorable_return_5": 0.0,
                "mean_max_adverse_return_5": 0.0,
                "positive_forward_rate_5": 0.0,
            },
            "burst_fade_trap": {
                "sample_count": 0.0,
                "mean_forward_return_5": 0.0,
                "mean_max_favorable_return_5": 0.0,
                "mean_max_adverse_return_5": 0.0,
                "negative_forward_rate_5": 0.0,
            },
        }

        for (family, _symbol), family_rows in grouped.items():
            for index in range(len(family_rows) - HORIZON):
                current_close = family_rows[index]["close"]
                future_rows = family_rows[index + 1 : index + HORIZON + 1]
                future_close = future_rows[-1]["close"]
                future_high = max(row["high"] for row in future_rows)
                future_low = min(row["low"] for row in future_rows)
                forward_return = future_close / current_close - 1.0
                max_favorable = future_high / current_close - 1.0
                max_adverse = future_low / current_close - 1.0

                metrics = family_metrics[family]
                metrics["sample_count"] += 1.0
                metrics["mean_forward_return_5"] += forward_return
                metrics["mean_max_favorable_return_5"] += max_favorable
                metrics["mean_max_adverse_return_5"] += max_adverse
                if family == "supportive_continuation":
                    metrics["positive_forward_rate_5"] += float(forward_return > 0.0)
                else:
                    metrics["negative_forward_rate_5"] += float(forward_return < 0.0)

        family_rows_output = []
        for family, metrics in family_metrics.items():
            sample_count = int(metrics["sample_count"])
            if sample_count == 0:
                continue
            row = {
                "family": family,
                "sample_count": sample_count,
                "mean_forward_return_5": round(metrics["mean_forward_return_5"] / sample_count, 8),
                "mean_max_favorable_return_5": round(metrics["mean_max_favorable_return_5"] / sample_count, 8),
                "mean_max_adverse_return_5": round(metrics["mean_max_adverse_return_5"] / sample_count, 8),
            }
            if family == "supportive_continuation":
                row["positive_forward_rate_5"] = round(metrics["positive_forward_rate_5"] / sample_count, 8)
            else:
                row["negative_forward_rate_5"] = round(metrics["negative_forward_rate_5"] / sample_count, 8)
            family_rows_output.append(row)

        summary = {
            "acceptance_posture": "freeze_v122b_cpo_1min_family_short_horizon_expectancy_audit_v1",
            "horizon_bars": HORIZON,
            "family_count": len(family_rows_output),
            "recommended_next_posture": "continue_only_with_family_that_keeps_directional_expectancy_edge",
        }
        interpretation = [
            "V1.22B is the first label-aligned audit on the recent 1-minute plane, using short-horizon forward outcomes instead of replay.",
            "This is still local and recent, but it is better than trusting raw geometry without any outcome alignment.",
            "The next step is to keep only the family that preserves directional expectancy edge under this audit.",
        ]
        return V122BCpo1MinFamilyShortHorizonExpectancyAuditReport(
            summary=summary,
            family_rows=family_rows_output,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122BCpo1MinFamilyShortHorizonExpectancyAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122BCpo1MinFamilyShortHorizonExpectancyAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122b_cpo_1min_family_short_horizon_expectancy_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
