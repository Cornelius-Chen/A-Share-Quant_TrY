from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class TriggerPriorityReport:
    summary: dict[str, Any]
    strategy_cycle_rows: list[dict[str, Any]]
    trigger_family_priority: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "strategy_cycle_rows": self.strategy_cycle_rows,
            "trigger_family_priority": self.trigger_family_priority,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class TriggerPriorityAnalyzer:
    """Rank trigger families by the unique trade cycles they create."""

    def analyze(
        self,
        *,
        timeline_payload: dict[str, Any],
        taxonomy_payload: dict[str, Any],
        symbol: str,
        incumbent_name: str,
        challenger_name: str,
    ) -> TriggerPriorityReport:
        candidate_records = timeline_payload.get("candidate_records", [])
        grouped: dict[str, dict[str, dict[str, Any]]] = {}
        for record in candidate_records:
            if str(record.get("symbol")) != symbol:
                continue
            grouped.setdefault(str(record["strategy_name"]), {})[str(record["candidate_name"])] = record

        strategy_cycle_rows: list[dict[str, Any]] = []
        incumbent_unique_total = 0.0
        challenger_unique_total = 0.0
        for strategy_name, candidates in sorted(grouped.items()):
            incumbent = candidates.get(incumbent_name)
            challenger = candidates.get(challenger_name)
            if incumbent is None or challenger is None:
                continue
            incumbent_unique, challenger_unique = self._diff_unique_trades(
                incumbent_trades=list(incumbent.get("closed_trades", [])),
                challenger_trades=list(challenger.get("closed_trades", [])),
            )
            incumbent_unique_pnl = round(sum(float(item["pnl"]) for item in incumbent_unique), 6)
            challenger_unique_pnl = round(sum(float(item["pnl"]) for item in challenger_unique), 6)
            incumbent_unique_total += incumbent_unique_pnl
            challenger_unique_total += challenger_unique_pnl
            strategy_cycle_rows.append(
                {
                    "strategy_name": strategy_name,
                    "incumbent_unique_trade_count": len(incumbent_unique),
                    "challenger_unique_trade_count": len(challenger_unique),
                    "incumbent_unique_total_pnl": incumbent_unique_pnl,
                    "challenger_unique_total_pnl": challenger_unique_pnl,
                    "incumbent_unique_trades": incumbent_unique,
                    "challenger_unique_trades": challenger_unique,
                }
            )

        taxonomy_rows = [
            row
            for row in taxonomy_payload.get("taxonomy_rows", [])
            if str(row.get("symbol")) == symbol
        ]
        trigger_family_priority = self._build_priority_rows(
            taxonomy_rows=taxonomy_rows,
            incumbent_unique_total=round(incumbent_unique_total, 6),
            challenger_unique_total=round(challenger_unique_total, 6),
        )
        summary = {
            "symbol": symbol,
            "strategy_count": len(strategy_cycle_rows),
            "incumbent_unique_total_pnl": round(incumbent_unique_total, 6),
            "challenger_unique_total_pnl": round(challenger_unique_total, 6),
            "net_unique_cycle_delta": round(challenger_unique_total - incumbent_unique_total, 6),
            "top_priority_family": trigger_family_priority[0] if trigger_family_priority else None,
        }
        interpretation = [
            "Unique incumbent-side cycles indicate trigger families that caused the challenger to miss profitable or less-damaging participation.",
            "Unique challenger-side cycles indicate trigger families that added extra path variance, but they are not necessarily the largest source of net damage.",
            "The repair priority should go first to the trigger family that aligns with the larger unique-cycle pnl disadvantage.",
        ]
        return TriggerPriorityReport(
            summary=summary,
            strategy_cycle_rows=strategy_cycle_rows,
            trigger_family_priority=trigger_family_priority,
            interpretation=interpretation,
        )

    def _diff_unique_trades(
        self,
        *,
        incumbent_trades: list[dict[str, Any]],
        challenger_trades: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        incumbent_signatures = {self._trade_signature(item) for item in incumbent_trades}
        challenger_signatures = {self._trade_signature(item) for item in challenger_trades}
        incumbent_unique = [
            item for item in incumbent_trades if self._trade_signature(item) not in challenger_signatures
        ]
        challenger_unique = [
            item for item in challenger_trades if self._trade_signature(item) not in incumbent_signatures
        ]
        return incumbent_unique, challenger_unique

    def _trade_signature(self, trade: dict[str, Any]) -> tuple[Any, ...]:
        return (
            str(trade.get("entry_date")),
            str(trade.get("exit_date")),
            int(trade.get("quantity", 0)),
            round(float(trade.get("entry_price", 0.0)), 6),
            round(float(trade.get("exit_price", 0.0)), 6),
        )

    def _build_priority_rows(
        self,
        *,
        taxonomy_rows: list[dict[str, Any]],
        incumbent_unique_total: float,
        challenger_unique_total: float,
    ) -> list[dict[str, Any]]:
        family_counts: dict[str, int] = {}
        for row in taxonomy_rows:
            family = str(row.get("trigger_type"))
            family_counts[family] = family_counts.get(family, 0) + 1

        rows = [
            {
                "trigger_family": "missed_buy_trigger",
                "owner": "incumbent",
                "count": family_counts.get("missed_buy_trigger", 0),
                "aligned_unique_cycle_pnl": round(incumbent_unique_total, 6),
                "priority_reason": "Incumbent-only profitable or less-damaging cycles are the clearest missed-opportunity damage.",
            },
            {
                "trigger_family": "position_gap_exit_trigger",
                "owner": "incumbent",
                "count": family_counts.get("position_gap_exit_trigger", 0),
                "aligned_unique_cycle_pnl": round(incumbent_unique_total, 6),
                "priority_reason": "Position-gap exits are the paired exit-side expression of missed incumbent-only cycles.",
            },
            {
                "trigger_family": "early_buy_trigger",
                "owner": "challenger",
                "count": family_counts.get("early_buy_trigger", 0),
                "aligned_unique_cycle_pnl": round(challenger_unique_total, 6),
                "priority_reason": "Challenger-only early entry cycles add path variance, but may be net positive or offsetting.",
            },
            {
                "trigger_family": "forced_sell_trigger",
                "owner": "challenger",
                "count": family_counts.get("forced_sell_trigger", 0),
                "aligned_unique_cycle_pnl": round(challenger_unique_total, 6),
                "priority_reason": "Forced sell is the unwind side of challenger-only extra cycles.",
            },
        ]
        return sorted(
            rows,
            key=lambda item: (
                -float(item["aligned_unique_cycle_pnl"]) if item["owner"] == "incumbent" else float(item["aligned_unique_cycle_pnl"]),
                -int(item["count"]),
            ),
        )


def write_trigger_priority_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: TriggerPriorityReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
