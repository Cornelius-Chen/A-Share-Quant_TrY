from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134OCommercialAerospaceBroaderHitSupervisionFailureReviewReport:
    summary: dict[str, Any]
    failure_rows: list[dict[str, Any]]
    recommendation_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "failure_rows": self.failure_rows,
            "recommendation_rows": self.recommendation_rows,
            "interpretation": self.interpretation,
        }


class V134OCommercialAerospaceBroaderHitSupervisionFailureReviewAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.sessions_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_broader_hit_simulator_sessions_v1.csv"
        )
        self.attr_path = (
            repo_root / "reports" / "analysis" / "v134n_commercial_aerospace_broader_hit_simulator_attribution_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_broader_hit_supervision_failure_review_v1.csv"
        )

    def analyze(self) -> V134OCommercialAerospaceBroaderHitSupervisionFailureReviewReport:
        with self.sessions_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        attr = json.loads(self.attr_path.read_text(encoding="utf-8"))

        failure_rows = []
        for row in rows:
            same_day_loss_avoided = float(row["same_day_loss_avoided"])
            if same_day_loss_avoided >= 0:
                continue
            failure_rows.append(
                {
                    "trade_date": row["trade_date"],
                    "symbol": row["symbol"],
                    "predicted_tier": row["predicted_tier"],
                    "filled_step_count": int(row["filled_step_count"]),
                    "first_reversal_minute": row["first_reversal_minute"],
                    "first_severe_minute": row["first_severe_minute"],
                    "baseline_hold_pnl": float(row["baseline_hold_pnl"]),
                    "simulated_pnl": float(row["simulated_pnl"]),
                    "same_day_loss_avoided": same_day_loss_avoided,
                }
            )

        failure_rows.sort(key=lambda row: (row["same_day_loss_avoided"], row["trade_date"], row["symbol"]))

        recommendation_rows = [
            {
                "optimization_area": "mild_predicted_session_execution",
                "status": "tighten",
                "detail": "Predicted mild sessions account for the broadening drag; keep them governance-only even if a later reversal minute appears.",
            },
            {
                "optimization_area": "reversal_first_broader_lane",
                "status": "retain",
                "detail": "Predicted reversal sessions remain the most credible broader-hit widening slice and should stay as the first executable wider lane.",
            },
            {
                "optimization_area": "severe_predicted_session_lane",
                "status": "retain",
                "detail": "Predicted severe sessions remain net-positive and should stay as a terminal emergency component in the broader-hit lane.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        if failure_rows:
            with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(failure_rows[0].keys()))
                writer.writeheader()
                writer.writerows(failure_rows)

        mild_tier = next(row for row in attr["tier_rows"] if row["predicted_tier"] == "mild_override_watch")
        summary = {
            "acceptance_posture": "freeze_v134o_commercial_aerospace_broader_hit_supervision_failure_review_v1",
            "negative_session_count": len(failure_rows),
            "worst_negative_same_day_loss_avoided": round(min((row["same_day_loss_avoided"] for row in failure_rows), default=0.0), 4),
            "mild_tier_same_day_loss_avoided_total": mild_tier["same_day_loss_avoided_total"],
            "recommended_boundary_change": "block_execution_for_predicted_mild_sessions_inside_broader_hit_lane",
            "failure_csv": str(self.output_csv.relative_to(self.repo_root)) if failure_rows else "",
            "authoritative_output": "commercial_aerospace_broader_hit_supervision_failure_review_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34O reviews the first broader-hit widening as a supervision object rather than as a trading result.",
            "The main failure pattern is that predicted mild sessions can still drag the wider lane when later reversal triggers are allowed to execute on them.",
        ]
        return V134OCommercialAerospaceBroaderHitSupervisionFailureReviewReport(
            summary=summary,
            failure_rows=failure_rows,
            recommendation_rows=recommendation_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134OCommercialAerospaceBroaderHitSupervisionFailureReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134OCommercialAerospaceBroaderHitSupervisionFailureReviewAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134o_commercial_aerospace_broader_hit_supervision_failure_review_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
