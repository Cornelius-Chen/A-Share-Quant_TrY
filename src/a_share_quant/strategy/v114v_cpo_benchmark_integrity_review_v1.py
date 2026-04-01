from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V114VCpoBenchmarkIntegrityReviewReport:
    summary: dict[str, Any]
    benchmark_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "benchmark_rows": self.benchmark_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V114VCpoBenchmarkIntegrityReviewAnalyzer:
    def analyze(
        self,
        *,
        v112aa_payload: dict[str, Any],
        v114t_payload: dict[str, Any],
    ) -> V114VCpoBenchmarkIntegrityReviewReport:
        summary_t = dict(v114t_payload.get("summary", {}))
        if str(summary_t.get("acceptance_posture")) != "freeze_v114t_cpo_replay_integrity_repair_v1":
            raise ValueError("V1.14V expects the V1.14T repaired replay report.")

        day_rows = list(v114t_payload.get("replay_day_rows", []))
        order_rows = list(v114t_payload.get("executed_order_rows", []))
        if not day_rows:
            raise ValueError("V1.14V requires repaired replay day rows.")

        action_logic_symbols = sorted(
            {
                str(row["symbol"])
                for row in order_rows
            }
        )
        all_board_symbols = sorted({str(row["symbol"]) for row in v112aa_payload.get("object_role_time_rows", [])})

        strategy_curve = float(day_rows[-1]["equity_after_close"]) / float(summary_t["initial_capital"])
        board_equal_curve = 1.0
        active_universe_curve = 1.0
        active_universe_weight_sum = 0.0
        for row in day_rows:
            board_context = dict(row["board_context"])
            board_equal_curve *= 1.0 + float(board_context.get("avg_return", 0.0))
            top_turnover_symbols = list(board_context.get("top_turnover_symbols", []))
            # Conservative executable proxy: only count days where the already-mature action universe participates in board leadership.
            active_hits = [symbol for symbol in top_turnover_symbols if symbol in action_logic_symbols]
            participation_ratio = 0.0 if not top_turnover_symbols else len(active_hits) / len(top_turnover_symbols)
            active_universe_weight_sum += participation_ratio
            active_universe_curve *= 1.0 + float(board_context.get("avg_return", 0.0)) * participation_ratio

        benchmark_rows = [
            {
                "benchmark_name": "strategy_repaired_replay",
                "curve": round(strategy_curve, 4),
                "coverage_basis": "actual_sparse_action_strategy",
                "use_case": "primary_judgement_surface",
            },
            {
                "benchmark_name": "board_equal_weight_opportunity",
                "curve": round(board_equal_curve, 4),
                "coverage_basis": f"all_{len(all_board_symbols)}_board_symbols_equal_weight_opportunity",
                "use_case": "opportunity_ceiling_not_execution_fair_benchmark",
            },
            {
                "benchmark_name": "action_coverage_proxy",
                "curve": round(active_universe_curve, 4),
                "coverage_basis": f"leadership-participation_proxy_from_{len(action_logic_symbols)}_action_symbols",
                "use_case": "fairer_comparison_for_sparse_action_logic",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v114v_cpo_benchmark_integrity_review_v1",
            "strategy_curve": round(strategy_curve, 4),
            "board_equal_weight_curve": round(board_equal_curve, 4),
            "action_coverage_proxy_curve": round(active_universe_curve, 4),
            "board_benchmark_is_opportunity_ceiling": True,
            "recommended_primary_comparison": "strategy_vs_action_coverage_proxy",
            "recommended_next_posture": "rerun_under_exposure_and_sizing_on_repaired_replay_using_action_coverage_proxy_as_the_fairer_reference",
        }

        interpretation = [
            "V1.14V separates opportunity benchmarking from executable benchmarking.",
            "Board equal-weight remains useful, but only as an opportunity ceiling; it is too loose as the main benchmark for a sparse-action strategy.",
            "The repaired replay should now be judged primarily against the action-coverage proxy and only secondarily against the full-board opportunity curve.",
        ]

        return V114VCpoBenchmarkIntegrityReviewReport(
            summary=summary,
            benchmark_rows=benchmark_rows,
            interpretation=interpretation,
        )


def write_v114v_cpo_benchmark_integrity_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V114VCpoBenchmarkIntegrityReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V114VCpoBenchmarkIntegrityReviewAnalyzer()
    result = analyzer.analyze(
        v112aa_payload=load_json_report(repo_root / "reports" / "analysis" / "v112aa_cpo_bounded_cohort_map_v1.json"),
        v114t_payload=load_json_report(repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json"),
    )
    output_path = write_v114v_cpo_benchmark_integrity_review_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v114v_cpo_benchmark_integrity_review_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
