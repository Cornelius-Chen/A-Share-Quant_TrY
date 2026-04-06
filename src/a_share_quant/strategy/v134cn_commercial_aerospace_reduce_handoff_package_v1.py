from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134CNCommercialAerospaceReduceHandoffPackageV1Report:
    summary: dict[str, Any]
    package_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "package_rows": self.package_rows,
            "interpretation": self.interpretation,
        }


class V134CNCommercialAerospaceReduceHandoffPackageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.reduce_completion_path = analysis_dir / "v134cm_commercial_aerospace_cl_reduce_completion_direction_triage_v1.json"
        self.reduce_stack_path = analysis_dir / "v134bo_commercial_aerospace_reduce_closure_governance_spec_v1.json"
        self.binding_path = analysis_dir / "v134ce_commercial_aerospace_cd_binding_quality_direction_triage_v1.json"
        self.horizon_path = analysis_dir / "v134cg_commercial_aerospace_cf_horizon_quality_direction_triage_v1.json"
        self.residue_path = analysis_dir / "v134ck_commercial_aerospace_cj_local_rebound_direction_triage_v1.json"
        self.blocker_path = analysis_dir / "v134bq_commercial_aerospace_reduce_execution_binding_blocker_audit_v1.json"
        self.output_csv = repo_root / "data" / "training" / "commercial_aerospace_reduce_handoff_package_v1.csv"

    def analyze(self) -> V134CNCommercialAerospaceReduceHandoffPackageV1Report:
        reduce_completion = json.loads(self.reduce_completion_path.read_text(encoding="utf-8"))
        reduce_stack = json.loads(self.reduce_stack_path.read_text(encoding="utf-8"))
        binding = json.loads(self.binding_path.read_text(encoding="utf-8"))
        horizon = json.loads(self.horizon_path.read_text(encoding="utf-8"))
        residue = json.loads(self.residue_path.read_text(encoding="utf-8"))
        blockers = json.loads(self.blocker_path.read_text(encoding="utf-8"))

        package_rows = [
            {
                "component": "reduce_mainline_completion",
                "status": "frozen_for_handoff",
                "detail": reduce_completion["summary"]["authoritative_status"],
            },
            {
                "component": "reduce_governance_stack",
                "status": "retained",
                "detail": f"closure_stage_count = {reduce_stack['summary']['closure_stage_count']}",
            },
            {
                "component": "sell_side_binding_reference",
                "status": "retained",
                "detail": binding["summary"]["authoritative_status"],
            },
            {
                "component": "sell_side_horizon_caveat",
                "status": "retained",
                "detail": horizon["summary"]["authoritative_status"],
            },
            {
                "component": "local_residue_registry",
                "status": "supervision_only",
                "detail": residue["summary"]["authoritative_status"],
            },
            {
                "component": "execution_blockers",
                "status": "still_open",
                "detail": f"remaining_execution_blocker_count = {blockers['summary']['full_reduce_binding_blocker_count']}",
            },
            {
                "component": "next_frontier_gate",
                "status": "ready_for_future_handoff_only",
                "detail": "Reduce mainline is frozen; any later shift to intraday add should treat reduce as fixed except for local residue maintenance.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(package_rows[0].keys()))
            writer.writeheader()
            writer.writerows(package_rows)

        summary = {
            "acceptance_posture": "freeze_v134cn_commercial_aerospace_reduce_handoff_package_v1",
            "reduce_mainline_frozen": True,
            "local_residue_supervision_only": True,
            "execution_blocker_count": blockers["summary"]["full_reduce_binding_blocker_count"],
            "future_handoff_ready": True,
            "handoff_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_reduce_handoff_package_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34CN packages the reduce branch for handoff without pretending that execution closure is finished.",
            "The point is to freeze what is learned, preserve what remains only as local residue maintenance, and make the next frontier explicitly conditional rather than emotionally implicit.",
        ]
        return V134CNCommercialAerospaceReduceHandoffPackageV1Report(
            summary=summary,
            package_rows=package_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CNCommercialAerospaceReduceHandoffPackageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CNCommercialAerospaceReduceHandoffPackageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cn_commercial_aerospace_reduce_handoff_package_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
