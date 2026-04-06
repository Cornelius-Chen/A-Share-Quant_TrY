from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V133CCommercialAerospaceIntradayExecutionUnblockProtocolReport:
    summary: dict[str, Any]
    requirement_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "requirement_rows": self.requirement_rows,
            "interpretation": self.interpretation,
        }


class V133CCommercialAerospaceIntradayExecutionUnblockProtocolAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.package_path = (
            repo_root / "reports" / "analysis" / "v133a_commercial_aerospace_intraday_governance_packaging_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_execution_unblock_protocol_v1.csv"
        )

    def analyze(self) -> V133CCommercialAerospaceIntradayExecutionUnblockProtocolReport:
        package = json.loads(self.package_path.read_text(encoding="utf-8"))

        requirement_rows = [
            {
                "requirement": "point_in_time_intraday_visibility",
                "status": "blocked",
                "current_state": "governance_only_minute_labels_and_day-level event framing exist, but no point-in-time intraday visibility chain exists",
                "unlock_condition": "a lawful intraday feature surface exists where minute-state and event-state are both timestamp-visible before action time",
            },
            {
                "requirement": "intraday_execution_simulation_surface",
                "status": "blocked",
                "current_state": "no intraday fill model or minute-level action simulator is attached to the governance package",
                "unlock_condition": "a reproducible minute-level execution simulator exists with explicit fill timing, slippage, and cost assumptions",
            },
            {
                "requirement": "replay_binding_surface",
                "status": "blocked",
                "current_state": "the lawful EOD replay remains authoritative and isolated from the minute governance branch",
                "unlock_condition": "a separate lawful intraday replay lane exists so the minute branch can be tested without contaminating the frozen EOD primary",
            },
            {
                "requirement": "commercial_aerospace_minute_package",
                "status": "ready",
                "current_state": package["summary"]["authoritative_output"],
                "unlock_condition": "already satisfied as the supervision/governance input for future intraday work",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(requirement_rows[0].keys()))
            writer.writeheader()
            writer.writerows(requirement_rows)

        blocked_count = sum(1 for row in requirement_rows if row["status"] == "blocked")
        summary = {
            "acceptance_posture": "freeze_v133c_commercial_aerospace_intraday_execution_unblock_protocol_v1",
            "current_primary_variant": package["summary"]["current_primary_variant"],
            "blocked_requirement_count": blocked_count,
            "ready_requirement_count": sum(1 for row in requirement_rows if row["status"] == "ready"),
            "protocol_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_intraday_execution_unblock_protocol_frozen",
        }
        interpretation = [
            "V1.33C turns the commercial-aerospace minute package blockers into an explicit intraday-execution unblock protocol.",
            "The intent is operational clarity: future work should wait for these gates rather than drifting into more local tuning.",
        ]
        return V133CCommercialAerospaceIntradayExecutionUnblockProtocolReport(
            summary=summary,
            requirement_rows=requirement_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V133CCommercialAerospaceIntradayExecutionUnblockProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V133CCommercialAerospaceIntradayExecutionUnblockProtocolAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133c_commercial_aerospace_intraday_execution_unblock_protocol_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
