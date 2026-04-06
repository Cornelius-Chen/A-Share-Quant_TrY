from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134HFCommercialAerospaceShadowBoundaryExtensionOpeningChecklistV1Report:
    summary: dict[str, Any]
    checklist_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "checklist_rows": self.checklist_rows,
            "interpretation": self.interpretation,
        }


class V134HFCommercialAerospaceShadowBoundaryExtensionOpeningChecklistV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.policy_path = analysis_dir / "v134hd_commercial_aerospace_derivation_boundary_policy_audit_v1.json"
        self.boundary_triage_path = analysis_dir / "v134hc_commercial_aerospace_hb_boundary_direction_triage_v1.json"
        self.shadow_lane_path = analysis_dir / "v134gp_commercial_aerospace_intraday_shadow_replay_lane_opening_v1.json"
        self.bridge_path = analysis_dir / "v134gr_commercial_aerospace_reentry_unlock_shadow_bridge_spec_v1.json"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_shadow_boundary_extension_opening_checklist_v1.csv"
        )

    def analyze(self) -> V134HFCommercialAerospaceShadowBoundaryExtensionOpeningChecklistV1Report:
        policy = json.loads(self.policy_path.read_text(encoding="utf-8"))
        boundary_triage = json.loads(self.boundary_triage_path.read_text(encoding="utf-8"))
        shadow_lane = json.loads(self.shadow_lane_path.read_text(encoding="utf-8"))
        bridge = json.loads(self.bridge_path.read_text(encoding="utf-8"))

        checklist_rows = [
            {
                "opening_gate": "explicit_shadow_only_policy_shift",
                "status": "mandatory",
                "detail": "Boundary extension may open only through an explicit shadow-only policy shift, never by silent refresh from existing raw coverage.",
            },
            {
                "opening_gate": "current_boundary_frozen_by_default",
                "status": "mandatory",
                "detail": "The existing lockout-aligned derivation boundary remains authoritative until the shift is explicitly approved.",
            },
            {
                "opening_gate": "read_only_shadow_lane_preserved",
                "status": "mandatory",
                "detail": "The shadow replay lane must remain read-only and protocol-first during any boundary-extension work.",
            },
            {
                "opening_gate": "execution_authority_stays_blocked",
                "status": "mandatory",
                "detail": "Boundary extension may not be used to smuggle execution authority into reentry, unlock, or add.",
            },
            {
                "opening_gate": "dual_surface_extension_required",
                "status": "mandatory",
                "detail": "Daily-state and phase-geometry surfaces must be extended together; one-sided extension is not sufficient.",
            },
            {
                "opening_gate": "unlock_quality_debate_deferred",
                "status": "mandatory",
                "detail": "Do not debate post-lockout unlock quality until the board surfaces themselves have been explicitly extended.",
            },
            {
                "opening_gate": "bridge_handoff_stays_blocked_during_prelaunch",
                "status": "mandatory",
                "detail": "Reentry-to-add handoff remains blocked during checklist/prelaunch work and does not reopen just because extension is being considered.",
            },
            {
                "opening_gate": "program_status_refresh_required",
                "status": "mandatory",
                "detail": "Program and frontier status cards must be refreshed when and only when the policy actually shifts.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(checklist_rows[0].keys()))
            writer.writeheader()
            writer.writerows(checklist_rows)

        summary = {
            "acceptance_posture": "freeze_v134hf_commercial_aerospace_shadow_boundary_extension_opening_checklist_v1",
            "boundary_classification": boundary_triage["summary"]["boundary_classification"],
            "current_policy": policy["summary"]["current_policy"],
            "future_policy_option": policy["summary"]["future_policy_option"],
            "shadow_lane_state": shadow_lane["summary"]["frontier_state"],
            "bridge_stage_count": bridge["summary"]["bridge_stage_count"],
            "opening_gate_count": len(checklist_rows),
            "checklist_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_shadow_boundary_extension_opening_checklist_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34HF does not open boundary extension; it formalizes how such an extension would have to be opened later if the project chooses to do so.",
            "The checklist keeps the order clean: policy shift first, synchronized board-surface extension second, unlock judgment only after that.",
        ]
        return V134HFCommercialAerospaceShadowBoundaryExtensionOpeningChecklistV1Report(
            summary=summary,
            checklist_rows=checklist_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HFCommercialAerospaceShadowBoundaryExtensionOpeningChecklistV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HFCommercialAerospaceShadowBoundaryExtensionOpeningChecklistV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134hf_commercial_aerospace_shadow_boundary_extension_opening_checklist_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
