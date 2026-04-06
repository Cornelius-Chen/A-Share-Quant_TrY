from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V131RCommercialAerospaceQRLocal5MinDirectionTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V131RCommercialAerospaceQRLocal5MinDirectionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v131q_commercial_aerospace_local_5min_resample_feasibility_audit_v1.json"
        )

    def analyze(self) -> V131RCommercialAerospaceQRLocal5MinDirectionTriageReport:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        if audit["summary"]["local_5min_fully_ready"]:
            authoritative_status = "commercial_aerospace_local_5min_override_branch_unblocked"
        else:
            authoritative_status = "keep_commercial_aerospace_5min_branch_governed"

        triage_rows = [
            {
                "component": "local_5min_override_branch",
                "status": authoritative_status,
                "rationale": "the exact retained override sessions can now be expressed as local 5min bars without external provider dependence",
            },
            {
                "component": "eod_primary_replay",
                "status": "unchanged",
                "rationale": "the local 5min branch opens a narrow prototype path only; it does not replace the current lawful EOD primary",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v131r_commercial_aerospace_qr_local_5min_direction_triage_v1",
            "authoritative_status": authoritative_status,
            "ready_count": audit["summary"]["ready_count"],
            "manifest_row_count": audit["summary"]["manifest_row_count"],
            "authoritative_rule": "once the retained override sessions are locally resampleable to 5min, the narrow commercial-aerospace 5min prototype is unblocked for governance-bound analysis",
        }
        interpretation = [
            "V1.31R turns local 5-minute resample readiness into a branch-level direction.",
            "It is still governed and narrow: only the retained override sessions are unblocked.",
        ]
        return V131RCommercialAerospaceQRLocal5MinDirectionTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131RCommercialAerospaceQRLocal5MinDirectionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V131RCommercialAerospaceQRLocal5MinDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131r_commercial_aerospace_qr_local_5min_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
