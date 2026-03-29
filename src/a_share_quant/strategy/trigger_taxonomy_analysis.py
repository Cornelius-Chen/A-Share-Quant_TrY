from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class TriggerTaxonomyReport:
    summary: dict[str, Any]
    taxonomy_rows: list[dict[str, Any]]
    trigger_leaderboard: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "taxonomy_rows": self.taxonomy_rows,
            "trigger_leaderboard": self.trigger_leaderboard,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class TriggerTaxonomyAnalyzer:
    """Classify action-state trigger rows into repair-relevant trigger types."""

    def analyze(self, *, payload: dict[str, Any], symbol: str) -> TriggerTaxonomyReport:
        trigger_rows = [
            row
            for row in payload.get("trigger_date_rows", [])
            if str(row.get("symbol")) == symbol
        ]
        taxonomy_rows = [self._classify_row(row) for row in trigger_rows]

        counter = Counter(row["trigger_type"] for row in taxonomy_rows)
        leaderboard = [
            {"trigger_type": trigger_type, "count": count}
            for trigger_type, count in counter.most_common()
        ]
        summary = {
            "symbol": symbol,
            "trigger_row_count": len(taxonomy_rows),
            "unique_trigger_type_count": len(counter),
            "top_trigger_type": leaderboard[0] if leaderboard else None,
            "core_rule": (
                "The most repair-worthy trigger types are the ones that repeatedly change the action sequence, "
                "not the ones that only alter passive state labels."
            ),
        }
        interpretation = [
            "Early-buy and missed-buy triggers usually point to entry-path issues.",
            "Forced-sell and missing-exit-partner triggers usually point to state carry or permission-loss issues.",
            "When the same trigger type repeats across all three strategies, it is much more likely to be a real structural blocker.",
        ]
        return TriggerTaxonomyReport(
            summary=summary,
            taxonomy_rows=taxonomy_rows,
            trigger_leaderboard=leaderboard,
            interpretation=interpretation,
        )

    def _classify_row(self, row: dict[str, Any]) -> dict[str, Any]:
        incumbent_actions = list(row.get("incumbent_emitted_actions", []))
        challenger_actions = list(row.get("challenger_emitted_actions", []))
        incumbent_position = int(row.get("incumbent_position_qty", 0))
        challenger_position = int(row.get("challenger_position_qty", 0))

        trigger_type = "other_action_state_trigger"
        if incumbent_actions == [] and challenger_actions == ["buy"]:
            trigger_type = "early_buy_trigger"
        elif incumbent_actions == [] and challenger_actions == ["sell"] and challenger_position > incumbent_position:
            trigger_type = "forced_sell_trigger"
        elif incumbent_actions == ["buy"] and challenger_actions == []:
            trigger_type = "missed_buy_trigger"
        elif incumbent_actions == ["sell"] and challenger_actions == [] and incumbent_position > challenger_position:
            trigger_type = "position_gap_exit_trigger"

        return {
            "symbol": str(row.get("symbol")),
            "strategy_name": str(row.get("strategy_name")),
            "trade_date": str(row.get("trade_date")),
            "trigger_type": trigger_type,
            "action_state_types": list(row.get("action_state_types", [])),
            "difference_types": list(row.get("difference_types", [])),
            "incumbent_emitted_actions": incumbent_actions,
            "challenger_emitted_actions": challenger_actions,
            "incumbent_position_qty": incumbent_position,
            "challenger_position_qty": challenger_position,
        }


def write_trigger_taxonomy_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: TriggerTaxonomyReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
