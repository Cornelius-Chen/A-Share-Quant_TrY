from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BRCommercialAerospaceBQExecutionBindingDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134BRCommercialAerospaceBQExecutionBindingDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134bq_commercial_aerospace_reduce_execution_binding_blocker_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_bq_execution_binding_direction_triage_v1.csv"
        )

    def analyze(self) -> V134BRCommercialAerospaceBQExecutionBindingDirectionTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        triage_rows = [
            {
                "component": "sell_side_binding",
                "status": "not_ready",
                "detail": "Still blocked by point_in_time_intraday_visibility and intraday_execution_simulation_surface.",
            },
            {
                "component": "board_gate_binding",
                "status": "not_ready",
                "detail": "Board expectancy and lockout/unlock remain governance-only until the intraday simulator exists.",
            },
            {
                "component": "reentry_binding",
                "status": "not_started",
                "detail": "Seed reentry ladder has supervision only; no reentry execution surface exists yet.",
            },
            {
                "component": "full_reduce_closure",
                "status": "execution_gap_only",
                "detail": "Conceptual closure largely exists; the remaining gap is execution infrastructure rather than semantic ambiguity.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134br_commercial_aerospace_bq_execution_binding_direction_triage_v1",
            "authoritative_status": "freeze_execution_binding_gap_and_keep_reduce_board_first_governance",
            "blocker_count": audit["summary"]["blocker_count"],
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34BR turns execution binding blockers into a direction judgment.",
            "The branch should now stop debating whether reduce is conceptually clear and instead admit that the remaining gap is execution infrastructure.",
        ]
        return V134BRCommercialAerospaceBQExecutionBindingDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BRCommercialAerospaceBQExecutionBindingDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BRCommercialAerospaceBQExecutionBindingDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134br_commercial_aerospace_bq_execution_binding_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
