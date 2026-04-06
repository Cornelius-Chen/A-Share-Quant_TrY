from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


HEURISTIC_FEATURE_GROUPS = {
    "shooting_star_trap_proxy": (
        "f30_upper_shadow_ratio_rz",
        "f60_upper_shadow_ratio_rz",
        "f30_close_location_rz",
        "f60_close_location_rz",
        "f30_high_time_ratio_rz",
        "f60_high_time_ratio_rz",
    ),
    "doji_exhaustion_proxy": (
        "f30_body_ratio_rz",
        "f60_body_ratio_rz",
        "f30_breakout_efficiency_rz",
        "f60_breakout_efficiency_rz",
        "f30_close_vs_vwap_rz",
        "f60_close_vs_vwap_rz",
    ),
    "false_breakout_damage_proxy": (
        "f30_breakout_efficiency_rz",
        "f60_breakout_efficiency_rz",
        "f30_pullback_from_high_rz",
        "f60_pullback_from_high_rz",
        "f30_failed_push_proxy",
        "f60_failed_push_proxy",
    ),
    "retail_chase_trap_proxy": (
        "f30_afternoon_volume_share_rz",
        "f60_afternoon_volume_share_rz",
        "f30_last_bar_volume_share_rz",
        "f60_last_bar_volume_share_rz",
        "f30_close_location_rz",
        "f60_close_location_rz",
    ),
}


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V117LCpoHumanHeuristicSignalQuantizationProtocolReport:
    summary: dict[str, Any]
    heuristic_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "heuristic_rows": self.heuristic_rows,
            "interpretation": self.interpretation,
        }


class V117LCpoHumanHeuristicSignalQuantizationProtocolAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, rows_path: Path) -> V117LCpoHumanHeuristicSignalQuantizationProtocolReport:
        rows = _load_csv_rows(rows_path)
        heuristic_rows: list[dict[str, Any]] = []
        for heuristic_name, features in HEURISTIC_FEATURE_GROUPS.items():
            nonzero_count = 0
            total_count = 0
            abs_sum = 0.0
            for row in rows:
                for feature in features:
                    total_count += 1
                    value = _to_float(row.get(feature))
                    abs_sum += abs(value)
                    if value != 0.0:
                        nonzero_count += 1
            heuristic_rows.append(
                {
                    "heuristic_name": heuristic_name,
                    "feature_count": len(features),
                    "nonzero_rate": round(nonzero_count / total_count, 6) if total_count else 0.0,
                    "mean_abs_feature_value": round(abs_sum / total_count, 6) if total_count else 0.0,
                    "context_requirement": "must_be_conditioned_on_board_phase_and_role_not_used_as_global_law",
                    "current_posture": "candidate_only",
                }
            )
        heuristic_rows.sort(key=lambda row: row["nonzero_rate"], reverse=True)

        summary = {
            "acceptance_posture": "freeze_v117l_cpo_human_heuristic_signal_quantization_protocol_v1",
            "heuristic_family_count": len(heuristic_rows),
            "top_currently_observable_heuristic": heuristic_rows[0]["heuristic_name"],
            "allow_interaction_terms": True,
            "recommended_next_posture": "treat_human_heuristics_as_context_conditioned_candidate_vectors_not_direct_trading_laws",
        }
        interpretation = [
            "V1.17L does not treat human pattern names as laws. It translates them into objective proxy families and checks whether the required fields are actually observable in the current mid-frequency base table.",
            "The correct use is context-conditioned: a heuristic proxy only matters inside the right board phase, role family, and continuation state. It should be a vector component or interaction term, not a standalone rule.",
            "This gives the project a disciplined way to borrow useful human experience without turning subjective candle lore into immediate policy.",
        ]
        return V117LCpoHumanHeuristicSignalQuantizationProtocolReport(
            summary=summary,
            heuristic_rows=heuristic_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V117LCpoHumanHeuristicSignalQuantizationProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V117LCpoHumanHeuristicSignalQuantizationProtocolAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_expanded_window_rebuilt_v1.csv",
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v117l_cpo_human_heuristic_signal_quantization_protocol_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
