from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134HICommercialAerospaceShadowBoundaryExtensionPrelaunchStatusCardV1Report:
    summary: dict[str, Any]
    status_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "status_rows": self.status_rows,
            "interpretation": self.interpretation,
        }


class V134HICommercialAerospaceShadowBoundaryExtensionPrelaunchStatusCardV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.policy_path = analysis_dir / "v134hd_commercial_aerospace_derivation_boundary_policy_audit_v1.json"
        self.opening_path = analysis_dir / "v134hf_commercial_aerospace_shadow_boundary_extension_opening_checklist_v1.json"
        self.direction_path = analysis_dir / "v134hg_commercial_aerospace_hf_boundary_extension_opening_triage_v1.json"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_shadow_boundary_extension_prelaunch_status_card_v1.csv"
        )

    def analyze(self) -> V134HICommercialAerospaceShadowBoundaryExtensionPrelaunchStatusCardV1Report:
        policy = json.loads(self.policy_path.read_text(encoding="utf-8"))
        opening = json.loads(self.opening_path.read_text(encoding="utf-8"))
        direction = json.loads(self.direction_path.read_text(encoding="utf-8"))

        status_rows = [
            {"key": "frontier_name", "value": "shadow_boundary_extension"},
            {"key": "frontier_state", "value": "deferred_prelaunch"},
            {"key": "boundary_classification", "value": policy["summary"]["boundary_classification"]},
            {"key": "current_policy", "value": policy["summary"]["current_policy"]},
            {"key": "future_policy_option", "value": policy["summary"]["future_policy_option"]},
            {"key": "opening_gate_count", "value": opening["summary"]["opening_gate_count"]},
            {"key": "ready_to_open_now", "value": "False"},
            {"key": "silent_opening_allowed", "value": "False"},
            {"key": "execution_authority", "value": "blocked"},
            {"key": "authoritative_status", "value": direction["summary"]["authoritative_status"]},
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(status_rows[0].keys()))
            writer.writeheader()
            writer.writerows(status_rows)

        summary = {
            "acceptance_posture": "freeze_v134hi_commercial_aerospace_shadow_boundary_extension_prelaunch_status_card_v1",
            "frontier_name": "shadow_boundary_extension",
            "frontier_state": "deferred_prelaunch",
            "opening_gate_count": opening["summary"]["opening_gate_count"],
            "ready_to_open_now": False,
            "silent_opening_allowed": False,
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_shadow_boundary_extension_prelaunch_status_card_ready",
        }
        interpretation = [
            "V1.34HI turns the current boundary-extension governance state into a compact prelaunch card.",
            "It makes explicit that the option now exists as a future frontier, but the current state is still deferred and blocked from silent opening.",
        ]
        return V134HICommercialAerospaceShadowBoundaryExtensionPrelaunchStatusCardV1Report(
            summary=summary,
            status_rows=status_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HICommercialAerospaceShadowBoundaryExtensionPrelaunchStatusCardV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HICommercialAerospaceShadowBoundaryExtensionPrelaunchStatusCardV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134hi_commercial_aerospace_shadow_boundary_extension_prelaunch_status_card_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
