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
class MaterializedAShareDailyMarketPromotionReviewV1:
    summary: dict[str, Any]
    review_rows: list[dict[str, Any]]
    residual_rows: list[dict[str, Any]]


class MaterializeAShareDailyMarketPromotionReviewV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.candidate_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "market_registry"
            / "a_share_daily_market_extension_candidate_surface_v1.csv"
        )
        self.index_registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "market_registry"
            / "a_share_index_market_registry_v1.csv"
        )
        self.raw_index_dir = repo_root / "data" / "raw" / "index_daily_bars"
        self.limit_halt_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "market_registry"
            / "a_share_limit_halt_surface_v1.csv"
        )
        self.limit_halt_semantic_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "market_registry"
            / "a_share_limit_halt_semantic_surface_v1.csv"
        )
        self.output_dir = repo_root / "data" / "reference" / "info_center" / "market_registry"
        self.review_path = self.output_dir / "a_share_daily_market_promotion_review_v1.csv"
        self.residual_path = self.output_dir / "a_share_daily_market_promotion_review_residual_v1.csv"
        self.manifest_path = self.output_dir / "a_share_daily_market_promotion_review_manifest_v1.json"

    def materialize(self) -> MaterializedAShareDailyMarketPromotionReviewV1:
        candidate_rows = _read_csv(self.candidate_path)
        index_rows = _read_csv(self.index_registry_path)
        raw_index_rows: list[dict[str, str]] = []
        for path in sorted(self.raw_index_dir.glob("*.csv")):
            raw_index_rows.extend(_read_csv(path))
        limit_halt_source_path = (
            self.limit_halt_semantic_path if self.limit_halt_semantic_path.exists() else self.limit_halt_path
        )
        limit_halt_rows = _read_csv(limit_halt_source_path)

        current_index_dates = {row["first_trade_date"] for row in index_rows} | {row["last_trade_date"] for row in index_rows}
        raw_index_dates = {_normalize_iso_date(row["trade_date"]) for row in raw_index_rows}
        limit_halt_dates = {row["trade_date"] for row in limit_halt_rows}

        review_rows: list[dict[str, Any]] = []
        promotable_now_count = 0
        blocked_by_paired_surface_count = 0
        blocked_no_candidate_count = 0

        for row in candidate_rows:
            trade_date = row["decision_trade_date"]
            state = row["extension_candidate_state"]
            current_index_present = trade_date in current_index_dates
            raw_index_candidate_present = trade_date in raw_index_dates
            compact_date = trade_date.replace("-", "")
            limit_halt_present = compact_date in limit_halt_dates

            if state == "candidate_cover_available":
                if raw_index_candidate_present and limit_halt_present:
                    promotion_state = "promotable_now"
                    promotable_now_count += 1
                else:
                    promotion_state = "blocked_by_paired_surface_gap"
                    blocked_by_paired_surface_count += 1
            elif state == "already_covered":
                promotion_state = "already_covered"
            else:
                promotion_state = "blocked_no_candidate_cover"
                blocked_no_candidate_count += 1

            review_rows.append(
                {
                    "slice_id": row["slice_id"],
                    "decision_trade_date": trade_date,
                    "daily_candidate_state": state,
                    "raw_index_candidate_present": raw_index_candidate_present,
                    "limit_halt_materialized": limit_halt_present,
                    "promotion_review_state": promotion_state,
                }
            )

        residual_rows = [
            {
                "residual_class": "index_daily_pair_missing",
                "residual_reason": "daily candidate rows beyond 2024 do not yet have matching raw index daily candidate coverage",
            },
            {
                "residual_class": "limit_halt_pair_missing",
                "residual_reason": "limit-halt surface is still only materialized through 2024-12-31 and blocks paired promotion",
            },
            {
                "residual_class": "candidate_cover_absent_before_2024_or_after_2026_04_03",
                "residual_reason": "some shadow slices still have no raw daily candidate at all",
            },
        ]

        self.output_dir.mkdir(parents=True, exist_ok=True)

        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.review_path, review_rows)
        _write(self.residual_path, residual_rows)

        summary = {
            "review_row_count": len(review_rows),
            "promotable_now_count": promotable_now_count,
            "blocked_by_paired_surface_count": blocked_by_paired_surface_count,
            "blocked_no_candidate_count": blocked_no_candidate_count,
            "limit_halt_source_path": str(limit_halt_source_path.relative_to(self.repo_root)),
            "review_path": str(self.review_path.relative_to(self.repo_root)),
            "residual_path": str(self.residual_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareDailyMarketPromotionReviewV1(
            summary=summary, review_rows=review_rows, residual_rows=residual_rows
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareDailyMarketPromotionReviewV1(repo_root).materialize()
    print(result.summary["review_path"])


if __name__ == "__main__":
    main()
