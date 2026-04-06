from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134CLCommercialAerospaceReduceCompletionStatusAuditV1Report:
    summary: dict[str, Any]
    status_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "status_rows": self.status_rows,
            "interpretation": self.interpretation,
        }


class V134CLCommercialAerospaceReduceCompletionStatusAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.reduce_stack_path = analysis_dir / "v134bo_commercial_aerospace_reduce_closure_governance_spec_v1.json"
        self.blocker_path = analysis_dir / "v134bq_commercial_aerospace_reduce_execution_binding_blocker_audit_v1.json"
        self.binding_path = analysis_dir / "v134ce_commercial_aerospace_cd_binding_quality_direction_triage_v1.json"
        self.horizon_path = analysis_dir / "v134cg_commercial_aerospace_cf_horizon_quality_direction_triage_v1.json"
        self.residue_path = analysis_dir / "v134ck_commercial_aerospace_cj_local_rebound_direction_triage_v1.json"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_reduce_completion_status_audit_v1.csv"
        )

    def analyze(self) -> V134CLCommercialAerospaceReduceCompletionStatusAuditV1Report:
        reduce_stack = json.loads(self.reduce_stack_path.read_text(encoding="utf-8"))
        blockers = json.loads(self.blocker_path.read_text(encoding="utf-8"))
        binding = json.loads(self.binding_path.read_text(encoding="utf-8"))
        horizon = json.loads(self.horizon_path.read_text(encoding="utf-8"))
        residue = json.loads(self.residue_path.read_text(encoding="utf-8"))

        status_rows = [
            {
                "component": "governance_stack",
                "status": "complete_for_research",
                "detail": f"closure_stage_count = {reduce_stack['summary']['closure_stage_count']}",
            },
            {
                "component": "sell_side_binding_surface",
                "status": "first_real_binding_reference_ready",
                "detail": f"authoritative_status = {binding['summary']['authoritative_status']}",
            },
            {
                "component": "sell_side_horizon_quality",
                "status": "understood_with_caveat",
                "detail": f"authoritative_status = {horizon['summary']['authoritative_status']}",
            },
            {
                "component": "broad_reduce_tuning",
                "status": "stopline_reached",
                "detail": f"authoritative_status = {residue['summary']['authoritative_status']}",
            },
            {
                "component": "execution_binding",
                "status": "still_blocked",
                "detail": f"full_reduce_binding_blocker_count = {blockers['summary']['full_reduce_binding_blocker_count']}",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(status_rows[0].keys()))
            writer.writeheader()
            writer.writerows(status_rows)

        summary = {
            "acceptance_posture": "freeze_v134cl_commercial_aerospace_reduce_completion_status_audit_v1",
            "governance_stack_ready": True,
            "sell_side_binding_reference_ready": True,
            "broad_reduce_tuning_stopped": True,
            "local_residue_supervision_only": True,
            "full_execution_binding_still_blocked": True,
            "remaining_execution_blocker_count": blockers["summary"]["full_reduce_binding_blocker_count"],
            "residue_seed_count": residue["summary"]["residue_seed_count"],
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_reduce_completion_status_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34CL answers a narrower question than replay readiness: whether reduce has been sufficiently researched and compressed into a stable mainline.",
            "The branch is now mature enough to separate research completion from execution closure. Those are no longer the same question.",
        ]
        return V134CLCommercialAerospaceReduceCompletionStatusAuditV1Report(
            summary=summary,
            status_rows=status_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CLCommercialAerospaceReduceCompletionStatusAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CLCommercialAerospaceReduceCompletionStatusAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cl_commercial_aerospace_reduce_completion_status_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
