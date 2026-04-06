from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134GICommercialAerospaceGHSlotCapacityDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134GICommercialAerospaceGHSlotCapacityDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v134gh_commercial_aerospace_slot_capacity_hierarchy_audit_v1.json"
        )

    def analyze(self) -> V134GICommercialAerospaceGHSlotCapacityDirectionTriageV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        triage_rows = [
            {
                "component": "zero_slot_veto",
                "status": "retain",
                "rationale": "same-wave exclusion already cleanly explains why some active-wave days should still resolve into no add slot at all",
            },
            {
                "component": "tiered_dual_slot",
                "status": "retain_as_local",
                "rationale": "the observed dual-slot day remains useful as a local supervision archetype, but it is still too narrow to promote",
            },
            {
                "component": "single_slot_fallback",
                "status": "still_unobserved",
                "rationale": "the current strict active-wave sample has not yet produced a promotable single-slot fallback day",
            },
            {
                "component": "execution_allocation_rule",
                "status": "still_blocked",
                "rationale": "slot capacity remains a local hierarchy rather than a portable execution sizing module",
            },
        ]
        interpretation = [
            "V1.34GI turns the slot-capacity hierarchy audit into the current governance verdict.",
            "The add branch should keep zero-slot veto and tiered dual-slot as local supervision states, while leaving single-slot fallback and execution allocation blocked.",
        ]
        return V134GICommercialAerospaceGHSlotCapacityDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134gi_commercial_aerospace_gh_slot_capacity_direction_triage_v1",
                "authoritative_status": (
                    "retain_slot_capacity_as_exclusion_first_local_hierarchy_and_keep_add_execution_blocked"
                ),
                "active_wave_day_count": audit["summary"]["active_wave_day_count"],
                "zero_slot_veto_day_count": audit["summary"]["zero_slot_veto_day_count"],
                "tiered_dual_slot_day_count": audit["summary"]["tiered_dual_slot_day_count"],
                "single_slot_unobserved_day_count": audit["summary"]["single_slot_unobserved_day_count"],
                "authoritative_rule": (
                    "current add slot capacity is best treated as an exclusion-first local hierarchy, not as a general allocation module"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GICommercialAerospaceGHSlotCapacityDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GICommercialAerospaceGHSlotCapacityDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134gi_commercial_aerospace_gh_slot_capacity_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
