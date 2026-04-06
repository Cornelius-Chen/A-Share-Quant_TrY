from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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


def _base_score(row: dict[str, Any]) -> float:
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


def _overheat_penalty(row: dict[str, Any]) -> float:
    d5_last = max(_to_float(row.get("d5_30_last_bar_return_rz")), 0.0)
    f60_high = max(_to_float(row.get("f60_high_time_ratio_rz")) - 750000000.0, 0.0)
    close_stretch = max(_to_float(row.get("f60_close_location_rz")) - 850000000.0, 0.0)
    return d5_last + f60_high + close_stretch


@dataclass(slots=True)
class V117WCpoCoolingReaccelerationFalsePositiveControlDiscoveryReport:
    summary: dict[str, Any]
    control_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "control_rows": self.control_rows,
            "interpretation": self.interpretation,
        }


class V117WCpoCoolingReaccelerationFalsePositiveControlDiscoveryAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, rows_path: Path) -> V117WCpoCoolingReaccelerationFalsePositiveControlDiscoveryReport:
        rows = [
            dict(row)
            for row in _load_csv_rows(rows_path)
            if str(row.get("board_phase")) in {"main_markup", "diffusion"}
            and str(row.get("action_context")) == "add_vs_hold"
        ]
        control_rows: list[dict[str, Any]] = []
        for row in rows:
            base_score = _base_score(row)
            overheat_penalty = _overheat_penalty(row)
            controlled_score = base_score - overheat_penalty
            control_rows.append(
                {
                    "signal_trade_date": str(row["signal_trade_date"]),
                    "symbol": str(row["symbol"]),
                    "positive_add_label": _is_positive_add(row),
                    "expectancy_proxy_3d": _to_float(row.get("expectancy_proxy_3d")),
                    "max_adverse_return_3d": _to_float(row.get("max_adverse_return_3d")),
                    "base_score": round(base_score, 6),
                    "overheat_penalty": round(overheat_penalty, 6),
                    "controlled_score": round(controlled_score, 6),
                }
            )
        control_rows.sort(key=lambda row: (not bool(row["positive_add_label"]), -_to_float(row["controlled_score"])))

        positives = [row for row in control_rows if bool(row["positive_add_label"])]
        negatives = [row for row in control_rows if not bool(row["positive_add_label"])]
        base_gap = sum(_to_float(r["base_score"]) for r in positives) / len(positives) - sum(_to_float(r["base_score"]) for r in negatives) / len(negatives)
        controlled_gap = sum(_to_float(r["controlled_score"]) for r in positives) / len(positives) - sum(_to_float(r["controlled_score"]) for r in negatives) / len(negatives)
        penalty_gap = sum(_to_float(r["overheat_penalty"]) for r in negatives) / len(negatives) - sum(_to_float(r["overheat_penalty"]) for r in positives) / len(positives)

        summary = {
            "acceptance_posture": "freeze_v117w_cpo_cooling_reacceleration_false_positive_control_discovery_v1",
            "candidate_name": "cooling_reacceleration_overheat_control_candidate",
            "row_count": len(control_rows),
            "positive_row_count": len(positives),
            "negative_row_count": len(negatives),
            "base_gap_positive_minus_negative": round(base_gap, 6),
            "controlled_gap_positive_minus_negative": round(controlled_gap, 6),
            "penalty_gap_negative_minus_positive": round(penalty_gap, 6),
            "control_helpful": controlled_gap > base_gap,
            "recommended_next_posture": "externally_audit_controlled_score_on_same_add_pool_and_keep_candidate_only",
        }
        interpretation = [
            "V1.17W adds one narrow false-positive control idea to the cooling-reacceleration branch: punish rows that are still too overheated to count as real cooling before reacceleration.",
            "The penalty is intentionally simple and visible-only: too-hot recent bar, too-high session occupancy, and too-stretched close location.",
            "This is still discovery only. If the controlled score does not improve the broader add-pool separation, the control idea should die quickly.",
        ]
        return V117WCpoCoolingReaccelerationFalsePositiveControlDiscoveryReport(
            summary=summary,
            control_rows=control_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V117WCpoCoolingReaccelerationFalsePositiveControlDiscoveryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V117WCpoCoolingReaccelerationFalsePositiveControlDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v117w_cpo_cooling_reacceleration_false_positive_control_discovery_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
