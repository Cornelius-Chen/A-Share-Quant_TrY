from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134GOCommercialAerospaceGNAddCompletionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134GOCommercialAerospaceGNAddCompletionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v134gn_commercial_aerospace_add_completion_status_audit_v1.json"
        )

    def analyze(self) -> V134GOCommercialAerospaceGNAddCompletionDirectionTriageV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        triage_rows = [
            {
                "component": "seed_supervision_stack",
                "status": "freeze_as_complete_enough",
                "rationale": "registry, seed rules, local permission hierarchy, and local slot-capacity hierarchy are already internally coherent",
            },
            {
                "component": "broader_positive_promotion",
                "status": "keep_blocked",
                "rationale": "broader positive add still fails portability because non-seed density remains too high",
            },
            {
                "component": "single_slot_template",
                "status": "keep_blocked",
                "rationale": "single-slot fallback remains unobserved and only survives as a forced-collapse local surrogate",
            },
            {
                "component": "execution_authority",
                "status": "keep_blocked",
                "rationale": "the branch still lacks portable permission and execution-safe capacity rules",
            },
            {
                "component": "future_work_posture",
                "status": "shift_to_local_residue_maintenance",
                "rationale": "future work should no longer be broad expansion, but only local residue maintenance unless a new portability unlock appears",
            },
        ]
        interpretation = [
            "V1.34GO turns the add completion audit into the current governance verdict.",
            "The branch should now be treated like the reduce branch was treated after its research layer stabilized: freeze the supervision mainline, keep portability and execution blocked, and stop broad tuning.",
        ]
        return V134GOCommercialAerospaceGNAddCompletionDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134go_commercial_aerospace_gn_add_completion_direction_triage_v1",
                "authoritative_status": (
                    "freeze_add_supervision_mainline_as_complete_enough_and_leave_only_local_residue_maintenance"
                ),
                "frozen_complete_count": audit["summary"]["frozen_complete_count"],
                "local_only_count": audit["summary"]["local_only_count"],
                "blocked_count": audit["summary"]["blocked_count"],
                "authoritative_rule": (
                    "the add branch is now complete enough at the supervision layer; broader promotion and execution remain blocked, "
                    "so the branch should stop broad tuning and shift to local residue maintenance"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GOCommercialAerospaceGNAddCompletionDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GOCommercialAerospaceGNAddCompletionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134go_commercial_aerospace_gn_add_completion_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
