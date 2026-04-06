from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134GSCommercialAerospaceGRReentryUnlockBridgeDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134GSCommercialAerospaceGRReentryUnlockBridgeDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.bridge_path = (
            repo_root / "reports" / "analysis" / "v134gr_commercial_aerospace_reentry_unlock_shadow_bridge_spec_v1.json"
        )

    def analyze(self) -> V134GSCommercialAerospaceGRReentryUnlockBridgeDirectionTriageV1Report:
        bridge = json.loads(self.bridge_path.read_text(encoding="utf-8"))
        triage_rows = [
            {
                "component": "shadow_bridge_module",
                "status": "approved_for_next_build",
                "rationale": "the branch now has enough frozen reduce, board, reentry, and add supervision assets to justify a unified read-only bridge",
            },
            {
                "component": "same_day_reentry",
                "status": "keep_blocked",
                "rationale": "the current supervision still blocks same-day chase across all reentry seeds",
            },
            {
                "component": "board_gating",
                "status": "mandatory",
                "rationale": "lockout, revival unlock, and expectancy gates must stay above symbol-level reentry timing",
            },
            {
                "component": "handoff_to_add",
                "status": "read_only_only",
                "rationale": "the bridge may consult frozen add supervision states but cannot promote add into execution",
            },
            {
                "component": "execution_authority",
                "status": "still_blocked",
                "rationale": "the new frontier remains a protocol and supervision-binding lane, not an execution lane",
            },
        ]
        interpretation = [
            "V1.34GS turns the reentry/unlock bridge spec into the current governance verdict.",
            "The next build should unify the missing middle in shadow form, while preserving every existing execution boundary.",
        ]
        return V134GSCommercialAerospaceGRReentryUnlockBridgeDirectionTriageV1Report(
            summary={
                "acceptance_posture": "open_v134gs_commercial_aerospace_gr_reentry_unlock_bridge_direction_triage_v1",
                "authoritative_status": (
                    "approve_reentry_unlock_shadow_bridge_as_first_module_of_intraday_shadow_replay_lane"
                ),
                "bridge_stage_count": bridge["summary"]["bridge_stage_count"],
                "same_day_block_seed_count": bridge["summary"]["same_day_block_seed_count"],
                "execution_authority": "still_blocked",
                "authoritative_rule": (
                    "the next build should bind the missing middle between reduce and add in a read-only shadow bridge, while keeping same-day chase and execution authority blocked"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GSCommercialAerospaceGRReentryUnlockBridgeDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GSCommercialAerospaceGRReentryUnlockBridgeDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134gs_commercial_aerospace_gr_reentry_unlock_bridge_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
