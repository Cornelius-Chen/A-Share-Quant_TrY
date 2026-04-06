from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V131PCommercialAerospaceOPLocal1MinDirectionTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V131PCommercialAerospaceOPLocal1MinDirectionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v131o_commercial_aerospace_local_1min_archive_readiness_audit_v1.json"
        )

    def analyze(self) -> V131PCommercialAerospaceOPLocal1MinDirectionTriageReport:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        if audit["summary"]["local_1min_fully_ready"]:
            authoritative_status = "commercial_aerospace_local_1min_override_branch_unblocked"
        else:
            authoritative_status = "keep_intraday_override_branch_governed_until_local_1min_is_complete"

        triage_rows = [
            {
                "component": "local_1min_override_branch",
                "status": authoritative_status,
                "rationale": "the exact retained override sessions now have local archive support and no longer depend on external provider stability",
            },
            {
                "component": "minute_collection_gate",
                "status": "superseded_for_retained_sessions" if audit["summary"]["local_1min_fully_ready"] else "retain",
                "rationale": "the original collection gate remains useful for future expansion, but the retained sessions can now move to local processing",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v131p_commercial_aerospace_op_local_1min_direction_triage_v1",
            "authoritative_status": authoritative_status,
            "ready_count": audit["summary"]["ready_count"],
            "manifest_row_count": audit["summary"]["manifest_row_count"],
            "authoritative_rule": "local retained-session coverage unlocks the commercial-aerospace intraday branch for local modeling work, but does not yet make the branch replay-facing by itself",
        }
        interpretation = [
            "V1.31P turns the local 1-minute archive audit into a go/no-go direction for the retained override sessions.",
            "This is still a governance step: it unblocks local intraday prototyping, not direct replay promotion.",
        ]
        return V131PCommercialAerospaceOPLocal1MinDirectionTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131PCommercialAerospaceOPLocal1MinDirectionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V131PCommercialAerospaceOPLocal1MinDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131p_commercial_aerospace_op_local_1min_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
