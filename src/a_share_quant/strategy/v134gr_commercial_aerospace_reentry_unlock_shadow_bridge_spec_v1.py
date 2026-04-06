from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134GRCommercialAerospaceReentryUnlockShadowBridgeSpecV1Report:
    summary: dict[str, Any]
    bridge_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "bridge_rows": self.bridge_rows,
            "interpretation": self.interpretation,
        }


class V134GRCommercialAerospaceReentryUnlockShadowBridgeSpecV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.reentry_timing_path = analysis_dir / "v134ba_commercial_aerospace_post_exit_reentry_timing_supervision_audit_v1.json"
        self.reentry_ladder_path = analysis_dir / "v134bc_commercial_aerospace_post_exit_reentry_ladder_audit_v1.json"
        self.lockout_path = analysis_dir / "v134be_commercial_aerospace_board_cooling_lockout_audit_v1.json"
        self.unlock_path = analysis_dir / "v134bg_commercial_aerospace_board_revival_unlock_audit_v1.json"
        self.expectancy_path = analysis_dir / "v134bm_commercial_aerospace_board_expectancy_supervision_audit_v1.json"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_reentry_unlock_shadow_bridge_spec_v1.csv"
        )

    def analyze(self) -> V134GRCommercialAerospaceReentryUnlockShadowBridgeSpecV1Report:
        reentry_timing = json.loads(self.reentry_timing_path.read_text(encoding="utf-8"))
        reentry_ladder = json.loads(self.reentry_ladder_path.read_text(encoding="utf-8"))
        lockout = json.loads(self.lockout_path.read_text(encoding="utf-8"))
        unlock = json.loads(self.unlock_path.read_text(encoding="utf-8"))
        expectancy = json.loads(self.expectancy_path.read_text(encoding="utf-8"))

        bridge_rows = [
            {
                "bridge_stage": "sell_exit_source",
                "status": "frozen_reduce_reference",
                "detail": "The bridge begins from frozen reduce outputs and cannot mutate reduce mainline history.",
            },
            {
                "bridge_stage": "board_lockout_gate",
                "status": "required",
                "detail": (
                    f"Use board_cooling_lockout as upper veto. Current seed count: {lockout['summary']['lockout_seed_count']}."
                ),
            },
            {
                "bridge_stage": "board_unlock_gate",
                "status": "required",
                "detail": (
                    f"Only unlock-worthy board states may reopen add-side permission. Positive sample count: {unlock['summary']['positive_seed_count']}."
                ),
            },
            {
                "bridge_stage": "expectancy_gate",
                "status": "required",
                "detail": (
                    f"Board state must not remain false_bounce_only or lockout_worthy. Unlock-worthy count: {expectancy['summary']['unlock_worthy_count']}."
                ),
            },
            {
                "bridge_stage": "same_day_reentry",
                "status": "blocked",
                "detail": f"All current reentry seeds block same-day chase. Blocked seeds: {reentry_timing['summary']['same_day_chase_block_seed_count']}.",
            },
            {
                "bridge_stage": "rebuild_watch_entry",
                "status": "seed_supervision_ready",
                "detail": (
                    "Deep-washout family opens rebuild watch at T+5+; delayed-rebound family opens rebuild watch at T+3+."
                ),
            },
            {
                "bridge_stage": "confirmation_shape",
                "status": "seed_supervision_ready",
                "detail": (
                    f"Persistent recovery seeds: {reentry_ladder['summary']['persistent_recovery_seed_count']}; "
                    f"late-only recovery seeds: {reentry_ladder['summary']['late_only_recovery_seed_count']}."
                ),
            },
            {
                "bridge_stage": "handoff_to_add",
                "status": "read_only_permission_bridge",
                "detail": "Only after board unlock plus reentry confirmation may the shadow lane consult frozen add supervision states.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(bridge_rows[0].keys()))
            writer.writeheader()
            writer.writerows(bridge_rows)

        summary = {
            "acceptance_posture": "build_v134gr_commercial_aerospace_reentry_unlock_shadow_bridge_spec_v1",
            "bridge_stage_count": len(bridge_rows),
            "reentry_seed_count": reentry_ladder["summary"]["seed_count"],
            "same_day_block_seed_count": reentry_timing["summary"]["same_day_chase_block_seed_count"],
            "lockout_seed_count": lockout["summary"]["lockout_seed_count"],
            "unlock_positive_day_count": unlock["summary"]["positive_seed_count"],
            "unlock_worthy_count": expectancy["summary"]["unlock_worthy_count"],
            "bridge_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_reentry_unlock_shadow_bridge_spec_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34GR specifies the first module of the new shadow replay lane: how frozen reduce hands off into board lockout, board unlock, seed-level reentry timing, later confirmation, and only then into frozen add supervision.",
            "The bridge is intentionally read-only. Its job is to define lawful sequencing, not to smuggle execution authority into either side.",
        ]
        return V134GRCommercialAerospaceReentryUnlockShadowBridgeSpecV1Report(
            summary=summary,
            bridge_rows=bridge_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GRCommercialAerospaceReentryUnlockShadowBridgeSpecV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GRCommercialAerospaceReentryUnlockShadowBridgeSpecV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134gr_commercial_aerospace_reentry_unlock_shadow_bridge_spec_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
