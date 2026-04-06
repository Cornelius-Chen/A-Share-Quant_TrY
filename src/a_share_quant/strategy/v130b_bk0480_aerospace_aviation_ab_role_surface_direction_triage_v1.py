from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V130BBK0480AerospaceAviationABRoleSurfaceDirectionTriageReport:
    summary: dict[str, Any]
    direction_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "direction_rows": self.direction_rows,
            "interpretation": self.interpretation,
        }


class V130BBK0480AerospaceAviationABRoleSurfaceDirectionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.role_surface_path = repo_root / "reports" / "analysis" / "v130a_bk0480_aerospace_aviation_role_surface_refresh_v2.json"

    def analyze(self) -> V130BBK0480AerospaceAviationABRoleSurfaceDirectionTriageReport:
        role_surface = json.loads(self.role_surface_path.read_text(encoding="utf-8"))
        direction_rows = [
            {"direction": "internal_owner_stack", "status": "retain_000738_and_600118", "reason": "BK0480 still needs the original dual-core owners to define authority/support semantics."},
            {"direction": "600760_confirmation_layer", "status": "admit_as_confirmation_only", "reason": "600760 is the only widening step justified by strong BK0480-native evidence, but it still lacks current-v6 owner authority."},
            {"direction": "002273_601989", "status": "keep_quarantined", "reason": "They are interesting enough to retain, but not clean enough to widen the actionable control surface."},
            {"direction": "000099", "status": "keep_reject_pending", "reason": "It remains a negative local example rather than a usable confirmation or mirror layer."},
            {"direction": "next_primary_direction", "status": "refresh_control_surface_with_feed_harmonization_guard", "reason": "The next lawful move is to refresh BK0480 control semantics while explicitly blocking cross-version authority leakage."},
            {"direction": "replay_unlock", "status": "still_blocked", "reason": "A wider role surface now exists, but replay should remain blocked until the refreshed control surface is audited."},
        ]
        summary = {
            "acceptance_posture": "freeze_v130b_bk0480_aerospace_aviation_ab_role_surface_direction_triage_v1",
            "board_name": role_surface["summary"]["board_name"],
            "sector_id": role_surface["summary"]["sector_id"],
            "confirmation_count": role_surface["summary"]["confirmation_count"],
            "quarantine_count": role_surface["summary"]["quarantine_count"],
            "authoritative_status": "freeze_bk0480_role_surface_v2_and_move_to_control_surface_refresh_with_harmonization_guard",
            "authoritative_rule": "bk0480_may_widen_locally_but_cannot_unlock_replay_until_the_wider_surface_is_reduced_to_a_clean_control_semantics_layer",
        }
        interpretation = [
            "V1.30B freezes BK0480 role surface v2 as the correct local expansion posture.",
            "The board can now move from local universe expansion to control-surface refresh, but replay remains explicitly blocked.",
        ]
        return V130BBK0480AerospaceAviationABRoleSurfaceDirectionTriageReport(summary=summary, direction_rows=direction_rows, interpretation=interpretation)


def write_report(*, reports_dir: Path, report_name: str, result: V130BBK0480AerospaceAviationABRoleSurfaceDirectionTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V130BBK0480AerospaceAviationABRoleSurfaceDirectionTriageAnalyzer(repo_root).analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130b_bk0480_aerospace_aviation_ab_role_surface_direction_triage_v1",
        result=result,
    )


if __name__ == "__main__":
    main()
