from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113PCPOFullBoardCoverageAndT1AuditReport:
    summary: dict[str, Any]
    cohort_symbol_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "cohort_symbol_rows": self.cohort_symbol_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


def load_symbol_set(path: Path) -> set[str]:
    symbols: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            symbol = str(row.get("symbol", "")).strip()
            if symbol:
                symbols.add(symbol)
    return symbols


class V113PCPOFullBoardCoverageAndT1AuditAnalyzer:
    def analyze(
        self,
        *,
        repo_root: Path,
        v112aa_payload: dict[str, Any],
        v113n_payload: dict[str, Any],
        v113o_payload: dict[str, Any],
    ) -> V113PCPOFullBoardCoverageAndT1AuditReport:
        cohort_rows = list(v112aa_payload.get("object_role_time_rows", []))
        if not cohort_rows:
            raise ValueError("V1.13P expects the bounded CPO cohort map.")

        n_summary = dict(v113n_payload.get("summary", {}))
        if str(n_summary.get("acceptance_posture")) != "freeze_v113n_cpo_real_board_episode_population_v1":
            raise ValueError("V1.13P expects V1.13N real episode population.")

        o_summary = dict(v113o_payload.get("summary", {}))
        if str(o_summary.get("acceptance_posture")) != "freeze_v113o_cpo_time_ordered_market_replay_prototype_v1":
            raise ValueError("V1.13P expects V1.13O replay prototype.")

        daily_symbols = load_symbol_set(repo_root / "data" / "raw" / "daily_bars" / "akshare_daily_bars_market_research_v1.csv")
        snapshot_symbols = load_symbol_set(repo_root / "data" / "derived" / "stock_snapshots" / "market_research_stock_snapshots_v1.csv")

        internal_rows = list(v113n_payload.get("internal_point_rows", []))
        labeled_objects = {str(row["object_id"]) for row in internal_rows}
        object_to_symbol = {
            "packaging_process_enabler": "300757",
            "core_module_leader": "300308",
            "high_beta_core_module": "300502",
            "laser_chip_component": "688498",
        }
        replay_action_symbols = {
            object_to_symbol[obj]
            for obj in labeled_objects
            if obj in object_to_symbol and object_to_symbol[obj] in daily_symbols
        }

        cohort_symbol_rows: list[dict[str, Any]] = []
        for row in cohort_rows:
            symbol = str(row["symbol"])
            cohort_symbol_rows.append(
                {
                    "symbol": symbol,
                    "cohort_layer": str(row["cohort_layer"]),
                    "role_family": str(row["role_family"]),
                    "current_posture": str(row["current_posture"]),
                    "in_daily_market_feed": symbol in daily_symbols,
                    "in_stock_snapshot_feed": symbol in snapshot_symbols,
                    "has_internal_episode_label": symbol in replay_action_symbols
                    or symbol in {
                        object_to_symbol.get(str(internal_row["object_id"]), "")
                        for internal_row in internal_rows
                    },
                    "action_replay_ready_now": symbol in replay_action_symbols,
                }
            )

        total_count = len(cohort_symbol_rows)
        daily_feed_count = sum(1 for row in cohort_symbol_rows if row["in_daily_market_feed"])
        snapshot_feed_count = sum(1 for row in cohort_symbol_rows if row["in_stock_snapshot_feed"])
        replay_ready_count = sum(1 for row in cohort_symbol_rows if row["action_replay_ready_now"])

        summary = {
            "acceptance_posture": "freeze_v113p_cpo_full_board_coverage_and_t1_audit_v1",
            "board_name": "CPO",
            "cohort_symbol_count": total_count,
            "daily_feed_covered_symbol_count": daily_feed_count,
            "snapshot_feed_covered_symbol_count": snapshot_feed_count,
            "action_replay_ready_symbol_count": replay_ready_count,
            "full_board_content_complete_now": daily_feed_count == total_count,
            "full_board_action_replay_ready_now": replay_ready_count == total_count,
            "t_plus_one_enabled_in_execution_layer": bool(o_summary.get("t_plus_one_enabled", False)),
            "recommended_next_posture": "complete_full_board_market_feed_binding_before_claiming_full_cpo_board_t_plus_one_replay_readiness",
        }
        interpretation = [
            "V1.13P audits full-board CPO coverage against the bounded cohort map instead of only the already-promoted replay subset.",
            "Current replay readiness is narrower than full board coverage: only symbols with lawful market feed plus internal action labels can trade now.",
            "T+1 is now enforced in the execution layer, but full-board T+1 replay readiness still depends on filling the missing CPO market feeds and labels.",
        ]
        return V113PCPOFullBoardCoverageAndT1AuditReport(
            summary=summary,
            cohort_symbol_rows=cohort_symbol_rows,
            interpretation=interpretation,
        )


def write_v113p_cpo_full_board_coverage_and_t1_audit_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113PCPOFullBoardCoverageAndT1AuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
