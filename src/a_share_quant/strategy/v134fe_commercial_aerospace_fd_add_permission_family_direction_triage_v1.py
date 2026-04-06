from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FECommercialAerospaceFDAddPermissionFamilyDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134FECommercialAerospaceFDAddPermissionFamilyDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v134fd_commercial_aerospace_add_permission_family_audit_v1.json"
        )

    def analyze(self) -> V134FECommercialAerospaceFDAddPermissionFamilyDirectionTriageV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        status = "retain_permission_families_as_local_supervision_and_do_not_promote_broad_positive_add_rules"
        triage_rows = [
            {
                "component": "persistent_permission_candidate",
                "status": "retain_as_local_permission_family",
                "rationale": "the narrow quantity-price clue does contain a real pocket of sessions that continue through the first hour and deserve dedicated supervision",
            },
            {
                "component": "fragile_and_failed_permission_families",
                "status": "retain_as_counterfactuals",
                "rationale": "the same clue family still contains fragile and failed sessions, so the branch cannot collapse the clue into a blanket add authorization",
            },
            {
                "component": "broader_positive_add_promotion",
                "status": "still_blocked",
                "rationale": "the permission clue now has structure, but that structure is family-level supervision rather than replay-facing permission authority",
            },
        ]
        interpretation = [
            "V1.34FE turns the first add-permission family audit into a governance verdict.",
            "The correct next move is to keep supervising the family split, not to pretend the clue has become a general positive add rule.",
        ]
        return V134FECommercialAerospaceFDAddPermissionFamilyDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134fe_commercial_aerospace_fd_add_permission_family_direction_triage_v1",
                "authoritative_status": status,
                "persistent_permission_candidate_count": audit["summary"]["persistent_permission_candidate_count"],
                "fragile_permission_watch_count": audit["summary"]["fragile_permission_watch_count"],
                "failed_permission_watch_count": audit["summary"]["failed_permission_watch_count"],
                "authoritative_rule": (
                    "the add branch should retain the new quantity-price permission split as local family supervision while keeping broader positive add promotion blocked"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FECommercialAerospaceFDAddPermissionFamilyDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FECommercialAerospaceFDAddPermissionFamilyDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134fe_commercial_aerospace_fd_add_permission_family_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
