from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from a_share_quant.strategy.v122_1min_label_plane_utils import load_recent_1min_labeled_rows
from a_share_quant.strategy.v122_supportive_continuation_utils import _zscore


@dataclass(slots=True)
class V122OCpo1MinDownsideFailureDiscoveryReport:
    summary: dict[str, Any]
    score_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "score_rows": self.score_rows,
            "interpretation": self.interpretation,
        }


class V122OCpo1MinDownsideFailureDiscoveryAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V122OCpo1MinDownsideFailureDiscoveryReport:
        rows = load_recent_1min_labeled_rows(self.repo_root)

        burst_z = _zscore([float(row["burst_then_fade_score"]) for row in rows])
        upper_shadow_z = _zscore([float(row["upper_shadow_pct"]) for row in rows])
        pullback_z = _zscore([float(row["micro_pullback_depth"]) for row in rows])
        push_z = _zscore([float(row["push_efficiency"]) for row in rows])
        late_z = _zscore([float(row["late_session_integrity_score"]) for row in rows])
        close_location_z = _zscore([float(row["close_location"]) for row in rows])
        reclaim_z = _zscore([float(row["reclaim_after_break_score"]) for row in rows])
        abs_close_vs_vwap_z = _zscore([abs(float(row["close_vs_vwap"])) for row in rows])

        for index, row in enumerate(rows):
            row["downside_failure_score"] = float(
                0.26 * burst_z[index]
                + 0.18 * upper_shadow_z[index]
                + 0.16 * pullback_z[index]
                - 0.14 * push_z[index]
                - 0.12 * late_z[index]
                - 0.08 * close_location_z[index]
                - 0.04 * reclaim_z[index]
                + 0.02 * abs_close_vs_vwap_z[index]
            )

        positive_rows = [
            row for row in rows if row["proxy_action_label"] in {"reduce_probe", "close_probe"}
        ]
        negative_rows = [
            row for row in rows if row["proxy_action_label"] in {"add_probe", "hold_probe"}
        ]
        positive_scores = [row["downside_failure_score"] for row in positive_rows]
        negative_scores = [row["downside_failure_score"] for row in negative_rows]
        discovery_gap = float(np.mean(positive_scores) - np.mean(negative_scores)) if positive_scores and negative_scores else 0.0
        threshold = float(np.quantile([row["downside_failure_score"] for row in rows], 0.75)) if rows else 0.0
        threshold_rows = [row for row in rows if row["downside_failure_score"] >= threshold]
        risk_rate_above_threshold = (
            float(np.mean([row["proxy_action_label"] in {"reduce_probe", "close_probe"} for row in threshold_rows]))
            if threshold_rows
            else 0.0
        )

        summary = {
            "acceptance_posture": "freeze_v122o_cpo_1min_downside_failure_discovery_v1",
            "sample_count": len(rows),
            "positive_count": len(positive_rows),
            "negative_count": len(negative_rows),
            "discovery_mean_gap_positive_minus_negative": round(discovery_gap, 8),
            "threshold_q75": round(threshold, 8),
            "risk_rate_above_threshold": round(risk_rate_above_threshold, 8),
            "recommended_next_posture": "date_split_audit_downside_failure_score",
        }
        score_rows = [
            {
                "group": "reduce_or_close_probe",
                "sample_count": len(positive_scores),
                "mean_score": round(float(np.mean(positive_scores)), 8) if positive_scores else 0.0,
            },
            {
                "group": "add_or_hold_probe",
                "sample_count": len(negative_scores),
                "mean_score": round(float(np.mean(negative_scores)), 8) if negative_scores else 0.0,
            },
        ]
        interpretation = [
            "V1.22O opens the new 1-minute downside branch on the proxy label plane instead of using unlabeled geometry.",
            "The score is meant to capture burst-fade, weak close quality, pullback damage, and deteriorating late-session integrity.",
            "The next step is chronology audit, not replay.",
        ]
        return V122OCpo1MinDownsideFailureDiscoveryReport(
            summary=summary,
            score_rows=score_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122OCpo1MinDownsideFailureDiscoveryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122OCpo1MinDownsideFailureDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122o_cpo_1min_downside_failure_discovery_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
