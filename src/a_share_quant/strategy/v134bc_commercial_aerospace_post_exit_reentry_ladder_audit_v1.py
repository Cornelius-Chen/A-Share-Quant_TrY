from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BCCommercialAerospacePostExitReentryLadderAuditV1Report:
    summary: dict[str, Any]
    seed_rows: list[dict[str, Any]]
    ladder_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "seed_rows": self.seed_rows,
            "ladder_rows": self.ladder_rows,
            "interpretation": self.interpretation,
        }


class V134BCCommercialAerospacePostExitReentryLadderAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.timing_path = (
            repo_root / "reports" / "analysis" / "v134ba_commercial_aerospace_post_exit_reentry_timing_supervision_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_post_exit_reentry_ladder_audit_v1.csv"
        )

    def analyze(self) -> V134BCCommercialAerospacePostExitReentryLadderAuditV1Report:
        timing = json.loads(self.timing_path.read_text(encoding="utf-8"))

        seed_rows: list[dict[str, Any]] = []
        ladder_rows: list[dict[str, Any]] = []

        persistent_recovery_seed_count = 0
        late_only_recovery_seed_count = 0

        for row in timing["seed_rows"]:
            positive_3d = float(row["horizon_pnl_3d"]) > 0
            positive_5d = float(row["horizon_pnl_5d"]) > 0
            if positive_3d and positive_5d:
                persistent_recovery_seed_count += 1
                recovery_shape = "persistent_recovery"
                late_phase_state = "persistent_reclaim_confirmation"
                late_phase_action = "allow_stronger_rebuild_observation"
            else:
                late_only_recovery_seed_count += 1
                recovery_shape = "late_only_recovery"
                late_phase_state = "late_base_confirmation"
                late_phase_action = "continue_base_watch_not_rebuild_chase"

            seed = {
                "trade_date": row["trade_date"],
                "symbol": row["symbol"],
                "reentry_family": row["reentry_family"],
                "same_day_chase_blocked": bool(row["same_day_chase_blocked"]),
                "rebuild_watch_start_day": row["rebuild_watch_start_day"],
                "observation_only_through_day": row["observation_only_through_day"],
                "rebuild_watch_label": row["rebuild_watch_label"],
                "recovery_shape": recovery_shape,
                "positive_3d": positive_3d,
                "positive_5d": positive_5d,
            }
            seed_rows.append(seed)

            ladder_rows.append(
                {
                    "trade_date": row["trade_date"],
                    "symbol": row["symbol"],
                    "ladder_step": 1,
                    "day_range": "T+0",
                    "state": "same_day_chase_blocked",
                    "action": "block_same_day_chase",
                }
            )
            ladder_rows.append(
                {
                    "trade_date": row["trade_date"],
                    "symbol": row["symbol"],
                    "ladder_step": 2,
                    "day_range": f"T+1~T+{row['observation_only_through_day']}",
                    "state": "observation_only",
                    "action": "observe_only_no_rebuild",
                }
            )
            ladder_rows.append(
                {
                    "trade_date": row["trade_date"],
                    "symbol": row["symbol"],
                    "ladder_step": 3,
                    "day_range": f"T+{row['rebuild_watch_start_day']}+",
                    "state": row["rebuild_watch_label"],
                    "action": "open_rebuild_watch",
                }
            )
            ladder_rows.append(
                {
                    "trade_date": row["trade_date"],
                    "symbol": row["symbol"],
                    "ladder_step": 4,
                    "day_range": "post_watch_confirmation",
                    "state": late_phase_state,
                    "action": late_phase_action,
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(ladder_rows[0].keys()))
            writer.writeheader()
            writer.writerows(ladder_rows)

        summary = {
            "acceptance_posture": "freeze_v134bc_commercial_aerospace_post_exit_reentry_ladder_audit_v1",
            "seed_count": len(seed_rows),
            "same_day_entry_authorized_seed_count": 0,
            "delayed_reclaim_watch_seed_count": sum(
                1 for row in seed_rows if row["rebuild_watch_label"] == "reclaim_rebuild_watch"
            ),
            "deep_washout_watch_seed_count": sum(
                1 for row in seed_rows if row["rebuild_watch_label"] == "base_then_rebuild_watch"
            ),
            "persistent_recovery_seed_count": persistent_recovery_seed_count,
            "late_only_recovery_seed_count": late_only_recovery_seed_count,
            "ladder_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_post_exit_reentry_ladder_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34BC turns the timing windows into a ladder: block, observe, open rebuild watch, then require later confirmation shape.",
            "This is still supervision only. The ladder names timing states; it does not authorize a reentry simulator or same-day rebuild.",
        ]
        return V134BCCommercialAerospacePostExitReentryLadderAuditV1Report(
            summary=summary,
            seed_rows=seed_rows,
            ladder_rows=ladder_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BCCommercialAerospacePostExitReentryLadderAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BCCommercialAerospacePostExitReentryLadderAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bc_commercial_aerospace_post_exit_reentry_ladder_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
