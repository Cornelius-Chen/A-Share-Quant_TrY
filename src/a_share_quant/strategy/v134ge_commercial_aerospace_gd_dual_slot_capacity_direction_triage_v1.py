from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134GECommercialAerospaceGDDualSlotCapacityDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134GECommercialAerospaceGDDualSlotCapacityDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v134gd_commercial_aerospace_dual_slot_capacity_audit_v1.json"
        )

    def analyze(self) -> V134GECommercialAerospaceGDDualSlotCapacityDirectionTriageV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        authoritative_status = (
            "retain_dual_slot_capacity_as_conditional_local_supervision_and_keep_add_execution_blocked"
        )
        triage_rows = [
            {
                "component": "dual_slot_capacity",
                "status": "retain_as_conditional",
                "rationale": "the current strict surface supports dual-slot coexistence only on a local minority of active-wave days",
            },
            {
                "component": "single_slot_fallback",
                "status": "retain",
                "rationale": "most active-wave days under the current strict surface do not justify simultaneous dual-slot retention",
            },
            {
                "component": "execution_allocation_rule",
                "status": "still_blocked",
                "rationale": "capacity remains local and conditional, so it is still too early to promote into execution sizing logic",
            },
        ]
        interpretation = [
            "V1.34GE turns the first dual-slot capacity audit into the current governance verdict.",
            "The branch should keep dual-slot coexistence as a conditional local supervision pattern, not as a default operational assumption.",
        ]
        return V134GECommercialAerospaceGDDualSlotCapacityDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134ge_commercial_aerospace_gd_dual_slot_capacity_direction_triage_v1",
                "authoritative_status": authoritative_status,
                "active_wave_day_count": audit["summary"]["active_wave_day_count"],
                "dual_slot_day_count": audit["summary"]["dual_slot_day_count"],
                "single_slot_day_count": audit["summary"]["single_slot_day_count"],
                "zero_slot_day_count": audit["summary"]["zero_slot_day_count"],
                "authoritative_rule": (
                    "dual-slot add capacity is currently a conditional local archetype; default dual-slot promotion and execution remain blocked"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GECommercialAerospaceGDDualSlotCapacityDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GECommercialAerospaceGDDualSlotCapacityDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ge_commercial_aerospace_gd_dual_slot_capacity_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
