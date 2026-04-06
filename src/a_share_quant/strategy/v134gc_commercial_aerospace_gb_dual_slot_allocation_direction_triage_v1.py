from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134GCCommercialAerospaceGBDualSlotAllocationDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134GCCommercialAerospaceGBDualSlotAllocationDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v134gb_commercial_aerospace_dual_slot_allocation_supervision_audit_v1.json"
        )

    def analyze(self) -> V134GCCommercialAerospaceGBDualSlotAllocationDirectionTriageV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        authoritative_status = (
            "retain_dual_slot_allocation_as_local_supervision_and_keep_add_execution_blocked"
        )
        triage_rows = [
            {
                "component": "reset_slot_primary_allocation",
                "status": "retain_as_local_archetype",
                "rationale": "the current dual-slot day allocates more weight to the clean-reset slot than to the continuation slot",
            },
            {
                "component": "continuation_slot_secondary_allocation",
                "status": "retain_as_local_archetype",
                "rationale": "the continuation slot behaves like an incremental participation layer rather than the primary slot",
            },
            {
                "component": "execution_allocation_rule",
                "status": "still_blocked",
                "rationale": "one local day is enough to encode a supervision archetype, not enough to promote an execution allocation rule",
            },
        ]
        interpretation = [
            "V1.34GC turns the first dual-slot allocation audit into a bounded governance verdict.",
            "The add frontier now has a local allocation archetype for risk-sharing, but that archetype remains supervision-only until it survives a wider and more diverse surface.",
        ]
        return V134GCCommercialAerospaceGBDualSlotAllocationDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134gc_commercial_aerospace_gb_dual_slot_allocation_direction_triage_v1",
                "authoritative_status": authoritative_status,
                "dual_slot_day_count": audit["summary"]["dual_slot_day_count"],
                "reset_to_continuation_weight_ratio": audit["summary"]["reset_to_continuation_weight_ratio"],
                "authoritative_rule": (
                    "the add frontier can now keep a local primary-reset plus secondary-continuation allocation archetype, while execution allocation remains blocked"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GCCommercialAerospaceGBDualSlotAllocationDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GCCommercialAerospaceGBDualSlotAllocationDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134gc_commercial_aerospace_gb_dual_slot_allocation_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
