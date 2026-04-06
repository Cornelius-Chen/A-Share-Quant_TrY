from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _normalize_iso_date(value: str) -> str:
    value = str(value).strip()
    if len(value) == 8 and value.isdigit():
        return f"{value[:4]}-{value[4:6]}-{value[6:]}"
    return value


@dataclass(slots=True)
class MaterializedAShareIndexDailyExtensionCandidateV1:
    summary: dict[str, Any]
    candidate_rows: list[dict[str, Any]]
    residual_rows: list[dict[str, Any]]


class MaterializeAShareIndexDailyExtensionCandidateV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.shadow_surface_path = (
            repo_root / "data" / "derived" / "info_center" / "replay" / "shadow" / "a_share_shadow_replay_surface_v1.csv"
        )
        self.current_index_path = (
            repo_root / "data" / "reference" / "info_center" / "market_registry" / "a_share_index_market_registry_v1.csv"
        )
        self.raw_index_dir = repo_root / "data" / "raw" / "index_daily_bars"
        self.output_dir = repo_root / "data" / "reference" / "info_center" / "market_registry"
        self.candidate_path = self.output_dir / "a_share_index_daily_extension_candidate_surface_v1.csv"
        self.residual_path = self.output_dir / "a_share_index_daily_extension_candidate_residual_v1.csv"
        self.manifest_path = self.output_dir / "a_share_index_daily_extension_candidate_manifest_v1.json"

    def materialize(self) -> MaterializedAShareIndexDailyExtensionCandidateV1:
        shadow_rows = _read_csv(self.shadow_surface_path)
        current_index_rows = _read_csv(self.current_index_path)
        raw_index_rows: list[dict[str, str]] = []
        raw_files = sorted(self.raw_index_dir.glob("*.csv"))
        for path in raw_files:
            raw_index_rows.extend(_read_csv(path))

        current_dates = {row["first_trade_date"] for row in current_index_rows} | {row["last_trade_date"] for row in current_index_rows}
        raw_dates = {_normalize_iso_date(row["trade_date"]) for row in raw_index_rows}

        candidate_rows: list[dict[str, Any]] = []
        candidate_cover_count = 0
        for row in shadow_rows:
            trade_date = row["decision_trade_date"]
            current_present = trade_date in current_dates
            raw_candidate_present = trade_date in raw_dates
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
                    "current_index_present": current_present,
                    "raw_index_candidate_present": raw_candidate_present,
                    "extension_candidate_state": state,
                }
            )

        residual_rows = [
            {
                "residual_class": "raw_index_window_stops_2024_12_31",
                "residual_reason": "current raw index daily files do not extend into the 2025-2026 shadow horizon",
            },
            {
                "residual_class": "candidate_cover_absent_for_shadow_horizon",
                "residual_reason": "paired index-daily promotion remains blocked until a longer raw index feed is added",
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
            "raw_file_count": len(raw_files),
            "raw_index_coverage_start": min(raw_dates),
            "raw_index_coverage_end": max(raw_dates),
            "candidate_path": str(self.candidate_path.relative_to(self.repo_root)),
            "residual_path": str(self.residual_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareIndexDailyExtensionCandidateV1(
            summary=summary, candidate_rows=candidate_rows, residual_rows=residual_rows
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareIndexDailyExtensionCandidateV1(repo_root).materialize()
    print(result.summary["candidate_path"])


if __name__ == "__main__":
    main()
