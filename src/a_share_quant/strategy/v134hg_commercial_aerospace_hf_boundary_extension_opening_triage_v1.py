from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134HGCommercialAerospaceHFBoundaryExtensionOpeningTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134HGCommercialAerospaceHFBoundaryExtensionOpeningTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.checklist_path = (
            repo_root / "reports" / "analysis" / "v134hf_commercial_aerospace_shadow_boundary_extension_opening_checklist_v1.json"
        )

    def analyze(self) -> V134HGCommercialAerospaceHFBoundaryExtensionOpeningTriageV1Report:
        checklist = json.loads(self.checklist_path.read_text(encoding="utf-8"))
        triage_rows = [
            {
                "component": "boundary_extension_opening_checklist",
                "status": "retain_as_prelaunch_protocol",
                "rationale": "future boundary extension now has an explicit prelaunch checklist and does not need speculative signal work",
            },
            {
                "component": "current_derivation_boundary",
                "status": "keep_frozen",
                "rationale": "the lockout-aligned derivation boundary remains the authoritative default until an explicit policy shift occurs",
            },
            {
                "component": "implicit_extension_now",
                "status": "blocked",
                "rationale": "existing raw coverage is insufficient reason to extend the boundary without an explicit shadow-only opening",
            },
        ]
        interpretation = [
            "V1.34HG converts the boundary-extension checklist into a simple governance verdict: the checklist is ready, but the current boundary remains frozen.",
            "The point is to make a future explicit extension clean without letting preparation mutate into automatic extension.",
        ]
        return V134HGCommercialAerospaceHFBoundaryExtensionOpeningTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134hg_commercial_aerospace_hf_boundary_extension_opening_triage_v1",
                "authoritative_status": (
                    "freeze_shadow_boundary_extension_opening_checklist_and_keep_derivation_boundary_frozen_until_explicit_shadow_only_shift"
                ),
                "opening_gate_count": checklist["summary"]["opening_gate_count"],
                "boundary_classification": checklist["summary"]["boundary_classification"],
                "current_policy": checklist["summary"]["current_policy"],
                "future_policy_option": checklist["summary"]["future_policy_option"],
                "authoritative_rule": (
                    "a future boundary-extension frontier may be prepared, but not opened, while the current derivation boundary remains frozen by default"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HGCommercialAerospaceHFBoundaryExtensionOpeningTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HGCommercialAerospaceHFBoundaryExtensionOpeningTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134hg_commercial_aerospace_hf_boundary_extension_opening_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
