from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


KEY_FEATURES = (
    "f30_close_vs_vwap_rz",
    "f60_close_vs_vwap_rz",
    "f30_close_location_rz",
    "f60_close_location_rz",
    "f30_high_time_ratio_rz",
    "f60_high_time_ratio_rz",
    "f30_afternoon_volume_share_rz",
    "f60_afternoon_volume_share_rz",
    "f30_upper_shadow_ratio_rz",
    "f60_upper_shadow_ratio_rz",
    "f30_body_ratio_rz",
    "f60_body_ratio_rz",
    "pc1_score",
    "pc2_score",
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
class V117BCpoCooledQ025QualityContrastAuditReport:
    summary: dict[str, Any]
    contrast_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "contrast_rows": self.contrast_rows,
            "interpretation": self.interpretation,
        }


class V117BCpoCooledQ025QualityContrastAuditAnalyzer:
    NEW_DAYS = ("2023-11-07", "2024-01-18", "2024-01-23")

    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v116x_payload: dict[str, Any],
        v117a_payload: dict[str, Any],
        rebuilt_rows_path: Path,
    ) -> V117BCpoCooledQ025QualityContrastAuditReport:
        contrast_map = {str(row["signal_trade_date"]): dict(row) for row in list(v116x_payload.get("contrast_rows", []))}
        retained = dict(v117a_payload.get("retained_variant_row", {}))
        retained_expectancy = _to_float(retained.get("avg_expectancy_proxy_3d"))
        retained_adverse = _to_float(retained.get("avg_max_adverse_return_3d"))

        rebuilt_rows = [
            row for row in _load_csv_rows(rebuilt_rows_path)
            if str(row.get("signal_trade_date")) in self.NEW_DAYS
        ]

        contrast_rows: list[dict[str, Any]] = []
        for day in self.NEW_DAYS:
            day_rows = [row for row in rebuilt_rows if str(row["signal_trade_date"]) == day]
            day_contrast = contrast_map[day]
            feature_means = {
                feature: round(sum(_to_float(row.get(feature)) for row in day_rows) / len(day_rows), 6)
                for feature in KEY_FEATURES
            }

            timing_gate = "early_visible" if bool(day_contrast["all_early_visible"]) else "late_only"
            continuation_gate = (
                "strong"
                if feature_means["f30_close_location_rz"] >= 0.8 and feature_means["f30_high_time_ratio_rz"] >= 0.8
                else "mixed"
            )
            vwap_gate = "positive" if feature_means["f30_close_vs_vwap_rz"] > 0 and feature_means["f60_close_vs_vwap_rz"] > 0 else "mixed_or_negative"
            outcome_gate = (
                "above_retained_avg"
                if _to_float(day_contrast["avg_expectancy_proxy_3d"]) >= retained_expectancy
                else "below_retained_avg"
            )
            risk_gate = (
                "contained"
                if _to_float(day_contrast["avg_max_adverse_return_3d"]) >= retained_adverse
                else "worse_than_retained_avg"
            )

            if bool(day_contrast["corrected_cooled_hit"]):
                final_judgement = "retained_quality_standard_met"
            elif timing_gate == "late_only" and outcome_gate == "above_retained_avg":
                final_judgement = "late_visibility_blocks_otherwise_good_day"
            elif timing_gate == "late_only" and outcome_gate == "below_retained_avg":
                final_judgement = "late_and_quality_weak"
            else:
                final_judgement = "mixed_failure"

            contrast_rows.append(
                {
                    "signal_trade_date": day,
                    "corrected_cooled_hit": bool(day_contrast["corrected_cooled_hit"]),
                    "timing_gate": timing_gate,
                    "continuation_gate": continuation_gate,
                    "vwap_gate": vwap_gate,
                    "outcome_gate_vs_retained": outcome_gate,
                    "risk_gate_vs_retained": risk_gate,
                    "state_bands": day_contrast["state_bands"],
                    "action_favored_count": int(day_contrast["action_favored_count"]),
                    "avg_expectancy_proxy_3d": _to_float(day_contrast["avg_expectancy_proxy_3d"]),
                    "avg_max_adverse_return_3d": _to_float(day_contrast["avg_max_adverse_return_3d"]),
                    **feature_means,
                    "final_judgement": final_judgement,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v117b_cpo_cooled_q025_quality_contrast_audit_v1",
            "retained_variant_name": str(v117a_payload.get("summary", {}).get("retained_variant_name")),
            "reviewed_day_count": len(self.NEW_DAYS),
            "authoritative_current_problem": "quality_side_contrast_for_cooled_q_0p25",
            "recommended_next_posture": "if_visible_only_continues_use_quality_axes_not_new_quantiles_or_timing_rework",
        }
        interpretation = [
            "V1.17B turns the rebuilt-new-day comparison into a cooled_q_0p25-specific quality audit instead of leaving the distinction as a narrative judgement.",
            "The report shows that 2024-01-18 is not simply 'the day that hit'; it is the only rebuilt new day that combines early visibility with acceptable risk and non-negative continuation quality under the retained cooled reference.",
            "2023-11-07 fails mainly because it arrives too late despite decent quality, while 2024-01-23 fails because it is both late and materially weaker.",
        ]
        return V117BCpoCooledQ025QualityContrastAuditReport(
            summary=summary,
            contrast_rows=contrast_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V117BCpoCooledQ025QualityContrastAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V117BCpoCooledQ025QualityContrastAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v116x_payload=json.loads((repo_root / "reports" / "analysis" / "v116x_cpo_rebuilt_new_day_timing_quality_contrast_v1.json").read_text(encoding="utf-8")),
        v117a_payload=json.loads((repo_root / "reports" / "analysis" / "v117a_cpo_quality_side_cooled_retention_v1.json").read_text(encoding="utf-8")),
        rebuilt_rows_path=repo_root / "data" / "training" / "cpo_midfreq_expanded_window_rebuilt_rows_v1.csv",
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v117b_cpo_cooled_q025_quality_contrast_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
