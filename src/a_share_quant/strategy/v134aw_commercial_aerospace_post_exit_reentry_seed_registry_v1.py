from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134AWCommercialAerospacePostExitReentrySeedRegistryV1Report:
    summary: dict[str, Any]
    registry_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "registry_rows": self.registry_rows,
            "interpretation": self.interpretation,
        }


class V134AWCommercialAerospacePostExitReentrySeedRegistryV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134au_commercial_aerospace_post_exit_rebound_pattern_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_post_exit_reentry_seed_registry_v1.csv"
        )

    def analyze(self) -> V134AWCommercialAerospacePostExitReentrySeedRegistryV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        registry_rows: list[dict[str, Any]] = []
        for row in audit["case_rows"]:
            pattern_key = row["pattern_key"]
            if pattern_key == "neg_1d|pos_3d|pos_5d":
                reentry_family = "delayed_rebound_reentry_gap"
            elif pattern_key == "neg_1d|neg_3d|pos_5d":
                reentry_family = "deep_washout_reentry_gap"
            else:
                reentry_family = "other_reentry_gap"
            registry_rows.append(
                {
                    "trade_date": row["trade_date"],
                    "symbol": row["symbol"],
                    "month_bucket": row["month_bucket"],
                    "reversal_minute": row["reversal_minute"],
                    "pattern_key": pattern_key,
                    "reentry_family": reentry_family,
                    "horizon_pnl_1d": row["horizon_pnl_1d"],
                    "horizon_pnl_3d": row["horizon_pnl_3d"],
                    "horizon_pnl_5d": row["horizon_pnl_5d"],
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(registry_rows[0].keys()))
            writer.writeheader()
            writer.writerows(registry_rows)

        family_counts: dict[str, int] = {}
        for row in registry_rows:
            family_counts[row["reentry_family"]] = family_counts.get(row["reentry_family"], 0) + 1

        summary = {
            "acceptance_posture": "freeze_v134aw_commercial_aerospace_post_exit_reentry_seed_registry_v1",
            "registry_count": len(registry_rows),
            "family_count": len(family_counts),
            "dominant_reentry_family": max(family_counts.items(), key=lambda item: item[1])[0] if family_counts else "",
            "registry_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_post_exit_reentry_seed_registry_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34AW freezes the first canonical seed registry for the next orthogonal supervision family: post-exit reentry gaps.",
            "The point is not to solve reentry yet, only to convert the remaining rebound-cost misses into a governed seed set.",
        ]
        return V134AWCommercialAerospacePostExitReentrySeedRegistryV1Report(
            summary=summary,
            registry_rows=registry_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134AWCommercialAerospacePostExitReentrySeedRegistryV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134AWCommercialAerospacePostExitReentrySeedRegistryV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134aw_commercial_aerospace_post_exit_reentry_seed_registry_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
