from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V131NCommercialAerospaceMN5MinDirectionTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V131NCommercialAerospaceMN5MinDirectionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v131m_commercial_aerospace_5min_feasibility_audit_v1.json"
        )

    def analyze(self) -> V131NCommercialAerospaceMN5MinDirectionTriageReport:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))

        if audit["summary"]["five_min_fully_ready"]:
            authoritative_status = "commercial_aerospace_5min_override_branch_unblocked"
        elif audit["summary"]["five_min_partially_ready"]:
            authoritative_status = "commercial_aerospace_5min_override_branch_partially_ready_but_still_governed"
        else:
            authoritative_status = "keep_commercial_aerospace_5min_branch_blocked"

        triage_rows = [
            {
                "component": "five_min_override_branch",
                "status": authoritative_status,
                "rationale": "the retained override sessions should only open a 5min line if the exact manifest is backfillable",
            },
            {
                "component": "intraday_governance",
                "status": "retain",
                "rationale": "the existing minute-data gate remains the primary governance layer regardless of 5min audit outcome",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v131n_commercial_aerospace_mn_5min_direction_triage_v1",
            "authoritative_status": authoritative_status,
            "success_nonempty_count": audit["summary"]["success_nonempty_count"],
            "attempt_count": audit["summary"]["attempt_count"],
            "authoritative_rule": "a 5min branch is only worth opening if the exact retained override sessions have concrete nonempty support, not just abstract provider availability",
        }
        interpretation = [
            "V1.31N turns the raw 5-minute feasibility check into a go/no-go direction.",
            "It is intentionally narrow: the question is not whether 5-minute data exists in general, but whether it exists for the exact governance-retained override sessions.",
        ]
        return V131NCommercialAerospaceMN5MinDirectionTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131NCommercialAerospaceMN5MinDirectionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V131NCommercialAerospaceMN5MinDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131n_commercial_aerospace_mn_5min_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
