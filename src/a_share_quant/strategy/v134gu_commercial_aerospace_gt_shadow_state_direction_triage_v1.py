from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134GUCommercialAerospaceGTShadowStateDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134GUCommercialAerospaceGTShadowStateDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.surface_path = (
            repo_root / "reports" / "analysis" / "v134gt_commercial_aerospace_reentry_unlock_shadow_state_surface_v1.json"
        )

    def analyze(self) -> V134GUCommercialAerospaceGTShadowStateDirectionTriageV1Report:
        surface = json.loads(self.surface_path.read_text(encoding="utf-8"))
        triage_rows = [
            {
                "component": "shadow_state_surface",
                "status": "approved_as_first_concrete_bridge_surface",
                "rationale": "the bridge now owns a concrete state table instead of only an abstract protocol",
            },
            {
                "component": "same_day_reentry",
                "status": "keep_blocked",
                "rationale": "all current seeds remain blocked from same-day chase",
            },
            {
                "component": "board_gate_dependency",
                "status": "mandatory",
                "rationale": "the surface shows that reentry timing is still subordinate to board lockout and later board unlock",
            },
            {
                "component": "add_handoff",
                "status": "not_ready_yet",
                "rationale": "no current seed is yet ready for add-permission consult while board unlock remains unresolved",
            },
            {
                "component": "execution_authority",
                "status": "still_blocked",
                "rationale": "the surface enumerates state but still does not authorize any replay-facing execution",
            },
        ]
        interpretation = [
            "V1.34GU converts the first reentry/unlock shadow state surface into the current governance verdict.",
            "The bridge now has a concrete supervision table, but it remains a pre-execution shadow surface: add handoff readiness is still zero and same-day chase remains blocked.",
        ]
        return V134GUCommercialAerospaceGTShadowStateDirectionTriageV1Report(
            summary={
                "acceptance_posture": "open_v134gu_commercial_aerospace_gt_shadow_state_direction_triage_v1",
                "authoritative_status": (
                    "retain_reentry_unlock_shadow_state_surface_as_first_concrete_bridge_surface_and_keep_execution_blocked"
                ),
                "seed_count": surface["summary"]["seed_count"],
                "pre_lockout_seed_count": surface["summary"]["pre_lockout_seed_count"],
                "in_lockout_seed_count": surface["summary"]["in_lockout_seed_count"],
                "current_add_handoff_ready_count": surface["summary"]["current_add_handoff_ready_count"],
                "authoritative_rule": (
                    "the bridge now has a concrete state surface, but all current seeds still remain pre-handoff and pre-execution"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GUCommercialAerospaceGTShadowStateDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GUCommercialAerospaceGTShadowStateDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134gu_commercial_aerospace_gt_shadow_state_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
