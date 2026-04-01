from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V114XCpoProbabilityExpectancySizingFrameworkRepairedReport:
    summary: dict[str, Any]
    exposure_floor_rows: list[dict[str, Any]]
    source_sizing_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "exposure_floor_rows": self.exposure_floor_rows,
            "source_sizing_rows": self.source_sizing_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V114XCpoProbabilityExpectancySizingFrameworkRepairedAnalyzer:
    def analyze(
        self,
        *,
        v114t_payload: dict[str, Any],
        v114w_payload: dict[str, Any],
    ) -> V114XCpoProbabilityExpectancySizingFrameworkRepairedReport:
        summary_t = dict(v114t_payload.get("summary", {}))
        summary_w = dict(v114w_payload.get("summary", {}))
        if str(summary_t.get("acceptance_posture")) != "freeze_v114t_cpo_replay_integrity_repair_v1":
            raise ValueError("V1.14X expects the repaired replay.")
        if str(summary_w.get("acceptance_posture")) != "freeze_v114w_cpo_under_exposure_attribution_repaired_v1":
            raise ValueError("V1.14X expects the repaired under-exposure review.")

        day_rows = list(v114t_payload.get("replay_day_rows", []))
        peak_exposure = max(float(row["gross_exposure_after_close"]) for row in day_rows) if day_rows else 0.0

        exposure_floor_rows = [
            {
                "board_state": "strong_board_with_one_high_probability_line",
                "trigger": {
                    "board_avg_return_min": 0.03,
                    "board_breadth_min": 0.60,
                },
                "minimum_target_gross_exposure": 0.30,
            },
            {
                "board_state": "strong_board_with_two_or_more_credible_lines",
                "trigger": {
                    "board_avg_return_min": 0.05,
                    "board_breadth_min": 0.80,
                },
                "minimum_target_gross_exposure": 0.45,
            },
            {
                "board_state": "mixed_board_or_probe_only",
                "trigger": {
                    "board_avg_return_min": 0.00,
                    "board_breadth_min": 0.00,
                },
                "minimum_target_gross_exposure": 0.10,
            },
        ]

        source_sizing_rows = [
            {
                "source_family": "core_module_leader",
                "expression_reading": "highest_expression",
                "repaired_weight_band": [0.16, 0.24],
            },
            {
                "source_family": "packaging_process_enabler",
                "expression_reading": "medium_to_high_expression",
                "repaired_weight_band": [0.10, 0.18],
            },
            {
                "source_family": "high_beta_core_module",
                "expression_reading": "medium_expression_with_derisk_readiness",
                "repaired_weight_band": [0.08, 0.14],
            },
            {
                "source_family": "laser_chip_component",
                "expression_reading": "probe_expression_only",
                "repaired_weight_band": [0.03, 0.08],
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v114x_cpo_probability_expectancy_sizing_framework_repaired_v1",
            "primary_gap_reading": summary_w["primary_under_exposure_reading"],
            "current_peak_gross_exposure_repaired": round(peak_exposure, 4),
            "recommended_strong_board_min_gross_exposure_repaired": 0.30,
            "recommended_two_line_strong_board_min_gross_exposure_repaired": 0.45,
            "framework_ready_for_replay_injection_next": True,
            "recommended_next_posture": "rebuild_future_cpo_sizing_trials_on_v114t_not_v113v",
        }

        interpretation = [
            "V1.14X reissues the sizing grammar on the repaired replay surface instead of the optimistic same-day replay.",
            "The core conclusion survives, but the floor recommendations are trimmed slightly to respect more realistic execution and cost drag.",
            "This repaired sizing grammar should replace the earlier V1.13X line for any future CPO experiments.",
        ]

        return V114XCpoProbabilityExpectancySizingFrameworkRepairedReport(
            summary=summary,
            exposure_floor_rows=exposure_floor_rows,
            source_sizing_rows=source_sizing_rows,
            interpretation=interpretation,
        )


def write_v114x_cpo_probability_expectancy_sizing_framework_repaired_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V114XCpoProbabilityExpectancySizingFrameworkRepairedReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V114XCpoProbabilityExpectancySizingFrameworkRepairedAnalyzer()
    result = analyzer.analyze(
        v114t_payload=load_json_report(repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json"),
        v114w_payload=load_json_report(repo_root / "reports" / "analysis" / "v114w_cpo_under_exposure_attribution_repaired_v1.json"),
    )
    output_path = write_v114x_cpo_probability_expectancy_sizing_framework_repaired_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v114x_cpo_probability_expectancy_sizing_framework_repaired_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
