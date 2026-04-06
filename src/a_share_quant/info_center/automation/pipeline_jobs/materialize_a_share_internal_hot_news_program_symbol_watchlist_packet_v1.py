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


def _to_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _accepted_priority(title: str) -> int:
    return 1 if title.startswith("accepted_rotation_from_") else 0


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramSymbolWatchlistPacketV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramSymbolWatchlistPacketV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.symbol_watch_surface_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_opportunity_symbol_watch_surface_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_symbol_watchlist_packet_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_symbol_watchlist_packet_registry_v1.csv"
        )
        self.rotation_acceptance_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_primary_consumer_rotation_acceptance_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramSymbolWatchlistPacketV1:
        source_rows = _read_csv(self.symbol_watch_surface_path)
        acceptance_rows = _read_csv(self.rotation_acceptance_path)
        acceptance = acceptance_rows[0] if acceptance_rows else None

        best_by_symbol: dict[str, dict[str, str]] = {}
        for row in source_rows:
            symbol = row.get("beneficiary_symbol", "").strip()
            if not symbol:
                continue
            incumbent = best_by_symbol.get(symbol)
            if incumbent is None:
                best_by_symbol[symbol] = row
                continue
            incumbent_score = _to_float(incumbent.get("program_priority_score", "0"))
            row_score = _to_float(row.get("program_priority_score", "0"))
            if row_score > incumbent_score:
                best_by_symbol[symbol] = row

        ranked_rows = sorted(
            best_by_symbol.values(),
            key=lambda row: (
                -_to_float(row.get("program_priority_score", "0")),
                -_accepted_priority(row.get("title", "")),
                row.get("beneficiary_symbol_rank", "999"),
                row.get("beneficiary_symbol", ""),
            ),
        )

        if acceptance and acceptance.get("acceptance_state") == "accepted":
            accepted_symbol = acceptance["accepted_top_watch_symbol"]
            accepted_theme = acceptance["accepted_top_opportunity_theme"]
            accepted_row_id = acceptance["accepted_source_row_id"]
            accepted_source_family = acceptance["accepted_source_family"]
            template = ranked_rows[0] if ranked_rows else {
                "public_ts": "",
                "program_priority_score": "55.9000",
                "priority_band": "critical",
                "target_board": accepted_theme,
                "consumer_action_class": "top_down_guidance",
                "consumer_focus_class": "symbol_focus_available",
                "opportunity_consumer_gate": "watch_opportunity_non_trading_day",
                "opportunity_action_bias": "update_market_guidance",
                "trading_day_state": "unknown",
                "session_phase": "unknown",
                "session_handling_mode": "unknown",
                "window_state": "active_impact_window",
                "title": f"accepted_rotation_from_{accepted_source_family}",
            }
            accepted_packet_row = {
                **template,
                "beneficiary_symbol": accepted_symbol,
                "telegraph_id": accepted_row_id,
                "primary_theme_slug": accepted_theme,
                "secondary_theme_slug": "",
                "theme_governance_state": "accepted_rotation_override",
                "target_board": accepted_theme,
                "board_hit_state": "theme_detected_with_symbol_route",
                "beneficiary_mapping_confidence": "medium",
                "beneficiary_linkage_class": "direct_beneficiary",
                "title": f"accepted_rotation_from_{accepted_source_family}",
            }
            ranked_rows = [accepted_packet_row] + [
                row for row in ranked_rows if row.get("beneficiary_symbol") != accepted_symbol
            ]

        rows: list[dict[str, Any]] = []
        for watch_rank, row in enumerate(ranked_rows, start=1):
            rows.append(
                {
                    "watch_rank": str(watch_rank),
                    "beneficiary_symbol": row["beneficiary_symbol"],
                    "telegraph_id": row["telegraph_id"],
                    "public_ts": row["public_ts"],
                    "program_priority_score": row["program_priority_score"],
                    "priority_band": row["priority_band"],
                    "primary_theme_slug": row["primary_theme_slug"],
                    "secondary_theme_slug": row["secondary_theme_slug"],
                    "theme_governance_state": row["theme_governance_state"],
                    "target_board": row["target_board"],
                    "consumer_action_class": row["consumer_action_class"],
                    "consumer_focus_class": row["consumer_focus_class"],
                    "board_hit_state": row["board_hit_state"],
                    "beneficiary_mapping_confidence": row["beneficiary_mapping_confidence"],
                    "beneficiary_linkage_class": row.get("beneficiary_linkage_class", "unknown"),
                    "opportunity_consumer_gate": row["opportunity_consumer_gate"],
                    "opportunity_action_bias": row["opportunity_action_bias"],
                    "trading_day_state": row["trading_day_state"],
                    "session_phase": row["session_phase"],
                    "session_handling_mode": row["session_handling_mode"],
                    "window_state": row["window_state"],
                    "title": row["title"],
                    "watch_packet_state": "symbol_watch_packet_ready",
                }
            )

        self._write_csv(self.output_path, rows)
        self._write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_program_symbol_watchlist_packet",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "watchlist_row_count": len(rows),
            "unique_symbol_count": len({row["beneficiary_symbol"] for row in rows}),
            "top_watch_symbol": rows[0]["beneficiary_symbol"] if rows else "",
            "top_primary_theme_slug": rows[0]["primary_theme_slug"] if rows else "none",
            "top_mapping_confidence": rows[0]["beneficiary_mapping_confidence"] if rows else "unknown",
            "top_linkage_class": rows[0]["beneficiary_linkage_class"] if rows else "unknown",
            "authoritative_output": "a_share_internal_hot_news_program_symbol_watchlist_packet_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramSymbolWatchlistPacketV1(summary=summary, rows=rows)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramSymbolWatchlistPacketV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
