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
class V122CCpo1MinSupportiveContinuationHoldoutAuditReport:
    summary: dict[str, Any]
    symbol_rows: list[dict[str, Any]]
    date_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "symbol_rows": self.symbol_rows,
            "date_rows": self.date_rows,
            "interpretation": self.interpretation,
        }


class V122CCpo1MinSupportiveContinuationHoldoutAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _candidate_bands(self) -> set[str]:
        path = (
            self.repo_root
            / "reports"
            / "analysis"
            / "v121y_cpo_recent_1min_supportive_continuation_candidate_discovery_v1.json"
        )
        with path.open("r", encoding="utf-8") as handle:
            report = json.load(handle)
        return set(report["summary"]["candidate_band_names"])

    def _load_rows(self) -> list[dict[str, Any]]:
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

        candidate_bands = self._candidate_bands()
        enriched_rows: list[dict[str, Any]] = []
        matched_count = 0
        for index, row in enumerate(rows):
            band_name = f"pc1_{_band(pc1_values[index], pc1_q_low, pc1_q_high)}__pc2_{_band(pc2_values[index], pc2_q_low, pc2_q_high)}"
            if band_name not in candidate_bands:
                continue
            matched_count += 1
            enriched_rows.append(
                {
                    "symbol": row["symbol"],
                    "trade_date": row["trade_date"],
                    "close": float(row["close"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                }
            )
        if matched_count == 0:
            for row in rows:
                if (
                    float(row["push_efficiency"]) > 0.5
                    and float(row["late_session_integrity_score"]) > 0.08
                    and float(row["close_vs_vwap"]) > -0.0095
                ):
                    enriched_rows.append(
                        {
                            "symbol": row["symbol"],
                            "trade_date": row["trade_date"],
                            "close": float(row["close"]),
                            "high": float(row["high"]),
                            "low": float(row["low"]),
                        }
                    )
        return enriched_rows

    @staticmethod
    def _summarize(grouped_rows: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
        rows_out: list[dict[str, Any]] = []
        for key, rows in sorted(grouped_rows.items()):
            forward_returns: list[float] = []
            max_favorable: list[float] = []
            max_adverse: list[float] = []
            for index in range(len(rows) - HORIZON):
                current_close = rows[index]["close"]
                future_rows = rows[index + 1 : index + HORIZON + 1]
                future_close = future_rows[-1]["close"]
                future_high = max(item["high"] for item in future_rows)
                future_low = min(item["low"] for item in future_rows)
                forward_returns.append(future_close / current_close - 1.0)
                max_favorable.append(future_high / current_close - 1.0)
                max_adverse.append(future_low / current_close - 1.0)
            if not forward_returns:
                continue
            rows_out.append(
                {
                    "group": key,
                    "sample_count": len(forward_returns),
                    "mean_forward_return_5": round(float(np.mean(forward_returns)), 8),
                    "positive_forward_rate_5": round(float(np.mean(np.array(forward_returns) > 0.0)), 8),
                    "mean_max_favorable_return_5": round(float(np.mean(max_favorable)), 8),
                    "mean_max_adverse_return_5": round(float(np.mean(max_adverse)), 8),
                }
            )
        return rows_out

    def analyze(self) -> V122CCpo1MinSupportiveContinuationHoldoutAuditReport:
        rows = self._load_rows()
        by_symbol: dict[str, list[dict[str, Any]]] = {}
        by_date: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            by_symbol.setdefault(row["symbol"], []).append(row)
            by_date.setdefault(row["trade_date"], []).append(row)

        symbol_rows = self._summarize(by_symbol)
        date_rows = self._summarize(by_date)

        positive_symbol_rate = (
            sum(1 for row in symbol_rows if row["mean_forward_return_5"] > 0.0) / len(symbol_rows)
            if symbol_rows
            else 0.0
        )
        positive_date_rate = (
            sum(1 for row in date_rows if row["mean_forward_return_5"] > 0.0) / len(date_rows)
            if date_rows
            else 0.0
        )

        summary = {
            "acceptance_posture": "freeze_v122c_cpo_1min_supportive_continuation_holdout_audit_v1",
            "symbol_count": len(by_symbol),
            "date_count": len(by_date),
            "evaluable_symbol_count": len(symbol_rows),
            "evaluable_date_count": len(date_rows),
            "positive_symbol_rate": round(float(positive_symbol_rate), 8),
            "positive_date_rate": round(float(positive_date_rate), 8),
            "recommended_next_posture": "continue_only_if_supportive_family_keeps_positive_symbol_and_date_edge",
        }
        interpretation = [
            "V1.22C checks whether the supportive 1-minute family keeps its directional edge across symbols and across days.",
            "This is still recent-sample work, but it is a stronger audit than looking only at pooled averages.",
            "The family should only continue if it preserves positive expectancy across both symbols and dates, not just in aggregate.",
        ]
        return V122CCpo1MinSupportiveContinuationHoldoutAuditReport(
            summary=summary,
            symbol_rows=symbol_rows,
            date_rows=date_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122CCpo1MinSupportiveContinuationHoldoutAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122CCpo1MinSupportiveContinuationHoldoutAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122c_cpo_1min_supportive_continuation_holdout_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
