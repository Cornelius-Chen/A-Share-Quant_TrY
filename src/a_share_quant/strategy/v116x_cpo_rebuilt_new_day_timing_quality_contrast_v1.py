from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


NEW_DAYS = ("2023-11-07", "2024-01-18", "2024-01-23")


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass(slots=True)
class V116XCpoRebuiltNewDayTimingQualityContrastReport:
    summary: dict[str, Any]
    contrast_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "contrast_rows": self.contrast_rows,
            "interpretation": self.interpretation,
        }


class V116XCpoRebuiltNewDayTimingQualityContrastAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v116u_payload: dict[str, Any],
        v116w_payload: dict[str, Any],
    ) -> V116XCpoRebuiltNewDayTimingQualityContrastReport:
        rebuilt_rows = [row for row in list(v116u_payload.get("rebuilt_rows", [])) if str(row.get("signal_trade_date")) in NEW_DAYS]
        hit_rows = [row for row in list(v116w_payload.get("hit_rows", [])) if str(row.get("signal_trade_date")) in NEW_DAYS]

        per_day_rebuilt: dict[str, list[dict[str, Any]]] = {day: [] for day in NEW_DAYS}
        per_day_hit: dict[str, list[dict[str, Any]]] = {day: [] for day in NEW_DAYS}
        for row in rebuilt_rows:
            per_day_rebuilt[str(row["signal_trade_date"])].append(row)
        for row in hit_rows:
            per_day_hit[str(row["signal_trade_date"])].append(row)

        contrast_rows: list[dict[str, Any]] = []
        for day in NEW_DAYS:
            rebuilt_day_rows = per_day_rebuilt[day]
            hit_day_rows = per_day_hit[day]
            corrected_hits = [row for row in hit_day_rows if str(row.get("variant_name")) == "corrected_cooled_shadow_candidate"]
            hot_hits = [row for row in hit_day_rows if str(row.get("variant_name")) == "hot_upper_bound_reference"]

            expectancy_values = [_to_float(row.get("expectancy_proxy_3d")) for row in rebuilt_day_rows]
            adverse_values = [_to_float(row.get("max_adverse_return_3d")) for row in rebuilt_day_rows]
            action_favored_count = sum(1 for row in rebuilt_day_rows if bool(row.get("action_favored_3d")))

            earliest_visible_set = sorted({str(row.get("earliest_visible_checkpoint")) for row in hot_hits if row.get("earliest_visible_checkpoint") is not None})
            late_confirmation_set = sorted({str(row.get("late_confirmation_checkpoint")) for row in hot_hits if row.get("late_confirmation_checkpoint") is not None})
            state_band_set = sorted({str(row.get("state_band")) for row in rebuilt_day_rows})

            avg_expectancy = sum(expectancy_values) / len(expectancy_values) if expectancy_values else 0.0
            avg_adverse = sum(adverse_values) / len(adverse_values) if adverse_values else 0.0
            all_late_only = bool(earliest_visible_set) and all(cp >= "14:00" for cp in earliest_visible_set)
            all_early_visible = bool(earliest_visible_set) and all(cp <= "10:30" for cp in earliest_visible_set)

            if corrected_hits:
                diagnosis = "early_visible_and_quality_sufficient_for_corrected_cooled_hit"
            elif all_late_only and avg_expectancy > 0.0:
                diagnosis = "late_only_positive_quality_not_enough_for_corrected_cooled"
            elif all_late_only and avg_expectancy <= 0.0:
                diagnosis = "late_only_and_quality_weak"
            else:
                diagnosis = "mixed_or_inconclusive"

            contrast_rows.append(
                {
                    "signal_trade_date": day,
                    "rebuilt_row_count": len(rebuilt_day_rows),
                    "symbol_set": [str(row["symbol"]) for row in rebuilt_day_rows],
                    "state_bands": state_band_set,
                    "avg_expectancy_proxy_3d": round(avg_expectancy, 6),
                    "avg_max_adverse_return_3d": round(avg_adverse, 6),
                    "action_favored_count": action_favored_count,
                    "corrected_cooled_hit": bool(corrected_hits),
                    "hot_upper_bound_hit": bool(hot_hits),
                    "earliest_visible_checkpoints": earliest_visible_set,
                    "late_confirmation_checkpoints": late_confirmation_set,
                    "all_early_visible": all_early_visible,
                    "all_late_only": all_late_only,
                    "diagnosis": diagnosis,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v116x_cpo_rebuilt_new_day_timing_quality_contrast_v1",
            "reviewed_new_day_count": len(NEW_DAYS),
            "corrected_cooled_new_hit_day_count": sum(1 for row in contrast_rows if bool(row["corrected_cooled_hit"])),
            "coverage_bug_remaining": False,
            "authoritative_current_problem": "quality_discrimination_after_coverage_repair",
            "recommended_next_posture": "keep_candidate_only_and_target_quality_side_refinement_not_timing_relitigation",
        }
        interpretation = [
            "V1.16X compares the three rebuilt expanded-window days side by side after the V116U/V116V coverage repair and the V116W rebuilt-base validation.",
            "The key distinction is no longer missing candidate rows. The surviving difference is whether a new day reaches the corrected cooled line early enough and with enough quality to survive the cooled confirmation gate.",
            "2024-01-18 is the only rebuilt new day that converts into a corrected cooled hit. 2023-11-07 stays positive but late-only, while 2024-01-23 is both late-only and materially weaker.",
        ]
        return V116XCpoRebuiltNewDayTimingQualityContrastReport(
            summary=summary,
            contrast_rows=contrast_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V116XCpoRebuiltNewDayTimingQualityContrastReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116XCpoRebuiltNewDayTimingQualityContrastAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v116u_payload=json.loads((repo_root / "reports" / "analysis" / "v116u_cpo_expanded_window_action_timepoint_rebuild_v1.json").read_text(encoding="utf-8")),
        v116w_payload=json.loads((repo_root / "reports" / "analysis" / "v116w_cpo_corrected_cooled_shadow_expanded_window_validation_rebuilt_base_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116x_cpo_rebuilt_new_day_timing_quality_contrast_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
