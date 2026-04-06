from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BACommercialAerospacePostExitReentryTimingSupervisionAuditV1Report:
    summary: dict[str, Any]
    family_rows: list[dict[str, Any]]
    seed_rows: list[dict[str, Any]]
    window_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "family_rows": self.family_rows,
            "seed_rows": self.seed_rows,
            "window_rows": self.window_rows,
            "interpretation": self.interpretation,
        }


class V134BACommercialAerospacePostExitReentryTimingSupervisionAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.spec_path = (
            repo_root / "reports" / "analysis" / "v134ay_commercial_aerospace_post_exit_reentry_supervision_spec_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_post_exit_reentry_timing_supervision_audit_v1.csv"
        )

    @staticmethod
    def _first_positive_horizon(seed: dict[str, Any]) -> int | None:
        for horizon in (1, 3, 5):
            if float(seed[f"horizon_pnl_{horizon}d"]) > 0:
                return horizon
        return None

    @staticmethod
    def _observation_end_day(first_positive_horizon: int | None) -> int | None:
        if first_positive_horizon is None:
            return None
        return max(first_positive_horizon - 1, 0)

    def analyze(self) -> V134BACommercialAerospacePostExitReentryTimingSupervisionAuditV1Report:
        spec = json.loads(self.spec_path.read_text(encoding="utf-8"))
        seed_rows: list[dict[str, Any]] = []
        window_rows: list[dict[str, Any]] = []
        family_buckets: dict[str, list[dict[str, Any]]] = {}

        for raw_seed in spec["seed_rows"]:
            first_positive_horizon = self._first_positive_horizon(raw_seed)
            observation_end_day = self._observation_end_day(first_positive_horizon)
            if raw_seed["reentry_family"] == "deep_washout_reentry_gap":
                pre_rebuild_state = "washout_observation_only"
                rebuild_watch_label = "base_then_rebuild_watch"
            else:
                pre_rebuild_state = "reclaim_observation_only"
                rebuild_watch_label = "reclaim_rebuild_watch"

            seed = {
                "trade_date": raw_seed["trade_date"],
                "symbol": raw_seed["symbol"],
                "month_bucket": raw_seed["month_bucket"],
                "reentry_family": raw_seed["reentry_family"],
                "supervision_label": raw_seed["supervision_label"],
                "same_day_chase_blocked": True,
                "rebuild_watch_start_day": first_positive_horizon or "",
                "observation_only_through_day": observation_end_day if observation_end_day is not None else "",
                "rebuild_watch_label": rebuild_watch_label,
                "horizon_pnl_1d": float(raw_seed["horizon_pnl_1d"]),
                "horizon_pnl_3d": float(raw_seed["horizon_pnl_3d"]),
                "horizon_pnl_5d": float(raw_seed["horizon_pnl_5d"]),
            }
            seed_rows.append(seed)
            family_buckets.setdefault(raw_seed["reentry_family"], []).append(seed)

            window_rows.append(
                {
                    "trade_date": raw_seed["trade_date"],
                    "symbol": raw_seed["symbol"],
                    "reentry_family": raw_seed["reentry_family"],
                    "window_name": "same_day",
                    "day_range": "T+0",
                    "supervision_state": "blocked",
                    "action": "block_same_day_chase",
                }
            )
            if observation_end_day and observation_end_day >= 1:
                window_rows.append(
                    {
                        "trade_date": raw_seed["trade_date"],
                        "symbol": raw_seed["symbol"],
                        "reentry_family": raw_seed["reentry_family"],
                        "window_name": "observation_only",
                        "day_range": f"T+1~T+{observation_end_day}",
                        "supervision_state": pre_rebuild_state,
                        "action": "observe_only_no_rebuild",
                    }
                )
            if first_positive_horizon is not None:
                window_rows.append(
                    {
                        "trade_date": raw_seed["trade_date"],
                        "symbol": raw_seed["symbol"],
                        "reentry_family": raw_seed["reentry_family"],
                        "window_name": "rebuild_watch",
                        "day_range": f"T+{first_positive_horizon}+",
                        "supervision_state": rebuild_watch_label,
                        "action": raw_seed["supervision_action"],
                    }
                )

        family_rows: list[dict[str, Any]] = []
        for family, rows in sorted(family_buckets.items()):
            watch_days = [int(row["rebuild_watch_start_day"]) for row in rows if row["rebuild_watch_start_day"] != ""]
            family_rows.append(
                {
                    "reentry_family": family,
                    "seed_count": len(rows),
                    "same_day_chase_block_count": sum(1 for row in rows if row["same_day_chase_blocked"]),
                    "positive_1d_count": sum(1 for row in rows if row["horizon_pnl_1d"] > 0),
                    "positive_3d_count": sum(1 for row in rows if row["horizon_pnl_3d"] > 0),
                    "positive_5d_count": sum(1 for row in rows if row["horizon_pnl_5d"] > 0),
                    "earliest_rebuild_watch_day": min(watch_days) if watch_days else "",
                    "latest_rebuild_watch_day": max(watch_days) if watch_days else "",
                    "dominant_rebuild_watch_label": rows[0]["rebuild_watch_label"],
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(window_rows[0].keys()))
            writer.writeheader()
            writer.writerows(window_rows)

        positive_1d_seed_count = sum(1 for row in seed_rows if row["horizon_pnl_1d"] > 0)
        positive_3d_seed_count = sum(1 for row in seed_rows if row["horizon_pnl_3d"] > 0)
        positive_5d_seed_count = sum(1 for row in seed_rows if row["horizon_pnl_5d"] > 0)
        summary = {
            "acceptance_posture": "freeze_v134ba_commercial_aerospace_post_exit_reentry_timing_supervision_audit_v1",
            "seed_count": len(seed_rows),
            "family_count": len(family_rows),
            "same_day_chase_block_seed_count": len(seed_rows),
            "positive_1d_seed_count": positive_1d_seed_count,
            "positive_3d_seed_count": positive_3d_seed_count,
            "positive_5d_seed_count": positive_5d_seed_count,
            "window_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_post_exit_reentry_timing_supervision_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34BA converts the new post-exit reentry seeds into time-window supervision rather than a simulator.",
            "The key question here is not same-day execution but when rebuild observation may begin without turning the branch into same-day chase behavior.",
        ]
        return V134BACommercialAerospacePostExitReentryTimingSupervisionAuditV1Report(
            summary=summary,
            family_rows=family_rows,
            seed_rows=seed_rows,
            window_rows=window_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BACommercialAerospacePostExitReentryTimingSupervisionAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BACommercialAerospacePostExitReentryTimingSupervisionAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ba_commercial_aerospace_post_exit_reentry_timing_supervision_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
