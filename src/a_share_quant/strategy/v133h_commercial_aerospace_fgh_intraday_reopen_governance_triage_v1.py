from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V133HCommercialAerospaceFGHIntradayReopenGovernanceTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V133HCommercialAerospaceFGHIntradayReopenGovernanceTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.heartbeat_path = (
            repo_root / "reports" / "analysis" / "v133g_commercial_aerospace_intraday_heartbeat_status_v1.json"
        )

    def analyze(self) -> V133HCommercialAerospaceFGHIntradayReopenGovernanceTriageReport:
        heartbeat = json.loads(self.heartbeat_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v133h_commercial_aerospace_fgh_intraday_reopen_governance_triage_v1",
            "authoritative_status": "freeze_commercial_aerospace_intraday_branch_and_wait_for_change_gate",
            "program_status": heartbeat["summary"]["program_status"],
            "rerun_required": heartbeat["summary"]["rerun_required"],
            "authoritative_rule": "the completed commercial-aerospace minute package should remain frozen until explicit infrastructural change gates open",
        }
        triage_rows = [
            {
                "component": "commercial_aerospace_intraday_branch",
                "status": "freeze_and_wait_for_change_gate",
                "rationale": "the remaining blockers are infrastructural rather than analytical, so continued local work would be empty motion",
            },
            {
                "component": "commercial_aerospace_governance_package",
                "status": "retain_frozen_and_reusable",
                "rationale": "the package is already complete enough to carry forward into any future lawful intraday context",
            },
        ]
        interpretation = [
            "V1.33H freezes the commercial-aerospace intraday branch behind an explicit reopen governance gate.",
            "The branch's next valid step now depends on infrastructure change, not more board-local research.",
        ]
        return V133HCommercialAerospaceFGHIntradayReopenGovernanceTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V133HCommercialAerospaceFGHIntradayReopenGovernanceTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V133HCommercialAerospaceFGHIntradayReopenGovernanceTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133h_commercial_aerospace_fgh_intraday_reopen_governance_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
