from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134AYCommercialAerospacePostExitReentrySupervisionSpecV1Report:
    summary: dict[str, Any]
    family_rows: list[dict[str, Any]]
    seed_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "family_rows": self.family_rows,
            "seed_rows": self.seed_rows,
            "interpretation": self.interpretation,
        }


class V134AYCommercialAerospacePostExitReentrySupervisionSpecV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.registry_path = (
            repo_root / "reports" / "analysis" / "v134aw_commercial_aerospace_post_exit_reentry_seed_registry_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_post_exit_reentry_supervision_spec_v1.csv"
        )

    def analyze(self) -> V134AYCommercialAerospacePostExitReentrySupervisionSpecV1Report:
        registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        seed_rows: list[dict[str, Any]] = []
        family_buckets: dict[str, list[dict[str, Any]]] = {}

        for row in registry["registry_rows"]:
            family = row["reentry_family"]
            if family == "delayed_rebound_reentry_gap":
                supervision_label = "delayed_reclaim_reentry_watch"
                supervision_action = "watch_for_reclaim_rebuild_not_same_day_chase"
                earliest_positive_horizon = "3d"
            elif family == "deep_washout_reentry_gap":
                supervision_label = "deep_washout_reentry_watch"
                supervision_action = "wait_for_base_then_rebuild_watch"
                earliest_positive_horizon = "5d"
            else:
                supervision_label = "other_reentry_watch"
                supervision_action = "observation_only"
                earliest_positive_horizon = "unknown"

            seed = {
                "trade_date": row["trade_date"],
                "symbol": row["symbol"],
                "month_bucket": row["month_bucket"],
                "reentry_family": family,
                "supervision_label": supervision_label,
                "supervision_action": supervision_action,
                "earliest_positive_horizon": earliest_positive_horizon,
                "horizon_pnl_1d": float(row["horizon_pnl_1d"]),
                "horizon_pnl_3d": float(row["horizon_pnl_3d"]),
                "horizon_pnl_5d": float(row["horizon_pnl_5d"]),
            }
            seed_rows.append(seed)
            family_buckets.setdefault(family, []).append(seed)

        family_rows = []
        for family, rows in sorted(family_buckets.items()):
            family_rows.append(
                {
                    "reentry_family": family,
                    "seed_count": len(rows),
                    "dominant_supervision_label": rows[0]["supervision_label"],
                    "dominant_supervision_action": rows[0]["supervision_action"],
                    "earliest_positive_horizon": rows[0]["earliest_positive_horizon"],
                    "mean_horizon_pnl_1d": round(sum(r["horizon_pnl_1d"] for r in rows) / len(rows), 4),
                    "mean_horizon_pnl_3d": round(sum(r["horizon_pnl_3d"] for r in rows) / len(rows), 4),
                    "mean_horizon_pnl_5d": round(sum(r["horizon_pnl_5d"] for r in rows) / len(rows), 4),
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(seed_rows[0].keys()))
            writer.writeheader()
            writer.writerows(seed_rows)

        summary = {
            "acceptance_posture": "freeze_v134ay_commercial_aerospace_post_exit_reentry_supervision_spec_v1",
            "seed_count": len(seed_rows),
            "family_count": len(family_rows),
            "dominant_family": max(family_buckets.items(), key=lambda item: len(item[1]))[0] if family_buckets else "",
            "spec_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_post_exit_reentry_supervision_spec_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34AY converts the new post-exit reentry seeds into supervision-side labels and actions.",
            "This step still does not build a reentry simulator; it only names the next supervised family in a point-in-time-safe way for future audits.",
        ]
        return V134AYCommercialAerospacePostExitReentrySupervisionSpecV1Report(
            summary=summary,
            family_rows=family_rows,
            seed_rows=seed_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134AYCommercialAerospacePostExitReentrySupervisionSpecV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134AYCommercialAerospacePostExitReentrySupervisionSpecV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ay_commercial_aerospace_post_exit_reentry_supervision_spec_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
