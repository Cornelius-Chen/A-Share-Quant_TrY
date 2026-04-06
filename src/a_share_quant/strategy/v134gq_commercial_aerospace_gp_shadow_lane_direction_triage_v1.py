from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134GQCommercialAerospaceGPShadowLaneDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134GQCommercialAerospaceGPShadowLaneDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.opening_path = (
            repo_root / "reports" / "analysis" / "v134gp_commercial_aerospace_intraday_shadow_replay_lane_opening_v1.json"
        )

    def analyze(self) -> V134GQCommercialAerospaceGPShadowLaneDirectionTriageV1Report:
        opening = json.loads(self.opening_path.read_text(encoding="utf-8"))
        triage_rows = [
            {
                "component": "intraday_shadow_replay_lane",
                "status": "opened_as_protocol_only",
                "rationale": "the next frontier should unify existing supervision branches before any new execution claims are made",
            },
            {
                "component": "reduce_branch",
                "status": "keep_read_only",
                "rationale": "reduce remains frozen mainline and should only be consumed as a shadow input",
            },
            {
                "component": "add_branch",
                "status": "keep_read_only",
                "rationale": "add remains supervision-complete enough but blocked on portability and execution",
            },
            {
                "component": "first_module",
                "status": "reentry_unlock_shadow_bridge",
                "rationale": "the biggest missing middle is not another add/reduce family but the bridge between exit, lockout, unlock, and later reentry/add permission",
            },
            {
                "component": "execution_authority",
                "status": "still_blocked",
                "rationale": "the lane is explicitly shadow-only and read-only until a lawful replay surface exists",
            },
        ]
        interpretation = [
            "V1.34GQ converts the new shadow-lane opening into a practical direction judgment.",
            "The correct first move is to bind the missing middle between reduce and add, not to reopen either branch as a local tuning frontier.",
        ]
        return V134GQCommercialAerospaceGPShadowLaneDirectionTriageV1Report(
            summary={
                "acceptance_posture": "open_v134gq_commercial_aerospace_gp_shadow_lane_direction_triage_v1",
                "authoritative_status": (
                    "open_intraday_shadow_replay_lane_as_protocol_frontier_and_start_with_reentry_unlock_shadow_bridge"
                ),
                "frontier_state": opening["summary"]["frontier_state"],
                "first_module": opening["summary"]["first_module"],
                "execution_authority": opening["summary"]["execution_authority"],
                "authoritative_rule": (
                    "the next frontier should begin by bridging frozen reduce and frozen add through reentry/unlock in a read-only shadow lane"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GQCommercialAerospaceGPShadowLaneDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GQCommercialAerospaceGPShadowLaneDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134gq_commercial_aerospace_gp_shadow_lane_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
