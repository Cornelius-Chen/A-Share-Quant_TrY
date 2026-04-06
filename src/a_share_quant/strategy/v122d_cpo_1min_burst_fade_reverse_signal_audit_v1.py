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
class V122DCpo1MinBurstFadeReverseSignalAuditReport:
    summary: dict[str, Any]
    symbol_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "symbol_rows": self.symbol_rows,
            "interpretation": self.interpretation,
        }


class V122DCpo1MinBurstFadeReverseSignalAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _candidate_bands(self) -> set[str]:
        path = self.repo_root / "reports" / "analysis" / "v121z_cpo_recent_1min_burst_fade_trap_candidate_discovery_v1.json"
        with path.open("r", encoding="utf-8") as handle:
            report = json.load(handle)
        return set(report["summary"]["candidate_band_names"])

    def analyze(self) -> V122DCpo1MinBurstFadeReverseSignalAuditReport:
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

        grouped: dict[str, list[dict[str, Any]]] = {}
        matched_count = 0
        for index, row in enumerate(rows):
            band_name = f"pc1_{_band(pc1_values[index], pc1_q_low, pc1_q_high)}__pc2_{_band(pc2_values[index], pc2_q_low, pc2_q_high)}"
            if band_name not in candidate_bands:
                continue
            matched_count += 1
            grouped.setdefault(row["symbol"], []).append(
                {
                    "close": float(row["close"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                }
            )
        if matched_count == 0:
            for row in rows:
                if (
                    float(row["push_efficiency"]) < -0.35
                    and float(row["late_session_integrity_score"]) < -0.01
                    and float(row["burst_then_fade_score"]) > 0.001
                ):
                    grouped.setdefault(row["symbol"], []).append(
                        {
                            "close": float(row["close"]),
                            "high": float(row["high"]),
                            "low": float(row["low"]),
                        }
                    )

        symbol_rows = []
        for symbol, items in sorted(grouped.items()):
            forward_returns: list[float] = []
            for index in range(len(items) - HORIZON):
                current_close = items[index]["close"]
                future_close = items[index + HORIZON]["close"]
                forward_returns.append(future_close / current_close - 1.0)
            if not forward_returns:
                continue
            symbol_rows.append(
                {
                    "symbol": symbol,
                    "sample_count": len(forward_returns),
                    "mean_forward_return_5": round(float(np.mean(forward_returns)), 8),
                    "negative_forward_rate_5": round(float(np.mean(np.array(forward_returns) < 0.0)), 8),
                }
            )

        stable_reverse_symbol_rate = (
            sum(1 for row in symbol_rows if row["mean_forward_return_5"] < 0.0) / len(symbol_rows)
            if symbol_rows
            else 0.0
        )
        summary = {
            "acceptance_posture": "freeze_v122d_cpo_1min_burst_fade_reverse_signal_audit_v1",
            "symbol_count": len(symbol_rows),
            "stable_reverse_symbol_rate": round(float(stable_reverse_symbol_rate), 8),
            "recommended_next_posture": "kill_trap_family_if_reverse_edge_is_not_symbol_stable",
        }
        interpretation = [
            "V1.22D tests whether the burst-fade 1-minute family behaves like a true reverse/risk family across symbols.",
            "A pooled negative-rate is not enough; the family should show negative forward edge by symbol to justify further work.",
            "If that edge is not symbol-stable, the family should be stopped instead of being kept as a vague risk metaphor.",
        ]
        return V122DCpo1MinBurstFadeReverseSignalAuditReport(
            summary=summary,
            symbol_rows=symbol_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122DCpo1MinBurstFadeReverseSignalAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122DCpo1MinBurstFadeReverseSignalAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122d_cpo_1min_burst_fade_reverse_signal_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
