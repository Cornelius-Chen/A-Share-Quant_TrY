from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    materialized_rows = rows or [{"row_state": "empty"}]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
        writer.writeheader()
        writer.writerows(materialized_rows)


def _join_top(rows: list[dict[str, Any]], key: str, limit: int = 5) -> str:
    values = [str(row.get(key, "")).strip() for row in rows[:limit]]
    return ",".join([value for value in values if value])


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsThemeSymbolHitReplayV1:
    summary: dict[str, Any]
    detail_rows: list[dict[str, Any]]
    summary_rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsThemeSymbolHitReplayV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        base = repo_root / "data" / "derived" / "info_center" / "time_slices"
        self.guidance_path = base / "a_share_internal_hot_news_trading_guidance_surface_v1.csv"
        self.watch_surface_path = base / "a_share_internal_hot_news_opportunity_symbol_watch_surface_v1.csv"
        self.detail_output_path = base / "a_share_internal_hot_news_theme_symbol_hit_replay_surface_v1.csv"
        self.summary_output_path = base / "a_share_internal_hot_news_theme_symbol_hit_replay_summary_v1.csv"
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_theme_symbol_hit_replay_registry_v1.csv"
        )

    def materialize(self) -> MaterializedAShareInternalHotNewsThemeSymbolHitReplayV1:
        guidance_rows = _read_csv(self.guidance_path)
        watch_rows = _read_csv(self.watch_surface_path)
        watch_by_telegraph = {row["telegraph_id"]: row for row in watch_rows}

        detail_rows: list[dict[str, Any]] = []
        for row in guidance_rows:
            primary_theme_slug = row.get("primary_theme_slug", "").strip() or "none"
            watch_row = watch_by_telegraph.get(row["telegraph_id"])

            if primary_theme_slug in {"", "none", "broad_market"}:
                replay_hit_state = "broad_market_only"
            elif watch_row:
                replay_hit_state = "theme_hit_with_symbol_watch"
            else:
                replay_hit_state = "theme_hit_without_symbol_watch"

            detail_rows.append(
                {
                    "telegraph_id": row["telegraph_id"],
                    "public_ts": row["public_ts"],
                    "guidance_class": row["guidance_class"],
                    "target_board": row["target_board"],
                    "target_theme_slug": row["target_theme_slug"],
                    "primary_theme_slug": primary_theme_slug,
                    "secondary_theme_slug": row.get("secondary_theme_slug", ""),
                    "theme_governance_state": row.get("theme_governance_state", ""),
                    "replay_hit_state": replay_hit_state,
                    "watch_symbol_count": "1" if watch_row else "0",
                    "top_watch_symbol": watch_row["beneficiary_symbol"] if watch_row else "",
                    "top_watch_linkage_class": watch_row["beneficiary_linkage_class"] if watch_row else "none",
                    "top_watch_mapping_confidence": watch_row["beneficiary_mapping_confidence"] if watch_row else "none",
                    "title": row["title"],
                    "replay_state": "theme_symbol_hit_replay_ready",
                }
            )

        themed_rows = [row for row in detail_rows if row["replay_hit_state"] != "broad_market_only"]
        symbol_rows = [row for row in detail_rows if row["replay_hit_state"] == "theme_hit_with_symbol_watch"]

        theme_counts: dict[str, int] = {}
        for row in themed_rows:
            theme_slug = row["primary_theme_slug"]
            theme_counts[theme_slug] = theme_counts.get(theme_slug, 0) + 1
        top_theme_slug = ""
        if theme_counts:
            top_theme_slug = max(theme_counts.items(), key=lambda item: (item[1], item[0]))[0]

        unique_watch_symbols = sorted({row["top_watch_symbol"] for row in symbol_rows if row["top_watch_symbol"]})
        summary_row = {
            "replay_id": "internal_hot_news_theme_symbol_hit_replay_latest",
            "sample_row_count": str(len(detail_rows)),
            "broad_market_only_count": str(sum(row["replay_hit_state"] == "broad_market_only" for row in detail_rows)),
            "theme_hit_count": str(len(themed_rows)),
            "theme_hit_with_symbol_watch_count": str(
                sum(row["replay_hit_state"] == "theme_hit_with_symbol_watch" for row in detail_rows)
            ),
            "theme_hit_without_symbol_watch_count": str(
                sum(row["replay_hit_state"] == "theme_hit_without_symbol_watch" for row in detail_rows)
            ),
            "unique_primary_theme_count": str(len({row["primary_theme_slug"] for row in themed_rows})),
            "unique_watch_symbol_count": str(len(unique_watch_symbols)),
            "top_primary_theme_slug": top_theme_slug or "none",
            "top_watch_symbol": symbol_rows[0]["top_watch_symbol"] if symbol_rows else "",
            "top_watch_symbols_top5": _join_top(symbol_rows, "top_watch_symbol"),
            "replay_summary_state": "theme_symbol_hit_replay_summarized",
        }

        _write_csv(self.detail_output_path, detail_rows)
        _write_csv(self.summary_output_path, [summary_row])
        _write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_theme_symbol_hit_replay_surface",
                    "artifact_path": str(self.detail_output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                },
                {
                    "view_id": "internal_hot_news_theme_symbol_hit_replay_summary",
                    "artifact_path": str(self.summary_output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                },
            ],
        )

        summary = {
            "sample_row_count": len(detail_rows),
            "broad_market_only_count": int(summary_row["broad_market_only_count"]),
            "theme_hit_count": int(summary_row["theme_hit_count"]),
            "theme_hit_with_symbol_watch_count": int(summary_row["theme_hit_with_symbol_watch_count"]),
            "theme_hit_without_symbol_watch_count": int(summary_row["theme_hit_without_symbol_watch_count"]),
            "unique_primary_theme_count": int(summary_row["unique_primary_theme_count"]),
            "unique_watch_symbol_count": int(summary_row["unique_watch_symbol_count"]),
            "top_primary_theme_slug": summary_row["top_primary_theme_slug"],
            "top_watch_symbol": summary_row["top_watch_symbol"],
            "authoritative_output": "a_share_internal_hot_news_theme_symbol_hit_replay_materialized",
        }
        return MaterializedAShareInternalHotNewsThemeSymbolHitReplayV1(
            summary=summary,
            detail_rows=detail_rows,
            summary_rows=[summary_row],
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsThemeSymbolHitReplayV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
