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
        _to_float(row.get("f30_high_time_ratio_rz"))
        + _to_float(row.get("f60_high_time_ratio_rz"))
        + _to_float(row.get("f30_afternoon_volume_share_rz"))
        + _to_float(row.get("f60_afternoon_volume_share_rz"))
        + _to_float(row.get("f30_last_bar_volume_share_rz"))
        + _to_float(row.get("f60_close_vs_vwap_rz"))
        + _to_float(row.get("f30_close_vs_vwap_rz"))
        - _to_float(row.get("f30_close_location_rz"))
        - _to_float(row.get("f60_close_location_rz"))
        + _to_float(row.get("f30_last_bar_return_rz"))
        - _to_float(row.get("f60_last_bar_return_rz"))
    )


def _prior_heat_and_late_fade_penalty(row: dict[str, Any]) -> float:
    prior_heat = max(_to_float(row.get("d5_30_last_bar_return_rz")), 0.0)
    late_fade = max(-_to_float(row.get("f60_last_bar_return_rz")), 0.0)
    tail_heat = max(_to_float(row.get("f30_last_bar_volume_share_rz")) - 100000000.0, 0.0)
    return prior_heat + late_fade + tail_heat


@dataclass(slots=True)
class V118XCpoSustainedParticipationFalsePositiveControlDiscoveryReport:
    summary: dict[str, Any]
    control_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "control_rows": self.control_rows,
            "interpretation": self.interpretation,
        }


class V118XCpoSustainedParticipationFalsePositiveControlDiscoveryAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, rows_path: Path) -> V118XCpoSustainedParticipationFalsePositiveControlDiscoveryReport:
        rows = [
            dict(row)
            for row in _load_csv_rows(rows_path)
            if str(row.get("board_phase")) in {"main_markup", "diffusion"}
            and str(row.get("action_context")) == "add_vs_hold"
        ]
        control_rows: list[dict[str, Any]] = []
        for row in rows:
            base_score = _base_score(row)
            control_penalty = _prior_heat_and_late_fade_penalty(row)
            controlled_score = base_score - control_penalty
            control_rows.append(
                {
                    "signal_trade_date": str(row["signal_trade_date"]),
                    "symbol": str(row["symbol"]),
                    "positive_add_label": _is_positive_add(row),
                    "expectancy_proxy_3d": _to_float(row.get("expectancy_proxy_3d")),
                    "max_adverse_return_3d": _to_float(row.get("max_adverse_return_3d")),
                    "base_score": round(base_score, 6),
                    "control_penalty": round(control_penalty, 6),
                    "controlled_score": round(controlled_score, 6),
                }
            )
        control_rows.sort(key=lambda row: (not bool(row["positive_add_label"]), -_to_float(row["controlled_score"])))

        positives = [row for row in control_rows if bool(row["positive_add_label"])]
        negatives = [row for row in control_rows if not bool(row["positive_add_label"])]
        base_gap = sum(_to_float(r["base_score"]) for r in positives) / len(positives) - sum(_to_float(r["base_score"]) for r in negatives) / len(negatives)
        controlled_gap = sum(_to_float(r["controlled_score"]) for r in positives) / len(positives) - sum(_to_float(r["controlled_score"]) for r in negatives) / len(negatives)
        penalty_gap = sum(_to_float(r["control_penalty"]) for r in negatives) / len(negatives) - sum(_to_float(r["control_penalty"]) for r in positives) / len(positives)

        summary = {
            "acceptance_posture": "freeze_v118x_cpo_sustained_participation_false_positive_control_discovery_v1",
            "candidate_name": "sustained_participation_non_chase_prior_heat_late_fade_control_candidate",
            "row_count": len(control_rows),
            "positive_row_count": len(positives),
            "negative_row_count": len(negatives),
            "base_gap_positive_minus_negative": round(base_gap, 6),
            "controlled_gap_positive_minus_negative": round(controlled_gap, 6),
            "penalty_gap_negative_minus_positive": round(penalty_gap, 6),
            "control_helpful": controlled_gap > base_gap,
            "recommended_next_posture": "externally_audit_controlled_score_once_then_drop_if_no_material_gain",
        }
        interpretation = [
            "V1.18X tries one narrow hardening idea for the sustained-participation branch: penalize rows that still carry obvious prior heat, late fade, and tail-volume overheat.",
            "The intent is not to invent a new branch, only to check whether a simple visible-only control can shave the head off the top false positives.",
            "If the controlled score does not improve broader add-pool separation, this same-family control idea should be dropped immediately.",
        ]
        return V118XCpoSustainedParticipationFalsePositiveControlDiscoveryReport(
            summary=summary,
            control_rows=control_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V118XCpoSustainedParticipationFalsePositiveControlDiscoveryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V118XCpoSustainedParticipationFalsePositiveControlDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v118x_cpo_sustained_participation_false_positive_control_discovery_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
