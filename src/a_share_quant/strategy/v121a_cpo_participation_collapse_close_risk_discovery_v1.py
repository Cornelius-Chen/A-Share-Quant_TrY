from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FEATURES = (
    "f30_afternoon_volume_share_rz",
    "f60_afternoon_volume_share_rz",
    "f30_close_location_rz",
    "f60_close_location_rz",
    "f30_high_time_ratio_rz",
    "f60_high_time_ratio_rz",
    "f30_last_bar_volume_share_rz",
    "f60_last_bar_volume_share_rz",
    "f30_breakout_efficiency_rz",
    "f60_breakout_efficiency_rz",
    "f30_close_vs_vwap_rz",
    "f60_close_vs_vwap_rz",
)


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _is_positive_close(row: dict[str, Any]) -> bool:
    return (
        str(row.get("action_context")) == "close_vs_hold"
        and str(row.get("action_favored_3d")) == "True"
        and _to_float(row.get("expectancy_proxy_3d")) < -0.05
        and _to_float(row.get("max_adverse_return_3d")) < -0.08
    )


def _candidate_score(row: dict[str, Any]) -> float:
    return (
        -_to_float(row.get("f30_afternoon_volume_share_rz"))
        - _to_float(row.get("f60_afternoon_volume_share_rz"))
        - _to_float(row.get("f30_close_location_rz"))
        - _to_float(row.get("f60_close_location_rz"))
        - _to_float(row.get("f30_high_time_ratio_rz"))
        - _to_float(row.get("f60_high_time_ratio_rz"))
        - 0.5 * _to_float(row.get("f30_breakout_efficiency_rz"))
        - 0.5 * _to_float(row.get("f60_breakout_efficiency_rz"))
        - 0.25 * _to_float(row.get("f30_close_vs_vwap_rz"))
        - 0.25 * _to_float(row.get("f60_close_vs_vwap_rz"))
    )


@dataclass(slots=True)
class V121ACpoParticipationCollapseCloseRiskDiscoveryReport:
    summary: dict[str, Any]
    feature_separation_rows: list[dict[str, Any]]
    candidate_score_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "feature_separation_rows": self.feature_separation_rows,
            "candidate_score_rows": self.candidate_score_rows,
            "interpretation": self.interpretation,
        }


class V121ACpoParticipationCollapseCloseRiskDiscoveryAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, rows_path: Path) -> V121ACpoParticipationCollapseCloseRiskDiscoveryReport:
        rows = [dict(row) for row in _load_csv_rows(rows_path)]
        positive_rows = [row for row in rows if _is_positive_close(row)]
        negative_rows = [row for row in rows if row not in positive_rows]

        feature_separation_rows: list[dict[str, Any]] = []
        for feature_name in FEATURES:
            pos_mean = sum(_to_float(row.get(feature_name)) for row in positive_rows) / len(positive_rows)
            neg_mean = sum(_to_float(row.get(feature_name)) for row in negative_rows) / len(negative_rows)
            feature_separation_rows.append(
                {
                    "feature_name": feature_name,
                    "positive_mean": round(pos_mean, 6),
                    "negative_mean": round(neg_mean, 6),
                    "mean_gap_positive_minus_negative": round(pos_mean - neg_mean, 6),
                    "preferred_direction": "higher_is_better" if pos_mean > neg_mean else "lower_is_better",
                    "abs_gap": round(abs(pos_mean - neg_mean), 6),
                }
            )
        feature_separation_rows.sort(key=lambda row: row["abs_gap"], reverse=True)

        candidate_score_rows: list[dict[str, Any]] = []
        for row in rows:
            candidate_score_rows.append(
                {
                    "signal_trade_date": str(row["signal_trade_date"]),
                    "symbol": str(row["symbol"]),
                    "action_context": str(row["action_context"]),
                    "board_phase": str(row["board_phase"]),
                    "positive_close_label": _is_positive_close(row),
                    "expectancy_proxy_3d": _to_float(row.get("expectancy_proxy_3d")),
                    "max_adverse_return_3d": _to_float(row.get("max_adverse_return_3d")),
                    "participation_collapse_close_risk_score": round(_candidate_score(row), 6),
                }
            )
        candidate_score_rows.sort(
            key=lambda row: (not bool(row["positive_close_label"]), -_to_float(row["participation_collapse_close_risk_score"]))
        )

        positive_mean = sum(_to_float(row["participation_collapse_close_risk_score"]) for row in candidate_score_rows if row["positive_close_label"]) / len(positive_rows)
        negative_mean = sum(_to_float(row["participation_collapse_close_risk_score"]) for row in candidate_score_rows if not row["positive_close_label"]) / len(negative_rows)

        summary = {
            "acceptance_posture": "freeze_v121a_cpo_participation_collapse_close_risk_discovery_v1",
            "candidate_discriminator_name": "participation_collapse_close_risk_score_candidate",
            "row_count": len(rows),
            "positive_close_row_count": len(positive_rows),
            "negative_row_count": len(negative_rows),
            "candidate_score_mean_gap_positive_minus_negative": round(positive_mean - negative_mean, 6),
            "top_separation_feature": feature_separation_rows[0]["feature_name"],
            "recommended_next_posture": "audit_close_risk_candidate_on_broader_context_pool_before_any_replay_use",
        }
        interpretation = [
            "V1.21A opens the first explicit downside branch for CPO around participation collapse and close-side risk.",
            "The branch looks for low afternoon participation, weak close location, poor high-time occupancy, and weak tail participation, treating them as close-risk structure rather than add structure.",
            "This is discovery only and should die quickly if the external pool gap is weak.",
        ]
        return V121ACpoParticipationCollapseCloseRiskDiscoveryReport(
            summary=summary,
            feature_separation_rows=feature_separation_rows,
            candidate_score_rows=candidate_score_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V121ACpoParticipationCollapseCloseRiskDiscoveryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V121ACpoParticipationCollapseCloseRiskDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v121a_cpo_participation_collapse_close_risk_discovery_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()

