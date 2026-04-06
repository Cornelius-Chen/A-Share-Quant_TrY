from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134GKCommercialAerospaceGJSingleSlotDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134GKCommercialAerospaceGJSingleSlotDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v134gj_commercial_aerospace_single_slot_fallback_supervision_audit_v1.json"
        )

    def analyze(self) -> V134GKCommercialAerospaceGJSingleSlotDirectionTriageV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        triage_rows = [
            {
                "component": "observed_single_slot_fallback",
                "status": "still_unobserved",
                "rationale": "the current strict active-wave sample still does not contain a genuine retained single-slot day",
            },
            {
                "component": "reset_slot_surrogate",
                "status": "retain_as_weak_local_surrogate",
                "rationale": "if a forced one-slot local reading is needed, reset-primary structure gives the reset slot the stronger provisional claim",
            },
            {
                "component": "continuation_slot",
                "status": "retain_as_companion_only",
                "rationale": "continuation remains useful as a companion slot but is not yet the branch's local fallback template",
            },
            {
                "component": "execution_single_slot_rule",
                "status": "still_blocked",
                "rationale": "single-slot fallback is not observed as a portable state, so execution promotion remains premature",
            },
        ]
        interpretation = [
            "V1.34GK turns the single-slot fallback audit into the current governance verdict.",
            "The branch should keep single-slot fallback blocked as a portable rule while allowing only a weak local reset-slot surrogate reading under explicit supervision.",
        ]
        return V134GKCommercialAerospaceGJSingleSlotDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134gk_commercial_aerospace_gj_single_slot_direction_triage_v1",
                "authoritative_status": (
                    "retain_single_slot_fallback_as_unobserved_and_keep_only_reset_slot_as_weak_local_surrogate"
                ),
                "observed_single_slot_day_count": audit["summary"]["observed_single_slot_day_count"],
                "weak_surrogate_count": audit["summary"]["weak_surrogate_count"],
                "surrogate_slot_name": audit["summary"]["surrogate_slot_name"],
                "authoritative_rule": (
                    "single-slot fallback remains unobserved; only a weak reset-slot surrogate may be retained under local supervision"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GKCommercialAerospaceGJSingleSlotDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GKCommercialAerospaceGJSingleSlotDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134gk_commercial_aerospace_gj_single_slot_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
