from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


VISIBLE_FEATURES = (
    "f30_high_time_ratio_rz",
    "f60_high_time_ratio_rz",
    "f30_close_location_rz",
    "f60_close_location_rz",
    "f30_breakout_efficiency_rz",
    "f60_breakout_efficiency_rz",
    "f30_afternoon_volume_share_rz",
    "f60_afternoon_volume_share_rz",
    "f30_close_vs_vwap_rz",
    "f60_close_vs_vwap_rz",
    "f30_upper_shadow_ratio_rz",
    "f60_upper_shadow_ratio_rz",
    "f30_failed_push_proxy",
    "f60_failed_push_proxy",
    "d15_60_failed_push_proxy",
)


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V117KCpoReverseSignalCandidateDiscoveryReport:
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


class V117KCpoReverseSignalCandidateDiscoveryAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, rows_path: Path) -> V117KCpoReverseSignalCandidateDiscoveryReport:
        rows = _load_csv_rows(rows_path)
        negative_rows = [row for row in rows if str(row.get("coarse_label")) == "decrease_expression"]
        non_negative_rows = [row for row in rows if str(row.get("coarse_label")) != "decrease_expression"]

        feature_separation_rows: list[dict[str, Any]] = []
        for feature in VISIBLE_FEATURES:
            neg_mean = sum(_to_float(row.get(feature)) for row in negative_rows) / len(negative_rows)
            pos_mean = sum(_to_float(row.get(feature)) for row in non_negative_rows) / len(non_negative_rows)
            separation = neg_mean - pos_mean
            preferred_direction = "higher_is_riskier" if separation > 0 else "lower_is_riskier"
            feature_separation_rows.append(
                {
                    "feature_name": feature,
                    "negative_mean": round(neg_mean, 6),
                    "non_negative_mean": round(pos_mean, 6),
                    "mean_separation": round(separation, 6),
                    "preferred_direction": preferred_direction,
                    "abs_separation": round(abs(separation), 6),
                }
            )
        feature_separation_rows.sort(key=lambda row: row["abs_separation"], reverse=True)

        # Candidate reverse score: weak continuation + weak close + weak breakout + failed-push pressure.
        candidate_score_rows: list[dict[str, Any]] = []
        for row in rows:
            weakness_score = (
                -_to_float(row.get("f30_high_time_ratio_rz"))
                - _to_float(row.get("f60_high_time_ratio_rz"))
                - _to_float(row.get("f30_close_location_rz"))
                - _to_float(row.get("f60_close_location_rz"))
                - _to_float(row.get("f30_breakout_efficiency_rz"))
                - _to_float(row.get("f60_breakout_efficiency_rz"))
            )
            damage_score = (
                _to_float(row.get("f30_upper_shadow_ratio_rz"))
                + _to_float(row.get("f60_upper_shadow_ratio_rz"))
                + _to_float(row.get("f30_failed_push_proxy"))
                + _to_float(row.get("f60_failed_push_proxy"))
                + _to_float(row.get("d15_60_failed_push_proxy"))
            )
            candidate_reverse_score = weakness_score + damage_score
            candidate_score_rows.append(
                {
                    "signal_trade_date": str(row.get("signal_trade_date")),
                    "symbol": str(row.get("symbol")),
                    "coarse_label": str(row.get("coarse_label")),
                    "action_context": str(row.get("action_context")),
                    "board_phase": str(row.get("board_phase")),
                    "reverse_weakness_score": round(weakness_score, 6),
                    "reverse_damage_score": round(damage_score, 6),
                    "candidate_reverse_score": round(candidate_reverse_score, 6),
                }
            )

        negative_scores = [row["candidate_reverse_score"] for row in candidate_score_rows if row["coarse_label"] == "decrease_expression"]
        non_negative_scores = [row["candidate_reverse_score"] for row in candidate_score_rows if row["coarse_label"] != "decrease_expression"]
        score_gap = (sum(negative_scores) / len(negative_scores)) - (sum(non_negative_scores) / len(non_negative_scores))

        candidate_score_rows.sort(key=lambda row: row["candidate_reverse_score"], reverse=True)

        summary = {
            "acceptance_posture": "freeze_v117k_cpo_reverse_signal_candidate_discovery_v1",
            "negative_row_count": len(negative_rows),
            "non_negative_row_count": len(non_negative_rows),
            "top_separation_feature": feature_separation_rows[0]["feature_name"],
            "candidate_discriminator_name": "continuation_failure_damage_score_candidate",
            "candidate_score_mean_gap_negative_minus_non_negative": round(score_gap, 6),
            "recommended_next_posture": "audit_reverse_signal_candidate_as_drawdown_control_component_and_keep_candidate_only",
        }
        interpretation = [
            "V1.17K opens the reverse-signal branch explicitly instead of treating drawdown control as merely the absence of positive signals.",
            "The resulting candidate score is built around continuation failure: weak close location, weak high-time ratio, weak breakout efficiency, plus explicit damage proxies.",
            "This branch is candidate-only. The goal is to discover a downside-control vector that can later sit beside the positive-side branch, not to promote a new sell law immediately.",
        ]
        return V117KCpoReverseSignalCandidateDiscoveryReport(
            summary=summary,
            feature_separation_rows=feature_separation_rows,
            candidate_score_rows=candidate_score_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V117KCpoReverseSignalCandidateDiscoveryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V117KCpoReverseSignalCandidateDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_expanded_window_rebuilt_v1.csv",
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v117k_cpo_reverse_signal_candidate_discovery_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
