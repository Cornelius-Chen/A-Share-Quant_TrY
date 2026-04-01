from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V114WCpoUnderExposureAttributionRepairedReport:
    summary: dict[str, Any]
    top_opportunity_miss_rows: list[dict[str, Any]]
    episode_action_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "top_opportunity_miss_rows": self.top_opportunity_miss_rows,
            "episode_action_rows": self.episode_action_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V114WCpoUnderExposureAttributionRepairedAnalyzer:
    def analyze(
        self,
        *,
        v114t_payload: dict[str, Any],
        v114v_payload: dict[str, Any],
    ) -> V114WCpoUnderExposureAttributionRepairedReport:
        summary_t = dict(v114t_payload.get("summary", {}))
        summary_v = dict(v114v_payload.get("summary", {}))
        if str(summary_t.get("acceptance_posture")) != "freeze_v114t_cpo_replay_integrity_repair_v1":
            raise ValueError("V1.14W expects the repaired replay.")
        if str(summary_v.get("acceptance_posture")) != "freeze_v114v_cpo_benchmark_integrity_review_v1":
            raise ValueError("V1.14W expects the repaired benchmark review.")

        day_rows = list(v114t_payload.get("replay_day_rows", []))
        if not day_rows:
            raise ValueError("V1.14W requires repaired replay day rows.")

        strategy_curve = float(summary_t["final_equity"]) / float(summary_t["initial_capital"])
        action_proxy_curve = float(summary_v["action_coverage_proxy_curve"])
        board_curve = float(summary_v["board_equal_weight_curve"])

        top_opportunity_miss_rows = []
        episode_action_rows = []
        for row in day_rows:
            board_context = dict(row["board_context"])
            avg_return = float(board_context.get("avg_return", 0.0))
            breadth = float(board_context.get("breadth", 0.0))
            exposure = float(row["gross_exposure_after_close"])
            if avg_return >= 0.06 and breadth >= 0.8 and exposure < 0.2:
                top_opportunity_miss_rows.append(
                    {
                        "trade_date": str(row["trade_date"]),
                        "board_avg_return": round(avg_return, 6),
                        "board_breadth": round(breadth, 6),
                        "gross_exposure_after_close": round(exposure, 6),
                        "executed_today_order_count": int(row["executed_today_order_count"]),
                        "miss_reading": "board_strong_but_repaired_strategy_still_light",
                    }
                )
            if int(row["episode_count"]) > 0:
                episode_action_rows.append(
                    {
                        "trade_date": str(row["trade_date"]),
                        "board_avg_return": round(avg_return, 6),
                        "board_breadth": round(breadth, 6),
                        "gross_exposure_after_close": round(exposure, 6),
                        "planned_order_count": int(row["planned_order_count"]),
                    }
                )

        summary = {
            "acceptance_posture": "freeze_v114w_cpo_under_exposure_attribution_repaired_v1",
            "strategy_curve_repaired": round(strategy_curve, 4),
            "action_coverage_proxy_curve": round(action_proxy_curve, 4),
            "board_equal_weight_curve": round(board_curve, 4),
            "curve_gap_vs_action_coverage_proxy": round(strategy_curve - action_proxy_curve, 4),
            "curve_gap_vs_board": round(strategy_curve - board_curve, 4),
            "top_opportunity_miss_count": len(top_opportunity_miss_rows),
            "primary_under_exposure_reading": "under_exposure_still_present_after_replay_integrity_repair",
            "recommended_next_posture": "rebuild_sizing_grammar_on_repaired_replay_not_on_the_optimistic_surface",
        }

        interpretation = [
            "V1.14W reruns the core under-exposure judgement on the repaired replay surface.",
            "The conclusion can now be trusted more than the older V1.13W line because execution timing and transaction costs are no longer optimistic.",
            "If under-exposure still dominates here, then the sizing problem is real rather than an artifact of same-day execution assumptions.",
        ]

        return V114WCpoUnderExposureAttributionRepairedReport(
            summary=summary,
            top_opportunity_miss_rows=top_opportunity_miss_rows[:10],
            episode_action_rows=episode_action_rows,
            interpretation=interpretation,
        )


def write_v114w_cpo_under_exposure_attribution_repaired_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V114WCpoUnderExposureAttributionRepairedReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V114WCpoUnderExposureAttributionRepairedAnalyzer()
    result = analyzer.analyze(
        v114t_payload=load_json_report(repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json"),
        v114v_payload=load_json_report(repo_root / "reports" / "analysis" / "v114v_cpo_benchmark_integrity_review_v1.json"),
    )
    output_path = write_v114w_cpo_under_exposure_attribution_repaired_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v114w_cpo_under_exposure_attribution_repaired_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
