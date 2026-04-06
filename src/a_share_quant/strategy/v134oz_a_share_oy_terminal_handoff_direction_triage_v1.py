from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134OZAShareOYTerminalHandoffDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134OZAShareOYTerminalHandoffDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.report_path = (
            repo_root / "reports" / "analysis" / "v134oy_a_share_information_center_terminal_handoff_package_v1.json"
        )

    def analyze(self) -> V134OZAShareOYTerminalHandoffDirectionTriageV1Report:
        report = json.loads(self.report_path.read_text(encoding="utf-8"))
        summary = report["summary"]
        triage_rows = [
            {
                "component": "core_build",
                "direction": "treat_internal_information_center_build_as_finished_enough",
            },
            {
                "component": "source_lane",
                "direction": "advance_only_by_manual_operator_execution_from_stage_1_checklist",
            },
            {
                "component": "replay_lane",
                "direction": "advance_only_after_replay_internal_build_preconditions_move",
            },
            {
                "component": "execution_gate",
                "direction": "retain_block_until_both_real_world_lanes_move",
            },
        ]
        result_summary = {
            "handoff_component_count": summary["handoff_component_count"],
            "foundation_complete_count": summary["foundation_complete_count"],
            "authoritative_status": "information_center_should_now_be_governed_as_terminal_internal_build_plus_two_real_world_closure_lanes",
        }
        interpretation = [
            "The correct next-step framing is no longer open-ended buildout.",
            "The remaining movement now belongs to manual execution and future source intake, not to additional internal architecture expansion.",
        ]
        return V134OZAShareOYTerminalHandoffDirectionTriageV1Report(
            summary=result_summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134OZAShareOYTerminalHandoffDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134OZAShareOYTerminalHandoffDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134oz_a_share_oy_terminal_handoff_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
