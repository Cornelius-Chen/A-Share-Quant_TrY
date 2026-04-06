from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V133FCommercialAerospaceIntradayReopenChangeGateReport:
    summary: dict[str, Any]
    artifact_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "artifact_rows": self.artifact_rows,
            "interpretation": self.interpretation,
        }


class V133FCommercialAerospaceIntradayReopenChangeGateAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_reopen_change_gate_v1.csv"
        )

    def analyze(self) -> V133FCommercialAerospaceIntradayReopenChangeGateReport:
        artifact_rows = [
            {
                "artifact_type": "minute_visibility_surface",
                "path": "data/training/commercial_aerospace_intraday_supervision_registry_v1.csv",
                "state": "present_but_governance_only",
                "reopen_relevance": "needs lawful point-in-time successor, not just current governance table",
            },
            {
                "artifact_type": "minute_session_archives",
                "path": "data/raw/intraday_a_share_1min_monthly",
                "state": "present",
                "reopen_relevance": "supports research, but not sufficient alone to unlock intraday execution",
            },
            {
                "artifact_type": "intraday_execution_simulator",
                "path": "MISSING: lawful_intraday_execution_simulator",
                "state": "missing",
                "reopen_relevance": "must exist before intraday replay can reopen",
            },
            {
                "artifact_type": "point_in_time_intraday_state_feed",
                "path": "MISSING: point_in_time_intraday_state_feed",
                "state": "missing",
                "reopen_relevance": "must exist before intraday execution can be lawful",
            },
            {
                "artifact_type": "separate_intraday_replay_lane",
                "path": "MISSING: commercial_aerospace_intraday_replay_lane",
                "state": "missing",
                "reopen_relevance": "must exist so minute execution can be tested without contaminating frozen EOD primary",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(artifact_rows[0].keys()))
            writer.writeheader()
            writer.writerows(artifact_rows)

        changed_artifact_count = 0
        missing_artifact_count = sum(1 for row in artifact_rows if row["state"] == "missing")
        summary = {
            "acceptance_posture": "freeze_v133f_commercial_aerospace_intraday_reopen_change_gate_v1",
            "artifact_count": len(artifact_rows),
            "changed_artifact_count": changed_artifact_count,
            "missing_artifact_count": missing_artifact_count,
            "rerun_required": False,
            "gate_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "the commercial-aerospace intraday lane should stay frozen until a lawful point-in-time state feed, an execution simulator, and a separate intraday replay lane exist",
        }
        interpretation = [
            "V1.33F defines the explicit change-gate for reopening commercial-aerospace intraday execution work.",
            "The gate is intentionally infrastructural, because the remaining blockers are no longer local analytical gaps.",
        ]
        return V133FCommercialAerospaceIntradayReopenChangeGateReport(
            summary=summary,
            artifact_rows=artifact_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V133FCommercialAerospaceIntradayReopenChangeGateReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V133FCommercialAerospaceIntradayReopenChangeGateAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133f_commercial_aerospace_intraday_reopen_change_gate_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
