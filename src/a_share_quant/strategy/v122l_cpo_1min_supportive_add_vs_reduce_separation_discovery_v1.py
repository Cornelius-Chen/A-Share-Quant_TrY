from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from a_share_quant.strategy.v122_supportive_continuation_utils import load_supportive_continuation_rows


def _zscore(values: list[float]) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    mean = float(array.mean())
    std = float(array.std())
    if std == 0.0:
        std = 1.0
    return (array - mean) / std


@dataclass(slots=True)
class V122LCpo1MinSupportiveAddVsReduceSeparationDiscoveryReport:
    summary: dict[str, Any]
    score_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "score_rows": self.score_rows,
            "interpretation": self.interpretation,
        }


class V122LCpo1MinSupportiveAddVsReduceSeparationDiscoveryAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V122LCpo1MinSupportiveAddVsReduceSeparationDiscoveryReport:
        supportive_rows = load_supportive_continuation_rows(self.repo_root)
        label_path = self.repo_root / "data" / "training" / "cpo_recent_1min_proxy_action_timepoint_label_base_v1.csv"
        with label_path.open("r", encoding="utf-8") as handle:
            label_rows = list(csv.DictReader(handle))

        label_map = {
            (row["symbol"], row["trade_date"], row["clock_time"]): row["proxy_action_label"]
            for row in label_rows
        }

        rows = []
        for row in supportive_rows:
            label = label_map.get((row["symbol"], row["trade_date"], row["clock_time"]))
            if label not in {"add_probe", "reduce_probe"}:
                continue
            rows.append({**row, "proxy_action_label": label})

        push_z = _zscore([row["push_efficiency"] for row in rows])
        late_z = _zscore([row["late_session_integrity_score"] for row in rows])
        reclaim_z = _zscore([row["reclaim_after_break_score"] for row in rows])
        close_loc_z = _zscore([row["close_location"] for row in rows])
        close_vs_vwap_abs_z = _zscore([abs(row["close_vs_vwap"]) for row in rows])
        upper_shadow_z = _zscore([row["upper_shadow_pct"] for row in rows])
        pullback_z = _zscore([row["micro_pullback_depth"] for row in rows])
        burst_z = _zscore([row["burst_then_fade_score"] for row in rows])

        for index, row in enumerate(rows):
            row["add_reduce_separation_score"] = float(
                0.28 * push_z[index]
                + 0.24 * late_z[index]
                + 0.18 * reclaim_z[index]
                + 0.10 * close_loc_z[index]
                - 0.08 * close_vs_vwap_abs_z[index]
                - 0.05 * upper_shadow_z[index]
                - 0.04 * pullback_z[index]
                - 0.03 * burst_z[index]
            )

        add_scores = [row["add_reduce_separation_score"] for row in rows if row["proxy_action_label"] == "add_probe"]
        reduce_scores = [row["add_reduce_separation_score"] for row in rows if row["proxy_action_label"] == "reduce_probe"]
        discovery_gap = float(np.mean(add_scores) - np.mean(reduce_scores)) if add_scores and reduce_scores else 0.0
        threshold = float(np.quantile([row["add_reduce_separation_score"] for row in rows], 0.75)) if rows else 0.0
        threshold_rows = [row for row in rows if row["add_reduce_separation_score"] >= threshold]
        add_rate_above_threshold = (
            float(np.mean([row["proxy_action_label"] == "add_probe" for row in threshold_rows]))
            if threshold_rows
            else 0.0
        )

        summary = {
            "acceptance_posture": "freeze_v122l_cpo_1min_supportive_add_vs_reduce_separation_discovery_v1",
            "sample_count": len(rows),
            "add_probe_count": len(add_scores),
            "reduce_probe_count": len(reduce_scores),
            "discovery_mean_gap_add_minus_reduce": round(discovery_gap, 8),
            "threshold_q75": round(threshold, 8),
            "add_rate_above_threshold": round(add_rate_above_threshold, 8),
            "recommended_next_posture": "time_split_audit_supportive_add_vs_reduce_score",
        }
        score_rows = [
            {
                "group": "add_probe",
                "sample_count": len(add_scores),
                "mean_score": round(float(np.mean(add_scores)), 8) if add_scores else 0.0,
            },
            {
                "group": "reduce_probe",
                "sample_count": len(reduce_scores),
                "mean_score": round(float(np.mean(reduce_scores)), 8) if reduce_scores else 0.0,
            },
        ]
        interpretation = [
            "V1.22L is the first direct add-vs-reduce separation discovery inside the surviving supportive 1-minute family.",
            "The goal is not to create a new family, but to test whether the surviving family can be narrowed into a cleaner add-skew subspace.",
            "The next required step is time-split audit on this separation score.",
        ]
        return V122LCpo1MinSupportiveAddVsReduceSeparationDiscoveryReport(
            summary=summary,
            score_rows=score_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122LCpo1MinSupportiveAddVsReduceSeparationDiscoveryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122LCpo1MinSupportiveAddVsReduceSeparationDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122l_cpo_1min_supportive_add_vs_reduce_separation_discovery_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
