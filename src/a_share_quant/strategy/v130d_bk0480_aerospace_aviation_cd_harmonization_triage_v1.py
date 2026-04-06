from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V130DBK0480AerospaceAviationCDHarmonizationTriageReport:
    summary: dict[str, Any]
    direction_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "direction_rows": self.direction_rows,
            "interpretation": self.interpretation,
        }


class V130DBK0480AerospaceAviationCDHarmonizationTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = repo_root / "reports" / "analysis" / "v130c_bk0480_aerospace_aviation_feed_harmonization_support_audit_v1.json"

    def analyze(self) -> V130DBK0480AerospaceAviationCDHarmonizationTriageReport:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        direction_rows = [
            {
                "direction": "role_surface_v2",
                "status": "freeze_current",
                "reason": "The local role surface is correct and should not be widened further until harmonization is solved.",
            },
            {
                "direction": "control_surface_refresh",
                "status": "blocked",
                "reason": "No non-core BK0480 name currently has same-plane support, so wider control math would be semantically dirty.",
            },
            {
                "direction": "replay_unlock",
                "status": "blocked",
                "reason": "Replay remains blocked until the board has a cleaner non-core evidence base inside the same plane.",
            },
            {
                "direction": "next_primary_direction",
                "status": "collect_more_v6_native_support_or_formalize_a_historical_bridge",
                "reason": "BK0480 now needs evidence harmonization, not further role speculation.",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v130d_bk0480_aerospace_aviation_cd_harmonization_triage_v1",
            "board_name": audit["summary"]["board_name"],
            "sector_id": audit["summary"]["sector_id"],
            "same_plane_support_count": audit["summary"]["same_plane_support_count"],
            "historical_bridge_only_count": audit["summary"]["historical_bridge_only_count"],
            "timeline_only_count": audit["summary"]["timeline_only_count"],
            "authoritative_status": "freeze_bk0480_role_surface_v2_and_block_wider_control_refresh_until_harmonization_exists",
            "authoritative_rule": "bk0480_cannot_progress_to_wider_control_math_or_replay_unlock_from_confirmation_language_alone",
        }
        interpretation = [
            "V1.30D freezes BK0480 after local expansion because harmonization, not role discovery, is now the binding constraint.",
            "The board should gather more same-plane evidence before any replay unlock attempt.",
        ]
        return V130DBK0480AerospaceAviationCDHarmonizationTriageReport(summary=summary, direction_rows=direction_rows, interpretation=interpretation)


def write_report(*, reports_dir: Path, report_name: str, result: V130DBK0480AerospaceAviationCDHarmonizationTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V130DBK0480AerospaceAviationCDHarmonizationTriageAnalyzer(repo_root).analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130d_bk0480_aerospace_aviation_cd_harmonization_triage_v1",
        result=result,
    )


if __name__ == "__main__":
    main()
