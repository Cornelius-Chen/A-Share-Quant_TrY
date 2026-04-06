from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V133ECommercialAerospaceCDEIntradayExecutionGovernanceTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V133ECommercialAerospaceCDEIntradayExecutionGovernanceTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.status_card_path = (
            repo_root / "reports" / "analysis" / "v133d_commercial_aerospace_intraday_execution_status_card_v1.json"
        )

    def analyze(self) -> V133ECommercialAerospaceCDEIntradayExecutionGovernanceTriageReport:
        status_card = json.loads(self.status_card_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v133e_commercial_aerospace_cde_intraday_execution_governance_triage_v1",
            "authoritative_status": "freeze_commercial_aerospace_intraday_execution_lane_until_protocol_unblocks",
            "intraday_execution_status": status_card["summary"]["intraday_execution_status"],
            "blocked_component_count": status_card["summary"]["blocked_component_count"],
            "authoritative_rule": "once the minute governance package is complete, the correct next step is to wait on explicit intraday-execution unblock conditions rather than continue local experimentation",
        }
        triage_rows = [
            {
                "component": "commercial_aerospace_intraday_execution_lane",
                "status": "freeze_until_protocol_unblocks",
                "rationale": "the governance package is complete and the remaining blockers are infrastructural rather than analytical",
            },
            {
                "component": "commercial_aerospace_minute_governance_package",
                "status": "retain_frozen",
                "rationale": "the package should remain stable and reusable while waiting for lawful intraday conditions",
            },
        ]
        interpretation = [
            "V1.33E freezes the commercial-aerospace intraday execution lane behind an explicit governance protocol.",
            "The remaining work is infrastructural, not another round of board-local minute research.",
        ]
        return V133ECommercialAerospaceCDEIntradayExecutionGovernanceTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V133ECommercialAerospaceCDEIntradayExecutionGovernanceTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V133ECommercialAerospaceCDEIntradayExecutionGovernanceTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133e_commercial_aerospace_cde_intraday_execution_governance_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
