from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134GTCommercialAerospaceReentryUnlockShadowStateSurfaceV1Report:
    summary: dict[str, Any]
    state_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "state_rows": self.state_rows,
            "interpretation": self.interpretation,
        }


class V134GTCommercialAerospaceReentryUnlockShadowStateSurfaceV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.reentry_timing_path = analysis_dir / "v134ba_commercial_aerospace_post_exit_reentry_timing_supervision_audit_v1.json"
        self.reentry_ladder_path = analysis_dir / "v134bc_commercial_aerospace_post_exit_reentry_ladder_audit_v1.json"
        self.lockout_path = analysis_dir / "v134be_commercial_aerospace_board_cooling_lockout_audit_v1.json"
        self.bridge_path = analysis_dir / "v134gr_commercial_aerospace_reentry_unlock_shadow_bridge_spec_v1.json"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_reentry_unlock_shadow_state_surface_v1.csv"
        )

    def analyze(self) -> V134GTCommercialAerospaceReentryUnlockShadowStateSurfaceV1Report:
        reentry_timing = json.loads(self.reentry_timing_path.read_text(encoding="utf-8"))
        reentry_ladder = json.loads(self.reentry_ladder_path.read_text(encoding="utf-8"))
        lockout = json.loads(self.lockout_path.read_text(encoding="utf-8"))
        bridge = json.loads(self.bridge_path.read_text(encoding="utf-8"))

        lockout_seed = lockout["seed_rows"][0]
        lockout_start = lockout_seed["lockout_start_trade_date"]
        lockout_end = lockout_seed["lockout_end_trade_date"]

        ladder_by_key = {
            (row["trade_date"], row["symbol"]): row
            for row in reentry_ladder["seed_rows"]
        }

        state_rows: list[dict[str, Any]] = []
        pre_lockout_seed_count = 0
        in_lockout_seed_count = 0
        current_add_handoff_ready_count = 0

        for row in reentry_timing["seed_rows"]:
            key = (row["trade_date"], row["symbol"])
            ladder_row = ladder_by_key[key]
            trade_date = row["trade_date"]

            if trade_date < lockout_start:
                board_gate_state = "pre_lockout_seed"
                pre_lockout_seed_count += 1
            elif lockout_start <= trade_date <= lockout_end:
                board_gate_state = "in_lockout_seed"
                in_lockout_seed_count += 1
            else:
                board_gate_state = "post_lockout_seed"

            add_handoff_state = "blocked_until_board_unlock"
            add_permission_consult_ready = False
            if add_permission_consult_ready:
                current_add_handoff_ready_count += 1

            state_rows.append(
                {
                    "trade_date": trade_date,
                    "symbol": row["symbol"],
                    "reentry_family": row["reentry_family"],
                    "board_gate_state": board_gate_state,
                    "same_day_state": "same_day_chase_blocked",
                    "observation_only_through_day": row["observation_only_through_day"],
                    "rebuild_watch_start_day": row["rebuild_watch_start_day"],
                    "rebuild_watch_label": row["rebuild_watch_label"],
                    "confirmation_state": ladder_row["recovery_shape"],
                    "confirmation_positive_3d": ladder_row["positive_3d"],
                    "confirmation_positive_5d": ladder_row["positive_5d"],
                    "add_handoff_state": add_handoff_state,
                    "add_permission_consult_ready": add_permission_consult_ready,
                    "lockout_window": f"{lockout_start}->{lockout_end}",
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(state_rows[0].keys()))
            writer.writeheader()
            writer.writerows(state_rows)

        summary = {
            "acceptance_posture": "build_v134gt_commercial_aerospace_reentry_unlock_shadow_state_surface_v1",
            "seed_count": len(state_rows),
            "pre_lockout_seed_count": pre_lockout_seed_count,
            "in_lockout_seed_count": in_lockout_seed_count,
            "current_add_handoff_ready_count": current_add_handoff_ready_count,
            "same_day_block_seed_count": reentry_timing["summary"]["same_day_chase_block_seed_count"],
            "bridge_stage_count": bridge["summary"]["bridge_stage_count"],
            "state_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_reentry_unlock_shadow_state_surface_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34GT is the first concrete state surface for the new reentry/unlock shadow bridge.",
            "It does not simulate execution. It simply enumerates where each current reentry seed sits inside board gating, same-day blocking, rebuild-watch timing, later confirmation, and handoff readiness to frozen add supervision.",
        ]
        return V134GTCommercialAerospaceReentryUnlockShadowStateSurfaceV1Report(
            summary=summary,
            state_rows=state_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GTCommercialAerospaceReentryUnlockShadowStateSurfaceV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GTCommercialAerospaceReentryUnlockShadowStateSurfaceV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134gt_commercial_aerospace_reentry_unlock_shadow_state_surface_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
