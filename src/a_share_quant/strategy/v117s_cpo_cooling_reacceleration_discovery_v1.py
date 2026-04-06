from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FEATURES = (
    "d5_30_last_bar_return_rz",
    "f30_last_bar_return_rz",
    "f30_afternoon_volume_share_rz",
    "f60_afternoon_volume_share_rz",
    "f30_high_time_ratio_rz",
    "f60_high_time_ratio_rz",
    "f60_close_vs_vwap_rz",
    "d5_30_close_vs_vwap_rz",
    "d15_60_close_vs_vwap_rz",
    "f30_close_location_rz",
    "f60_close_location_rz",
)


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _is_positive_add(row: dict[str, Any]) -> bool:
    return (
        str(row.get("action_context")) == "add_vs_hold"
        and str(row.get("action_favored_3d")) == "True"
        and _to_float(row.get("expectancy_proxy_3d")) > 0.0
        and _to_float(row.get("max_adverse_return_3d")) > -0.04
    )


def _candidate_score(row: dict[str, Any]) -> float:
    return (
        -_to_float(row.get("d5_30_last_bar_return_rz"))
        + _to_float(row.get("f30_last_bar_return_rz"))
        + _to_float(row.get("f30_afternoon_volume_share_rz"))
        + _to_float(row.get("f60_afternoon_volume_share_rz"))
        + _to_float(row.get("f30_high_time_ratio_rz"))
        + _to_float(row.get("f60_high_time_ratio_rz"))
        + _to_float(row.get("f60_close_vs_vwap_rz"))
        - _to_float(row.get("d5_30_close_vs_vwap_rz"))
        - _to_float(row.get("d15_60_close_vs_vwap_rz"))
        - _to_float(row.get("f30_close_location_rz"))
        - _to_float(row.get("f60_close_location_rz"))
    )


@dataclass(slots=True)
class V117SCpoCoolingReaccelerationDiscoveryReport:
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


class V117SCpoCoolingReaccelerationDiscoveryAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, rows_path: Path) -> V117SCpoCoolingReaccelerationDiscoveryReport:
        rows = [
            dict(row)
            for row in _load_csv_rows(rows_path)
            if str(row.get("board_phase")) in {"main_markup", "diffusion"}
            and str(row.get("action_context")) == "add_vs_hold"
        ]
        positive_rows = [row for row in rows if _is_positive_add(row)]
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
                    "board_phase": str(row["board_phase"]),
                    "positive_add_label": _is_positive_add(row),
                    "expectancy_proxy_3d": _to_float(row.get("expectancy_proxy_3d")),
                    "max_adverse_return_3d": _to_float(row.get("max_adverse_return_3d")),
                    "cooling_reacceleration_score": round(_candidate_score(row), 6),
                }
            )
        candidate_score_rows.sort(
            key=lambda row: (not bool(row["positive_add_label"]), -_to_float(row["cooling_reacceleration_score"]))
        )

        positive_mean = sum(_to_float(row["cooling_reacceleration_score"]) for row in candidate_score_rows if row["positive_add_label"]) / len(positive_rows)
        negative_mean = sum(_to_float(row["cooling_reacceleration_score"]) for row in candidate_score_rows if not row["positive_add_label"]) / len(negative_rows)

        summary = {
            "acceptance_posture": "freeze_v117s_cpo_cooling_reacceleration_discovery_v1",
            "candidate_discriminator_name": "cooling_reacceleration_score_candidate",
            "add_row_count": len(rows),
            "positive_add_row_count": len(positive_rows),
            "negative_add_row_count": len(negative_rows),
            "candidate_score_mean_gap_positive_minus_negative": round(positive_mean - negative_mean, 6),
            "top_separation_feature": feature_separation_rows[0]["feature_name"],
            "recommended_next_posture": "audit_cooling_reacceleration_on_broader_add_pool_and_keep_candidate_only",
        }
        interpretation = [
            "V1.17S reopens quality-side discovery from the broader add pool instead of the neat retained family.",
            "The candidate branch targets a different semantic: cool first, then reaccelerate, with sustained afternoon participation and without an overextended chase close.",
            "This is discovery only. The branch is new only if it survives the broader external audit next.",
        ]
        return V117SCpoCoolingReaccelerationDiscoveryReport(
            summary=summary,
            feature_separation_rows=feature_separation_rows,
            candidate_score_rows=candidate_score_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V117SCpoCoolingReaccelerationDiscoveryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V117SCpoCoolingReaccelerationDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v117s_cpo_cooling_reacceleration_discovery_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
