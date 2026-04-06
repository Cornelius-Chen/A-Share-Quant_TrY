from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class MaterializedAShareLimitHaltExtensionCandidateV1:
    summary: dict[str, Any]
    candidate_rows: list[dict[str, Any]]
    residual_rows: list[dict[str, Any]]


class MaterializeAShareLimitHaltExtensionCandidateV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.shadow_surface_path = (
            repo_root / "data" / "derived" / "info_center" / "replay" / "shadow" / "a_share_shadow_replay_surface_v1.csv"
        )
        self.current_limit_halt_path = (
            repo_root / "data" / "reference" / "info_center" / "market_registry" / "a_share_limit_halt_surface_v1.csv"
        )
        self.raw_daily_path = (
            repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
        )
        self.output_dir = repo_root / "data" / "reference" / "info_center" / "market_registry"
        self.candidate_path = self.output_dir / "a_share_limit_halt_extension_candidate_surface_v1.csv"
        self.residual_path = self.output_dir / "a_share_limit_halt_extension_candidate_residual_v1.csv"
        self.manifest_path = self.output_dir / "a_share_limit_halt_extension_candidate_manifest_v1.json"

    def materialize(self) -> MaterializedAShareLimitHaltExtensionCandidateV1:
        shadow_rows = _read_csv(self.shadow_surface_path)
        current_limit_rows = _read_csv(self.current_limit_halt_path)
        raw_daily_rows = _read_csv(self.raw_daily_path)

        current_dates = {f"{row['trade_date'][:4]}-{row['trade_date'][4:6]}-{row['trade_date'][6:]}" for row in current_limit_rows}
        raw_daily_dates = {f"{row['trade_date'][:4]}-{row['trade_date'][4:6]}-{row['trade_date'][6:]}" for row in raw_daily_rows}

        candidate_rows: list[dict[str, Any]] = []
        candidate_cover_count = 0
        for row in shadow_rows:
            trade_date = row["decision_trade_date"]
            current_present = trade_date in current_dates
            raw_candidate_present = trade_date in raw_daily_dates
            state = (
                "candidate_cover_available"
                if raw_candidate_present and not current_present
                else "already_covered"
                if current_present
                else "no_candidate_cover"
            )
            if state == "candidate_cover_available":
                candidate_cover_count += 1
            candidate_rows.append(
                {
                    "slice_id": row["slice_id"],
                    "decision_trade_date": trade_date,
                    "current_limit_halt_present": current_present,
                    "raw_daily_candidate_present": raw_candidate_present,
                    "extension_candidate_state": state,
                }
            )

        residual_rows = [
            {
                "residual_class": "board_rule_derivation_pending",
                "residual_reason": "raw daily candidate exists, but board/ST-specific limit ratios still need controlled derivation",
            },
            {
                "residual_class": "suspension_binding_pending",
                "residual_reason": "raw daily candidate does not by itself resolve suspension-state linkage for post-2024 dates",
            },
        ]

        self.output_dir.mkdir(parents=True, exist_ok=True)

        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.candidate_path, candidate_rows)
        _write(self.residual_path, residual_rows)

        summary = {
            "shadow_slice_count": len(candidate_rows),
            "candidate_cover_count": candidate_cover_count,
            "raw_daily_coverage_start": min(raw_daily_dates),
            "raw_daily_coverage_end": max(raw_daily_dates),
            "candidate_path": str(self.candidate_path.relative_to(self.repo_root)),
            "residual_path": str(self.residual_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareLimitHaltExtensionCandidateV1(
            summary=summary, candidate_rows=candidate_rows, residual_rows=residual_rows
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareLimitHaltExtensionCandidateV1(repo_root).materialize()
    print(result.summary["candidate_path"])


if __name__ == "__main__":
    main()
