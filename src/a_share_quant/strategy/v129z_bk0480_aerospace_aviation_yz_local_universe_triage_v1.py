from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V129ZBK0480AerospaceAviationYZLocalUniverseTriageReport:
    summary: dict[str, Any]
    direction_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "direction_rows": self.direction_rows,
            "interpretation": self.interpretation,
        }


class V129ZBK0480AerospaceAviationYZLocalUniverseTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = repo_root / "reports" / "analysis" / "v129y_bk0480_aerospace_aviation_local_universe_expansion_audit_v1.json"

    def analyze(self) -> V129ZBK0480AerospaceAviationYZLocalUniverseTriageReport:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        direction_rows = [
            {
                "direction": "confirmation_admission",
                "status": "admit_600760_confirmation_only",
                "reason": "600760 is the only non-core name with strong BK0480-native evidence across both historical snapshot and timeline captures.",
            },
            {
                "direction": "quarantine_stack",
                "status": "retain_002273_and_601989",
                "reason": "Both names have enough BK0480-native timeline support to keep under watch, but not enough snapshot support to upgrade today.",
            },
            {
                "direction": "reject_or_mirror_pending",
                "status": "retain_000099_as_reject_pending",
                "reason": "000099 has too many junk/sell signatures under BK0480 approval to justify confirmation admission.",
            },
            {
                "direction": "replay_unlock",
                "status": "still_blocked",
                "reason": "The board now has a slightly wider local surface, but not enough harmonized evidence to unlock replay or supervised training.",
            },
            {
                "direction": "next_primary_direction",
                "status": "refresh_role_surface_then_harmonize_control_surface",
                "reason": "The next lawful move is to refresh the BK0480 role surface and then re-audit a harmonized control surface.",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v129z_bk0480_aerospace_aviation_yz_local_universe_triage_v1",
            "board_name": audit["summary"]["board_name"],
            "sector_id": audit["summary"]["sector_id"],
            "confirmation_candidate_count": audit["summary"]["confirmation_candidate_count"],
            "quarantine_candidate_count": audit["summary"]["quarantine_candidate_count"],
            "reject_candidate_count": audit["summary"]["reject_candidate_count"],
            "authoritative_status": "admit_600760_as_confirmation_only_keep_002273_601989_quarantined_and_reject_000099_for_now",
            "authoritative_rule": "bk0480_local_expansion_can_widen_the_role_surface_but_not_yet_the_control_authority_surface",
        }
        interpretation = [
            "V1.29Z freezes BK0480 local universe expansion into one admission, two quarantines, and one rejection.",
            "The board may widen locally, but replay remains blocked until the wider surface is harmonized into a clean control surface.",
        ]
        return V129ZBK0480AerospaceAviationYZLocalUniverseTriageReport(summary=summary, direction_rows=direction_rows, interpretation=interpretation)


def write_report(*, reports_dir: Path, report_name: str, result: V129ZBK0480AerospaceAviationYZLocalUniverseTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V129ZBK0480AerospaceAviationYZLocalUniverseTriageAnalyzer(repo_root).analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129z_bk0480_aerospace_aviation_yz_local_universe_triage_v1",
        result=result,
    )


if __name__ == "__main__":
    main()
