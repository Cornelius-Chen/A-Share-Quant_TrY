from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V129VBK0480AerospaceAviationUVWControlSeedTriageReport:
    summary: dict[str, Any]
    direction_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "direction_rows": self.direction_rows,
            "interpretation": self.interpretation,
        }


class V129VBK0480AerospaceAviationUVWControlSeedTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.control_seed_path = (
            repo_root / "reports" / "analysis" / "v129u_bk0480_aerospace_aviation_control_seed_extraction_v1.json"
        )
        self.role_triage_path = (
            repo_root / "reports" / "analysis" / "v129t_bk0480_aerospace_aviation_stu_role_triage_v1.json"
        )

    def analyze(self) -> V129VBK0480AerospaceAviationUVWControlSeedTriageReport:
        control_seed = json.loads(self.control_seed_path.read_text(encoding="utf-8"))
        role_triage = json.loads(self.role_triage_path.read_text(encoding="utf-8"))

        direction_rows = [
            {
                "direction": "minimal_dual_core_control_seed",
                "status": "freeze_as_authoritative_kickoff_control_surface",
                "reason": "BK0480 needs a narrow local control surface first, not a replay unlock or borrowed breadth expansion.",
            },
            {
                "direction": "borrowed_commercial_aerospace_control_surface",
                "status": "blocked",
                "reason": "The destination board must not inherit commercial-aerospace authority breadth or symbol facts.",
            },
            {
                "direction": "next_phase",
                "status": "control_seed_audit",
                "reason": control_seed["summary"]["recommended_next_posture"],
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v129v_bk0480_aerospace_aviation_uvw_control_seed_triage_v1",
            "board_name": control_seed["summary"]["board_name"],
            "sector_id": control_seed["summary"]["sector_id"],
            "authoritative_status": "freeze_bk0480_minimal_control_seed_and_move_to_control_seed_audit",
            "worker_status": role_triage["summary"]["authoritative_status"],
            "authoritative_rule": "bk0480_starts_with_minimal_local_control_seed_then_proves_control_quality_before_any_replay_or_universe_expansion",
        }
        interpretation = [
            "V1.29V freezes the first BK0480 control surface as a deliberately narrow seed rather than a replay-ready system.",
            "The next lawful step is control-seed audit, not replay or broad concept expansion.",
        ]
        return V129VBK0480AerospaceAviationUVWControlSeedTriageReport(
            summary=summary,
            direction_rows=direction_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V129VBK0480AerospaceAviationUVWControlSeedTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V129VBK0480AerospaceAviationUVWControlSeedTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129v_bk0480_aerospace_aviation_uvw_control_seed_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
