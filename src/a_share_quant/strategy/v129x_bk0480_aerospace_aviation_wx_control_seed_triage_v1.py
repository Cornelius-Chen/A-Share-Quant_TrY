from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V129XBK0480AerospaceAviationWXControlSeedTriageReport:
    summary: dict[str, Any]
    direction_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "direction_rows": self.direction_rows,
            "interpretation": self.interpretation,
        }


class V129XBK0480AerospaceAviationWXControlSeedTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = repo_root / "reports" / "analysis" / "v129w_bk0480_aerospace_aviation_control_seed_audit_v1.json"
        self.control_seed_path = repo_root / "reports" / "analysis" / "v129u_bk0480_aerospace_aviation_control_seed_extraction_v1.json"

    def analyze(self) -> V129XBK0480AerospaceAviationWXControlSeedTriageReport:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        control_seed = json.loads(self.control_seed_path.read_text(encoding="utf-8"))

        direction_rows = [
            {
                "direction": "minimal_dual_core_control_seed",
                "status": "retain_as_kickoff_surface",
                "reason": "000738 still wins the composite ranking on most overlap dates and has a clear expected-upside edge.",
            },
            {
                "direction": "bk0480_replay_unlock",
                "status": "blocked",
                "reason": "600118 flips the authority/support ordering on too many dates for a replay unlock from a two-name seed alone.",
            },
            {
                "direction": "bk0480_local_universe_expansion",
                "status": "next_primary_direction",
                "reason": "The next lawful move is to expand locally around the dual core and relearn authority/support under a wider BK0480-native surface.",
            },
            {
                "direction": "commercial_aerospace_style_borrowing",
                "status": "blocked",
                "reason": "The instability must be solved with BK0480-native evidence, not borrowed confirmation or mirror layers.",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v129x_bk0480_aerospace_aviation_wx_control_seed_triage_v1",
            "board_name": control_seed["summary"]["board_name"],
            "sector_id": control_seed["summary"]["sector_id"],
            "authority_overlap_composite_win_rate": audit["summary"]["authority_overlap_composite_win_rate"],
            "support_role_flip_count": audit["summary"]["support_role_flip_count"],
            "authoritative_status": "retain_bk0480_dual_core_seed_but_block_replay_and_move_to_local_universe_expansion",
            "authoritative_rule": "bk0480_needs_more_local_names_before_control_surface_quality_is_strong_enough_for_replay_or_supervised_unlock",
        }
        interpretation = [
            "V1.29X freezes the BK0480 dual-core seed as a valid kickoff surface but not a replay-ready one.",
            "The board now needs local universe expansion rather than borrowed confirmation layers or premature replay tuning.",
        ]
        return V129XBK0480AerospaceAviationWXControlSeedTriageReport(
            summary=summary,
            direction_rows=direction_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V129XBK0480AerospaceAviationWXControlSeedTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V129XBK0480AerospaceAviationWXControlSeedTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129x_bk0480_aerospace_aviation_wx_control_seed_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
