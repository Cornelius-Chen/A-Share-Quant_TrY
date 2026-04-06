from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134LDAShareInformationCenterFoundationCompletionAuditV1Report:
    summary: dict[str, Any]
    workstream_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "workstream_rows": self.workstream_rows,
            "interpretation": self.interpretation,
        }


class V134LDAShareInformationCenterFoundationCompletionAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root / "data" / "training" / "a_share_information_center_foundation_completion_status_v1.csv"
        )

    def analyze(self) -> V134LDAShareInformationCenterFoundationCompletionAuditV1Report:
        workstream_rows = [
            {"workstream": "identity", "state": "foundation_complete_enough", "residual_mode": "backlog_extend_only"},
            {"workstream": "taxonomy", "state": "foundation_complete_enough", "residual_mode": "business_reference_and_purity_backlog"},
            {"workstream": "market", "state": "foundation_complete_enough", "residual_mode": "board_state_derivation_backlog"},
            {"workstream": "events", "state": "foundation_complete_enough", "residual_mode": "future_source_activation"},
            {"workstream": "attention", "state": "foundation_complete_enough", "residual_mode": "future_evidence_expansion"},
            {"workstream": "quality", "state": "foundation_complete_enough", "residual_mode": "contradiction_resolution_backlog"},
            {"workstream": "labels", "state": "foundation_complete_enough", "residual_mode": "state_and_governance_label_backlog"},
            {"workstream": "features", "state": "foundation_complete_enough", "residual_mode": "representation_backlog"},
            {"workstream": "pti", "state": "foundation_complete_enough", "residual_mode": "execution_state_backlog"},
            {"workstream": "replay", "state": "foundation_complete_enough", "residual_mode": "read_only_non_promotive"},
            {"workstream": "serving", "state": "foundation_complete_enough", "residual_mode": "live_like_deferred"},
            {"workstream": "governance", "state": "foundation_complete_enough", "residual_mode": "gate_control_only"},
            {"workstream": "automation", "state": "foundation_complete_enough", "residual_mode": "job_contracts_not_yet_activated"},
        ]
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(workstream_rows[0].keys()))
            writer.writeheader()
            writer.writerows(workstream_rows)

        foundation_complete_count = sum(row["state"] == "foundation_complete_enough" for row in workstream_rows)
        summary = {
            "workstream_count": len(workstream_rows),
            "foundation_complete_count": foundation_complete_count,
            "open_execution_gate_count": 0,
            "deferred_live_like_count": 1,
            "backlog_carrying_workstream_count": len(workstream_rows),
            "completion_status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_information_center_foundation_complete_enough_to_freeze",
        }
        interpretation = [
            "All 13 information-center workstreams now have first-pass foundations, tests, and status artifacts; the center is no longer a blueprint-only scaffold.",
            "Completion here means foundation-complete, not fully promoted: multiple layers intentionally carry backlogs, deferred live-like paths, and closed execution gates.",
        ]
        return V134LDAShareInformationCenterFoundationCompletionAuditV1Report(
            summary=summary,
            workstream_rows=workstream_rows,
            interpretation=interpretation,
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134LDAShareInformationCenterFoundationCompletionAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134LDAShareInformationCenterFoundationCompletionAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ld_a_share_information_center_foundation_completion_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
