from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134GACommercialAerospaceFZDualSlotDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134GACommercialAerospaceFZDualSlotDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v134fz_commercial_aerospace_active_wave_dual_slot_permission_audit_v1.json"
        )

    def analyze(self) -> V134GACommercialAerospaceFZDualSlotDirectionTriageV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        authoritative_status = (
            "retain_dual_slot_permission_view_as_local_supervision_and_keep_single_ranker_blocked"
        )
        triage_rows = [
            {
                "component": "recent_reduce_residue_exclusion",
                "status": "retain",
                "rationale": "the first same-wave exclusion clue remains the clean outer filter",
            },
            {
                "component": "dual_slot_permission_view",
                "status": "retain_as_local_positive_structure",
                "rationale": "the retained selected states look complementary enough to justify parallel risk-sharing slots instead of a forced single winner",
            },
            {
                "component": "single_positive_ranker",
                "status": "still_blocked",
                "rationale": "the current local sample does not justify collapsing the two retained states into a single dominant rank order",
            },
            {
                "component": "add_execution_authority",
                "status": "still_blocked",
                "rationale": "dual-slot supervision is still a governance object, not execution authority",
            },
        ]
        interpretation = [
            "V1.34GA turns the dual-slot audit into the next governance verdict for active-wave add selection.",
            "The frontier should now preserve a dual-slot permission view locally instead of overforcing a single positive ranker where the data still prefers complementary participation states.",
        ]
        return V134GACommercialAerospaceFZDualSlotDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134ga_commercial_aerospace_fz_dual_slot_direction_triage_v1",
                "authoritative_status": authoritative_status,
                "selected_candidate_count": audit["summary"]["selected_candidate_count"],
                "slot_count": audit["summary"]["slot_count"],
                "authoritative_rule": (
                    "active-wave add selection now supports a local dual-slot permission view, while single-ranker promotion and execution remain blocked"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GACommercialAerospaceFZDualSlotDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GACommercialAerospaceFZDualSlotDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ga_commercial_aerospace_fz_dual_slot_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
