from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134AHCommercialAerospaceAGHorizonDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134AHCommercialAerospaceAGHorizonDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134ag_commercial_aerospace_reversal_full_horizon_sanity_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_ag_horizon_direction_triage_v1.csv"
        )

    def analyze(self) -> V134AHCommercialAerospaceAGHorizonDirectionTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        horizon_5 = next(row for row in audit["horizon_rows"] if row["horizon_days"] == 5)
        net_5d = horizon_5["net_horizon_pnl_if_held"]
        positive_5d = horizon_5["positive_rebound_cost_total"]
        negative_5d = horizon_5["negative_followthrough_benefit_total"]

        keep = negative_5d <= -positive_5d
        triage_rows = [
            {
                "component": "reversal_100pct_same_day_shadow",
                "status": "retain_with_horizon_caveat" if keep else "retain_as_same_day_only_and_do_not_promote_further",
                "detail": f"net_horizon_pnl_if_held_5d = {net_5d}, rebound_cost_total_5d = {positive_5d}",
            },
            {
                "component": "all_session_widening",
                "status": "still_blocked",
                "detail": "Horizon sanity does not authorize wider surface expansion.",
            },
            {
                "component": "phase3_replay_lane",
                "status": "still_blocked",
                "detail": "Horizon sanity is supervisory only and does not convert same-day shadow optimization into replay binding.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134ah_commercial_aerospace_ag_horizon_direction_triage_v1",
            "authoritative_status": (
                "retain_reversal_100pct_with_horizon_caveat"
                if keep
                else "retain_reversal_100pct_as_same_day_shadow_only_and_stop_promotion"
            ),
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34AH converts the horizon sanity audit into the next supervision judgment.",
            "The branch is allowed to keep the same-day optimal full-reversal reference, but the result must stay explicitly labeled as horizon-limited if later rebound opportunity cost remains material.",
        ]
        return V134AHCommercialAerospaceAGHorizonDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134AHCommercialAerospaceAGHorizonDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134AHCommercialAerospaceAGHorizonDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ah_commercial_aerospace_ag_horizon_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
